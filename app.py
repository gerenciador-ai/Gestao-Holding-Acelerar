import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO
from PIL import Image

# ===== CONFIGURAÇÃO DE PÁGINA E TEMA =====
st.set_page_config(
    page_title="Dashboard Comercial - Acelerar.tech",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== PALETA DE CORES ACELERAR.TECH =====
CORES = {
    "azul_escuro": "#0D3B66",      # Azul escuro primário
    "azul_claro": "#6DAFDB",       # Azul claro secundário
    "branco": "#FFFFFF",           # Branco
    "cinza_suave": "#F5F5F5",      # Cinza suave
    "azul_muito_claro": "#E8F4F8", # Azul muito claro para backgrounds
}

# ===== CSS PERSONALIZADO PARA TEMA =====
css_personalizado = f"""
<style>
    /* Configuração geral */
    :root {{
        --primary-color: {CORES['azul_escuro']};
        --secondary-color: {CORES['azul_claro']};
        --background-color: {CORES['cinza_suave']};
        --text-color: {CORES['azul_escuro']};
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {CORES['azul_escuro']};
    }}
    
    [data-testid="stSidebar"] * {{
        color: {CORES['branco']};
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {CORES['azul_escuro']};
        font-weight: 700;
    }}
    
    /* Texto geral */
    body {{
        background-color: {CORES['cinza_suave']};
        color: {CORES['azul_escuro']};
    }}
    
    /* Métrica (KPI) */
    [data-testid="metric-container"] {{
        background-color: {CORES['branco']};
        border-left: 4px solid {CORES['azul_claro']};
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
    }}
    
    /* Dividers */
    hr {{
        border-color: {CORES['azul_claro']};
    }}
</style>
"""

st.markdown(css_personalizado, unsafe_allow_html=True)

# ===== LOGO FIXO NO CANTO SUPERIOR ESQUERDO =====
col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        logo = Image.open('/home/ubuntu/logo_acelerar.png')
        # Redimensionar logo para caber bem
        logo = logo.resize((120, 120))
        st.image(logo, use_column_width=True)
    except:
        st.warning("Logo não encontrado")

with col_titulo:
    st.markdown(f"""
    <div style="padding: 20px 0;">
        <h1 style="color: {CORES['azul_escuro']}; margin: 0;">📊 Dashboard Comercial</h1>
        <p style="color: {CORES['azul_claro']}; font-size: 14px; margin: 5px 0;">Acelerar.tech - Relatório de Vendas e Cancelamentos</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===== FUNÇÃO PARA CARREGAR DADOS =====
@st.cache_data(ttl=3600)
def load_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = StringIO(response.text)
        df = pd.read_csv(data)
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return pd.DataFrame()

# ===== CARREGAR DADOS =====
URL_VENDAS = "https://docs.google.com/spreadsheets/d/1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M/gviz/tq?tqx=out:csv&sheet=Vendas%20Realizadas"
URL_CANCELADOS = "https://docs.google.com/spreadsheets/d/1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw/gviz/tq?tqx=out:csv&sheet=Cancelados"

df_vendas = load_data(URL_VENDAS)
df_cancelados = load_data(URL_CANCELADOS)

if df_vendas.empty or df_cancelados.empty:
    st.error("Erro ao carregar os dados das planilhas.")
    st.stop()

# ===== PRÉ-PROCESSAMENTO =====
df_vendas.columns = df_vendas.columns.str.strip()
df_cancelados.columns = df_cancelados.columns.str.strip()

# Renomear colunas
df_vendas = df_vendas.rename(columns={
    'Data da Venda': 'Data_Venda',
    'CNPJ do Cliente': 'CNPJ_Cliente',
    'Valor da Venda': 'Valor_Venda',
    'Nome do Vendedor': 'Nome_Vendedor',
    'Plano Contratado': 'Plano_Contratado'
})

df_cancelados = df_cancelados.rename(columns={
    'CNPJ do Cliente': 'CNPJ_Cliente',
    'Data de Cancelamento': 'Data_Cancelamento'
})

# Converter datas
df_vendas['Data_Venda'] = pd.to_datetime(df_vendas['Data_Venda'], errors='coerce')
df_cancelados['Data_Cancelamento'] = pd.to_datetime(df_cancelados['Data_Cancelamento'], errors='coerce')

# Mesclar dados
df_merged = pd.merge(df_vendas, df_cancelados, on='CNPJ_Cliente', how='left', suffixes=('_Venda', '_Cancelamento'))
df_merged['Status'] = df_merged['Data_Cancelamento'].apply(lambda x: 'Cancelado' if pd.notna(x) else 'Ativo')
df_merged['Valor_Liquido'] = df_merged.apply(lambda row: 0 if row['Status'] == 'Cancelado' else row['Valor_Venda'], axis=1)

# ===== FILTROS NA SIDEBAR =====
st.sidebar.markdown(f"<h2 style='color: {CORES['branco']}; text-align: center;'>🔍 Filtros</h2>", unsafe_allow_html=True)
st.sidebar.divider()

data_min = df_merged['Data_Venda'].min().date()
data_max = df_merged['Data_Venda'].max().date()

data_inicio, data_fim = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

vendedores = ['Todos'] + sorted(df_merged['Nome_Vendedor'].dropna().unique().tolist())
vendedor_selecionado = st.sidebar.selectbox("Vendedor", vendedores)

planos = ['Todos'] + sorted(df_merged['Plano_Contratado'].dropna().unique().tolist())
plano_selecionado = st.sidebar.selectbox("Plano", planos)

# ===== APLICAR FILTROS =====
df_filtered = df_merged[(df_merged['Data_Venda'].dt.date >= data_inicio) & (df_merged['Data_Venda'].dt.date <= data_fim)]

if vendedor_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['Nome_Vendedor'] == vendedor_selecionado]

if plano_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['Plano_Contratado'] == plano_selecionado]

# ===== SEÇÃO DE KPIs =====
st.markdown(f"<h2 style='color: {CORES['azul_escuro']}; border-bottom: 3px solid {CORES['azul_claro']}; padding-bottom: 10px;'>📊 Principais Indicadores de Desempenho (KPIs)</h2>", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

# Calcular KPIs
vendas_brutas = df_filtered['Valor_Venda'].sum()
vendas_liquidas = df_filtered['Valor_Liquido'].sum()
total_vendas = len(df_filtered)
total_cancelamentos = len(df_filtered[df_filtered['Status'] == 'Cancelado'])
taxa_cancelamento = (total_cancelamentos / total_vendas * 100) if total_vendas > 0 else 0
ticket_medio = vendas_liquidas / total_vendas if total_vendas > 0 else 0

# Exibir KPIs com estilo personalizado
kpis = [
    (col1, "Vendas Brutas", f"R$ {vendas_brutas:,.2f}", "💰"),
    (col2, "Vendas Líquidas", f"R$ {vendas_liquidas:,.2f}", "📈"),
    (col3, "Total de Vendas", f"{total_vendas}", "🛍️"),
    (col4, "Cancelamentos", f"{total_cancelamentos}", "❌"),
    (col5, "Taxa de Cancelamento", f"{taxa_cancelamento:.2f}%", "📉"),
    (col6, "Ticket Médio", f"R$ {ticket_medio:,.2f}", "🎯"),
]

for col, titulo, valor, emoji in kpis:
    with col:
        st.markdown(f"""
        <div style="
            background-color: {CORES['branco']};
            border-left: 4px solid {CORES['azul_claro']};
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
            text-align: center;
        ">
            <p style="color: {CORES['azul_claro']}; font-size: 24px; margin: 0;">{emoji}</p>
            <p style="color: {CORES['azul_escuro']}; font-size: 12px; margin: 5px 0; font-weight: 600;">{titulo}</p>
            <p style="color: {CORES['azul_escuro']}; font-size: 18px; margin: 0; font-weight: 700;">{valor}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ===== SEÇÃO DE GRÁFICOS =====
st.markdown(f"<h2 style='color: {CORES['azul_escuro']}; border-bottom: 3px solid {CORES['azul_claro']}; padding-bottom: 10px;'>📈 Análises Visuais</h2>", unsafe_allow_html=True)

# Gráfico 1: Evolução de Vendas Líquidas
col1, col2 = st.columns(2)

with col1:
    st.subheader("Evolução das Vendas Líquidas ao Longo do Tempo")
    df_vendas_por_data = df_filtered.groupby('Data_Venda')['Valor_Liquido'].sum().reset_index()
    
    fig_line = px.line(
        df_vendas_por_data,
        x='Data_Venda',
        y='Valor_Liquido',
        labels={'Valor_Liquido': 'Vendas Líquidas (R$)', 'Data_Venda': 'Data'},
        color_discrete_sequence=[CORES['azul_claro']]
    )
    fig_line.update_layout(
        plot_bgcolor=CORES['cinza_suave'],
        paper_bgcolor=CORES['branco'],
        font=dict(color=CORES['azul_escuro'], family="Arial"),
        hovermode='x unified',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    fig_line.update_traces(line=dict(color=CORES['azul_claro'], width=3))
    st.plotly_chart(fig_line, use_container_width=True)

# Gráfico 2: Ranking de Vendedores
with col2:
    st.subheader("Ranking de Vendedores por Vendas Líquidas")
    df_vendas_por_vendedor = df_filtered.groupby('Nome_Vendedor')['Valor_Liquido'].sum().reset_index().sort_values('Valor_Liquido', ascending=True)
    
    fig_bar = px.barh(
        df_vendas_por_vendedor,
        x='Valor_Liquido',
        y='Nome_Vendedor',
        labels={'Valor_Liquido': 'Vendas Líquidas (R$)', 'Nome_Vendedor': 'Vendedor'},
        color_discrete_sequence=[CORES['azul_claro']]
    )
    fig_bar.update_layout(
        plot_bgcolor=CORES['cinza_suave'],
        paper_bgcolor=CORES['branco'],
        font=dict(color=CORES['azul_escuro'], family="Arial"),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Gráfico 3: Distribuição por Plano
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição de Vendas por Plano")
    df_vendas_por_plano = df_filtered.groupby('Plano_Contratado')['Valor_Liquido'].sum().reset_index()
    
    fig_pie = px.pie(
        df_vendas_por_plano,
        values='Valor_Liquido',
        names='Plano_Contratado',
        color_discrete_sequence=[CORES['azul_escuro'], CORES['azul_claro'], CORES['azul_muito_claro'], "#4A90C4"]
    )
    fig_pie.update_layout(
        paper_bgcolor=CORES['branco'],
        font=dict(color=CORES['azul_escuro'], family="Arial"),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Gráfico 4: Status das Vendas
with col2:
    st.subheader("Distribuição por Status")
    df_status = df_filtered['Status'].value_counts().reset_index()
    df_status.columns = ['Status', 'Quantidade']
    
    fig_status = px.bar(
        df_status,
        x='Status',
        y='Quantidade',
        labels={'Quantidade': 'Quantidade', 'Status': 'Status'},
        color='Status',
        color_discrete_map={'Ativo': CORES['azul_claro'], 'Cancelado': '#E74C3C'}
    )
    fig_status.update_layout(
        plot_bgcolor=CORES['cinza_suave'],
        paper_bgcolor=CORES['branco'],
        font=dict(color=CORES['azul_escuro'], family="Arial"),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_status, use_container_width=True)

st.divider()

# ===== TABELA DETALHADA =====
st.markdown(f"<h2 style='color: {CORES['azul_escuro']}; border-bottom: 3px solid {CORES['azul_claro']}; padding-bottom: 10px;'>📋 Tabela Detalhada de Vendas</h2>", unsafe_allow_html=True)

colunas_exibicao = ['Nome_Vendedor', 'CNPJ_Cliente', 'Plano_Contratado', 'Valor_Venda', 'Data_Venda', 'Status']
colunas_disponiveis = [col for col in colunas_exibicao if col in df_filtered.columns]

df_tabela = df_filtered[colunas_disponiveis].copy()
df_tabela['Valor_Venda'] = df_tabela['Valor_Venda'].apply(lambda x: f"R$ {x:,.2f}")
df_tabela = df_tabela.sort_values('Data_Venda', ascending=False)

st.dataframe(df_tabela, use_container_width=True, hide_index=True)

# ===== RODAPÉ =====
st.divider()
st.markdown(f"""
<div style="text-align: center; padding: 20px; color: {CORES['azul_claro']}; font-size: 12px;">
    <p>Dashboard Comercial - Acelerar.tech © 2024 | Todos os direitos reservados</p>
</div>
""", unsafe_allow_html=True)
