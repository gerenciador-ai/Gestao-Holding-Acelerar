import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import requests
from io import StringIO

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO SÊNIOR PREMIUM DO COMERCIAL.PY) ---
st.set_page_config(
    layout="wide", 
    page_title="Hub Holding Acelerar - Portal Estratégico", 
    page_icon="🏢", 
    initial_sidebar_state="expanded"
)

# CORES EXATAS DO SEU COMERCIAL.PY
COLOR_PRIMARY = "#0B2A4E"
COLOR_SECONDARY = "#89CFF0"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#0A1E2E"

# CONFIGURAÇÕES DE ACESSO (LITERAL DO COMERCIAL.PY)
USUARIOS_SHEET_ID = '15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk'
SENHA_MESTRA = 'Acelerar@2026'

# ESTADOS DE SESSÃO
if 'usuario_logado' not in st.session_state: st.session_state.usuario_logado = False
if 'email_usuario' not in st.session_state: st.session_state.email_usuario = None
if 'modulo' not in st.session_state: st.session_state.modulo = 'hub'

# FUNÇÃO DE CARREGAMENTO (LITERAL DO COMERCIAL.PY)
@st.cache_data(ttl=600)
def carregar_usuarios_autorizados():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{USUARIOS_SHEET_ID}/export?format=csv"
        response = requests.get(url )
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df.iloc[:, 0].astype(str).str.strip().str.lower().tolist()
        return []
    except:
        return []

# CSS DO LOGIN (ESTILO SÊNIOR PREMIUM DO COMERCIAL.PY)
st.markdown(f"""
    <style>
    .main {{ background-color: {COLOR_BG}; }}
    .login-container {{
        background-color: {COLOR_PRIMARY};
        padding: 40px;
        border-radius: 15px;
        border: 1px solid {COLOR_SECONDARY};
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        max-width: 450px;
        margin: auto;
        text-align: center;
    }}
    </style>
""", unsafe_allow_html=True)

def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        # Usando o logo de login centralizado
        st.image("https://raw.githubusercontent.com/gerenciador-ai/Relat-rios-Comercial/main/logo_acelerar_sidebar.png", width=250 )
        st.markdown(f"<h2 style='color: {COLOR_TEXT};'>Portal da Holding</h2>", unsafe_allow_html=True)
        
        email = st.text_input("E-mail corporativo")
        senha = st.text_input("Senha mestra", type="password")
        
        if st.button("Acessar Portal", use_container_width=True):
            usuarios_permitidos = carregar_usuarios_autorizados()
            email_input = email.strip().lower()
            
            # VERIFICAÇÃO LITERAL DO COMERCIAL.PY
            if (email_input in usuarios_permitidos or email_input == 'acelerar@acelerar.tech') and senha == SENHA_MESTRA:
                st.session_state.usuario_logado = True
                st.session_state.email_usuario = email_input
                st.rerun()
            else:
                st.error("❌ Acesso negado. Verifique seu e-mail ou a senha mestra.")
        st.markdown("</div>", unsafe_allow_html=True)

def portal_hub():
    st.title(f"🚀 Bem-vindo, {st.session_state.email_usuario.split('@')[0].upper()}!")
    st.subheader("Escolha o módulo da Holding Acelerar:")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 📊 Módulo Comercial")
        st.write("Vendas, Churn e Inadimplência.")
        if st.button("Acessar Comercial", use_container_width=True, type="primary"):
            st.session_state.modulo = 'comercial'
            st.rerun()
    with col2:
        st.success("### 💰 Módulo Financeiro")
        st.write("DRE, DFC e Nibo (Bllog).")
        if st.button("Acessar Financeiro", use_container_width=True, type="primary"):
            st.session_state.modulo = 'financeiro'
            st.rerun()
    
    st.divider()
    if st.button("🚪 Sair do Portal"):
        st.session_state.usuario_logado = False
        st.rerun()

# NAVEGAÇÃO PRINCIPAL
if not st.session_state.usuario_logado:
    tela_login()
else:
    if st.session_state.modulo == 'hub':
        portal_hub()
    elif st.session_state.modulo == 'comercial':
        try:
            with open("comercial/comercial.py", encoding="utf-8") as f:
                exec(f.read())
        except Exception as e:
            st.error(f"Erro ao carregar comercial.py: {e}")
    elif st.session_state.modulo == 'financeiro':
        st.info("Módulo Financeiro em desenvolvimento.")
        if st.button("Voltar ao Hub"):
            st.session_state.modulo = 'hub'
            st.rerun()
