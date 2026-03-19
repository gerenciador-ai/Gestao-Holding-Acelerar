import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import os
from core.nibo_api import NiboAPI
from core.dre_engine import DREEngine

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
    
    /* Layout Fluido da Sidebar e REMOVER BOTÃO DE RECOLHER (DEIXAR FIXO) */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
    }}
    
    /* Esconde o botão de fechar (dentro da sidebar) */
    button[data-testid="sidebar-collapse-button"] {{
        display: none !important;
    }}
    
    /* Esconde o botão de abrir (no topo da página) */
    button[kind="headerNoPadding"] {{
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

def get_sheet_url(sheet_id, gid='0'):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

@st.cache_data(ttl=600)
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def parse_currency(value):
    if pd.isna(value): return 0.0
    if isinstance(value, (int, float)): return float(value)
    clean = str(value).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try: return float(clean)
    except: return 0.0

# 1. TELA DE LOGIN
if not st.session_state.usuario_logado:
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.image(LOGOS["ACELERAR_LOGIN"], use_container_width=True)
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                df_users = load_data(get_sheet_url(USUARIOS_SHEET_ID))
                if df_users is not None:
                    user_exists = df_users[df_users['email'].str.lower() == email.lower()]
                    if not user_exists.empty and senha == SENHA_MESTRA:
                        st.session_state.usuario_logado = True
                        st.session_state.email_usuario = email
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")

# 2. DASHBOARD (SÓ RENDERIZA SE LOGADO)
else:
    # Sidebar
    with st.sidebar:
        st.image(LOGOS["ACELERAR_SIDEBAR"], use_container_width=True)
        st.divider()
        st.session_state.empresa = st.selectbox("Selecione a Unidade", list(EMPRESAS.keys()))
        
        # Carregamento de dados base
        conf = EMPRESAS[st.session_state.empresa]
        df_v = load_data(get_sheet_url(conf['vendas_id'], conf['vendas_gid']))
        df_c = load_data(get_sheet_url(conf['cancelados_id'], conf['cancelados_gid']))
        df_cr = load_data(get_sheet_url(conf['contas_receber_id']))
        
        df_p = None
        if df_v is not None and df_c is not None:
            df_v_proc = df_v.copy()
            df_v_proc.columns = df_v_proc.columns.str.strip().str.lower()
            df_c_proc = df_c.copy()
            df_c_proc.columns = df_c_proc.columns.str.strip().str.lower()
            
            df_v_proc['mrr'] = df_v_proc['mrr'].apply(parse_currency)
            df_v_proc['upgrade'] = df_v_proc['upgrade'].apply(parse_currency)
            df_v_proc['adesao'] = df_v_proc['adesao'].apply(parse_currency)
            df_v_proc['data'] = pd.to_datetime(df_v_proc['data'], errors='coerce', dayfirst=True)
            
            df_c_proc['mrr'] = df_c_proc['mrr'].apply(parse_currency)
            df_c_proc['data_cancelamento'] = pd.to_datetime(df_c_proc['data_cancelamento'], errors='coerce', dayfirst=True)
            
            df_p = df_v_proc.copy()
            
            # Filtros de Data
            anos = sorted(df_p['data'].dt.year.dropna().unique().astype(int), reverse=True)
            ano_sel = st.selectbox("Ano", anos)
            df_ano = df_p[df_p['data'].dt.year == ano_sel].copy()
            
            meses_pt = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
            df_ano['mes_num'] = df_ano['data'].dt.month
            df_ano['mes_nome'] = df_ano['mes_num'].map(meses_pt)
            
            meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            meses_disponiveis = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
            mes_atual_nome = meses_pt.get(datetime.now().month)
            mes_padrao = [mes_atual_nome] if mes_atual_nome in meses_disponiveis else ([meses_disponiveis[-1]] if meses_disponiveis else [])
            
            meses_sel = st.multiselect("Meses", meses_disponiveis, default=mes_padrao)
            
            # Filtros de Segmentação
            st.divider()
            prod_sel = st.selectbox("Produto", ["Todos"] + sorted(df_p['produto'].dropna().unique().tolist()))
            vend_sel = st.selectbox("Vendedor", ["Todos"] + sorted(df_p['vendedor'].dropna().unique().tolist()))
            sdr_sel = st.selectbox("SDR", ["Todos"] + sorted(df_p['sdr'].dropna().unique().tolist()))
            
            st.divider()
            if st.button("Sair"):
                st.session_state.usuario_logado = False
                st.rerun()

    # 3. RENDERIZAÇÃO DAS PÁGINAS
    logo_unidade_url = LOGOS["VMC_TECH"] if st.session_state.empresa == "VMC Tech" else LOGOS["VICTEC"]

    if df_p is not None:
        if st.session_state.page == 'comercial':
            # FILTRAGEM DE DADOS PARA A PÁGINA COMERCIAL
            df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
            if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
            if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
            if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]

            # HEADER E NAVEGAÇÃO
            col_nav_left, col_nav_right, col_nav_mid = st.columns([0.6, 0.2, 0.2])
            with col_nav_right:
                if st.button("📋 Inadimplência", use_container_width=True):
                    st.session_state.page = 'inadimplencia'
                    st.rerun()
            with col_nav_mid:
                if st.button("💰 Financeiro", use_container_width=True):
                    st.session_state.page = 'financeiro'
                    st.rerun()

            # Logo da Unidade redimensionado via width acima do título
            st.image(logo_unidade_url, width=150)
            st.title(f"📊 Resumo Comercial - {st.session_state.empresa}")
            
            # --- CORREÇÃO FINAL DA CONTABILIDADE COMERCIAL (CHURN DO MÊS) ---
            meses_pt_inv = {'Janeiro':1, 'Fevereiro':2, 'Março':3, 'Abril':4, 'Maio':5, 'Junho':6, 'Julho':7, 'Agosto':8, 'Setembro':9, 'Outubro':10, 'Novembro':11, 'Dezembro':12}
            mrr_conq = df_f['mrr'].sum()
            clientes_fechados = len(df_f)
            df_c_mes = df_c_proc[(df_c_proc['data_cancelamento'].dt.year == ano_sel) & 
                                 (df_c_proc['data_cancelamento'].dt.month.isin([meses_pt_inv[m] for m in meses_sel]))]
            churn_mrr = df_c_mes['mrr'].sum()
            mrr_liquido = mrr_conq - churn_mrr

            # KPIs Principais
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Vendas Brutas (MRR)", f"R$ {mrr_conq:,.2f}")
            with col2: st.metric("Vendas Líquidas", f"R$ {mrr_liquido:,.2f}")
            with col3: st.metric("Churn do Mês", f"R$ {churn_mrr:,.2f}", delta_color="inverse")
            with col4: st.metric("Contratos", clientes_fechados)

            st.divider()

            # Gráficos
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                df_evol = df_f.groupby('data')['mrr'].sum().reset_index()
                fig_evol = px.line(df_evol, x='data', y='mrr', title='Evolução de Vendas (MRR)', markers=True, color_discrete_sequence=[COLOR_SECONDARY])
                fig_evol.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_evol, use_container_width=True)
            
            with col_g2:
                df_planos = df_f.groupby('produto')['mrr'].sum().reset_index()
                fig_planos = px.pie(df_planos, values='mrr', names='produto', title='Distribuição por Plano', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
                fig_planos.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_planos, use_container_width=True)

            # Rankings de Vendedores
            st.markdown("#### 👤 Vendedores")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                df_rank_v_mrr = df_f.groupby('vendedor')['mrr'].sum().sort_values(ascending=True).reset_index()
                fig_v_mrr = px.bar(df_rank_v_mrr.tail(5), x='mrr', y='vendedor', orientation='h', title='Top 5 Vendedores (MRR)', text=df_rank_v_mrr.tail(5)['mrr'].apply(lambda x: f"R$ {int(x):,}"), color_discrete_sequence=[COLOR_PRIMARY])
                fig_v_mrr.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_v_mrr, use_container_width=True)
            with col_v2:
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
        
        elif st.session_state.page == 'inadimplencia':
            # PÁGINA DE INADIMPLÊNCIA
            col_nav_left, col_nav_right, col_nav_mid = st.columns([0.6, 0.2, 0.2])
            with col_nav_right:
                if st.button("📊 Comercial", use_container_width=True):
                    st.session_state.page = 'comercial'
                    st.rerun()
            with col_nav_mid:
                if st.button("💰 Financeiro", use_container_width=True):
                    st.session_state.page = 'financeiro'
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
                    else: return '+90 dias'
                
                df_cr_proc['faixa_atraso'] = df_cr_proc['dias_atraso'].apply(categorizar_atraso)
                
                # KPIs Inadimplência
                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1: st.metric("Total em Atraso", f"R$ {df_cr_proc['valor_numerico'].sum():,.2f}")
                with col_i2: st.metric("Títulos Vencidos", len(df_cr_proc))
                with col_i3: st.metric("Clientes Inadimplentes", df_cr_proc[cpf_col].nunique() if cpf_col else 0)
                
                st.divider()
                
                # 1. Gráfico de Envelhecimento (Aging)
                df_aging = df_cr_proc.groupby('faixa_atraso')['valor_numerico'].sum().reset_index()
                ordem_faixas = ['0-30 dias', '31-60 dias', '61-90 dias', '+90 dias']
                df_aging['faixa_atraso'] = pd.Categorical(df_aging['faixa_atraso'], categories=ordem_faixas, ordered=True)
                df_aging = df_aging.sort_values('faixa_atraso')
                
                fig = px.bar(df_aging, x='faixa_atraso', y='valor_numerico', title="Inadimplência por Faixa de Atraso (Aging)", color_discrete_sequence=[COLOR_CHURN], text=df_aging['valor_numerico'].apply(lambda x: f"R$ {x:,.0f}"))
                fig.update_layout(font=dict(color='white'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                
                # 2. Tabela de Resumo por Cliente (Ocupando largura total com Faixa de Atraso)
                st.subheader("👥 Resumo por Cliente")
                col_cliente = nome_col if nome_col else (cpf_col if cpf_col else df_cr_proc.columns[0])
                
                # Agrupamento que inclui a Faixa de Atraso predominante
                df_aging_cliente = df_cr_proc[df_cr_proc['faixa_atraso'] != 'Sem Data'].groupby(col_cliente).agg({
                    'valor_numerico': 'sum', 
                    'data_vencimento': 'count',
                    'faixa_atraso': lambda x: x.iloc[0] # Pega a primeira faixa de atraso encontrada para o cliente
                }).reset_index()
                
                # Renomeia as colunas para exibição
                df_aging_cliente.columns = ['Cliente', 'Valor Total', 'Mensalidades em Atraso', 'Faixa de Atraso']
                
                # Formata o valor para Real (R$)
                df_aging_cliente_view = df_aging_cliente.copy()
                df_aging_cliente_view['Valor Total'] = df_aging_cliente_view['Valor Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
                # Exibe a tabela ordenada pelas mensalidades em atraso
                st.dataframe(df_aging_cliente_view.sort_values(by='Mensalidades em Atraso', ascending=False), use_container_width=True, hide_index=True)
                
                st.divider()
                
                # 3. Detalhamento de Títulos (Largura total)
                st.subheader("📋 Detalhamento de Títulos")
                st.dataframe(df_cr_proc[[venc_col, cpf_col, nome_col, valor_col, 'faixa_atraso']].sort_values(by=venc_col), use_container_width=True, hide_index=True)
            
        elif st.session_state.page == 'financeiro':
            # PÁGINA FINANCEIRA (DRE/DFC)
            col_nav_left, col_nav_right, col_nav_mid = st.columns([0.6, 0.2, 0.2])
            with col_nav_right:
                if st.button("📊 Comercial", use_container_width=True):
                    st.session_state.page = 'comercial'
                    st.rerun()
            with col_nav_mid:
                if st.button("📋 Inadimplência", use_container_width=True):
                    st.session_state.page = 'inadimplencia'
                    st.rerun()

            st.image(logo_unidade_url, width=150)
            st.title(f"💰 Financeiro (DRE/DFC) - {st.session_state.empresa}")
            
            # Configuração da API Key (Bllog Tecnologia por enquanto)
            api_keys = {
                "Bllog Tecnologia": "9164337AD3094A38B40ECD97A26F8B41"
            }
            
            if st.session_state.empresa in api_keys:
                api_token = api_keys[st.session_state.empresa]
                nibo = NiboAPI(api_token)
                engine = DREEngine()
                
                with st.spinner(f"Extraindo dados do Nibo para {st.session_state.empresa}..."):
                    # Extrair dados do Nibo
                    df_receber = nibo.get_all_contas_receber()
                    df_pagar = nibo.get_all_contas_pagar()
                    
                    # Consolidar lançamentos
                    df_lancamentos = pd.concat([df_receber, df_pagar], ignore_index=True)
                    
                    if not df_lancamentos.empty:
                        # Processar com DREEngine
                        engine.processar_lançamentos(df_lancamentos, st.session_state.empresa)
                        
                        # Exibir DRE
                        st.subheader("📈 DRE (Demonstração do Resultado do Exercício)")
                        df_dre = engine.gerar_dre(st.session_state.empresa)
                        
                        # Estilizar DRE
                        def highlight_subtotal(s):
                            return ['font-weight: bold; background-color: #f0f2f6; color: #000000' if v == 'Subtotal' else '' for v in s]
                        
                        st.dataframe(
                            df_dre.style.apply(highlight_subtotal, axis=1),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        st.divider()
                        
                        # Exibir DFC
                        st.subheader("💰 DFC (Demonstração do Fluxo de Caixa)")
                        df_dfc = engine.gerar_dfc(df_lancamentos, st.session_state.empresa)
                        
                        # Gráfico de Fluxo de Caixa
                        fig_dfc = px.line(df_dfc, x='data', y='value', color='categoria', title="Evolução do Fluxo de Caixa por Categoria")
                        fig_dfc.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig_dfc, use_container_width=True)
                        
                        st.dataframe(df_dfc.sort_values('data', ascending=False), use_container_width=True, hide_index=True)
                        
                    else:
                        st.info(f"Nenhum lançamento financeiro encontrado no Nibo para {st.session_state.empresa}.")
            else:
                st.warning(f"Integração Nibo ainda não configurada para a empresa: {st.session_state.empresa}")
            
    else:
        st.error("Erro ao carregar os dados das planilhas.")

# Rodapé Dinâmico (Escondido via CSS para usuários, mas mantido no código para referência)
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
        © {datetime.now().year} Acelerar.tech - Sistema de Inteligência Comercial | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
""", unsafe_allow_html=True)
