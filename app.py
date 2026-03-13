import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import os

# 1. MENU FIXO: Configuração da página com Sidebar sempre expandida
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

# 2. MENU FIXO E COMPACTO: Estilização CSS para travar a sidebar e reduzir fontes
st.markdown(f"""
    <style>
    /* Fundo Principal */
    .main {{ background-color: {COLOR_BG}; }}
    
    /* MENU FIXO: Trava a sidebar para não recolher e ajusta largura mínima */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
        min-width: 250px !important;
        max-width: 250px !important;
    }}
    
    /* Esconde o botão de recolhimento da sidebar */
    button[data-testid="sidebar-collapse-button"] {{
        display: none !important;
    }}
    
    /* Fontes menores na Sidebar para ocupar menos espaço */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label {{
        font-size: 0.85rem !important;
        color: {COLOR_TEXT} !important;
    }}

    /* Estilo Base dos Cards de KPI */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_PRIMARY} !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        color: {COLOR_TEXT} !important;
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 1.4rem !important;
        color: {COLOR_TEXT} !important;
    }}
    
    /* WHITE LABEL - CAMUFLAGEM VISUAL */
    header[data-testid="stHeader"] {{ background: transparent !important; display: none !important; }}
    footer {{ display: none !important; }}
    [data-testid="stDecoration"] {{ display: none !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    
    /* Login Styles - REPOSICIONADO NO TOPO */
    .login-container {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 15vh;
        margin-top: 0.5vh;
        text-align: center;
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

# Configurações
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

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid and gid != '0': url += f"&gid={gid}"
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
        if not s: return 0.0
        if ',' in s: s = s.replace('.', '').replace(',', '.')
        elif '.' in s:
            parts = s.split('.')
            if len(parts[-1]) != 2: s = s.replace('.', '')
        try: return float(s)
        except: return 0.0
    return series.apply(clean_val)

def processar_dados(empresa):
    config = EMPRESAS[empresa]
    df_v_raw = load_data(config['vendas_id'], config['vendas_gid'])
    df_c_raw = load_data(config['cancelados_id'], config['cancelados_gid'])
    df_cr = load_data(config['contas_receber_id'])
    
    if df_v_raw.empty: return None, None, None
    
    # Processamento Vendas
    df_v = pd.DataFrame()
    df_v['vendedor'] = df_v_raw['Vendedor'].fillna("N/A")
    df_v['sdr'] = df_v_raw['SDR'].fillna("N/A")
    df_v['cliente'] = df_v_raw['Cliente'].fillna("N/A")
    df_v['cnpj'] = df_v_raw['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True)
    df_v['produto'] = df_v_raw['Qual produto?'].fillna("Sittax Simples")
    df_v['mrr'] = parse_currency(df_v_raw['Mensalidade - Simples'])
    df_v['adesao'] = parse_currency(df_v_raw['Adesão - Simples']) + parse_currency(df_v_raw['Adesão - Recupera'])
    df_v['upgrade'] = parse_currency(df_v_raw['Aumento da mensalidade'])
    df_v['data'] = pd.to_datetime(df_v_raw['Data de Ativação'], errors='coerce')
    df_v = df_v.dropna(subset=['data'])
    df_v['ano'] = df_v['data'].dt.year.astype(int)
    df_v['mes_num'] = df_v['data'].dt.month.astype(int)
    meses_pt = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
    df_v['mes_nome'] = df_v['mes_num'].map(meses_pt)
    
    # 3 & 6. LÓGICA DE CHURN E CRUZAMENTO: MRR real da planilha de vendas
    df_c = pd.DataFrame()
    if not df_c_raw.empty:
        df_c['cnpj'] = df_c_raw['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True)
        data_col = next((c for c in df_c_raw.columns if 'data' in c.lower() or 'cancelamento' in c.lower()), df_c_raw.columns[0])
        df_c['data_canc'] = pd.to_datetime(df_c_raw[data_col], errors='coerce')
        df_c = df_c.dropna(subset=['data_canc'])
        df_c['ano_canc'] = df_c['data_canc'].dt.year.astype(int)
        df_c['mes_canc_num'] = df_c['data_canc'].dt.month.astype(int)
        df_c['mes_canc_nome'] = df_c['mes_canc_num'].map(meses_pt)
        
        # Cruzamento para pegar o MRR real de Vendas
        df_v_unique = df_v.sort_values('data', ascending=False).drop_duplicates(subset=['cnpj'])
        df_c = pd.merge(df_c, df_v_unique[['cnpj', 'mrr', 'cliente']], on='cnpj', how='left')
        df_c['mrr'] = df_c['mrr'].fillna(0.0)
        
    return df_v, df_cr, df_c

if not st.session_state.usuario_logado:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    col_img1, col_img2, col_img3 = st.columns([1, 0.4, 1])
    with col_img2: st.image(LOGOS["ACELERAR_LOGIN"], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login"):
            email = st.text_input("📧 E-mail")
            senha = st.text_input("🔑 Senha", type="password")
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                if email and senha == SENHA_MESTRA:
                    st.session_state.usuario_logado = True
                    st.session_state.email_usuario = email
                    st.rerun()
                else: st.error("❌ Credenciais inválidas.")
else:
    df_p, df_cr, df_c = processar_dados(st.session_state.empresa)
    
    # 4. SIDEBAR INTELIGENTE: Filtros dinâmicos por aba
    with st.sidebar:
        st.image(LOGOS["ACELERAR_SIDEBAR"], width=140)
        st.markdown(f"👤 **{st.session_state.email_usuario}**")
        st.divider()
        
        st.markdown("### 🏢 Empresa")
        empresa_sel = st.selectbox("Selecione", list(EMPRESAS.keys()), index=list(EMPRESAS.keys()).index(st.session_state.empresa))
        if empresa_sel != st.session_state.empresa:
            st.session_state.empresa = empresa_sel
            st.cache_data.clear()
            st.rerun()
        
        # Filtros apenas na aba Comercial
        if st.session_state.page == 'comercial' and df_p is not None:
            st.divider()
            st.markdown("### 🔍 Filtros")
            anos = sorted(df_p['ano'].unique(), reverse=True)
            ano_sel = st.selectbox("📅 Ano", anos)
            df_ano = df_p[df_p['ano'] == ano_sel]
            
            meses_ordem = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
            meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
            meses_sel = st.multiselect("📅 Meses", meses_disp, default=meses_disp)
            
            vend_sel = st.selectbox("👤 Vendedor", ["Todos"] + sorted(df_p['vendedor'].unique().tolist()))
            sdr_sel = st.selectbox("🎧 SDR", ["Todos"] + sorted(df_p['sdr'].unique().tolist()))
        
        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_logado = False
            st.rerun()

    logo_url = LOGOS["VMC_TECH"] if st.session_state.empresa == "VMC Tech" else LOGOS["VICTEC"]

    if st.session_state.page == 'comercial':
        col_nav_left, col_nav_right = st.columns([0.8, 0.2])
        with col_nav_right:
            if st.button("📋 Inadimplência", use_container_width=True):
                st.session_state.page = 'inadimplencia'
                st.rerun()

        st.image(logo_url, width=150)
        st.title(f"📊 Resumo Comercial - {st.session_state.empresa}")
        
        if df_p is not None:
            df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
            if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
            if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]
            
            # Churn do período selecionado (Independente da venda original)
            df_c_f = df_c[(df_c['ano_canc'] == ano_sel) & (df_c['mes_canc_nome'].isin(meses_sel))] if df_c is not None else pd.DataFrame()
            
            mrr_conq = df_f['mrr'].sum()
            mrr_perd = df_c_f['mrr'].sum()
            cl_fech = len(df_f)
            cl_canc = len(df_c_f)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
            c2.metric("MRR Ativo (Net)", f"R$ {int(mrr_conq - mrr_perd):,}".replace(",", "."))
            c3.metric("MRR Perdido (Churn)", f"R$ {int(mrr_perd):,}".replace(",", "."), delta=f"{cl_canc} cancelados", delta_color="inverse")
            c4.metric("Clientes Fechados", cl_fech)
            
            st.divider()
            st.subheader("🏆 Rankings Top 5")
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                df_rv_m = df_f.groupby('vendedor')['mrr'].sum().nlargest(5).reset_index().sort_values('mrr')
                st.plotly_chart(px.bar(df_rv_m, x='mrr', y='vendedor', orientation='h', title='Vendedores (MRR)', color_discrete_sequence=[COLOR_PRIMARY]), use_container_width=True)
                df_rv_q = df_f.groupby('vendedor')['cliente'].count().nlargest(5).reset_index().sort_values('cliente')
                st.plotly_chart(px.bar(df_rv_q, x='cliente', y='vendedor', orientation='h', title='Vendedores (Contratos)', color_discrete_sequence=[COLOR_SECONDARY]), use_container_width=True)
            with c_r2:
                df_rs_m = df_f.groupby('sdr')['mrr'].sum().nlargest(5).reset_index().sort_values('mrr')
                st.plotly_chart(px.bar(df_rs_m, x='mrr', y='sdr', orientation='h', title='SDRs (MRR)', color_discrete_sequence=[COLOR_PRIMARY]), use_container_width=True)
                df_rs_q = df_f.groupby('sdr')['cliente'].count().nlargest(5).reset_index().sort_values('cliente')
                st.plotly_chart(px.bar(df_rs_q, x='cliente', y='sdr', orientation='h', title='SDRs (Contratos)', color_discrete_sequence=[COLOR_SECONDARY]), use_container_width=True)

    else:
        col_nav_left, col_nav_right = st.columns([0.8, 0.2])
        with col_nav_right:
            if st.button("📊 Comercial", use_container_width=True):
                st.session_state.page = 'comercial'
                st.rerun()
        
        st.image(logo_url, width=150)
        st.title(f"📋 Inadimplência - {st.session_state.empresa}")
        
        if not df_cr.empty:
            df_cr['valor_num'] = parse_currency(df_cr[next(c for c in df_cr.columns if 'valor' in c.lower())])
            df_cr['data_venc'] = pd.to_datetime(df_cr[next(c for c in df_cr.columns if 'vencimento' in c.lower())], errors='coerce', dayfirst=True)
            df_cr['dias'] = (datetime.now() - df_cr['data_venc']).dt.days
            
            def cat_aging(d):
                if d <= 30: return '0-30 dias'
                elif d <= 60: return '31-60 dias'
                elif d <= 90: return '61-90 dias'
                else: return '>90 dias'
            df_cr['faixa'] = df_cr['dias'].apply(cat_aging)
            
            # 5. REGRA PIOR FAIXA: Cliente aparece apenas uma vez
            nome_col = next(c for c in df_cr.columns if 'nome' in c.lower() or 'cliente' in c.lower())
            df_pior = df_cr.sort_values('dias', ascending=False).drop_duplicates(subset=[nome_col])
            
            c_i1, c_i2 = st.columns(2)
            c_i1.metric("Total Inadimplente", f"R$ {int(df_cr['valor_num'].sum()):,}".replace(",", "."))
            c_i2.metric("Qtd Clientes", len(df_pior))
            
            st.divider()
            aging_q = df_pior.groupby('faixa').size().reset_index(name='qtd')
            fig_aging = px.pie(aging_q, values='qtd', names='faixa', hole=0.4, title="Distribuição por Pior Faixa (Qtd Clientes)", color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#FF6B6B', '#E74C3C'])
            st.plotly_chart(fig_aging, use_container_width=True)
