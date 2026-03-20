import streamlit as st
import pandas as pd
import requests
from io import StringIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(layout="wide", page_title="Hub Holding Acelerar", page_icon="🏢", initial_sidebar_state="collapsed")

# 2. CONFIGURAÇÕES DE ACESSO
ID_SHEET = "15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk"
PASS_MESTRA = "Acelerar@2026"

# 3. ESTADOS DE SESSÃO
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False
if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = None
if "modulo" not in st.session_state:
    st.session_state.modulo = "hub"

# 4. CARREGAMENTO DE USUÁRIOS
@st.cache_data(ttl=600)
def carregar_usuarios():
    try:
        url_base = "https://docs.google.com/spreadsheets/d/"
        url_mid = ID_SHEET
        url_end = "/export?format=csv"
        url = url_base + url_mid + url_end
        res = requests.get(url )
        if res.status_code == 200:
            df = pd.read_csv(StringIO(res.text))
            return df.iloc[:, 0].astype(str).str.strip().str.lower().tolist()
        return []
    except:
        return []

# 5. INJEÇÃO DE CSS (FORMATO ULTRA SEGURO)
# Strings curtas e concatenadas para evitar erros de interpretador
s1 = "<style>.stApp { background-color: #0A1E2E; } "
s2 = "[data-testid='stSidebar'] { display: none !important; } "
s3 = "[data-testid='collapsedControl'] { display: none !important; } "
s4 = ".login-box { background-color: #0B2A4E; padding: 40px; border-radius: 15px; "
s5 = "border: 1px solid #89CFF0; box-shadow: 0 10px 25px rgba(0,0,0,0.5); "
s6 = "max-width: 450px; margin: 5% auto; text-align: center; }</style>"
st.write(s1 + s2 + s3 + s4 + s5 + s6, unsafe_allow_html=True)

# 6. TELA DE LOGIN
def tela_login():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.write("<div class='login-box'>", unsafe_allow_html=True)
        img_url = "https://raw.githubusercontent.com/gerenciador-ai/Relat-rios-Comercial/main/logo_acelerar_sidebar.png"
        st.image(img_url, width=250 )
        st.write("<h2 style='color: white; margin-top: 20px;'>Portal da Holding</h2>", unsafe_allow_html=True)
        email = st.text_input("E-mail corporativo", placeholder="seuemail@acelerar.tech")
        senha = st.text_input("Senha mestra", type="password")
        st.write("  
", unsafe_allow_html=True)
        if st.button("Acessar Portal", use_container_width=True):
            users = carregar_usuarios()
            email_in = email.strip().lower()
            if (email_in in users or email_in == "acelerar@acelerar.tech") and senha == PASS_MESTRA:
                st.session_state.usuario_logado = True
                st.session_state.email_usuario = email_in
                st.rerun()
            else:
                st.error("❌ Acesso negado.")
        st.write("</div>", unsafe_allow_html=True)

# 7. PORTAL HUB
def portal_hub():
    user_name = st.session_state.email_usuario.split("@")[0].upper()
    st.write("<h1 style='color: white; text-align: center;'>🚀 Bem-vindo, " + user_name + "!</h1>", unsafe_allow_html=True)
    st.write("<h4 style='color: #89CFF0; text-align: center;'>Escolha o módulo para iniciar:</h4>", unsafe_allow_html=True)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 📊 Módulo Comercial")
        if st.button("Acessar Comercial", use_container_width=True, type="primary"):
            st.session_state.modulo = "comercial"
            st.rerun()
    with col2:
        st.success("### 💰 Módulo Financeiro")
        if st.button("Acessar Financeiro", use_container_width=True, type="primary"):
            st.session_state.modulo = "financeiro"
            st.rerun()
    st.divider()
    if st.button("🚪 Sair do Portal"):
        st.session_state.usuario_logado = False
        st.rerun()

# 8. NAVEGAÇÃO
if not st.session_state.usuario_logado:
    tela_login()
else:
    if st.session_state.modulo == "hub":
        portal_hub()
    elif st.session_state.modulo == "comercial":
        try:
            with open("comercial/comercial.py", encoding="utf-8") as f:
                code_to_run = f.read()
                exec(code_to_run)
        except Exception as e:
            st.error("Erro no módulo Comercial: " + str(e))
    elif st.session_state.modulo == "financeiro":
        st.info("### 💰 Módulo Financeiro em Desenvolvimento")
        if st.button("Voltar ao Hub"):
            st.session_state.modulo = "hub"
            st.rerun()
