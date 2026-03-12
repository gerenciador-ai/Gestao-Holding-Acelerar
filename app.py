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

st.markdown(f"""
    <style>
    * {{
        margin: 0;
        padding: 0;
    }}
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {{
        background-color: #0A1E2E !important;
        color: #FFFFFF !important;
        width: 100% !important;
        height: 100% !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: #0B2A4E !important;
    }}
    [data-testid="stHeader"] {{
        background-color: #0A1E2E !important;
        display: none !important;
    }}
    [data-testid="stToolbar"] {{
        display: none !important;
    }}
    footer {{
        display: none !important;
    }}
    .stApp > header {{
        display: none !important;
    }}
    [data-testid="stDecoration"] {{
        display: none !important;
    }}
    a[href*="github"], a[href*="deploy"], a[href*="settings"] {{
        display: none !important;
    }}
    
    /* CORREÇÃO DE TÍTULOS - AZUL CLARO PARA ALTO CONTRASTE */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_SECONDARY} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: bold !important;
    }}
    
    div[data-testid="stMetric"] {{
        background-color: #0B2A4E !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        color: #FFFFFF !important;
        min-width: 180px !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        color: #FFFFFF !important;
    }}
    div[data-testid="stMetricLabel"] > div {{
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
    }}
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {{
        border: 2px solid #E74C3C !important;
    }}
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricLabel"] > div,
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {{
        color: #E74C3C !important;
    }}
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] > div {{
        background-color: rgba(231, 76, 60, 0.2) !important;
        color: #E74C3C !important;
        padding: 2px 8px !important;
        border-radius: 15px !important;
    }}
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] svg {{
        fill: #E74C3C !important;
        stroke: #E74C3C !important;
    }}
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stExpander p,
    [data-testid="stSidebar"] .stMultiSelect label {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {{
        background-color: #F8F9FA !important;
        color: #0B2A4E !important;
        border-radius: 5px !important;
    }}
    [data-testid="stSidebar"] .stExpander {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }}
    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }}
    .login-card {{
        background-color: rgba(10, 30, 46, 0.95) !important;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        width: 100%;
        max-width: 400px;
        border: 2px solid #89CFF0;
    }}
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
    except:
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div style="text-align: center; margin-top: 80px; margin-bottom: 40px;">
                <h1 style="color: {COLOR_SECONDARY} !important; font-size: 2.5rem; font-weight: bold;">🔐 Dashboard Comercial</h1>
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
                            st.error("❌ E-mail não autorizado.")
                        else:
                            st.session_state.usuario_logado = True
                            st.session_state.email_usuario = email
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
    df['data'] = pd.to_datetime(df_v['Data de Ativação'], errors='coerce', dayfirst=False)
    df = df.dropna(subset=['data'])
    df['ano'] = df['data'].dt.year.astype(int)
    df['mes_num'] = df['data'].dt.month.astype(int)
    meses_pt = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
                7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
    df['mes_nome'] = df['mes_num'].map(meses_pt)
    df['inicio_semana'] = df['data'].apply(lambda x: x - pd.Timedelta(days=x.weekday()))
    df['status'] = "Confirmada"
    if not df_c.empty:
        canc_cnpjs = df_c['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True).unique()
        df.loc[df['cnpj'].isin(canc_cnpjs), 'status'] = "Cancelada"
    return df, df_cr

def render_page_comercial(df):
    st.sidebar.markdown(f"<h3 style='color: {COLOR_SECONDARY};'>⚙️ Filtros</h3>", unsafe_allow_html=True)
    st.session_state.empresa = st.sidebar.selectbox("🏢 Empresa", list(EMPRESAS.keys()), index=list(EMPRESAS.keys()).index(st.session_state.empresa))
    anos = sorted(df['ano'].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("📅 Ano", anos)
    df_ano = df[df['ano'] == ano_sel]
    meses_ordem = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
    meses_sel = st.sidebar.multiselect("🗓️ Meses", meses_disp, default=meses_disp)
    prod_sel = st.sidebar.selectbox("📦 Produto", ["Todos"] + sorted(df['produto'].unique().tolist()))
    vend_sel = st.sidebar.selectbox("👤 Vendedor", ["Todos"] + sorted(df['vendedor'].unique().tolist()))
    sdr_sel = st.sidebar.selectbox("🎧 SDR", ["Todos"] + sorted(df['sdr'].unique().tolist()))
    df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]
    col_nav_left, col_nav_right = st.columns([1, 1])
    with col_nav_left:
        if st.button("📋 Resumo Inadimplência", use_container_width=True):
            st.session_state.page = 'inadimplencia'
            st.rerun()
    st.markdown(f"<h1 style='color: {COLOR_SECONDARY};'>📊 Resumo Comercial - {st.session_state.empresa}</h1>", unsafe_allow_html=True)
    mrr_conq = df_f[df_f['status'] == "Confirmada"]['mrr'].sum()
    mrr_perd = df_f[df_f['status'] == "Cancelada"]['mrr'].sum()
    upsell_v = df_f['upgrade'].sum()
    upsell_q = len(df_f[df_f['upgrade'] > 0])
    cl_fech = len(df_f[(df_f['status'] == "Confirmada") & (df_f['mrr'] > 0)])
    cl_canc = len(df_f[df_f['status'] == "Cancelada"])
    tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
    base_ativa = len(df[df['status'] == "Confirmada"]) - len(df[df['status'] == "Cancelada"])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
    c2.metric("MRR Ativo (Net)", f"R$ {int(mrr_conq - mrr_perd):,}".replace(",", "."))
    c3.metric("MRR Perdido (Churn)", f"R$ {int(mrr_perd):,}".replace(",", "."), delta=f"- {churn_p:.1f}%", delta_color="inverse")
    c4, c5, c6 = st.columns(3)
    c4.metric("Total de Upsell", f"R$ {int(upsell_v):,}".replace(",", "."), delta=f"{upsell_q} eventos")
    c5.metric("Ticket Médio", f"R$ {int(tkt_med):,}".replace(",", "."))
    c6.metric("Adesão Total", f"R$ {int(df_f['adesao'].sum()):,}".replace(",", "."))
    c7, c8, c9 = st.columns(3)
    c7.metric("Clientes fechado (no periodo)", cl_fech)
    c8.metric("Clientes Cancelados (no periodo)", cl_canc)
    c9.metric("Total Clientes Ativos (Base)", base_ativa)
    st.divider()
    st.markdown(f"<h2 style='color: {COLOR_SECONDARY};'>📈 Evolução Mensal</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        df_m = df_ano[df_ano['status'] == "Confirmada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        fig = px.bar(df_m, x="mes_nome", y="mrr", text="cliente", title="MRR Conquistado", color_discrete_sequence=[COLOR_SECONDARY])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        df_u = df_ano[df_ano['upgrade'] > 0].groupby(["mes_num","mes_nome"]).agg({"upgrade":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        fig = px.bar(df_u, x="mes_nome", y="upgrade", text="cliente", title="Evolução de Upsell", color_discrete_sequence=[COLOR_TEXT])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        df_c = df_ano[df_ano['status'] == "Cancelada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        df_c = df_c[df_c['mrr'] > 0]
        fig = px.bar(df_c, x="mes_nome", y="mrr", text="cliente", title="Churn Mensal", color_discrete_sequence=[COLOR_CHURN])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    st.divider()
    st.markdown(f"<h2 style='color: {COLOR_SECONDARY};'>🎯 Performance vs. Metas</h2>", unsafe_allow_html=True)
    col4, col5 = st.columns(2)
    df_meta = df_f[df_f['status'] == "Confirmada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
    df_meta['mrr_a'] = df_meta['mrr'].cumsum()
    df_meta['cont_a'] = df_meta['cliente'].cumsum()
    df_meta['meta_m'] = [8000 * (i+1) for i in range(len(df_meta))]
    df_meta['meta_c'] = [17 * (i+1) for i in range(len(df_meta))]
    with col4:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["mrr_a"], name="Real", marker_color=COLOR_SECONDARY))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_m"], name="Meta (8k/mês)", line=dict(color=COLOR_TEXT, width=4)))
        fig.update_layout(title="MRR Acumulado vs. Meta", xaxis_title=None, yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    with col5:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["cont_a"], name="Real", marker_color=COLOR_SECONDARY))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_c"], name="Meta (17/mês)", line=dict(color=COLOR_TEXT, width=4)))
        fig.update_layout(title="Contratos Acumulados vs. Meta", xaxis_title=None, yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    st.divider()
    col6, col7 = st.columns(2)
    with col6:
        df_s = df_f[df_f['status'] == "Confirmada"].groupby("inicio_semana")["mrr"].sum().reset_index().sort_values("inicio_semana")
        df_s["data_s"] = df_s["inicio_semana"].dt.strftime("%d/%m/%Y")
        fig = go.Figure(go.Scatter(x=df_s["data_s"], y=df_s["mrr"], mode="lines+markers+text", text=df_s["mrr"].apply(lambda x: f"{x:,.0f}"), textposition="top center", line=dict(color=COLOR_SECONDARY, width=4)))
        fig.update_layout(title="MRR SEMANA", xaxis_title=None, yaxis_title=None, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    with col7:
        fig = px.pie(df_f, names="produto", values="mrr", title="Receita por Produto", hole=0.4, color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, "#FFFFFF", "#FFC107"])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    st.divider()
    st.markdown(f"<h2 style='color: {COLOR_SECONDARY};'>🏆 Ranking de Vendedores</h2>", unsafe_allow_html=True)
    col8, col9 = st.columns(2)
    with col8:
        df_vc = df_f[df_f['status'] == "Confirmada"].groupby("vendedor")["cliente"].count().reset_index().sort_values("cliente", ascending=False)
        fig = px.pie(df_vc, names="vendedor", values="cliente", title="Top Vendedores (Contratos)", hole=0.4, color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY])
        fig.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}  
%{value}")
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    with col9:
        df_vm = df_f[df_f['status'] == "Confirmada"].groupby("vendedor")["mrr"].sum().reset_index().sort_values("mrr", ascending=False)
        fig = px.pie(df_vm, names="vendedor", values="mrr", title="Top Vendedores (MRR)", hole=0.4, color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY])
        fig.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}  
R$ %{value:,.2f}")
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    st.divider()
    st.markdown(f"<h2 style='color: {COLOR_SECONDARY};'>📋 Detalhamento</h2>", unsafe_allow_html=True)
    st.dataframe(df_f[["data", "cliente", "vendedor", "produto", "status", "mrr", "upgrade", "adesao"]].sort_values("data", ascending=False), use_container_width=True, hide_index=True)

def render_page_inadimplencia(df_cr):
    col_nav_left, col_nav_right = st.columns([1, 1])
    with col_nav_right:
        if st.button("📊 Resumo Comercial", use_container_width=True):
            st.session_state.page = 'comercial'
            st.rerun()
    st.markdown(f"<h1 style='color: {COLOR_SECONDARY};'>📋 Resumo Inadimplência - {st.session_state.empresa}</h1>", unsafe_allow_html=True)
    if df_cr is None or df_cr.empty:
        st.warning("Base de Contas a Receber não encontrada ou vazia.")
        return
    df_cr_proc = df_cr.copy()
    df_cr_proc.columns = df_cr_proc.columns.str.strip()
    valor_col = next((c for c in df_cr_proc.columns if 'valor' in c.lower()), None)
    venc_col = next((c for c in df_cr_proc.columns if 'vencimento' in c.lower()), None)
    cpf_col = next((c for c in df_cr_proc.columns if 'cpf' in c.lower() or 'cnpj' in c.lower()), None)
    nome_col = next((c for c in df_cr_proc.columns if 'nome' in c.lower() and 'cliente' in c.lower()), next((c for c in df_cr_proc.columns if 'nome' in c.lower()), None))
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
    st.markdown(f"<h2 style='color: {COLOR_SECONDARY};'>📊 Distribuição de Clientes por Faixa de Atraso</h2>", unsafe_allow_html=True)
    col_rosca, col_tabela = st.columns([1.2, 1.8])
    with col_rosca:
        aging_data = df_cr_proc[df_cr_proc['faixa_atraso'] != 'Sem Data'].groupby('faixa_atraso')[cpf_col if cpf_col else df_cr_proc.columns[0]].nunique().reset_index()
        aging_data.columns = ['Faixa', 'Quantidade']
        ordem_faixas = ['0-30 dias', '31-60 dias', '61-90 dias', '>90 dias']
        aging_data['Faixa'] = pd.Categorical(aging_data['Faixa'], categories=ordem_faixas, ordered=True)
        aging_data = aging_data.sort_values('Faixa')
        fig = px.pie(aging_data, values='Quantidade', names='Faixa', title="Clientes por Faixa", hole=0.4, color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, '#FF6B6B', '#E74C3C'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
        st.plotly_chart(fig, use_container_width=True)
    with col_tabela:
        df_aging_cliente = df_cr_proc[df_cr_proc['faixa_atraso'] != 'Sem Data'].groupby(nome_col if nome_col else (cpf_col if cpf_col else df_cr_proc.columns[0])).agg({'valor_numerico': 'sum', 'data_vencimento': 'count'}).reset_index()
        df_aging_cliente.columns = ['Cliente', 'Valor Total', 'Mensalidades']
        st.dataframe(df_aging_cliente, use_container_width=True, hide_index=True)
    st.divider()
    st.markdown(f"<h2 style='color: {COLOR_SECONDARY};'>📈 Total em Aberto por Mês de Vencimento</h2>", unsafe_allow_html=True)
    df_cr_proc['mes_ano_venc'] = df_cr_proc['data_vencimento'].dt.strftime('%m/%Y')
    evolucao_mes = df_cr_proc[df_cr_proc['data_vencimento'].notna()].groupby('mes_ano_venc')['valor_numerico'].sum().reset_index().sort_values('mes_ano_venc')
    fig = px.bar(evolucao_mes, x='mes_ano_venc', y='valor_numerico', color_discrete_sequence=[COLOR_SECONDARY])
    fig.update_layout(xaxis_title=None, yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_TEXT)
    st.plotly_chart(fig, use_container_width=True)
    st.divider()
    st.markdown(f"<h2 style='color: {COLOR_SECONDARY};'>📋 Detalhamento de Contas a Receber</h2>", unsafe_allow_html=True)
    st.dataframe(df_cr_proc[[venc_col, cpf_col, nome_col, valor_col]].dropna(how='all', axis=1), use_container_width=True)

if not st.session_state.usuario_logado:
    render_login()
else:
    st.sidebar.markdown(f"<h4 style='color: white;'>👤 {st.session_state.email_usuario}</h4>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sair"):
        st.session_state.usuario_logado = False
        st.rerun()
    df_p, df_cr = processar_dados(st.session_state.empresa)
    if df_p is not None:
        if st.session_state.page == 'comercial': render_page_comercial(df_p)
        else: render_page_inadimplencia(df_cr)
    else: st.error("Erro ao carregar dados.")
