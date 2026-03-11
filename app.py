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

# Estilização CSS Customizada - CORREÇÃO AGRESSIVA DO CHURN
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
    
    div[data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        color: {COLOR_TEXT} !important;
    }}
    
    div[data-testid="stMetricLabel"] > div {{
        color: {COLOR_TEXT} !important;
        font-weight: bold !important;
    }}

    /* --- CORREÇÃO DO CARD DE CHURN (3º CARD) --- */
    /* Forçar cor vermelha no label e valor */
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricLabel"] > div,
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] {{
        color: {COLOR_CHURN} !important;
    }}
    
    /* Forçar cor vermelha na pílula do Delta e inverter seta */
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricDelta"] > div {{
        color: {COLOR_CHURN} !important;
        background-color: rgba(231, 76, 60, 0.2) !important;
    }}
    
    /* Inverter a seta para baixo e mudar cor do ícone */
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricDelta"] svg {{
        fill: {COLOR_CHURN} !important;
        transform: rotate(180deg) !important;
    }}

    /* REFINAMENTO DA SIDEBAR */
    [data-testid="stSidebar"] {{ background-color: {COLOR_PRIMARY} !important; }}
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stExpander p,
    [data-testid="stSidebar"] .stMultiSelect label {{
        color: {COLOR_TEXT} !important;
    }}
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {{
        background-color: #F8F9FA !important;
        color: {COLOR_PRIMARY} !important;
    }}
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
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv" + (f"&gid={gid}" if gid else "" )
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

def parse_currency(series):
    def clean_val(val):
        if pd.isna(val) or val == "": return 0.0
        if isinstance(val, (int, float)): return float(val)
        s = str(val).replace('R$', '').strip()
        if ',' in s: s = s.replace('.', '').replace(',', '.')
        elif '.' in s and len(s.split('.')[-1]) != 2: s = s.replace('.', '')
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
    df['mrr'] = parse_currency(df_v['Mensalidade - Simples'])
    df['adesao'] = parse_currency(df_v['Adesão - Simples']) + parse_currency(df_v['Adesão - Recupera'])
    df['upgrade'] = parse_currency(df_v['Aumento da mensalidade'])
    df['data'] = pd.to_datetime(df_v['Data de Ativação'], errors='coerce')
    df = df.dropna(subset=['data'])
    df['ano'] = df['data'].dt.year.astype(int)
    df['mes_num'] = df['data'].dt.month.astype(int)
    meses_pt = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
    df['mes_nome'] = df['mes_num'].map(meses_pt)
    df['inicio_semana'] = df['data'].apply(lambda x: x - pd.Timedelta(days=x.weekday()))
    df['status'] = 'Confirmada'
    if not df_c.empty:
        canc_cnpjs = df_c['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True).unique()
        df.loc[df['cnpj'].isin(canc_cnpjs), 'status'] = 'Cancelada'
    return df, df_cr

df_processed, df_contas_receber = processar_dados()
if df_processed is not None:
    df = df_processed
    logo_base64 = get_base64_of_bin_file('/home/ubuntu/logo_acelerar_tech.png')
    if logo_base64:
        st.sidebar.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{logo_base64}" width="180"></div>', unsafe_allow_html=True)
    
    anos = sorted(df['ano'].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("📅 Ano", anos)
    df_ano = df[df['ano'] == ano_sel]
    with st.sidebar.expander("📅 Período (Meses)"):
        meses_ordem = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
        meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
        meses_sel = st.multiselect("Meses", meses_disp, default=meses_disp)
    
    prod_sel = st.sidebar.selectbox("📦 Produto", ["Todos"] + sorted(df['produto'].unique().tolist()))
    vend_sel = st.sidebar.selectbox("👤 Vendedor", ["Todos"] + sorted(df['vendedor'].unique().tolist()))
    sdr_sel = st.sidebar.selectbox("🎧 SDR", ["Todos"] + sorted(df['sdr'].unique().tolist()))

    df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]

    mrr_conq = df_f[df_f['status'] == 'Confirmada']['mrr'].sum()
    mrr_perd = df_f[df_f['status'] == 'Cancelada']['mrr'].sum()
    upsell_v = df_f['upgrade'].sum()
    cl_fech = len(df_f[(df_f['status'] == 'Confirmada') & (df_f['mrr'] > 0)])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0

    st.title("📊 Dashboard Comercial Estratégico")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
    c2.metric("MRR Ativo (Net)", f"R$ {int(mrr_conq - mrr_perd):,}".replace(",", "."))
    # Card de Churn com Delta formatado
    c3.metric("MRR Perdido (Churn)", f"R$ {int(mrr_perd):,}".replace(",", "."), delta=f"{churn_p:.1f}% do Conq")
    c4.metric("Total de Upsell", f"R$ {int(upsell_v):,}".replace(",", "."))
    c5.metric("Ticket Médio", f"R$ {int(mrr_conq/cl_fech if cl_fech > 0 else 0):,}".replace(",", "."))
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        df_m = df_ano[df_ano['status'] == 'Confirmada'].groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
        st.plotly_chart(px.bar(df_m, x='mes_nome', y='mrr', text='cliente', title="MRR Conquistado", color_discrete_sequence=[COLOR_PRIMARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)
    with col2:
        df_u = df_ano[df_ano['upgrade'] > 0].groupby(['mes_num','mes_nome']).agg({'upgrade':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
        st.plotly_chart(px.bar(df_u, x='mes_nome', y='upgrade', text='cliente', title="Evolução de Upsell", color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)
    with col3:
        df_c_evol = df_ano[df_ano['status'] == 'Cancelada'].groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
        st.plotly_chart(px.bar(df_c_evol[df_c_evol['mrr']>0], x='mes_nome', y='mrr', text='cliente', title="Evolução de Churn", color_discrete_sequence=[COLOR_PRIMARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)

    st.divider()
    st.subheader("🏆 Rankings de SDRs (Top 5)")
    cs1, cs2 = st.columns(2)
    with cs1:
        df_s_c = df_f[df_f['status'] == 'Confirmada'].groupby('sdr')['cliente'].count().sort_values().tail(5).reset_index()
        st.plotly_chart(px.bar(df_s_c, x='cliente', y='sdr', orientation='h', title='Top 5 SDRs (Contratos)', text='cliente', color_discrete_sequence=[COLOR_PRIMARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', height=300), use_container_width=True)
    with cs2:
        df_s_m = df_f[df_f['status'] == 'Confirmada'].groupby('sdr')['mrr'].sum().sort_values().tail(5).reset_index()
        st.plotly_chart(px.bar(df_s_m, x='mrr', y='sdr', orientation='h', title='Top 5 SDRs (MRR)', text=df_s_m['mrr'].apply(lambda x: f"R$ {int(x):,}"), color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', height=300), use_container_width=True)

    st.divider()
    st.subheader("🏆 Rankings de Vendedores")
    cv1, cv2 = st.columns(2)
    with cv1:
        df_v_c = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['cliente'].count().sort_values().tail(10).reset_index()
        st.plotly_chart(px.bar(df_v_c, x='cliente', y='vendedor', orientation='h', title='Top Vendedores (Contratos)', text='cliente', color_discrete_sequence=[COLOR_PRIMARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', height=400), use_container_width=True)
    with cv2:
        df_v_m = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['mrr'].sum().sort_values().tail(10).reset_index()
        st.plotly_chart(px.bar(df_v_m, x='mrr', y='vendedor', orientation='h', title='Top Vendedores (MRR)', text=df_v_m['mrr'].apply(lambda x: f"R$ {int(x):,}"), color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', height=400), use_container_width=True)

    st.divider()
    st.subheader("📋 Detalhamento")
    st.dataframe(df_f[['data', 'cliente', 'vendedor', 'sdr', 'produto', 'status', 'mrr', 'upgrade']].sort_values('data', ascending=False), use_container_width=True)
