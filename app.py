import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import os

# Configuração da página - Estilo Sênior Premium (Layout Wide e Sidebar Expansível)
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

# Estilização CSS Customizada - VERSÃO WHITE LABEL (LIMPEZA TOTAL E LOGIN REPOSICIONADO)
st.markdown(f"""
    <style>
    /* Fundo Principal */
    .main {{ background-color: {COLOR_BG}; }}
    
    /* Layout Fluido da Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
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
    
    /* WHITE LABEL - BLOQUEIO DE MENUS GERCENCIAIS (REMOÇÃO DO GITHUB, SHARE, ETC) */
    header[data-testid="stHeader"] {{ background: transparent !important; display: none !important; }}
    footer {{ display: none !important; }}
    [data-testid="stDecoration"] {{ display: none !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    
    /* Esconder especificamente botões de Share, GitHub e Menu no topo */
    button[title="View source on GitHub"], 
    button[title="Share this app"], 
    #MainMenu {{ display: none !important; }}
    
    /* Esconder rodapé "Gerenciar aplicativo" no Streamlit Cloud */
    .viewerBadge_container__1QS1n, .viewerBadge_link__3S19W {{ display: none !important; }}
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    
    /* Login Styles - ESTÉTICA CLEAN E REPOSICIONADA (MAIS ALTO NA TELA) */
    .login-container {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 20vh; /* Reduzido ainda mais para subir o logo */
        background-color: transparent !important;
        margin-top: 1vh; /* Reduzido para subir o logo ao máximo */
        text-align: center;
    }}
    
    /* Estilo dos campos de input no login */
    div[data-testid="stForm"] {{
        border: none !important;
        padding: 0 !important;
        background-color: transparent !important;
    }}

    /* Ajuste de Padding para evitar rolagem e subir conteúdo */
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
    # RENDERIZAÇÃO ESTÉTICA CLEAN E ALTA: APENAS O LOGO CENTRALIZADO NO TOPO
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Inserção do Logo da Acelerar centralizado e redimensionado
    col_img1, col_img2, col_img3 = st.columns([1, 0.4, 1])
    with col_img2:
        st.image(LOGOS["ACELERAR_LOGIN"], use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Campos de login centralizados
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
    df['status'] = 'Confirmada'
    if not df_c.empty:
        canc_cnpjs = df_c['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True).unique()
        df.loc[df['cnpj'].isin(canc_cnpjs), 'status'] = 'Cancelada'
    return df, df_cr

# LÓGICA DE EXECUÇÃO
if not st.session_state.usuario_logado:
    render_login()
else:
    # 1. CARREGAMENTO DE DADOS (CRÍTICO PARA OS FILTROS)
    df_p, df_cr = processar_dados(st.session_state.empresa)
    
    # 2. RENDERIZAÇÃO DA SIDEBAR (GARANTIDA COM TODOS OS FILTROS)
    with st.sidebar:
        # Logo Acelerar fixo no topo da sidebar e redimensionado via width
        st.image(LOGOS["ACELERAR_SIDEBAR"], width=160)
        st.markdown(f"<h4 style='color: white;'>👤 Usuário: {st.session_state.email_usuario}</h4>", unsafe_allow_html=True)
        st.divider()
        
        st.markdown("<h3 style='color: white; text-align: center;'>🏢 Empresa</h3>", unsafe_allow_html=True)
        empresa_sel = st.selectbox("Selecione", list(EMPRESAS.keys()), index=list(EMPRESAS.keys()).index(st.session_state.empresa))
        if empresa_sel != st.session_state.empresa:
            st.session_state.empresa = empresa_sel
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        st.markdown("<h3 style='color: white; text-align: center;'>🔍 Filtros</h3>", unsafe_allow_html=True)
        
        if df_p is not None:
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
        else:
            st.error("Dados não carregados.")
            meses_sel = []
            prod_sel = "Todos"
            vend_sel = "Todos"
            sdr_sel = "Todos"
            df_ano = pd.DataFrame()

        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_logado = False
            st.rerun()

    # Lógica de Logo Dinâmico da Unidade
    logo_unidade_url = LOGOS["VMC_TECH"] if st.session_state.empresa == "VMC Tech" else LOGOS["VICTEC"]

    # 3. RENDERIZAÇÃO DAS PÁGINAS
    if df_p is not None:
        if st.session_state.page == 'comercial':
            # FILTRAGEM DE DADOS PARA A PÁGINA COMERCIAL
            df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
            if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
            if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
            if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]

            # HEADER E NAVEGAÇÃO
            col_nav_left, col_nav_right = st.columns([0.8, 0.2])
            with col_nav_right:
                if st.button("📋 Inadimplência", use_container_width=True):
                    st.session_state.page = 'inadimplencia'
                    st.rerun()

            # Logo da Unidade redimensionado via width acima do título
            st.image(logo_unidade_url, width=150)
            st.title(f"📊 Resumo Comercial - {st.session_state.empresa}")
            
            # --- CORREÇÃO DA LÓGICA DE KPIs (CONTABILIDADE COMERCIAL) ---
            # MRR Conquistado: Soma total das vendas ativadas no mês (independente se cancelou depois)
            mrr_conq = df_f['mrr'].sum()
            
            # MRR Perdido (Churn): Soma do MRR das vendas que estão com status 'Cancelada'
            mrr_perd = df_f[df_f['status'] == 'Cancelada']['mrr'].sum()
            
            # MRR Ativo (Net): Saldo líquido (Conquistado - Perdido)
            mrr_ativo_net = mrr_conq - mrr_perd
            
            # Clientes Fechados: Contagem total de novos contratos ativados (independente se cancelou)
            cl_fech = len(df_f[df_f['mrr'] > 0])
            
            # Clientes Cancelados: Contagem de cancelamentos no período
            cl_canc = len(df_f[df_f['status'] == 'Cancelada'])
            
            # Outros cálculos
            upsell_v = df_f['upgrade'].sum()
            upsell_q = len(df_f[df_f['upgrade'] > 0])
            tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
            base_ativa = len(df_p[df_p['status'] == 'Confirmada']) - len(df_p[df_p['status'] == 'Cancelada'])
            churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0
            
            # LINHA 1 DE KPIs
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
            c2.metric("MRR Ativo (Net)", f"R$ {int(mrr_ativo_net):,}".replace(",", "."))
            c3.metric("MRR Perdido (Churn)", f"R$ {int(mrr_perd):,}".replace(",", "."), delta=f"{-churn_p:.1f}%", delta_color="inverse")
            c4.metric("Total de Upsell", f"R$ {int(upsell_v):,}".replace(",", "."), delta=f"{upsell_q} eventos", delta_color="normal")
            c5.metric("Ticket Médio", f"R$ {int(tkt_med):,}".replace(",", "."))
            
            # LINHA 2 DE KPIs
            c6, c7, c8, c9 = st.columns(4)
            c6.metric("Adesão Total", f"R$ {int(df_f['adesao'].sum()):,}".replace(",", "."))
            c7.metric("Clientes fechado", cl_fech)
            c8.metric("Clientes Cancelados", cl_canc)
            c9.metric("Total Base Ativa", base_ativa)

            st.divider()
            
            # GRÁFICOS DE EVOLUÇÃO
            st.subheader("📈 Evolução Mensal")
            col1, col2, col3 = st.columns(3)
            with col1:
                df_m = df_ano.groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
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
                fig = px.bar(df_c_evol, x='mes_nome', y='mrr', text='cliente', title="Evolução de Churn", color_discrete_sequence=[COLOR_PRIMARY])
                fig.update_traces(texttemplate='%{text}', textposition='inside')
                fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            
            # METAS
            st.subheader("🎯 Performance vs. Metas")
            col4, col5 = st.columns(2)
            df_meta = df_f.groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
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
            
            # RANKINGS EXPANDIDOS (VENDEDORES E SDRS)
            st.subheader("🏆 Rankings de Performance Comercial")
            
            # Rankings de Vendedores
            st.markdown("#### 👤 Vendedores")
            col_vend1, col_vend2 = st.columns(2)
            with col_vend1:
                df_rank_v_mrr = df_f.groupby('vendedor')['mrr'].sum().sort_values(ascending=True).reset_index()
                fig_v_mrr = px.bar(df_rank_v_mrr.tail(5), x='mrr', y='vendedor', orientation='h', title='Top 5 Vendedores (MRR)', text=df_rank_v_mrr.tail(5)['mrr'].apply(lambda x: f"R$ {int(x):,}"), color_discrete_sequence=[COLOR_PRIMARY])
                fig_v_mrr.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_v_mrr, use_container_width=True)
            with col_vend2:
                df_rank_v_cont = df_f.groupby('vendedor')['cliente'].count().sort_values(ascending=True).reset_index()
                fig_v_cont = px.bar(df_rank_v_cont.tail(5), x='cliente', y='vendedor', orientation='h', title='Top 5 Vendedores (Contratos)', text=df_rank_v_cont.tail(5)['cliente'], color_discrete_sequence=[COLOR_SECONDARY])
                fig_v_cont.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_v_cont, use_container_width=True)
            
            # Rankings de SDRs
            st.markdown("#### 🎧 SDRs")
            col_sdr1, col_sdr2 = st.columns(2)
            with col_sdr1:
                df_rank_s_mrr = df_f.groupby('sdr')['mrr'].sum().sort_values(ascending=True).reset_index()
                fig_s_mrr = px.bar(df_rank_s_mrr.tail(5), x='mrr', y='sdr', orientation='h', title='Top 5 SDRs (MRR)', text=df_rank_s_mrr.tail(5)['mrr'].apply(lambda x: f"R$ {int(x):,}"), color_discrete_sequence=[COLOR_PRIMARY])
                fig_s_mrr.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_s_mrr, use_container_width=True)
            with col_sdr2:
                df_rank_s_cont = df_f.groupby('sdr')['cliente'].count().sort_values(ascending=True).reset_index()
                fig_s_cont = px.bar(df_rank_s_cont.tail(5), x='cliente', y='sdr', orientation='h', title='Top 5 SDRs (Contratos)', text=df_rank_s_cont.tail(5)['cliente'], color_discrete_sequence=[COLOR_SECONDARY])
                fig_s_cont.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_s_cont, use_container_width=True)

            st.divider()
            st.subheader("📋 Detalhamento")
            st.dataframe(df_f[['data', 'cliente', 'vendedor', 'sdr', 'produto', 'status', 'mrr', 'upgrade', 'adesao']].sort_values('data', ascending=False), use_container_width=True)
        
        else:
            # PÁGINA DE INADIMPLÊNCIA
            col_nav_left, col_nav_right = st.columns([0.8, 0.2])
            with col_nav_right:
                if st.button("📊 Comercial", use_container_width=True):
                    st.session_state.page = 'comercial'
                    st.rerun()
            
            # Logo da Unidade redimensionado via width acima do título
            st.image(logo_unidade_url, width=150)
            st.title(f"📋 Inadimplência - {st.session_state.empresa}")
            
            if df_cr.empty:
                st.warning("Sem dados de inadimplência disponíveis.")
            else:
                df_cr_proc = df_cr.copy()
                df_cr_proc.columns = df_cr_proc.columns.str.strip()
                
                valor_col = next((c for c in df_cr_proc.columns if 'valor' in c.lower()), None)
                venc_col = next((c for c in df_cr_proc.columns if 'vencimento' in c.lower()), None)
                cpf_col = next((c for c in df_cr_proc.columns if 'cpf' in c.lower() or 'cnpj' in c.lower()), None)
                nome_col = next((c for c in df_cr_proc.columns if 'nome' in c.lower()), None)
                
                df_cr_proc['valor_numerico'] = parse_currency(df_cr_proc[valor_col]) if valor_col else 0.0
                df_cr_proc['data_vencimento'] = pd.to_datetime(df_cr_proc[venc_col], errors='coerce', dayfirst=True) if venc_col else pd.NaT
                df_cr_proc['dias_atraso'] = (datetime.now() - df_cr_proc['data_vencimento']).dt.days
                
                def categorizar_atraso(dias):
                    if pd.isna(dias): return 'Sem Data'
                    elif dias <= 30: return '0-30 dias'
                    elif dias <= 60: return '31-60 dias'
                    elif dias <= 90: return '61-90 dias'
                    else: return '>90 dias'
                df_cr_proc['faixa_atraso'] = df_cr_proc['dias_atraso'].apply(categorizar_atraso)
                
                total_aberto = df_cr_proc['valor_numerico'].sum()
                clientes_inadimplentes = df_cr_proc[cpf_col].nunique() if cpf_col else len(df_cr_proc)
                repasse_sittax = total_aberto * 0.30
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total em Aberto", f"R$ {int(total_aberto):,}".replace(",", "."))
                c2.metric("Clientes Inadimplentes", int(clientes_inadimplentes))
                c3.metric("Repasse Sittax (30%)", f"R$ {int(repasse_sittax):,}".replace(",", "."))
                
                st.divider()
                
                st.subheader("📊 Distribuição por Faixa de Atraso")
                col_rosca, col_tabela = st.columns([1.2, 1.8])
                with col_rosca:
                    aging_data = df_cr_proc[df_cr_proc['faixa_atraso'] != 'Sem Data'].groupby('faixa_atraso')[cpf_col if cpf_col else df_cr_proc.columns[0]].nunique().reset_index()
                    aging_data.columns = ['Faixa', 'Quantidade']
                    ordem_faixas = ['0-30 dias', '31-60 dias', '61-90 dias', '>90 dias']
                    aging_data['Faixa'] = pd.Categorical(aging_data['Faixa'], categories=ordem_faixas, ordered=True)
                    aging_data = aging_data.sort_values('Faixa')
                    fig = px.pie(aging_data, values='Quantidade', names='Faixa', hole=0.4, title="Clientes por Faixa", color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#FF6B6B', '#E74C3C'])
                    fig.update_layout(font=dict(color='white'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                with col_tabela:
                    st.markdown("### 📋 Resumo por Cliente")
                    df_aging_cliente = df_cr_proc[df_cr_proc['faixa_atraso'] != 'Sem Data'].groupby(nome_col if nome_col else (cpf_col if cpf_col else df_cr_proc.columns[0])).agg({'valor_numerico': 'sum', 'data_vencimento': 'count'}).reset_index()
                    df_aging_cliente.columns = ['Cliente', 'Valor Total', 'Mensalidades']
                    df_aging_cliente['Faixa de Atraso'] = df_aging_cliente['Mensalidades'].apply(lambda x: '0-30 dias' if x==1 else ('31-60 dias' if x==2 else ('61-90 dias' if x==3 else '>90 dias')))
                    st.dataframe(df_aging_cliente.sort_values(by='Mensalidades', ascending=False), use_container_width=True, hide_index=True)
                
                st.divider()
                st.subheader("📋 Detalhamento de Títulos")
                st.dataframe(df_cr_proc[[venc_col, cpf_col, nome_col, valor_col, 'faixa_atraso']].sort_values(by=venc_col), use_container_width=True)
    else:
        st.error("Erro ao carregar os dados das planilhas.")

# Rodapé Dinâmico (Escondido via CSS para usuários, mas mantido no código para referência)
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
        © {datetime.now().year} Acelerar.tech - Sistema de Inteligência Comercial | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
""", unsafe_allow_html=True)
