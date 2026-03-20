import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Hub Holding Acelerar", page_icon="🏢", layout="wide")

# 2. CONFIGURAÇÕES DE ACESSO (IDÊNTICAS AO COMERCIAL.PY)
USUARIOS_SHEET_ID = '15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk'
SENHA_MESTRA = 'Acelerar@2026'

# 3. FUNÇÃO DE CARREGAMENTO DE USUÁRIOS (EXATA DO COMERCIAL.PY)
@st.cache_data(ttl=600)
def carregar_usuarios_autorizados():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{USUARIOS_SHEET_ID}/export?format=csv"
        response = requests.get(url )
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            # Pega a primeira coluna (E-mail) e limpa espaços/letras
            return df.iloc[:, 0].astype(str).str.strip().str.lower().tolist()
        return []
    except:
        return []

# 4. INICIALIZAÇÃO DO ESTADO DA SESSÃO
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = False
if 'email_usuario' not in st.session_state:
    st.session_state.email_usuario = ""
if 'modulo' not in st.session_state:
    st.session_state.modulo = 'hub'

# 5. TELA DE LOGIN (ESTILO ACELERAR)
def tela_login():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        }
        .login-box {
            background-color: rgba(45, 45, 45, 0.9);
            padding: 3rem;
            border-radius: 15px;
            border: 1px solid #4CAF50;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            max-width: 450px;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        # Usa o logo de login centralizado
        st.image("logo_acelerar_login.png", width=250)
        st.markdown("<h2 style='text-align: center; color: white;'>Portal da Holding</h2>", unsafe_allow_html=True)
        
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Acessar Portal", use_container_width=True):
            usuarios_permitidos = carregar_usuarios_autorizados()
            email_input = email.strip().lower()
            
            # VERIFICAÇÃO IDÊNTICA AO COMERCIAL.PY
            if (email_input in usuarios_permitidos or email_input == 'acelerar@acelerar.tech') and senha == SENHA_MESTRA:
                st.session_state.usuario_logado = True
                st.session_state.email_usuario = email_input
                st.rerun()
            else:
                st.error("❌ Acesso negado. Verifique seu e-mail ou a senha mestra.")
        st.markdown("</div>", unsafe_allow_html=True)

# 6. PORTAL DE SELEÇÃO DE MÓDULOS
def portal_hub():
    st.title(f"🚀 Bem-vindo, {st.session_state.email_usuario.split('@')[0].upper()}!")
    st.subheader("Escolha o módulo que deseja acessar:")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("### 📊 Módulo Comercial")
        st.write("Gestão de Vendas, Churn e Inadimplência.")
        if st.button("Acessar Comercial", use_container_width=True, type="primary"):
            st.session_state.modulo = 'comercial'
            st.rerun()
            
    with col2:
        st.success("### 💰 Módulo Financeiro")
        st.write("DRE, DFC e Integração Nibo (Piloto Bllog).")
        if st.button("Acessar Financeiro", use_container_width=True, type="primary"):
            st.session_state.modulo = 'financeiro'
            st.rerun()
            
    st.divider()
    if st.button("🚪 Sair do Portal", use_container_width=False):
        st.session_state.usuario_logado = False
        st.rerun()

# 7. LÓGICA PRINCIPAL DE NAVEGAÇÃO
if not st.session_state.usuario_logado:
    tela_login()
else:
    if st.session_state.modulo == 'hub':
        portal_hub()
    elif st.session_state.modulo == 'comercial':
        # Executa o comercial.py sem alterações
        try:
            with open("comercial/comercial.py", encoding="utf-8") as f:
                exec(f.read())
        except Exception as e:
            st.error(f"Erro ao carregar o módulo Comercial: {e}")
    elif st.session_state.modulo == 'financeiro':
        st.info("Módulo Financeiro em desenvolvimento.")
        if st.button("Voltar ao Hub"):
            st.session_state.modulo = 'hub'
            st.rerun()
