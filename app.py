import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

# Configuração da página - Estilo Sênior Premium
st.set_page_config(layout="wide", page_title="Dashboard Comercial Estratégico", page_icon="📊")

# Paleta de Cores Acelerar.tech
COLOR_PRIMARY = "#0B2A4E"  # Azul Marinho
COLOR_SECONDARY = "#89CFF0" # Azul Claro (Usado para Títulos e Destaques)
COLOR_TEXT = "#FFFFFF"      # Branco
COLOR_BG = "#0B2A4E"        # Fundo Escuro (Conforme print)
COLOR_CHURN = "#E74C3C"     # Vermelho para Perdas

# Função para carregar imagem local e converter para base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# Estilização CSS Customizada - VERSÃO CONTRASTE PREMIUM
st.markdown(f"""
    <style>
    .main {{ background-color: {COLOR_BG}; }}
    
    /* Estilo Base dos Cards */
    div[data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 15px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: {COLOR_TEXT} !important;
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: {COLOR_TEXT} !important;
    }}
    
    div[data-testid="stMetricLabel"] > div {{
        color: {COLOR_TEXT} !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }}

    /* CORREÇÃO DO CARD DE CHURN (3º CARD DA LINHA 1) */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] > div {{
        background-color: rgba(231, 76, 60, 0.2) !important; /* Fundo vermelho suave */
        color: {COLOR_CHURN} !important;
        padding: 2px 10px !important;
        border-radius: 20px !important;
    }}
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] svg {{
        fill: {COLOR_CHURN} !important;
        transform: rotate(180deg) !important; /* Seta para baixo */
    }}

    /* AJUSTE DE CONTRASTE NOS TÍTULOS (GERAL) */
    h1 {{ color: {COLOR_SECONDARY} !important; font-weight: 800 !important; }}
    h2, h3 {{ color: {COLOR_SECONDARY} !important; font-weight: 700 !important; }}
    
    /* REFINAMENTO DA SIDEBAR */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label {{
        color: {COLOR_TEXT} !important;
        font-weight: 600 !important;
    }}
    
    /* Estilo para as caixas de seleção (Inputs) */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {{
        background-color: #F8F9FA !important;
        color: {COLOR_PRIMARY} !important;
        border-radius: 5px !important;
    }}

    /* Cor do texto dentro do expander e ícones */
    [data-testid="stSidebar"] .stExpander {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# IDs e GIDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719"
CONTAS_RECEBER_ID = "1Nqmn2c9p0QFu8LFIqFQ0EBxA8klHFUsVjAW15la-Fjg"

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv" + (f"&gid={gid}" if gid else "" )
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
        if ',' in s: s = s.replace('.', '').replace(',', '.')
        elif '.' in s and len(s.split('.')[-1]) != 2: s = s.replace('.', '')
        try: return float(s)
        except: return 0.0
    return series.apply(clean_val)

def processar_dados():
    df_v = load_data(VENDAS_ID, VENDAS_GID)
    df_c = load_data(CANCELADOS_ID, CANCELADOS_GID)
    df_cr = load_data(CONTAS_RECEBER_ID)
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
    df['inicio_semana'] = df['data'].apply(lambda x: x - pd.Timedelta(days=x.weekday()))
    df['status'] = 'Confirmada'
    if not df_c.empty:
        canc_cnpjs = df_c['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True).unique()
        df.loc[df['cnpj'].isin(canc_cnpjs), 'status'] = 'Cancelada'
    
    # Processamento Contas a Receber (Inadimplência)
    if not df_cr.empty:
        df_cr['valor'] = parse_currency(df_cr['Valor'])
        df_cr['vencimento'] = pd.to_datetime(df_cr['Vencimento'], errors='coerce')
        df_cr = df_cr.dropna(subset=['vencimento'])
        df_cr['ano'] = df_cr['vencimento'].dt.year.astype(int)
        df_cr['mes_nome'] = df_cr['vencimento'].dt.month.map(meses_pt)
        df_cr['status_pagamento'] = df_cr['Status'].fillna("Pendente")
    
    return df, df_cr

df_processed, df_cr_processed = processar_dados()

if df_processed is not None:
    # Sidebar com Logotipo FIXO NO TOPO
    logo_base64 = get_base64_of_bin_file('/home/ubuntu/logo_acelerar_tech.png')
    if logo_base64:
        st.sidebar.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{logo_base64}" width="180"></div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("<h3 style='color: white; text-align: center;'>🔍 Filtros Estratégicos</h3>", unsafe_allow_html=True)
    
    # Navegação entre Abas
    aba_selecionada = st.sidebar.radio("Navegação", ["Resumo Comercial", "Resumo Inadimplência"])
    
    st.sidebar.divider()
    
    if aba_selecionada == "Resumo Comercial":
        anos = sorted(df_processed['ano'].unique(), reverse=True)
        ano_sel = st.sidebar.selectbox("📅 Ano", anos)
        df_ano = df_processed[df_processed['ano'] == ano_sel]
        
        with st.sidebar.expander("📅 Período (Meses)"):
            meses_ordem = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
            meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
            meses_sel = st.multiselect("Meses", meses_disp, default=meses_disp)
        
        prod_sel = st.sidebar.selectbox("📦 Produto", ["Todos"] + sorted(df_processed['produto'].unique().tolist()))
        vend_sel = st.sidebar.selectbox("👤 Vendedor", ["Todos"] + sorted(df_processed['vendedor'].unique().tolist()))
        sdr_sel = st.sidebar.selectbox("🎧 SDR", ["Todos"] + sorted(df_processed['sdr'].unique().tolist()))

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
        base_ativa = len(df_processed[df_processed['status'] == 'Confirmada']) - len(df_processed[df_processed['status'] == 'Cancelada'])
        churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0

        st.title("📊 Resumo Comercial - VMC Tech")
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
        c2.metric("MRR Ativo (Net)", f"R$ {int(mrr_conq - mrr_perd):,}".replace(",", "."))
        c3.metric("MRR Perdido (Churn)", f"R$ {int(mrr_perd):,}".replace(",", "."), delta=f"{churn_p:.1f}% do Conq")
        c4.metric("Total de Upsell", f"R$ {int(upsell_v):,}".replace(",", "."), delta=f"{upsell_q} eventos")
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
            st.plotly_chart(px.bar(df_m, x='mes_nome', y='mrr', text='cliente', title="MRR Conquistado", color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white")), use_container_width=True)
        with col2:
            df_u = df_ano[df_ano['upgrade'] > 0].groupby(['mes_num','mes_nome']).agg({'upgrade':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
            st.plotly_chart(px.bar(df_u, x='mes_nome', y='upgrade', text='cliente', title="Evolução de Upsell", color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white")), use_container_width=True)
        with col3:
            df_c_evol = df_ano[df_ano['status'] == 'Cancelada'].groupby(['mes_num','mes_nome']).agg({'mrr':'sum', 'cliente':'count'}).reset_index().sort_values('mes_num')
            st.plotly_chart(px.bar(df_c_evol[df_c_evol['mrr']>0], x='mes_nome', y='mrr', text='cliente', title="Evolução de Churn", color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white")), use_container_width=True)

        st.divider()
        
        # Rankings de SDRs (Top 5)
        st.subheader("🏆 Rankings de SDRs (Top 5)")
        cs1, cs2 = st.columns(2)
        with cs1:
            df_s_c = df_f[df_f['status'] == 'Confirmada'].groupby('sdr')['cliente'].count().sort_values().tail(5).reset_index()
            st.plotly_chart(px.bar(df_s_c, x='cliente', y='sdr', orientation='h', title='Top 5 SDRs (Contratos)', text='cliente', color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=300), use_container_width=True)
        with cs2:
            df_s_m = df_f[df_f['status'] == 'Confirmada'].groupby('sdr')['mrr'].sum().sort_values().tail(5).reset_index()
            st.plotly_chart(px.bar(df_s_m, x='mrr', y='sdr', orientation='h', title='Top 5 SDRs (MRR)', text=df_s_m['mrr'].apply(lambda x: f"R$ {int(x):,}"), color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=300), use_container_width=True)

        st.divider()
        
        # Rankings de Vendedores
        st.subheader("🏆 Rankings de Vendedores")
        cv1, cv2 = st.columns(2)
        with cv1:
            df_v_c = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['cliente'].count().sort_values().tail(10).reset_index()
            st.plotly_chart(px.bar(df_v_c, x='cliente', y='vendedor', orientation='h', title='Top Vendedores (Contratos)', text='cliente', color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400), use_container_width=True)
        with cv2:
            df_v_m = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['mrr'].sum().sort_values().tail(10).reset_index()
            st.plotly_chart(px.bar(df_v_m, x='mrr', y='vendedor', orientation='h', title='Top Vendedores (MRR)', text=df_v_m['mrr'].apply(lambda x: f"R$ {int(x):,}"), color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400), use_container_width=True)

        st.divider()
        st.subheader("📋 Detalhamento Comercial")
        st.dataframe(df_f[['data', 'cliente', 'vendedor', 'sdr', 'produto', 'status', 'mrr', 'upgrade']].sort_values('data', ascending=False), use_container_width=True)

    elif aba_selecionada == "Resumo Inadimplência":
        st.title("📉 Resumo Inadimplência - VMC Tech")
        
        if df_cr_processed is not None and not df_cr_processed.empty:
            anos_cr = sorted(df_cr_processed['ano'].unique(), reverse=True)
            ano_cr_sel = st.sidebar.selectbox("📅 Ano Inadimplência", anos_cr)
            df_cr_f = df_cr_processed[(df_cr_processed['ano'] == ano_cr_sel) & (df_cr_processed['status_pagamento'] != "Pago")]
            
            total_inad = df_cr_f['valor'].sum()
            total_clientes_inad = df_cr_f['Cliente'].nunique()
            
            ci1, ci2 = st.columns(2)
            ci1.metric("Total Inadimplência", f"R$ {int(total_inad):,}".replace(",", "."))
            ci2.metric("Clientes Inadimplentes", total_clientes_inad)
            
            st.divider()
            
            st.subheader("📈 Inadimplência por Mês")
            df_cr_m = df_cr_f.groupby('mes_nome')['valor'].sum().reset_index()
            st.plotly_chart(px.bar(df_cr_m, x='mes_nome', y='valor', title="Inadimplência Mensal", color_discrete_sequence=[COLOR_SECONDARY]).update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white")), use_container_width=True)
            
            st.divider()
            st.subheader("📋 Detalhamento Inadimplência")
            st.dataframe(df_cr_f[['vencimento', 'Cliente', 'valor', 'Status']].sort_values('vencimento', ascending=False), use_container_width=True)
        else:
            st.warning("Dados de Contas a Receber não encontrados ou vazios.")

else:
    st.error("Nenhum dado válido encontrado para os filtros selecionados.")
