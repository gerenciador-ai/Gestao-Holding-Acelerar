import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Comercial - Acelerar.tech", layout="wide")

# Identidade Visual (Cores)
AZUL_MARINHO = "#0B2A4E"
AZUL_CLARO = "#89CFF0"
VERMELHO_CHURN = "#FF4B4B"

# CSS Customizado para Estilo Sênior Premium
st.markdown(f"""
    <style>
    .main {{
        background-color: #f5f7f9;
    }}
    .stMetric {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid {AZUL_MARINHO};
    }}
    /* Estilo Específico para o Card de Churn (MRR Perdido) */
    [data-testid="stMetricValue"] {{
        font-weight: bold;
    }}
    /* Seletor para o card de Churn baseado no label (Streamlit 1.24+) */
    div[data-testid="stMetric"]:has(label:contains("MRR Perdido (Churn)")) {{
        border-left: 5px solid {VERMELHO_CHURN} !important;
    }}
    div[data-testid="stMetric"]:has(label:contains("MRR Perdido (Churn)")) [data-testid="stMetricValue"] {{
        color: {VERMELHO_CHURN} !important;
    }}
    div[data-testid="stMetric"]:has(label:contains("MRR Perdido (Churn)")) [data-testid="stMetricDelta"] svg {{
        fill: {VERMELHO_CHURN} !important;
    }}
    div[data-testid="stMetric"]:has(label:contains("MRR Perdido (Churn)")) [data-testid="stMetricDelta"] {{
        color: {VERMELHO_CHURN} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Título do Dashboard
st.title("🚀 Dashboard Comercial Estratégico - Acelerar.tech")
st.markdown("---")

# Função para carregar dados (Simulada com base na estrutura enviada)
@st.cache_data
def load_data():
    # Aqui deve entrar a sua URL do Google Sheets CSV
    # df = pd.read_csv("SUA_URL_AQUI")
    # Para fins de visualização, criaremos um DataFrame de exemplo baseado no seu contexto
    data = {
        'Vendedor': ['Vendedor A', 'Vendedor B', 'Vendedor C', 'Vendedor D'],
        'MRR': [5000, 3500, 2000, 1500],
        'Contratos': [10, 8, 5, 4],
        'Upsell': [500, 200, 100, 50],
        'Churn': [1000, 0, 500, 0],
        'Data': pd.to_datetime(['2024-01-01', '2024-01-05', '2024-01-10', '2024-01-15']),
        'Produto': ['Produto X', 'Produto Y', 'Produto X', 'Produto Z']
    }
    return pd.DataFrame(data)

df = load_data()

# --- FILTROS ---
st.sidebar.header("Filtros")
vendedores = st.sidebar.multiselect("Vendedor", options=df['Vendedor'].unique(), default=df['Vendedor'].unique())
produtos = st.sidebar.multiselect("Produto", options=df['Produto'].unique(), default=df['Produto'].unique())

df_filtered = df[(df['Vendedor'].isin(vendedores)) & (df['Produto'].isin(produtos))]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)

total_mrr = df_filtered['MRR'].sum()
total_upsell = df_filtered['Upsell'].sum()
total_churn = df_filtered['Churn'].sum()
total_contratos = df_filtered['Contratos'].sum()

with col1:
    st.metric("Total MRR", f"R$ {total_mrr:,.2f}")
with col2:
    st.metric("Total Upsell", f"R$ {total_upsell:,.2f}")
with col3:
    # Card de Churn com seta para baixo e cor vermelha via CSS injetado
    st.metric("MRR Perdido (Churn)", f"R$ {total_churn:,.2f}", delta=f"-R$ {total_churn:,.2f}", delta_color="normal")
with col4:
    st.metric("Total Contratos", total_contratos)

st.markdown("---")

# --- GRÁFICOS DE PIZZA (VENDEDORES) ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Top Vendedores (Contratos)")
    fig_pie_contratos = px.pie(
        df_filtered, 
        values='Contratos', 
        names='Vendedor',
        color_discrete_sequence=[AZUL_MARINHO, AZUL_CLARO, "#1E4A7A", "#A5D8F3"],
        hole=0.4
    )
    fig_pie_contratos.update_traces(
        textinfo="label+value", 
        textposition="inside",
        texttemplate="%{label}  
%{value} contratos"
    )
    st.plotly_chart(fig_pie_contratos, use_container_width=True)

with col_graf2:
    st.subheader("Top Vendedores (MRR)")
    fig_pie_mrr = px.pie(
        df_filtered, 
        values='MRR', 
        names='Vendedor',
        color_discrete_sequence=[AZUL_MARINHO, AZUL_CLARO, "#1E4A7A", "#A5D8F3"],
        hole=0.4
    )
    fig_pie_mrr.update_traces(
        textinfo="label+value", 
        textposition="inside",
        texttemplate="%{label}  
R$ %{value:,.2f}"
    )
    st.plotly_chart(fig_pie_mrr, use_container_width=True)

st.markdown("---")

# --- RANKING DOS VENDEDORES (Reposicionado antes da tabela) ---
st.subheader("🏆 Ranking de Performance dos Vendedores")
ranking_df = df_filtered.groupby('Vendedor').agg({
    'MRR': 'sum',
    'Contratos': 'sum',
    'Upsell': 'sum'
}).sort_values(by='MRR', ascending=False)

st.dataframe(ranking_df.style.format({"MRR": "R$ {:,.2f}", "Upsell": "R$ {:,.2f}"}), use_container_width=True)

st.markdown("---")

# --- TABELA DE DETALHAMENTO ---
st.subheader("📋 Detalhamento de Vendas")
st.dataframe(df_filtered, use_container_width=True)

st.markdown("---")
st.caption("Dashboard desenvolvido para Acelerar.tech | VMC Tech")
