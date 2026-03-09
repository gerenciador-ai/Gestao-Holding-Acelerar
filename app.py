import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard de Vendas e Cancelamentos")

# IDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"

@st.cache_data
def load_vendas():
    """Carregar dados de vendas do Google Sheets"""
    url = f"https://docs.google.com/spreadsheets/d/{VENDAS_ID}/export?format=csv"
    df = pd.read_csv(url)
    return df

@st.cache_data
def load_cancelados():
    """Carregar dados de cancelamentos do Google Sheets"""
    url = f"https://docs.google.com/spreadsheets/d/{CANCELADOS_ID}/export?format=csv"
    df = pd.read_csv(url)
    return df

def processar_dados():
    """Processar e mesclar os dados"""
    try:
        # Carregar dados
        df_vendas = load_vendas()
        df_cancelados = load_cancelados()
        
        # Limpar nomes de colunas
        df_vendas.columns = df_vendas.columns.str.strip()
        df_cancelados.columns = df_cancelados.columns.str.strip()
        
        # Normalizar CNPJ para mesclagem
        df_vendas['CNPJ_Normalizado'] = df_vendas['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True)
        df_cancelados['CNPJ_Normalizado'] = df_cancelados['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True)
        
        # Criar coluna de status
        df_vendas['Status'] = 'Confirmada'
        
        # Mesclar dados
        df_merged = df_vendas.merge(
            df_cancelados[['CNPJ_Normalizado']].drop_duplicates(),
            on='CNPJ_Normalizado',
            how='left',
            indicator=True
        )
        
        # Atualizar status
        df_merged.loc[df_merged['_merge'] == 'both', 'Status'] = 'Cancelada'
        df_merged = df_merged.drop('_merge', axis=1)
        
        # Converter datas
        df_merged['Data de Ativação'] = pd.to_datetime(df_merged['Data de Ativação'], errors='coerce')
        
        return df_merged
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        return None

# Carregar e processar dados
df = processar_dados()

if df is not None:
    # ===== SEÇÃO DE FILTROS =====
    st.sidebar.title("🔍 Filtros")
    
    # Filtro de data
    data_min = df['Data de Ativação'].min()
    data_max = df['Data de Ativação'].max()
    
    date_range = st.sidebar.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max
    )
    
    # Filtro de vendedor
    vendedores = ['Todos'] + sorted(df['Vendedor'].unique().tolist())
    vendedor_selecionado = st.sidebar.selectbox("Vendedor", vendedores)
    
    # Filtro de plano
    planos = ['Todos'] + sorted(df['Plano'].unique().tolist())
    plano_selecionado = st.sidebar.selectbox("Plano", planos)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if len(date_range) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado['Data de Ativação'].dt.date >= date_range[0]) &
            (df_filtrado['Data de Ativação'].dt.date <= date_range[1])
        ]
    
    if vendedor_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Vendedor'] == vendedor_selecionado]
    
    if plano_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Plano'] == plano_selecionado]
    
    # ===== SEÇÃO DE KPIs =====
    st.title("📊 Dashboard de Vendas e Cancelamentos")
    
    # Calcular KPIs
    vendas_brutas = df_filtrado['Valor'].sum()
    vendas_canceladas = df_filtrado[df_filtrado['Status'] == 'Cancelada']['Valor'].sum()
    vendas_liquidas = vendas_brutas - vendas_canceladas
    total_vendas = len(df_filtrado)
    total_cancelamentos = len(df_filtrado[df_filtrado['Status'] == 'Cancelada'])
    taxa_cancelamento = (total_cancelamentos / total_vendas * 100) if total_vendas > 0 else 0
    ticket_medio = vendas_liquidas / total_vendas if total_vendas > 0 else 0
    
    # Exibir KPIs
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Vendas Brutas (R$)", f"R$ {vendas_brutas:,.2f}")
    
    with col2:
        st.metric("Vendas Líquidas (R$)", f"R$ {vendas_liquidas:,.2f}")
    
    with col3:
        st.metric("Total de Vendas", total_vendas)
    
    with col4:
        st.metric("Total de Cancelamentos", total_cancelamentos)
    
    with col5:
        st.metric("Taxa de Cancelamento (%)", f"{taxa_cancelamento:.2f}%")
    
    with col6:
        st.metric("Ticket Médio (R$)", f"R$ {ticket_medio:,.2f}")
    
    st.divider()
    
    # ===== SEÇÃO DE GRÁFICOS =====
    st.subheader("📈 Análises Visuais")
    
    # Gráfico 1: Evolução de Vendas Líquidas por Dia
    col1, col2 = st.columns(2)
    
    with col1:
        df_diario = df_filtrado.groupby(df_filtrado['Data de Ativação'].dt.date).agg({
            'Valor': 'sum',
            'Status': lambda x: (x == 'Cancelada').sum()
        }).reset_index()
        df_diario.columns = ['Data', 'Vendas_Brutas', 'Cancelamentos']
        df_diario['Vendas_Liquidas'] = df_diario['Vendas_Brutas'] - (df_diario['Cancelamentos'] * df_filtrado['Valor'].mean())
        
        fig_linha = px.line(
            df_diario,
            x='Data',
            y='Vendas_Liquidas',
            title='Evolução de Vendas Líquidas por Dia',
            labels={'Vendas_Liquidas': 'Vendas Líquidas (R$)', 'Data': 'Data'}
        )
        st.plotly_chart(fig_linha, use_container_width=True)
    
    # Gráfico 2: Ranking de Vendedores por Vendas Líquidas
    with col2:
        df_vendedor = df_filtrado.groupby('Vendedor').agg({
            'Valor': 'sum',
            'Status': lambda x: (x == 'Cancelada').sum()
        }).reset_index()
        df_vendedor.columns = ['Vendedor', 'Vendas_Brutas', 'Cancelamentos']
        df_vendedor['Vendas_Liquidas'] = df_vendedor['Vendas_Brutas'] - (df_vendedor['Cancelamentos'] * df_filtrado['Valor'].mean())
        df_vendedor = df_vendedor.sort_values('Vendas_Liquidas', ascending=True)
        
        fig_barras = px.barh(
            df_vendedor,
            x='Vendas_Liquidas',
            y='Vendedor',
            title='Ranking de Vendedores por Vendas Líquidas',
            labels={'Vendas_Liquidas': 'Vendas Líquidas (R$)', 'Vendedor': 'Vendedor'}
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    
    # Gráfico 3: Distribuição de Vendas por Plano
    col1, col2 = st.columns(2)
    
    with col1:
        df_plano = df_filtrado.groupby('Plano')['Valor'].sum().reset_index()
        fig_pizza = px.pie(
            df_plano,
            values='Valor',
            names='Plano',
            title='Distribuição de Vendas por Plano'
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    # Gráfico 4: Status das Vendas
    with col2:
        df_status = df_filtrado['Status'].value_counts().reset_index()
        df_status.columns = ['Status', 'Quantidade']
        fig_status = px.bar(
            df_status,
            x='Status',
            y='Quantidade',
            title='Quantidade de Vendas por Status',
            labels={'Quantidade': 'Quantidade', 'Status': 'Status'}
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    st.divider()
    
    # ===== TABELA DETALHADA =====
    st.subheader("📋 Tabela Detalhada de Vendas")
    
    # Selecionar colunas para exibição
    colunas_exibicao = ['Vendedor', 'Cliente', 'CNPJ do Cliente', 'Plano', 'Valor', 'Data de Ativação', 'Status']
    colunas_disponiveis = [col for col in colunas_exibicao if col in df_filtrado.columns]
    
    # Exibir tabela com formatação
    df_tabela = df_filtrado[colunas_disponiveis].copy()
    df_tabela['Valor'] = df_tabela['Valor'].apply(lambda x: f"R$ {x:,.2f}")
    df_tabela = df_tabela.sort_values('Data de Ativação', ascending=False)
    
    st.dataframe(df_tabela, use_container_width=True)
    
else:
    st.error("Erro ao carregar os dados. Verifique os IDs das planilhas.")
