import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import os

# Configuração da página - Sidebar sempre expandida
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Comercial Estratégico - Acelerar.tech", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

COLOR_PRIMARY = "#0B2A4E"
COLOR_SECONDARY = "#89CFF0"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#0A1E2E"
COLOR_CHURN = "#E74C3C"

# --- LINKS DIRETOS DO GITHUB PARA OS LOGOS ---
GITHUB_USER = "gerenciador-ai"
GITHUB_REPO = "Relat-rios-Comercial"
GITHUB_BRANCH = "main"

def get_github_url(filename):
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{filename}"

LOGOS = {
    "ACELERAR_LOGIN": get_github_url("logo_acelerar_sidebar.png"), 
    "ACELERAR_SIDEBAR": get_github_url("logo_acelerar_sidebar.png"),
    "VMC_TECH": get_github_url("logo_vmctech.png"),
    "VICTEC": get_github_url("logo_victec.png")
}

# Estilização CSS Customizada - VERSÃO WHITE LABEL (LIMPEZA TOTAL E SIDEBAR FIXA)
st.markdown(f"""
    <style>
    /* Fundo Principal */
    .main {{ background-color: {COLOR_BG}; }}
    
    /* Layout Fluido da Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
    }}
    
    /* REMOVER BOTÃO DE RECOLHER SIDEBAR (DEIXAR FIXO) */
    button[data-testid="sidebar-collapse-button"] {{
        display: none !important;
    }}
    
    /* Estilo Base dos Cards de KPI */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_PRIMARY} !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        color: {COLOR_TEXT} !important;
        min-width: 180px !important;
    }}
    
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
    
    /* Destaque para o Card de Churn (Coluna 3) */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {{
        border: 2px solid {COLOR_CHURN} !important;
    }}
    
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricLabel"] > div,
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {{
        color: {COLOR_CHURN} !important;
    }}
    
    /* Estilo do Delta no Churn */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] > div {{
        background-color: rgba(231, 76, 60, 0.2) !important;
        color: {COLOR_CHURN} !important;
        padding: 2px 8px !important;
        border-radius: 15px !important;
    }}
    
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] svg {{
        fill: {COLOR_CHURN} !important;
        stroke: {COLOR_CHURN} !important;
    }}
    
    /* Estilo dos Elementos da Sidebar */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stExpander p,
    [data-testid="stSidebar"] .stMultiSelect label {{
        color: {COLOR_TEXT} !important;
        font-weight: 600 !important;
    }}
    
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {{
        background-color: #F8F9FA !important;
        color: {COLOR_PRIMARY} !important;
        border-radius: 5px !important;
    }}
    
    [data-testid="stSidebar"] .stExpander {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }}
    
    /* Títulos e Gráficos */
    h1, h2, h3 {{
        color: {COLOR_SECONDARY} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }}
    
    /* WHITE LABEL - BLOQUEIO DE MENUS GERCENCIAIS */
    header[data-testid="stHeader"] {{ background: transparent !important; display: none !important; }}
    footer {{ display: none !important; }}
    [data-testid="stDecoration"] {{ display: none !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    
    button[title="View source on GitHub"], 
    button[title="Share this app"], 
    #MainMenu {{ display: none !important; }}
    
    .viewerBadge_container__1QS1n, .viewerBadge_link__3S19W {{ display: none !important; }}
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    
    /* Login Styles */
    .login-container {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 20vh;
        background-color: transparent !important;
        margin-top: 1vh;
        text-align: center;
    }}
    
    div[data-testid="stForm"] {{
        border: none !important;
        padding: 0 !important;
        background-color: transparent !important;
    }}

    .block-container {{
        padding-top: 0.2rem !important;
        padding-bottom: 1rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Estados de Sessão
if 'page' not in st.session_state: st.session_state.page = 'comercial'
if 'empresa' not in st.session_state: st.session_state.empresa = 'VMC Tech'
if 'usuario_logado' not in st.session_state: st.session_state.usuario_logado = False
if 'email_usuario' not in st.session_state: st.session_state.email_usuario = None

# Configurações de Empresas e Usuários
EMPRESAS = {
    'VMC Tech': {
        'vendas_id': '1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M',
        'vendas_gid': '1202307787',
        'cancelados_id': '1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw',
        'cancelados_gid': '606807719',
        'contas_receber_id': '1Nqmn2c9p0QFu8LFIqFQ0EBxA8klHFUsVjAW15la-Fjg'
    },
    'Victec': {
        'vendas_id': '1o0RJI58HW-NLX97Jab4YpKiM4b8_kIw2o11EL8iMgCo',
        'vendas_gid': '0',
        'cancelados_id': '1-eXWcie9mPwtWOiQDDiPlwrDmexvXeeQ4FAIDPEQ9c4',
        'cancelados_gid': '0',
        'contas_receber_id': '1Y28LP_ZPqWKMjXqf88ahzaDET_DneOYhxuNOmyinxus'
    }
}
USUARIOS_SHEET_ID = '15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk'
SENHA_MESTRA = 'Acelerar@2026'

# Funções de Carregamento de Dados
@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    if gid and gid != '0':
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

def load_usuarios():
    url = f"https://docs.google.com/spreadsheets/d/{USUARIOS_SHEET_ID}/export?format=csv"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
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

def render_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    col_img1, col_img2, col_img3 = st.columns([1, 0.4, 1])
    with col_img2:
        st.image(LOGOS["ACELERAR_LOGIN"], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login"):
            email = st.text_input("📧 E-mail", placeholder="seu.email@empresa.com")
            senha = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                if not email or not senha: st.error("❌ Preencha todos os campos.")
                elif senha != SENHA_MESTRA: st.error("❌ Senha incorreta.")
                else:
                    df_u = load_usuarios()
                    if not df_u.empty and email.lower() in df_u['Email'].str.lower().values:
                        st.session_state.usuario_logado = True
                        st.session_state.email_usuario = email
                        st.rerun()
                    else: st.error("❌ E-mail não autorizado.")

def processar_dados(empresa):
    config = EMPRESAS[empresa]
    df_v = load_data(config['vendas_id'], config['vendas_gid'])
    df_c = load_data(config['cancelados_id'], config['cancelados_gid'])
    df_cr = load_data(config['contas_receber_id'])
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
    return df, df_cr

# LÓGICA DE EXECUÇÃO
if not st.session_state.usuario_logado:
    render_login()
else:
    df_p, df_cr = processar_dados(st.session_state.empresa)
    
    with st.sidebar:
        st.image(LOGOS["ACELERAR_SIDEBAR"], width=160)
        st.markdown(f"<h4 style='color: white;'>👤 Usuário: {st.session_state.email_usuario}</h4>", unsafe_allow_html=True)
        st.divider()
        
        st.markdown("<h3 style='color: white; text-align: center;'>🏢 Empresa</h3>", unsafe_allow_html=True)
        empresa_sel = st.selectbox("Selecione", list(EMPRESAS.keys()), index=list(EMPRESAS.keys()).index(st.session_state.empresa))
        if empresa_sel != st.session_state.empresa:
            st.session_state.empresa = empresa_sel
            st.cache_data.clear()
            st.rerun()
        
        if df_p is not None:
            st.divider()
            st.markdown("<h3 style='color: white; text-align: center;'>🔍 Filtros</h3>", unsafe_allow_html=True)
            anos = sorted(df_p['ano'].unique(), reverse=True)
            ano_sel = st.selectbox("📅 Ano", anos)
            df_ano = df_p[df_p['ano'] == ano_sel]
            
            with st.expander("📅 Meses"):
                meses_ordem = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
                meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
                meses_sel = st.multiselect("Selecionar", meses_disp, default=meses_disp)
            
            prod_sel = st.selectbox("📦 Produto", ["Todos"] + sorted(df_p['produto'].unique().tolist()))
            vend_sel = st.selectbox("👤 Vendedor", ["Todos"] + sorted(df_p['vendedor'].unique().tolist()))
            sdr_sel = st.selectbox("🎧 SDR", ["Todos"] + sorted(df_p['sdr'].unique().tolist()))
        
        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_logado = False
            st.rerun()

    logo_unidade_url = LOGOS["VMC_TECH"] if st.session_state.empresa == "VMC Tech" else LOGOS["VICTEC"]

    if df_p is not None:
        if st.session_state.page == 'comercial':
            df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
            if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
            if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
            if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]

            col_nav_left, col_nav_right = st.columns([0.8, 0.2])
            with col_nav_right:
                if st.button("📋 Inadimplência", use_container_width=True):
                    st.session_state.page = 'inadimplencia'
                    st.rerun()

            st.image(logo_unidade_url, width=150)
            st.title(f"📊 Resumo Comercial - {st.session_state.empresa}")
            
            mrr_conq = df_f['mrr'].sum()
            cl_fech = len(df_f)
            tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
            c2.metric("Clientes fechado", cl_fech)
            c3.metric("Ticket Médio", f"R$ {int(tkt_med):,}".replace(",", "."))
            c4.metric("Adesão Total", f"R$ {int(df_f['adesao'].sum()):,}".replace(",", "."))

            st.divider()
            st.subheader("🏆 Rankings Top 5")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                df_rank_v_mrr = df_f.groupby('vendedor')['mrr'].sum().nlargest(5).reset_index().sort_values('mrr')
                st.plotly_chart(px.bar(df_rank_v_mrr, x='mrr', y='vendedor', orientation='h', title='Vendedores (MRR)', color_discrete_sequence=[COLOR_PRIMARY]), use_container_width=True)
                df_rank_v_cont = df_f.groupby('vendedor')['cliente'].count().nlargest(5).reset_index().sort_values('cliente')
                st.plotly_chart(px.bar(df_rank_v_cont, x='cliente', y='vendedor', orientation='h', title='Vendedores (Contratos)', color_discrete_sequence=[COLOR_SECONDARY]), use_container_width=True)
            with col_r2:
                df_rank_s_mrr = df_f.groupby('sdr')['mrr'].sum().nlargest(5).reset_index().sort_values('mrr')
                st.plotly_chart(px.bar(df_rank_s_mrr, x='mrr', y='sdr', orientation='h', title='SDRs (MRR)', color_discrete_sequence=[COLOR_PRIMARY]), use_container_width=True)
                df_rank_s_cont = df_f.groupby('sdr')['cliente'].count().nlargest(5).reset_index().sort_values('cliente')
                st.plotly_chart(px.bar(df_rank_s_cont, x='cliente', y='sdr', orientation='h', title='SDRs (Contratos)', color_discrete_sequence=[COLOR_SECONDARY]), use_container_width=True)
        
        else:
            col_nav_left, col_nav_right = st.columns([0.8, 0.2])
            with col_nav_right:
                if st.button("📊 Comercial", use_container_width=True):
                    st.session_state.page = 'comercial'
                    st.rerun()
            
            st.image(logo_unidade_url, width=150)
            st.title(f"📋 Inadimplência - {st.session_state.empresa}")
            
            if not df_cr.empty:
                df_cr['valor_num'] = parse_currency(df_cr[next(c for c in df_cr.columns if 'valor' in c.lower())])
                st.metric("Total Inadimplente", f"R$ {int(df_cr['valor_num'].sum()):,}".replace(",", "."))
                st.dataframe(df_cr, use_container_width=True)
