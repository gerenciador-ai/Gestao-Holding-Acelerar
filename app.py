import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import hashlib
import os

st.set_page_config(layout="wide", page_title="Dashboard Comercial Estratégico - Acelerar.tech", page_icon="📊", initial_sidebar_state="collapsed")

COLOR_PRIMARY = "#0B2A4E"
COLOR_SECONDARY = "#89CFF0"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#0A1E2E"
COLOR_CHURN = "#E74C3C"

st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {
        background-color: #0A1E2E !important;
        color: #FFFFFF !important;
        width: 100% !important;
        height: 100% !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0B2A4E !important;
    }
    [data-testid="stHeader"] {
        background-color: #0A1E2E !important;
        display: none !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .stApp > header {
        display: none !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    a[href*="github"], a[href*="deploy"], a[href*="settings"] {
        display: none !important;
    }
    div[data-testid="stMetric"] {
        background-color: #0B2A4E !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        color: #FFFFFF !important;
        min-width: 180px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        border: 2px solid #E74C3C !important;
    }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricLabel"] > div,
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {
        color: #E74C3C !important;
    }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] > div {
        background-color: rgba(231, 76, 60, 0.2) !important;
        color: #E74C3C !important;
        padding: 2px 8px !important;
        border-radius: 15px !important;
    }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] svg {
        fill: #E74C3C !important;
        stroke: #E74C3C !important;
    }
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stExpander p,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
        background-color: #F8F9FA !important;
        color: #0B2A4E !important;
        border-radius: 5px !important;
    }
    [data-testid="stSidebar"] .stExpander {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    h1, h2, h3 {
        color: #0B2A4E !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .login-card {
        background-color: rgba(10, 30, 46, 0.95) !important;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        width: 100%;
        max-width: 400px;
        border: 2px solid #89CFF0;
    }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'comercial'

if 'empresa' not in st.session_state:
    st.session_state.empresa = 'VMC Tech'

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = False

if 'email_usuario' not in st.session_state:
    st.session_state.email_usuario = None

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
    if gid and gid != '0':
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

def load_usuarios():
    url = f"https://docs.google.com/spreadsheets/d/{USUARIOS_SHEET_ID}/export?format=csv"
    try:
        df = pd.read_csv(url )
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
    img_base64 = ""
    try:
        if os.path.exists('logo_acelerar.png'):
            with open('logo_acelerar.png', 'rb') as f:
                img_data = f.read()
            img_base64 = base64.b64encode(img_data).decode()
    except:
        pass
    
    if img_base64:
        st.markdown(f"""
            <style>
            .login-bg {{
                background-image: url('data:image/png;base64,{img_base64}');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
            }}
            </style>
            <div class="login-bg"></div>
            """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-top: 80px; margin-bottom: 40px;">
                <h1 style="color: #89CFF0; font-size: 2.5rem; font-weight: bold;">🔐 Dashboard Comercial</h1>
                <p style="color: #FFFFFF; font-size: 1.1rem; margin-top: 10px;">Acelerar.tech - Holding</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.form("form_login"):
            email = st.text_input("📧 E-mail", placeholder="seu.email@empresa.com", key="login_email")
            senha = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha", key="login_senha")
            
            submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
            
            if submit:
                if not email or not senha:
                    st.error("❌ Por favor, preencha e-mail e senha.")
                elif senha != SENHA_MESTRA:
                    st.error("❌ Senha incorreta.")
                else:
                    df_usuarios = load_usuarios()
                    
                    if df_usuarios.empty:
                        st.error("❌ Erro ao carregar base de usuários.")
                    else:
                        usuario = df_usuarios[df_usuarios['Email'].str.lower() == email.lower()]
                        
                        if usuario.empty:
                            st.error("❌ E-mail não autorizado para acessar o dashboard.")
                        else:
                            st.session_state.usuario_logado = True
                            st.session_state.email_usuario = email
                            st.success("✅ Login realizado com sucesso!")
                            st.rerun()

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

def render_page_comercial(df):
    st.sidebar.markdown("<h3 style='color: white; text-align: center;'>🏢 Seletor de Empresa</h3>", unsafe_allow_html=True)
    empresa_sel = st.sidebar.selectbox("Selecione a Empresa", list(EMPRESAS.keys()), index=list(EMPRESAS.keys()).index(st.session_state.empresa))
    if empresa_sel != st.session_state.empresa:
        st.session_state.empresa = empresa_sel
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("<h3 style='color: white; text-align: center;'>🔍 Filtros Estratégicos</h3>", unsafe_allow_html=True)
    
    anos = sorted(df['ano'].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("📅 Ano de Referência", anos)
    df_ano = df[df['ano'] == ano_sel]
    
    with st.sidebar.expander("📅 Selecionar Período (Meses)"):
        meses_ordem = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
        meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
        meses_sel = st.multiselect("Meses", meses_disp, default=meses_disp)
    
    st.sidebar.divider()
    prod_sel = st.sidebar.selectbox("📦 Produto", ["Todos"] + sorted(df['produto'].unique().tolist()))
    vend_sel = st.sidebar.selectbox("👤 Vendedor", ["Todos"] + sorted(df['vendedor'].unique().tolist()))
    sdr_sel = st.sidebar.selectbox("🎧 SDR", ["Todos"] + sorted(df['sdr'].unique().tolist()))
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario_logado = False
        st.session_state.email_usuario = None
        st.rerun()

    df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]

    mrr_conq = df_f[df_f['status'] == 'Confirmada']['mrr'].sum()
    mrr_perd = df_f[df_f['status'] == 'Cancelada']['mrr'].sum()
    upsell_v = df_f['upgrade'].sum()
    upsell_q = len(df_f[df_f['upgrade'] > 0])
    cl_fech = len(df_f[(df_f['status'] == 'Confirmada') & (df_f['mrr'] > 0)])
    cl_canc = len(df_f[df_f['status'] == 'Cancelada'])
    tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
    base_ativa = len(df[df['status'] == 'Confirmada']) - len(df[df['status'] == 'Cancelada'])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0

    col_nav_left, col_nav_right = st.columns([0.8, 0.2])
    with col_nav_right:
        if st.button("📋 Resumo Inadimplência", use_container_width=True):
            st.session_state.page = 'inadimplencia'
            st.rerun()

    st.title(f"📊 Resumo Comercial - {st.session_state.empresa}")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
    c2.metric("MRR Ativo (Net)", f"R$ {int(mrr_conq - mrr_perd):,}".replace(",", "."))
    c3.metric("MRR Perdido (Churn)", f"R$ {int(mrr_perd):,}".replace(",", "."), delta=f"{-churn_p:.1f}%", delta_color="inverse")
    c4.metric("Total de Upsell", f"R$ {int(upsell_v):,}".replace(",", "."), delta=f"{upsell_q} eventos", delta_color="normal")
    c5.metric("Ticket Médio", f"R$ {int(tkt_med):,}".replace(",", "."))
    
    c6, c7, c8, c9 = st.columns(4)
    c6.metric("Adesão Total", f"R$ {int(df_f['adesao'].sum()):,}".replace(",", "."))
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
        fig = px.bar(df_c_evol, x='mes_nome', y='mrr', text='cliente', title="Evolução de Churn", color_discrete_sequence=[COLOR_PRIMARY])
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
        fig = go.Figure(go.Scatter(x=df_s['data_s'], y=df_s['mrr'], mode='lines+markers+text', text=df_s['mrr'].apply(lambda x: f"{int(x):,}"), textposition="top center", line=dict(color=COLOR_PRIMARY, width=4)))
        fig.update_layout(title="MRR SEMANA", xaxis_title=None, yaxis_title=None, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col7:
        fig = px.pie(df_f, names='produto', values='mrr', title="Receita por Produto", hole=0.4, color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#1A3A5A', '#2E5A88'])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("🏆 Rankings de SDRs (Top 5)")
    col_sdr1, col_sdr2 = st.columns(2)

    with col_sdr1:
        df_rank_sdr_cont = df_f[df_f['status'] == 'Confirmada'].groupby('sdr')['cliente'].count().sort_values(ascending=True).reset_index()
        df_rank_sdr_cont.columns = ['SDR', 'Contratos']
        fig_sdr_cont = px.bar(df_rank_sdr_cont.tail(5), x='Contratos', y='SDR', orientation='h',
                               title='Top 5 SDRs (Contratos)', text='Contratos',
                               color_discrete_sequence=[COLOR_PRIMARY])
        fig_sdr_cont.update_traces(textposition='inside', textfont_color='white')
        fig_sdr_cont.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_sdr_cont, use_container_width=True)

    with col_sdr2:
        df_rank_sdr_mrr = df_f[df_f['status'] == 'Confirmada'].groupby('sdr')['mrr'].sum().sort_values(ascending=True).reset_index()
        df_rank_sdr_mrr.columns = ['SDR', 'MRR']
        fig_sdr_mrr = px.bar(df_rank_sdr_mrr.tail(5), x='MRR', y='SDR', orientation='h',
                         title='Top 5 SDRs (MRR)', text=df_rank_sdr_mrr.tail(5)['MRR'].apply(lambda x: f"R$ {int(x):,}"),
                         color_discrete_sequence=[COLOR_SECONDARY])
        fig_sdr_mrr.update_traces(textposition='inside', textfont_color=COLOR_PRIMARY)
        fig_sdr_mrr.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_sdr_mrr, use_container_width=True)

    st.divider()

    st.subheader("🏆 Rankings de Vendedores")
    col_rank1, col_rank2 = st.columns(2)

    with col_rank1:
        df_rank_contratos = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['cliente'].count().sort_values(ascending=True).reset_index()
        df_rank_contratos.columns = ['Vendedor', 'Contratos']
        fig_contratos = px.bar(df_rank_contratos.tail(10), x='Contratos', y='Vendedor', orientation='h',
                               title='Top Vendedores (Contratos)', text='Contratos',
                               color_discrete_sequence=[COLOR_PRIMARY])
        fig_contratos.update_traces(textposition='inside', textfont_color='white')
        fig_contratos.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_contratos, use_container_width=True)

    with col_rank2:
        df_rank_mrr = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['mrr'].sum().sort_values(ascending=True).reset_index()
        df_rank_mrr.columns = ['Vendedor', 'MRR']
        fig_mrr = px.bar(df_rank_mrr.tail(10), x='MRR', y='Vendedor', orientation='h',
                         title='Top Vendedores (MRR)', text=df_rank_mrr.tail(10)['MRR'].apply(lambda x: f"R$ {int(x):,}"),
                         color_discrete_sequence=[COLOR_SECONDARY])
        fig_mrr.update_traces(textposition='inside', textfont_color=COLOR_PRIMARY)
        fig_mrr.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_mrr, use_container_width=True)

    st.divider()

    st.subheader("📋 Detalhamento")
    st.dataframe(df_f[['data', 'cliente', 'vendedor', 'sdr', 'produto', 'status', 'mrr', 'upgrade', 'adesao']].sort_values('data', ascending=False), use_container_width=True)

def render_page_inadimplencia(df_cr):
    col_nav_left, col_nav_right = st.columns([0.8, 0.2])
    with col_nav_right:
        if st.button("📊 Resumo Comercial", use_container_width=True):
            st.session_state.page = 'comercial'
            st.rerun()

    st.title(f"📋 Resumo Inadimplência - {st.session_state.empresa}")
    
    if df_cr is None or df_cr.empty:
        st.warning("Base de Contas a Receber não encontrada ou vazia.")
        return
    
    df_cr_proc = df_cr.copy()
    df_cr_proc.columns = df_cr_proc.columns.str.strip()
    
    valor_col = None
    for col in df_cr_proc.columns:
        if 'valor' in col.lower():
            valor_col = col
            break
    
    venc_col = None
    for col in df_cr_proc.columns:
        if 'vencimento' in col.lower():
            venc_col = col
            break
    
    cpf_col = None
    for col in df_cr_proc.columns:
        if 'cpf' in col.lower() or 'cnpj' in col.lower():
            cpf_col = col
            break
    
    nome_col = None
    for col in df_cr_proc.columns:
        if 'nome' in col.lower() and 'cliente' in col.lower():
            nome_col = col
            break
    if not nome_col:
        for col in df_cr_proc.columns:
            if 'nome' in col.lower():
                nome_col = col
                break
    
    if valor_col:
        df_cr_proc['valor_numerico'] = parse_currency(df_cr_proc[valor_col])
    else:
        df_cr_proc['valor_numerico'] = 0.0
    
    if venc_col:
        df_cr_proc['data_vencimento'] = pd.to_datetime(df_cr_proc[venc_col], errors='coerce', dayfirst=True)
    else:
        df_cr_proc['data_vencimento'] = pd.NaT
    
    hoje = datetime.now()
    df_cr_proc['dias_atraso'] = (hoje - df_cr_proc['data_vencimento']).dt.days
    
    def categorizar_atraso(dias):
        if pd.isna(dias):
            return 'Sem Data'
        elif dias <= 30:
            return '0-30 dias'
        elif dias <= 60:
            return '31-60 dias'
        elif dias <= 90:
            return '61-90 dias'
        else:
            return '>90 dias'
    
    df_cr_proc['faixa_atraso'] = df_cr_proc['dias_atraso'].apply(categorizar_atraso)
    
    total_aberto = df_cr_proc['valor_numerico'].sum()
    clientes_inadimplentes = df_cr_proc[cpf_col].nunique() if cpf_col else len(df_cr_proc)
    repasse_sittax = total_aberto * 0.30
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total em Aberto", f"R$ {int(total_aberto):,}".replace(",", "."))
    c2.metric("Clientes Inadimplentes", int(clientes_inadimplentes))
    c3.metric("Repasse Sittax (30%)", f"R$ {int(repasse_sittax):,}".replace(",", "."))
    
    st.divider()
    
    st.subheader("📊 Distribuição de Clientes por Faixa de Atraso")
    col_rosca, col_tabela = st.columns([1.2, 1.8])
    
    with col_rosca:
        aging_data = df_cr_proc[df_cr_proc['faixa_atraso'] != 'Sem Data'].groupby('faixa_atraso')[cpf_col if cpf_col else df_cr_proc.columns[0]].nunique().reset_index()
        aging_data.columns = ['Faixa', 'Quantidade']
        
        ordem_faixas = ['0-30 dias', '31-60 dias', '61-90 dias', '>90 dias']
        aging_data['Faixa'] = pd.Categorical(aging_data['Faixa'], categories=ordem_faixas, ordered=True)
        aging_data = aging_data.sort_values('Faixa')
        
        total_clientes = aging_data['Quantidade'].sum()
        aging_data['Percentual'] = (aging_data['Quantidade'] / total_clientes * 100).round(1)
        aging_data['Label'] = aging_data['Faixa'].astype(str) + ' - ' + aging_data['Percentual'].astype(str) + '%'
        
        fig = px.pie(aging_data, values='Quantidade', names='Label', title="Clientes por Faixa de Atraso", 
                     hole=0.4, color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#FF6B6B', '#E74C3C'])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_tabela:
        df_aging_cliente = df_cr_proc[df_cr_proc['faixa_atraso'] != 'Sem Data'].copy()
        
        if nome_col:
            df_aging_cliente = df_aging_cliente.groupby(nome_col).agg({
                'valor_numerico': 'sum',
                'data_vencimento': 'count'
            }).reset_index()
            df_aging_cliente.columns = ['Cliente', 'Valor Total', 'Mensalidades']
        else:
            df_aging_cliente = df_aging_cliente.groupby(cpf_col if cpf_col else df_aging_cliente.columns[0]).agg({
                'valor_numerico': 'sum',
                'data_vencimento': 'count'
            }).reset_index()
            df_aging_cliente.columns = ['Cliente', 'Valor Total', 'Mensalidades']
        
        def faixa_por_qtd(qtd):
            if qtd == 1:
                return '0-30 dias'
            elif qtd == 2:
                return '31-60 dias'
            elif qtd == 3:
                return '61-90 dias'
            else:
                return '>90 dias'
        
        df_aging_cliente['Faixa de Atraso'] = df_aging_cliente['Mensalidades'].apply(faixa_por_qtd)
        df_aging_cliente['Valor Total'] = df_aging_cliente['Valor Total'].apply(lambda x: f"R$ {int(x):,}".replace(",", "."))
        df_aging_cliente = df_aging_cliente[['Cliente', 'Mensalidades', 'Valor Total', 'Faixa de Atraso']]
        df_aging_cliente.columns = ['Cliente', 'Mensalidades em Aberto', 'Valor Total em Aberto', 'Dias em Atraso']
        
        st.dataframe(df_aging_cliente, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.subheader("📈 Total em Aberto por Mês de Vencimento")
    
    df_cr_proc['mes_ano_venc'] = df_cr_proc['data_vencimento'].dt.strftime('%m/%Y')
    evolucao_mes = df_cr_proc[df_cr_proc['data_vencimento'].notna()].groupby('mes_ano_venc')['valor_numerico'].sum().reset_index()
    evolucao_mes = evolucao_mes.sort_values('mes_ano_venc')
    evolucao_mes.columns = ['Mês/Ano', 'Valor']
    
    fig = px.bar(evolucao_mes, x='Mês/Ano', y='Valor', title="Total em Aberto por Mês de Vencimento", 
                 color_discrete_sequence=[COLOR_PRIMARY], labels={'Valor': 'Valor (R$)'})
    fig.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
    fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("📋 Detalhamento de Contas a Receber")
    
    colunas_selecionadas = []
    for col in [venc_col, cpf_col, 'Nome', 'Descrição', valor_col]:
        if col and col in df_cr_proc.columns:
            colunas_selecionadas.append(col)
    
    if not colunas_selecionadas:
        colunas_selecionadas = df_cr_proc.columns[:5].tolist()
    
    df_exibicao = df_cr_proc[colunas_selecionadas].copy()
    st.dataframe(df_exibicao, use_container_width=True)
    
    csv = df_cr.to_csv(index=False)
    st.download_button(
        label="📥 Baixar Base Completa (CSV)",
        data=csv,
        file_name="contas_receber_completa.csv",
        mime="text/csv"
    )

if not st.session_state.usuario_logado:
    render_login()
else:
    st.sidebar.markdown(f"<h4 style='color: white;'>👤 Usuário: {st.session_state.email_usuario}</h4>", unsafe_allow_html=True)
    
    df_processed, df_contas_receber = processar_dados(st.session_state.empresa)
    
    if df_processed is not None:
        if st.session_state.page == 'comercial':
            render_page_comercial(df_processed)
        else:
            render_page_inadimplencia(df_contas_receber)
    else:
        st.error("Erro ao carregar os dados.")
