import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Configuração da página - Estilo Sênior
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Comercial Otimizado",
    page_icon="📊"
)

# IDs e GIDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787" # Aba 'Base de Dados'
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719" # Aba 'Cancelados'

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    """Carregamento otimizado via exportação CSV do Google Sheets"""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid:
        url += f"&gid={gid}"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro crítico ao carregar dados: {e}")
        return pd.DataFrame()

def encontrar_coluna(df, termos):
    """Busca flexível de colunas por múltiplos termos possíveis"""
    if isinstance(termos, str): termos = [termos]
    for col in df.columns:
        for termo in termos:
            if termo.lower() in col.lower():
                return col
    return None

def parse_currency(series):
    """Conversão robusta de Moeda BRL para Float"""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(r'[R$]', '', regex=True)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip(),
        errors='coerce'
    ).fillna(0.0)

def processar_dados():
    df_vendas = load_data(VENDAS_ID, gid=VENDAS_GID)
    df_cancelados = load_data(CANCELADOS_ID, gid=CANCELADOS_GID)
    
    if df_vendas.empty:
        return None

    # Mapeamento Dinâmico de Colunas
    map_cols = {
        'vendedor': encontrar_coluna(df_vendas, 'vendedor'),
        'sdr': encontrar_coluna(df_vendas, 'sdr'),
        'cliente': encontrar_coluna(df_vendas, 'cliente'),
        'cnpj': encontrar_coluna(df_vendas, 'cnpj'),
        'plano': encontrar_coluna(df_vendas, 'plano'),
        'data': encontrar_coluna(df_vendas, 'data'),
        'mrr': encontrar_coluna(df_vendas, 'Mensalidade - Simples'),
        'adesao_s': encontrar_coluna(df_vendas, 'Adesão - Simples'),
        'adesao_r': encontrar_coluna(df_vendas, 'Adesão - Recupera'),
        'upgrade': encontrar_coluna(df_vendas, 'Aumento da mensalidade'),
        'downgrade': encontrar_coluna(df_vendas, 'Redução da mensalidade')
    }

    # Construção do DataFrame de Análise
    df = pd.DataFrame()
    df['vendedor'] = df_vendas[map_cols['vendedor']] if map_cols['vendedor'] else "N/A"
    df['sdr'] = df_vendas[map_cols['sdr']] if map_cols['sdr'] else "N/A"
    df['cliente'] = df_vendas[map_cols['cliente']] if map_cols['cliente'] else "N/A"
    df['plano'] = df_vendas[map_cols['plano']] if map_cols['plano'] else "N/A"
    
    # Engenharia de Datas Otimizada
    if map_cols['data']:
        df['data'] = pd.to_datetime(df_vendas[map_cols['data']], errors='coerce', dayfirst=True)
        df['mes_ano'] = df['data'].dt.strftime('%Y-%m')
        df['semana'] = df['data'].dt.isocalendar().week
        df['inicio_semana'] = df['data'].dt.to_period('W').apply(lambda r: r.start_time)
    else:
        df['data'] = None
        df['mes_ano'] = "N/A"

    # Processamento Financeiro
    df['mrr'] = parse_currency(df_vendas[map_cols['mrr']]) if map_cols['mrr'] else 0.0
    df['adesao'] = parse_currency(df_vendas[map_cols['adesao_s']]) + parse_currency(df_vendas[map_cols['adesao_r']])
    df['upgrade'] = parse_currency(df_vendas[map_cols['upgrade']]) if map_cols['upgrade'] else 0.0
    df['downgrade'] = parse_currency(df_vendas[map_cols['downgrade']]) if map_cols['downgrade'] else 0.0
    df['receita_total'] = df['mrr'] + df['adesao']

    # Cruzamento de Cancelados (Churn)
    df['status'] = 'Confirmada'
    if map_cols['cnpj'] and not df_cancelados.empty:
        vendas_cnpj = df_vendas[map_cols['cnpj']].astype(str).str.replace(r'\D', '', regex=True)
        col_cnpj_canc = encontrar_coluna(df_cancelados, 'cnpj')
        if col_cnpj_canc:
            canc_cnpjs = df_cancelados[col_cnpj_canc].astype(str).str.replace(r'\D', '', regex=True).unique()
            df.loc[vendas_cnpj.isin(canc_cnpjs), 'status'] = 'Cancelada'
    
    return df

# --- UI DASHBOARD ---
df = processar_dados()

if df is not None:
    st.title("📊 Dashboard Comercial Estratégico")
    
    # Sidebar - Filtros Avançados
    st.sidebar.header("🔍 Filtros de Análise")
    
    # Filtro de Mês/Ano
    meses = ["Todos"] + sorted(df['mes_ano'].unique().tolist(), reverse=True)
    mes_sel = st.sidebar.selectbox("Período (Mês/Ano)", meses)
    
    # Filtro de Vendedor
    vendedores = ["Todos"] + sorted(df['vendedor'].unique().tolist())
    vendedor_sel = st.sidebar.selectbox("Vendedor", vendedores)
    
    # Filtro de SDR
    sdrs = ["Todos"] + sorted(df['sdr'].unique().tolist())
    sdr_sel = st.sidebar.selectbox("SDR", sdrs)
    
    # Aplicação de Filtros em Cascata
    df_f = df.copy()
    if mes_sel != "Todos":
        df_f = df_f[df_f['mes_ano'] == mes_sel]
    if vendedor_sel != "Todos":
        df_f = df_f[df_f['vendedor'] == vendedor_sel]
    if sdr_sel != "Todos":
        df_f = df_f[df_f['sdr'] == sdr_sel]
    
    # KPIs Estratégicos
    c1, c2, c3, c4 = st.columns(4)
    
    mrr_total = df_f['mrr'].sum()
    adesao_total = df_f['adesao'].sum()
    saldo_up_down = df_f['upgrade'].sum() - df_f['downgrade'].sum()
    taxa_cancelamento = (len(df_f[df_f['status'] == 'Cancelada']) / len(df_f) * 100) if len(df_f) > 0 else 0
    
    c1.metric("MRR Total", f"R$ {mrr_total:,.2f}")
    c2.metric("Adesão Total", f"R$ {adesao_total:,.2f}")
    c3.metric("Saldo Up/Down", f"R$ {saldo_up_down:,.2f}", delta=saldo_up_down)
    c4.metric("Churn Rate", f"{taxa_cancelamento:.1f}%", delta_color="inverse")

    st.divider()
    
    # Visualizações
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        fig_plano = px.pie(df_f, names='plano', values='receita_total', 
                          title="Receita Total por Plano", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_plano, use_container_width=True)
        
    with col_dir:
        # Gráfico de Status com cores semânticas
        status_counts = df_f['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'quantidade']
        fig_status = px.bar(status_counts, x='status', y='quantidade', 
                           title="Volume de Vendas por Status",
                           color='status',
                           color_discrete_map={'Confirmada': '#2ECC71', 'Cancelada': '#E74C3C'})
        st.plotly_chart(fig_status, use_container_width=True)

    # Tabela de Detalhamento com colunas selecionadas
    st.subheader("📋 Detalhamento das Operações")
    cols_view = ['data', 'cliente', 'vendedor', 'sdr', 'plano', 'status', 'mrr', 'adesao']
    st.dataframe(df_f[cols_view].sort_values('data', ascending=False), use_container_width=True)

else:
    st.error("Falha na conexão com os dados. Verifique as permissões das planilhas.")
