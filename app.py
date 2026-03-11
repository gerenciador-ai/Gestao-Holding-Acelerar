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

# Inicializar session_state para navegação
if 'page' not in st.session_state:
    st.session_state.page = 'comercial'

# Função para carregar imagem local e converter para base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# Estilização CSS Customizada
st.markdown(f"""
    <style>
    .main {{ background-color: {COLOR_BG}; }}
    div[data-testid="stMetric"] {{
        background-color: {COLOR_PRIMARY} !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        color: {COLOR_TEXT} !important;
        min-width: 180px !important;
    }}
    div[data-testid="stMetricValue"] {{ font-size: 1.6rem !important; color: {COLOR_TEXT} !important; }}
    div[data-testid="stMetricLabel"] > div {{ color: {COLOR_TEXT} !important; font-weight: bold !important; }}
    [data-testid="stSidebar"] {{ background-color: {COLOR_PRIMARY} !important; }}
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {{ color: {COLOR_TEXT} !important; }}
    h1, h2, h3 {{ color: {COLOR_PRIMARY}; font-family: 'Segoe UI', sans-serif; }}
    </style>
    """, unsafe_allow_html=True)

# IDs Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719"
CONTAS_RECEBER_ID = "1Nqmn2c9p0QFu8LFIqFQ0EBxA8klHFUsVjAW15la-Fjg"

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid: url += f"&gid={gid}"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

def parse_currency(series):
    def clean_val(val):
        if pd.isna(val) or val == "": return 0.0
        s = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
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
    df['upgrade'] = parse_currency(df_v['Aumento da mensalidade'])
    df['adesao'] = parse_currency(df_v['Adesão - Simples']) + parse_currency(df_v['Adesão - Recupera'])
    df['data'] = pd.to_datetime(df_v['Data de Ativação'], errors='coerce')
    df = df.dropna(subset=['data'])
    df['ano'] = df['data'].dt.year
    df['mes_nome'] = df['data'].dt.month.map({1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'})
    df['status'] = 'Confirmada'
    if not df_c.empty:
        canc = df_c['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True).unique()
        df.loc[df['cnpj'].isin(canc), 'status'] = 'Cancelada'
    return df, df_cr

def render_page_comercial(df):
    col_nav_left, col_nav_right = st.columns([0.8, 0.2])
    with col_nav_right:
        if st.button("📋 Resumo Inadimplência", use_container_width=True):
            st.session_state.page = 'inadimplencia'; st.rerun()
    st.title("📊 Resumo Comercial")
    f = df[df['status'] == 'Confirmada']
    c1, c2, c3 = st.columns(3)
    c1.metric("MRR Conquistado", f"R$ {int(f['mrr'].sum()):,}".replace(",", "."))
    c2.metric("Clientes Ativos", len(f))
    c3.metric("Total Upsell", f"R$ {int(df['upgrade'].sum()):,}".replace(",", "."))
    st.divider()
    st.subheader("🏆 Ranking Vendedores (MRR)")
    rank = f.groupby('vendedor')['mrr'].sum().sort_values().reset_index()
    fig = px.bar(rank, x='mrr', y='vendedor', orientation='h', color_discrete_sequence=[COLOR_PRIMARY])
    st.plotly_chart(fig, use_container_width=True)

def render_page_inadimplencia(df_cr):
    col_nav_left, col_nav_right = st.columns([0.8, 0.2])
    with col_nav_right:
        if st.button("📊 Resumo Comercial", use_container_width=True):
            st.session_state.page = 'comercial'; st.rerun()
    st.title("📋 Resumo Inadimplência")
    if df_cr is None or df_cr.empty: st.warning("Base vazia"); return
    
    # Lógica de Aging e KPIs
    df_cr['valor_n'] = parse_currency(df_cr.iloc[:, 4]) # Assume coluna 5 é valor
    df_cr['venc'] = pd.to_datetime(df_cr.iloc[:, 0], errors='coerce', dayfirst=True) # Assume coluna 1 é vencimento
    df_cr['atraso'] = (datetime.now() - df_cr['venc']).dt.days
    
    def faixa(d):
        if d <= 30: return '0-30 dias'
        elif d <= 60: return '31-60 dias'
        elif d <= 90: return '61-90 dias'
        else: return '>90 dias'
    df_cr['faixa'] = df_cr['atraso'].apply(faixa)
    
    total = df_cr['valor_n'].sum()
    clientes = df_cr.iloc[:, 1].nunique() # Assume coluna 2 é CPF/CNPJ
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total em Aberto", f"R$ {int(total):,}".replace(",", "."))
    c2.metric("Clientes Inadimplentes", int(clientes))
    c3.metric("Repasse Sittax (30%)", f"R$ {int(total*0.3):,}".replace(",", "."))
    
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        aging = df_cr.groupby('faixa').size().reset_index(name='qtd')
        fig = px.pie(aging, values='qtd', names='faixa', hole=.4, title="Faixas de Atraso (%)", color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#FF6B6B', '#E74C3C'])
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        df_cr['mes'] = df_cr['venc'].dt.strftime('%Y-%m')
        evol = df_cr.groupby('mes')['valor_n'].sum().reset_index()
        fig = px.bar(evol, x='mes', y='valor_n', title="Aberto por Mês", color_discrete_sequence=[COLOR_PRIMARY])
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("📋 Detalhamento (Colunas Selecionadas)")
    cols = [0, 1, 2, 3, 4] # Vencimento, CPF/CNPJ, Nome, Descrição, Valor
    st.dataframe(df_cr.iloc[:, cols], use_container_width=True)
    st.download_button("📥 Baixar Base Completa", df_cr.to_csv(index=False), "inadimplencia.csv", "text/csv")

df_p, df_cr = processar_dados()
if df_p is not None:
    if st.session_state.page == 'comercial': render_page_comercial(df_p)
    else: render_page_inadimplencia(df_cr)
