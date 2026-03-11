import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Comercial - Acelerar.tech", layout="wide")

# Identidade Visual (Cores)
AZUL_MARINHO = "#0B2A4E"
AZUL_CLARO = "#89CFF0"
VERMELHO_CHURN = "#FF4B4B"

# CSS Customizado - Versão Simplificada e Robusta
st.markdown(f"""
<style>
    .main {{ background-color: #f5f7f9; }}
    div[data-testid="stMetric"] {{
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid {AZUL_MARINHO};
    }}
    /* Estilo para o Card de Churn */
    div[data-testid="stMetric"]:has(label:contains("MRR Perdido (Churn)")) {{
        border-left: 5px solid {VERMELHO_CHURN} !important;
    }}
    div[data-testid="stMetric"]:has(label:contains("MRR Perdido (Churn)")) [data-testid="stMetricValue"] {{
        color: {VERMELHO_CHURN} !important;
    }}
    div[data-testid="stMetric"]:has(label:contains("MRR Perdido (Churn)")) [data-testid="stMetricDelta"] {{
        color: {VERMELHO_CHURN} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Dashboard Comercial Estratégico - Acelerar.tech")

# Função de carga de dados (Substitua pela sua URL do Google Sheets)
@st.cache_data
def load_data():
    # Exemplo de estrutura baseada no seu contexto
    data = {
        'Vendedor': ['Vendedor A', 'Vendedor B', 'Vendedor C', 'Vendedor D'],
        'MRR': [5000.0, 3500.0, 2000.0, 1500.0],
        'Contratos': [10, 8, 5, 4],
        'Upsell': [500.0, 200.0, 100.0, 50.0],
        'Churn': [1000.0, 0.0, 500.0, 0.0],
        'Produto': ['Produto X', 'Produto Y', 'Produto X', 'Produto Z']
    }
    return pd.DataFrame(data)

df = load_data()

# Filtros
vendedores = st.sidebar.multiselect("Vendedor", options=df['Vendedor'].unique(), default=df['Vendedor'].unique())
df_filtered = df[df['Vendedor'].isin(vendedores)]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total MRR", f"R$ {df_filtered['MRR'].sum():,.2f}")
with col2: st.metric("Total Upsell", f"R$ {df_filtered['Upsell'].sum():,.2f}")
with col3: st.metric("MRR Perdido (Churn)", f"R$ {df_filtered['Churn'].sum():,.2f}", delta=f"-R$ {df_filtered['Churn'].sum():,.2f}", delta_color="normal")
with col4: st.metric("Total Contratos", int(df_filtered['Contratos'].sum()))

st.markdown("---")

# Gráficos de Pizza
c1, c2 = st.columns(2)

with c1:
    st.subheader("Top Vendedores (Contratos)")
    fig1 = px.pie(df_filtered, values='Contratos', names='Vendedor', hole=0.4, color_discrete_sequence=[AZUL_MARINHO, AZUL_CLARO])
    # String em linha única para evitar erro de sintaxe
    fig1.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}: %{value} und")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Top Vendedores (MRR)")
    fig2 = px.pie(df_filtered, values='MRR', names='Vendedor', hole=0.4, color_discrete_sequence=[AZUL_MARINHO, AZUL_CLARO])
    # String em linha única para evitar erro de sintaxe
    fig2.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}: R$ %{value:,.2f}")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Ranking (Antes da tabela)
st.subheader("🏆 Ranking de Performance")
ranking = df_filtered.groupby('Vendedor')[['MRR', 'Contratos', 'Upsell']].sum().sort_values('MRR', ascending=False)
st.dataframe(ranking.style.format({"MRR": "R$ {:,.2f}", "Upsell": "R$ {:,.2f}"}), use_container_width=True)

# Detalhamento
st.subheader("📋 Detalhamento")
st.dataframe(df_filtered, use_container_width=True)
