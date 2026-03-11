import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

# Configuração da página - Estilo Sênior Premium
st.set_page_config(layout="wide", page_title="Dashboard Comercial Estratégico", page_icon="📊")

# Paleta de Cores Acelerar.tech
COLOR_PRIMARY = "#0B2A4E"  # Azul Marinho
COLOR_SECONDARY = "#89CFF0" # Azul Claro
COLOR_TEXT = "#FFFFFF"      # Branco
COLOR_BG = "#F0F2F6"        # Cinza Claro Fundo
COLOR_CHURN = "#E74C3C"     # Vermelho para Perdas

# Função para carregar imagem local e converter para base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# Estilização CSS Customizada - REFINADA
st.markdown(f"""
    <style>
    .main {{ background-color: {COLOR_BG}; }}
    
    /* Estilo Base dos Cards */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_PRIMARY} !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        color: {COLOR_TEXT} !important;
        min-width: 180px !important;
    }}
    
    /* Ajuste para evitar corte de texto */
    div[data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        color: {COLOR_TEXT} !important;
    }}
    
    div[data-testid="stMetricLabel"] > div {{
        color: {COLOR_TEXT} !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
    }}

    /* CSS EXCLUSIVO PARA O CARD DE CHURN (3º CARD DA LINHA 1) */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {{
        border: 2px solid {COLOR_CHURN} !important;
    }}
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricLabel"] > div,
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"],
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] > div {{
        color: {COLOR_CHURN} !important;
    }}
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] svg {{
        fill: {COLOR_CHURN} !important;
        transform: rotate(180deg) !important; /* Seta para baixo */
    }}

    /* CSS para o Upsell (Manter Original) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricDelta"] {{
        color: {COLOR_SECONDARY} !important;
    }}
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricDelta"] svg {{
        fill: {COLOR_SECONDARY} !important;
    }}

    h1, h2, h3 {{ color: {COLOR_PRIMARY}; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    
    [data-testid="stSidebar"] {{ background-color: {COLOR_PRIMARY}; color: {COLOR_TEXT}; }}
    [data-testid="stSidebar"] label {{ color: {COLOR_TEXT} !important; }}
    [data-testid="stSidebar"] .stSelectbox div {{ color: {COLOR_PRIMARY} !important; }}
    </style>
    """, unsafe_allow_html=True)

# IDs e GIDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719"
CONTAS_RECEBER_ID = "1Nqmn2c9p0QFu8LFIqFQ0EBxA8klHFUsVjAW15la-Fjg"

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    if gid:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

def parse_currency(series):
    def clean_val(val):
        if pd.isna(val) or val == "": return 0.0
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
    df_v = load_data(VENDAS_ID, VENDAS_GID)
    df_c = load_data(CANCELADOS_ID, CANCELADOS_GID)
    df_cr = load_data(CONTAS_RECEBER_ID)

    if df_v.empty: return None, None

    df = pd.DataFrame()
    df['vendedor'] = df_v['Vendedor'].fillna("N/A")
    df['sdr'] = df_v['SDR'].fillna("N/A")
    df['cliente'] = df_v['Cliente'].fillna("N/A")
    df['cnpj'] = df_v['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True)
    df['produto'] = df_v['Qual produto?'].fillna("Sittax Simples")
    df.loc[df['produto'].astype(str).str.strip() == "", 'produto'] = "Sittax Simples"

    df['mrr'] = parse_currency(df_v['Mensalidade - Simples'])
    df['adesao'] = parse_currency(df_v['Adesão - Simples']) + parse_currency(df_v['Adesão - Recupera'])
    df['upgrade'] = parse_currency(df_v['Aumento da mensalidade'])
    df['downgrade'] = parse_currency(df_v['Redução da mensalidade'])

    df['data_h'] = pd.to_datetime(df_v['Data de Ativação'], errors='coerce', dayfirst=False)
    df['data_x'] = pd.to_datetime(df_v['Data alteração de CNPJ'], errors='coerce', dayfirst=False)
    
    df['data'] = df['data_h']
    df.loc[df['upgrade'] > 0, 'data'] = df['data_x']
    
    df = df.dropna(subset=['data'])
    df['ano'] = df['data'].dt.year.astype(int)
    df['mes_num'] = df['data'].dt.month.astype(int)
    meses_pt = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho',
                7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
    df['mes_nome'] = df['mes_num'].map(meses_pt)
    df['inicio_semana'] = df['data'].apply(lambda x: x - pd.Timedelta(days=x.weekday()))

    df['status'] = 'Confirmada'
    if not df_c.empty:
        canc_cnpjs = df_c['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True).unique()
        df.loc[df['cnpj'].isin(canc_cnpjs), 'status'] = 'Cancelada'
    
    return df, df_cr

# --- UI ---
df_processed, df_contas_receber = processar_dados()
if df_processed is not None:
    df = df_processed

    # Sidebar com Logotipo
    logo_base64 = get_base64_of_bin_file('/home/ubuntu/logo_acelerar_tech.png')
    if logo_base64:
        st.sidebar.markdown(
            f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_base64}" width="200"></div>',
            unsafe_allow_html=True
        )
    
    st.sidebar.divider()
    st.sidebar.header("🔍 Filtros")
    anos = sorted(df['ano'].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano", anos)
    df_ano = df[df['ano'] == ano_sel]
    
    meses_ordem = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
    meses_sel = st.sidebar.multiselect("Meses", meses_disp, default=meses_disp)
    
    prod_sel = st.sidebar.selectbox("Produto", ["Todos"] + sorted(df['produto'].unique().tolist()))
    vend_sel = st.sidebar.selectbox("Vendedor", ["Todos"] + sorted(df['vendedor'].unique().tolist()))
    sdr_sel = st.sidebar.selectbox("SDR", ["Todos"] + sorted(df['sdr'].unique().tolist()))

    df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]

    # KPIs
    mrr_conq = df_f[df_f['status'] == 'Confirmada']['mrr'].sum()
    mrr_perd = df_f[df_f['status'] == 'Cancelada']['mrr'].sum()
    upsell_v = df_f['upgrade'].sum()
    upsell_q = len(df_f[df_f['upgrade'] > 0])
    cl_fech = len(df_f[(df_f['status'] == 'Confirmada') & (df_f['mrr'] > 0)])
    cl_canc = len(df_f[df_f['status'] == 'Cancelada'])
    tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
    base_ativa = len(df[df['status'] == 'Confirmada']) - len(df[df['status'] == 'Cancelada'])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0

    st.title("📊 Dashboard Comercial Estratégico")
    
    # Linha 1 de KPIs (5 colunas)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("MRR Conquistado", f"R$ {mrr_conq:,.2f}")
    c2.metric("MRR Ativo (Net)", f"R$ {mrr_conq - mrr_perd:,.2f}")
    c3.metric("MRR Perdido (Churn)", f"R$ {mrr_perd:,.2f}", delta=f"{churn_p:.1f}% do Conq", delta_color="normal")
    c4.metric("Total de Upsell", f"R$ {upsell_v:,.2f}", delta=f"{upsell_q} eventos", delta_color="normal")
    c5.metric("Ticket Médio", f"R$ {tkt_med:,.2f}")
    
    # Linha 2 de KPIs (4 colunas)
    c6, c7, c8, c9 = st.columns(4)
    c6.metric("Adesão Total", f"R$ {df_f['adesao'].sum():,.2f}")
    c7.metric("Clientes fechado", cl_fech)
    c8.metric("Clientes Cancelados", cl_canc)
    c9.metric("Total Base Ativa", base_ativa)

    st.divider()
    
    st.subheader("📈 Evolução Mensal")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        df_m = df_ano[df_ano['status'] == 'Confirmada'].groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
        fig = px.bar(df_m, x='mes_nome', y='mrr', text='cliente', title="MRR Conquistado", color_discrete_sequence=[COLOR_PRIMARY])
        fig.update_traces(texttemplate='%{text}', textposition='inside')
        fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_u = df_ano[df_ano['upgrade'] > 0].groupby(['mes_num','mes_nome']).agg({'upgrade':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
        fig = px.bar(df_u, x='mes_nome', y='upgrade', text='cliente', title="Evolução de Upsell", color_discrete_sequence=[COLOR_SECONDARY])
        fig.update_traces(texttemplate='%{text}', textposition='inside')
        fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        df_c_evol = df_ano[df_ano['status'] == 'Cancelada'].groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
        df_c_evol = df_c_evol[df_c_evol['mrr'] > 0]
        fig = px.bar(df_c_evol, x='mes_nome', y='mrr', text='cliente', title="Evolução de Churn", color_discrete_sequence=[COLOR_CHURN])
        fig.update_traces(texttemplate='%{text}', textposition='inside')
        fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    st.subheader("🎯 Performance vs. Metas")
    col4, col5 = st.columns(2)
    
    df_meta = df_f[df_f['status'] == 'Confirmada'].groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
    if not df_meta.empty:
        df_meta['mrr_a'] = df_meta['mrr'].cumsum()
        df_meta['cont_a'] = df_meta['cliente'].cumsum()
        df_meta['meta_m'] = [8000 * (i+1) for i in range(len(df_meta))]
        df_meta['meta_c'] = [17 * (i+1) for i in range(len(df_meta))]

        with col4:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_meta['mes_nome'], y=df_meta['mrr_a'], name='Real', marker_color=COLOR_PRIMARY))
            fig.add_trace(go.Scatter(x=df_meta['mes_nome'], y=df_meta['meta_m'], name='Meta (8k/mês)', line=dict(color='#F1C40F', width=4)))
            fig.update_layout(title="MRR Acumulado vs. Meta", xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col5:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_meta['mes_nome'], y=df_meta['cont_a'], name='Real', marker_color=COLOR_SECONDARY))
            fig.add_trace(go.Scatter(x=df_meta['mes_nome'], y=df_meta['meta_c'], name='Meta (17/mês)', line=dict(color='#F39C12', width=4)))
            fig.update_layout(title="Contratos Acumulados vs. Meta", xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    col6, col7 = st.columns(2)
    with col6:
        df_s = df_f[df_f['status'] == 'Confirmada'].groupby('inicio_semana')['mrr'].sum().reset_index().sort_values('inicio_semana')
        df_s['data_s'] = df_s['inicio_semana'].dt.strftime('%d/%m/%Y')
        fig = go.Figure(go.Scatter(x=df_s['data_s'], y=df_s['mrr'], mode='lines+markers+text', text=df_s['mrr'].apply(lambda x: f"{x:,.0f}"), textposition="top center", line=dict(color=COLOR_PRIMARY, width=4)))
        fig.update_layout(title="MRR SEMANA", xaxis_title=None, yaxis_title=None, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col7:
        fig = px.pie(df_f, names='produto', values='mrr', title="Receita por Produto", hole=0.4, color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#1A3A5A', '#2E5A88'])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- RANKINGS DE VENDEDORES (REPOSICIONADO AQUI) ---
    st.subheader("🏆 Rankings de Vendedores")
    col_rank1, col_rank2 = st.columns(2)

    with col_rank1:
        df_rank_contratos = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['cliente'].count().sort_values(ascending=False).reset_index()
        df_rank_contratos.columns = ['Vendedor', 'Contratos']
        # Alterado para Pizza conforme solicitado
        fig_contratos = px.pie(df_rank_contratos.head(10), values='Contratos', names='Vendedor', 
                               title='Top Vendedores (Contratos)', hole=0.4,
                               color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#1A3A5A', '#2E5A88'])
        fig_contratos.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}: %{value}")
        st.plotly_chart(fig_contratos, use_container_width=True)

    with col_rank2:
        df_rank_mrr = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['mrr'].sum().sort_values(ascending=False).reset_index()
        df_rank_mrr.columns = ['Vendedor', 'MRR']
        # Alterado para Pizza conforme solicitado
        fig_mrr = px.pie(df_rank_mrr.head(10), values='MRR', names='Vendedor', 
                         title='Top Vendedores (MRR)', hole=0.4,
                         color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#1A3A5A', '#2E5A88'])
        fig_mrr.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}: R$ %{value:,.2f}")
        st.plotly_chart(fig_mrr, use_container_width=True)

    st.divider()

    st.subheader("📋 Detalhamento")
    st.dataframe(df_f[['data', 'cliente', 'vendedor', 'produto', 'status', 'mrr', 'upgrade', 'adesao']].sort_values('data', ascending=False), use_container_width=True)

    # Verificação silenciosa da nova planilha
    if df_contas_receber is not None and not df_contas_receber.empty:
        with st.expander("🔍 Verificação: Dados Contas a Receber"):
            st.dataframe(df_contas_receber.head())

else:
    st.error("Nenhum dado válido encontrado para os filtros selecionados.")
