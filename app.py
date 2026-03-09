import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Configuração da página - Estilo Sênior de Alta Densidade
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Comercial Estratégico",
    page_icon="📊"
)

# CSS Customizado para reduzir fontes e otimizar espaço
st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: bold;
    }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# IDs e GIDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787" # Aba 'Base de Dados'
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719" # Aba 'Cancelados'

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid: url += f"&gid={gid}"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro crítico ao carregar dados: {e}")
        return pd.DataFrame()

def encontrar_coluna(df, termos):
    if isinstance(termos, str): termos = [termos]
    for col in df.columns:
        for termo in termos:
            if termo.lower() in col.lower(): return col
    return None

def parse_currency(series):
    if series is None: return 0.0
    def clean_val(val):
        if pd.isna(val): return 0.0
        if isinstance(val, (int, float)): return float(val)
        s = str(val).replace('R$', '').strip()
        if not s: return 0.0
        if ',' in s: s = s.replace('.', '').replace(',', '.')
        elif '.' in s:
            parts = s.split('.')
            if len(parts[-1]) != 2: s = s.replace('.', '')
        try: return float(s)
        except: return 0.0
    return series.apply(clean_val)

def processar_dados():
    df_vendas_raw = load_data(VENDAS_ID, gid=VENDAS_GID)
    df_cancelados_raw = load_data(CANCELADOS_ID, gid=CANCELADOS_GID)
    if df_vendas_raw.empty: return None

    map_cols = {
        'vendedor': encontrar_coluna(df_vendas_raw, 'vendedor'),
        'sdr': encontrar_coluna(df_vendas_raw, 'sdr'),
        'cliente': encontrar_coluna(df_vendas_raw, 'cliente'),
        'cnpj': encontrar_coluna(df_vendas_raw, 'cnpj'),
        'produto': encontrar_coluna(df_vendas_raw, 'Qual produto?'),
        'data_ativacao': encontrar_coluna(df_vendas_raw, 'Data de Ativação'),
        'mrr': encontrar_coluna(df_vendas_raw, 'Mensalidade - Simples'),
        'adesao_s': encontrar_coluna(df_vendas_raw, 'Adesão - Simples'),
        'adesao_r': encontrar_coluna(df_vendas_raw, 'Adesão - Recupera'),
        'upgrade': encontrar_coluna(df_vendas_raw, 'Aumento da mensalidade'),
        'downgrade': encontrar_coluna(df_vendas_raw, 'Redução da mensalidade')
    }

    df = pd.DataFrame()
    df['vendedor'] = df_vendas_raw[map_cols['vendedor']] if map_cols['vendedor'] else "N/A"
    df['sdr'] = df_vendas_raw[map_cols['sdr']] if map_cols['sdr'] else "N/A"
    df['cliente'] = df_vendas_raw[map_cols['cliente']] if map_cols['cliente'] else "N/A"
    df['cnpj'] = df_vendas_raw[map_cols['cnpj']] if map_cols['cnpj'] else "N/A"
    
    if map_cols['produto']:
        df['produto'] = df_vendas_raw[map_cols['produto']].fillna("Sittax Simples")
        df.loc[df['produto'].astype(str).str.strip() == "", 'produto'] = "Sittax Simples"
    else: df['produto'] = "Sittax Simples"
    
    if map_cols['data_ativacao']:
        df['data'] = pd.to_datetime(df_vendas_raw[map_cols['data_ativacao']], errors='coerce', dayfirst=True)
        df['ano'] = df['data'].dt.year.fillna(0).astype(int)
        df['mes_num'] = df['data'].dt.month.fillna(0).astype(int)
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['mes_nome'] = df['mes_num'].map(meses_pt).fillna("Sem Data")
    else:
        df['data'] = pd.NaT
        df['ano'] = 0
        df['mes_nome'] = "Sem Data"

    df['mrr'] = parse_currency(df_vendas_raw[map_cols['mrr']]) if map_cols['mrr'] else 0.0
    df['adesao'] = parse_currency(df_vendas_raw[map_cols['adesao_s']]) + parse_currency(df_vendas_raw[map_cols['adesao_r']])
    df['upgrade'] = parse_currency(df_vendas_raw[map_cols['upgrade']]) if map_cols['upgrade'] else 0.0
    df['downgrade'] = parse_currency(df_vendas_raw[map_cols['downgrade']]) if map_cols['downgrade'] else 0.0
    df['receita_total'] = df['mrr'] + df['adesao']

    df['status'] = 'Confirmada'
    if map_cols['cnpj'] and not df_cancelados_raw.empty:
        vendas_cnpj = df_vendas_raw[map_cols['cnpj']].astype(str).str.replace(r'\D', '', regex=True)
        col_cnpj_canc = encontrar_coluna(df_cancelados_raw, 'cnpj')
        if col_cnpj_canc:
            canc_cnpjs = df_cancelados_raw[col_cnpj_canc].astype(str).str.replace(r'\D', '', regex=True).unique()
            df.loc[vendas_cnpj.isin(canc_cnpjs), 'status'] = 'Cancelada'
    
    df = df[~((df['cliente'] == "N/A") | (df['vendedor'] == "N/A") | (df['cliente'].isna()))]
    return df

# --- UI ---
df = processar_dados()

if df is not None and not df.empty:
    st.title("📊 Dashboard Comercial Estratégico")
    
    st.sidebar.header("🔍 Filtros de Análise")
    anos_lista = sorted([a for a in df['ano'].unique() if a != 0], reverse=True)
    ano_sel = st.sidebar.selectbox("Selecione o Ano", anos_lista)
    
    df_ano = df[df['ano'] == ano_sel]
    meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    meses_disponiveis = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
    meses_sel = st.sidebar.multiselect("Selecione os Meses", meses_disponiveis, default=meses_disponiveis)
    
    produtos = ["Todos"] + sorted(df['produto'].unique().tolist())
    produto_sel = st.sidebar.selectbox("Produto", produtos)
    
    vendedores = ["Todos"] + sorted(df['vendedor'].unique().tolist())
    vendedor_sel = st.sidebar.selectbox("Vendedor", vendedores)
    
    sdrs = ["Todos"] + sorted(df['sdr'].unique().tolist())
    sdr_sel = st.sidebar.selectbox("SDR", sdrs)
    
    df_f = df[df['ano'] == ano_sel].copy()
    if meses_sel: df_f = df_f[df_f['mes_nome'].isin(meses_sel)]
    if produto_sel != "Todos": df_f = df_f[df_f['produto'] == produto_sel]
    if vendedor_sel != "Todos": df_f = df_f[df_f['vendedor'] == vendedor_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]
    
    # --- CÁLCULOS ---
    mrr_conquistado = df_f[df_f['status'] == 'Confirmada']['mrr'].sum()
    mrr_cancelado = df_f[df_f['status'] == 'Cancelada']['mrr'].sum()
    mrr_ativo = mrr_conquistado - mrr_cancelado
    clientes_fechados = len(df_f[df_f['status'] == 'Confirmada'])
    clientes_cancelados = len(df_f[df_f['status'] == 'Cancelada'])
    ticket_medio = mrr_conquistado / clientes_fechados if clientes_fechados > 0 else 0
    total_ativacoes_hist = len(df[df['status'] == 'Confirmada'])
    total_cancelamentos_hist = len(df[df['status'] == 'Cancelada'])
    base_ativa_total = total_ativacoes_hist - total_cancelamentos_hist
    
    # Percentual de Churn para o Card
    perc_churn = (mrr_cancelado / mrr_conquistado * 100) if mrr_conquistado > 0 else 0

    # --- EXIBIÇÃO DE CARDS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MRR Conquistado", f"R$ {mrr_conquistado:,.2f}")
    c2.metric("MRR Ativo (Net New)", f"R$ {mrr_ativo:,.2f}")
    c3.metric("MRR Perdido (Churn)", f"R$ {mrr_cancelado:,.2f}", delta=f"{perc_churn:.1f}% do Conquistado", delta_color="inverse")
    c4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    
    st.write("")
    
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Clientes fechado (no periodo)", clientes_fechados)
    c6.metric("Clientes Cancelados (no periodo)", clientes_cancelados)
    c7.metric("Adesão total (no periodo)", f"R$ {df_f['adesao'].sum():,.2f}")
    c8.metric("Total Clientes Ativos (Base)", base_ativa_total)

    st.divider()
    
    # --- VISUALIZAÇÕES ---
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        # Evolução MRR Conquistado com Volume de Contratos
        df_evol = df_ano[df_ano['status'] == 'Confirmada'].groupby(['mes_num', 'mes_nome']).agg(
            mrr=('mrr', 'sum'),
            contratos=('cliente', 'count')
        ).reset_index().sort_values('mes_num')
        
        fig_evol = px.bar(df_evol, x='mes_nome', y='mrr', text='contratos',
                         title=f"Evolução Mensal de MRR Conquistado - {ano_sel}",
                         labels={'mes_nome': 'Mês', 'mrr': 'MRR (R$)', 'contratos': 'Contratos'},
                         color_discrete_sequence=['#2ECC71'])
        fig_evol.update_traces(texttemplate='%{text} Contratos', textposition='inside')
        st.plotly_chart(fig_evol, use_container_width=True)
        
    with col_dir:
        # Evolução MRR Perdido com Volume de Contratos
        df_churn_evol = df_ano[df_ano['status'] == 'Cancelada'].groupby(['mes_num', 'mes_nome']).agg(
            mrr=('mrr', 'sum'),
            contratos=('cliente', 'count')
        ).reset_index().sort_values('mes_num')
        
        # Garantir meses vazios
        df_meses = pd.DataFrame({'mes_num': range(1, 13), 'mes_nome': meses_ordem})
        df_churn_evol = df_meses.merge(df_churn_evol, on=['mes_num', 'mes_nome'], how='left').fillna(0)
        
        fig_churn = px.bar(df_churn_evol, x='mes_nome', y='mrr', text='contratos',
                          title=f"Evolução Mensal de MRR Perdido (Churn) - {ano_sel}",
                          labels={'mes_nome': 'Mês', 'mrr': 'MRR Perdido (R$)', 'contratos': 'Contratos'},
                          color_discrete_sequence=['#E74C3C'])
        fig_churn.update_traces(texttemplate='%{text} Contratos', textposition='inside')
        st.plotly_chart(fig_churn, use_container_width=True)

    # Gráfico de Pizza Restaurado
    st.divider()
    col_pizza, col_vazio = st.columns([1, 1])
    with col_pizza:
        fig_produto = px.pie(df_f, names='produto', values='receita_total', 
                          title="Distribuição de Receita por Produto", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_produto, use_container_width=True)

    # Tabela de Detalhamento
    st.subheader("📋 Detalhamento das Operações")
    cols_view = ['data', 'cliente', 'vendedor', 'sdr', 'produto', 'status', 'mrr', 'adesao']
    st.dataframe(df_f[cols_view].sort_values('data', ascending=False), use_container_width=True)

else:
    st.error("Nenhum dado válido encontrado para os filtros selecionados.")
