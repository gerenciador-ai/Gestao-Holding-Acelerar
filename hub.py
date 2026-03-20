import streamlit as st
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Hub Holding Acelerar", page_icon="🏢", layout="wide")

# DICIONÁRIO DE USUÁRIOS (Migrado do comercial.py)
USUARIOS = {
    "acelerar@acelerar.tech": "Acelerar@2024",
    "vmctech@acelerar.tech": "Vmc@2024",
    "victec@acelerar.tech": "Victec@2024",
    "bllog@acelerar.tech": "Bllog@2024"
}

# INICIALIZAÇÃO DO ESTADO DA SESSÃO
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = False
if 'email_usuario' not in st.session_state:
    st.session_state.email_usuario = ""
if 'modulo' not in st.session_state:
    st.session_state.modulo = 'hub' # hub, comercial, financeiro

# FUNÇÃO DE LOGIN (Visual idêntico ao comercial.py)
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
        # Usando o logo de login centralizado
        st.image("logo_acelerar_login.png", width=250)
        st.markdown("<h2 style='text-align: center; color: white;'>Portal da Holding</h2>", unsafe_allow_html=True)
        
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Acessar Portal", use_container_width=True):
            if email in USUARIOS and USUARIOS[email] == senha:
                st.session_state.usuario_logado = True
                st.session_state.email_usuario = email
                st.rerun()
            else:
                st.error("Credenciais inválidas. Tente novamente.")
        st.markdown("</div>", unsafe_allow_html=True)

# PORTAL DE MÓDULOS (O Hub Real)
def portal_hub():
    st.title(f"🚀 Bem-vindo, {st.session_state.email_usuario.split('@')[0].upper()}!")
    st.subheader("Escolha o módulo que deseja acessar:")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("### 📊 Módulo Comercial")
        st.write("Gestão de Vendas, Churn e Inadimplência das unidades da holding.")
        if st.button("Acessar Comercial", use_container_width=True, type="primary"):
            st.session_state.modulo = 'comercial'
            st.rerun()
            
    with col2:
        st.success("### 💰 Módulo Financeiro")
        st.write("DRE, DFC e Integração com Nibo (Piloto Bllog).")
        if st.button("Acessar Financeiro", use_container_width=True, type="primary"):
            st.session_state.modulo = 'financeiro'
            st.rerun()
            
    st.divider()
    if st.button("🚪 Sair do Portal", use_container_width=False):
        st.session_state.usuario_logado = False
        st.rerun()

# LÓGICA PRINCIPAL DE NAVEGAÇÃO
if not st.session_state.usuario_logado:
    tela_login()
else:
    if st.session_state.modulo == 'hub':
        portal_hub()
    elif st.session_state.modulo == 'comercial':
        # Executa o arquivo comercial.py sem precisar alterar nada nele
        try:
            with open("comercial/comercial.py", encoding="utf-8") as f:
                exec(f.read())
        except FileNotFoundError:
            st.error("Arquivo comercial/comercial.py não encontrado.")
    elif st.session_state.modulo == 'financeiro':
        st.info("Módulo Financeiro em desenvolvimento (Piloto Bllog).")
        if st.button("Voltar ao Hub"):
            st.session_state.modulo = 'hub'
            st.rerun()
