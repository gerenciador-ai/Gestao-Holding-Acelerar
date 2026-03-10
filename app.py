import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    layout="wide",
    page_title="Dashboard Comercial - Acelerar.tech",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ==================== PALETA DE CORES CORPORATIVA ACELERAR.TECH ====================
CORES = {
    "primaria_escura": "#1B3A5C",      # Azul Marinho (backgrounds, headers)
    "primaria_media": "#2E5A8C",       # Azul Médio (destaques)
    "primaria_clara": "#5BA3D0",       # Azul Claro (elementos secundários)
    "branco": "#FFFFFF",               # Branco puro
    "cinza_claro": "#F5F5F5",          # Cinza muito claro (backgrounds)
    "cinza_medio": "#BDBDBD",          # Cinza médio (bordas)
    "verde": "#4CAF50",                # Verde (confirmado, positivo)
    "vermelho": "#F44336",             # Vermelho (cancelado, negativo)
    "laranja": "#FF9800"               # Laranja (atenção, destaque)
}

# ==================== CSS CUSTOMIZADO ====================
st.markdown(f"""
<style>
    /* Configuração geral */
    :root {{
        --primary-dark: {CORES['primaria_escura']};
        --primary-medium: {CORES['primaria_media']};
        --primary-light: {CORES['primaria_clara']};
        --white: {CORES['branco']};
        --gray-light: {CORES['cinza_claro']};
        --gray-medium: {CORES['cinza_medio']};
        --green: {CORES['verde']};
        --red: {CORES['vermelho']};
        --orange: {CORES['laranja']};
    }}
    
    /* Background da página */
    .stApp {{
        background-color: {CORES['cinza_claro']};
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {CORES['primaria_escura']};
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: {CORES['branco']};
    }}
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label {{
        color: {CORES['branco']};
        font-weight: 600;
    }}
    
    /* Título principal */
    h1 {{
        color: {CORES['primaria_escura']};
        border-bottom: 3px solid {CORES['primaria_clara']};
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}
    
    /* Subtítulos */
    h2, h3 {{
        color: {CORES['primaria_escura']};
        margin-top: 30px;
        margin-bottom: 15px;
    }}
    
    /* Cartões de métrica */
    [data-testid="metric-container"] {{
        background-color: {CORES['branco']};
        border-left: 4px solid {CORES['primaria_clara']};
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* Divisor */
    hr {{
        border-color: {CORES['cinza_medio']};
        margin: 30px 0;
    }}
    
    /* Tabela */
    [data-testid="stDataFrame"] {{
        background-color: {CORES['branco']};
    }}
    
    /* Botões */
    .stButton > button {{
        background-color: {CORES['primaria_media']};
        color: {CORES['branco']};
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {CORES['primaria_escura']};
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    /* Download button */
    .stDownloadButton > button {{
        background-color: {CORES['verde']};
        color: {CORES['branco']};
    }}
    
    .stDownloadButton > button:hover {{
        background-color: #45a049;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== IDs E GIDs DAS PLANILHAS GOOGLE SHEETS ====================
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719"

# ==================== FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO ====================
@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    """Carrega dados das planilhas Google Sheets com cache."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid:
        url += f"&gid={gid}"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def parse_currency(series):
    """Converte strings de moeda para float."""
    def clean_val(val):
        if pd.isna(val) or val == "":
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).replace("R$", "").strip()
        if not s:
            return 0.0
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
        elif "." in s:
            parts = s.split(".")
            if len(parts[-1]) != 2:
                s = s.replace(".", "")
        try:
            return float(s)
        except:
            return 0.0
    return series.apply(clean_val)

def processar_dados():
    """Processa e consolida dados de vendas e cancelamentos."""
    df_v = load_data(VENDAS_ID, VENDAS_GID)
    df_c = load_data(CANCELADOS_ID, CANCELADOS_GID)
    if df_v.empty:
        return None

    df = pd.DataFrame()
    df["vendedor"] = df_v["Vendedor"].fillna("N/A")
    df["sdr"] = df_v["SDR"].fillna("N/A")
    df["cliente"] = df_v["Cliente"].fillna("N/A")
    df["cnpj"] = df_v["CNPJ do Cliente"].astype(str).str.replace(r"\D", "", regex=True)
    df["produto"] = df_v["Qual produto?"].fillna("Sittax Simples")
    df.loc[df["produto"].astype(str).str.strip() == "", "produto"] = "Sittax Simples"

    df["mrr"] = parse_currency(df_v["Mensalidade - Simples"])
    df["adesao"] = parse_currency(df_v["Adesão - Simples"]) + parse_currency(df_v["Adesão - Recupera"])
    df["upgrade"] = parse_currency(df_v["Aumento da mensalidade"])
    df["downgrade"] = parse_currency(df_v["Redução da mensalidade"])

    df["data_h"] = pd.to_datetime(df_v["Data de Ativação"], errors="coerce", dayfirst=False)
    df["data_x"] = pd.to_datetime(df_v["Data alteração de CNPJ"], errors="coerce", dayfirst=False)
    
    df["data"] = df["data_h"]
    df.loc[df["upgrade"] > 0, "data"] = df["data_x"]
    
    df = df.dropna(subset=["data"])
    df["ano"] = df["data"].dt.year.astype(int)
    df["mes_num"] = df["data"].dt.month.astype(int)
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    df["mes_nome"] = df["mes_num"].map(meses_pt)
    df["inicio_semana"] = df["data"].apply(lambda x: x - pd.Timedelta(days=x.weekday()))

    df["status"] = "Confirmada"
    if not df_c.empty:
        canc_cnpjs = df_c["CNPJ do Cliente"].astype(str).str.replace(r"\D", "", regex=True).unique()
        df.loc[df["cnpj"].isin(canc_cnpjs), "status"] = "Cancelada"
    
    return df

# ==================== INTERFACE PRINCIPAL ====================
# Header com Título
st.markdown(f"""
<h1 style='color: {CORES['primaria_escura']}; border-bottom: 3px solid {CORES['primaria_clara']}; padding-bottom: 10px;'>
    📊 Dashboard Comercial Estratégico
</h1>
<p style='color: {CORES['primaria_media']}; margin: 5px 0 0 0; font-size: 14px;'>
    Acelerar.tech - Análise de Performance de Vendas
</p>
""", unsafe_allow_html=True)

# Processamento de dados
df = processar_dados()

if df is not None:
    # ==================== SIDEBAR - FILTROS ====================
    st.sidebar.markdown(f"<h2 style='color: {CORES['branco']}; margin-top: 0;'>🔍 Filtros</h2>", unsafe_allow_html=True)
    
    anos = sorted(df["ano"].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano", anos, key="ano_filter")
    df_ano = df[df["ano"] == ano_sel]
    
    meses_ordem = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    meses_disp = [m for m in meses_ordem if m in df_ano["mes_nome"].unique()]
    meses_sel = st.sidebar.multiselect("Meses", meses_disp, default=meses_disp, key="meses_filter")
    
    prod_sel = st.sidebar.selectbox("Produto", ["Todos"] + sorted(df["produto"].unique().tolist()), key="prod_filter")
    vend_sel = st.sidebar.selectbox("Vendedor", ["Todos"] + sorted(df["vendedor"].unique().tolist()), key="vend_filter")
    sdr_sel = st.sidebar.selectbox("SDR", ["Todos"] + sorted(df["sdr"].unique().tolist()), key="sdr_filter")

    # Aplicar filtros
    df_f = df_ano[df_ano["mes_nome"].isin(meses_sel)].copy()
    if prod_sel != "Todos":
        df_f = df_f[df_f["produto"] == prod_sel]
    if vend_sel != "Todos":
        df_f = df_f[df_f["vendedor"] == vend_sel]
    if sdr_sel != "Todos":
        df_f = df_f[df_f["sdr"] == sdr_sel]

    # ==================== CÁLCULO DE KPIs ====================
    mrr_conq = df_f[df_f["status"] == "Confirmada"]["mrr"].sum()
    mrr_perd = df_f[df_f["status"] == "Cancelada"]["mrr"].sum()
    mrr_net = mrr_conq - mrr_perd
    upsell_v = df_f["upgrade"].sum()
    upsell_q = len(df_f[df_f["upgrade"] > 0])
    cl_fech = len(df_f[(df_f["status"] == "Confirmada") & (df_f["mrr"] > 0)])
    cl_canc = len(df_f[df_f["status"] == "Cancelada"])
    tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
    base_ativa = len(df[df["status"] == "Confirmada"]) - len(df[df["status"] == "Cancelada"])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0
    adesao_total = df_f["adesao"].sum()

    # ==================== SEÇÃO 1: KPIs PRINCIPAIS (DESTAQUE) ====================
    st.markdown(f"<h2 style='color: {CORES['primaria_escura']};'>💰 KPIs Principais</h2>", unsafe_allow_html=True)
    
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.metric(
            label="MRR Conquistado",
            value=f"R$ {mrr_conq:,.2f}",
            delta=f"{len(df_f[df_f['status'] == 'Confirmada'])} clientes",
            delta_color="normal"
        )
    
    with kpi2:
        st.metric(
            label="MRR Ativo (Net)",
            value=f"R$ {mrr_net:,.2f}",
            delta=f"R$ {mrr_perd:,.2f} em churn",
            delta_color="inverse"
        )
    
    with kpi3:
        st.metric(
            label="Taxa de Churn",
            value=f"{churn_p:.1f}%",
            delta=f"{cl_canc} cancelamentos",
            delta_color="inverse"
        )

    # ==================== SEÇÃO 2: KPIs SECUNDÁRIOS ====================
    st.markdown(f"<h3 style='color: {CORES['primaria_escura']};'>📊 Indicadores Complementares</h3>", unsafe_allow_html=True)
    
    kpi4, kpi5, kpi6, kpi7, kpi8, kpi9 = st.columns(6)
    
    with kpi4:
        st.metric("Upsell (R$)", f"R$ {upsell_v:,.2f}", f"{upsell_q} eventos")
    
    with kpi5:
        st.metric("Ticket Médio", f"R$ {tkt_med:,.2f}", "por cliente")
    
    with kpi6:
        st.metric("Adesão Total", f"R$ {adesao_total:,.2f}", "")
    
    with kpi7:
        st.metric("Clientes Fechados", cl_fech, "no período")
    
    with kpi8:
        st.metric("Clientes Cancelados", cl_canc, "no período")
    
    with kpi9:
        st.metric("Base Ativa", base_ativa, "total")

    st.markdown("---")

    # ==================== SEÇÃO 3: EVOLUÇÃO MENSAL ====================
    st.markdown(f"<h2 style='color: {CORES['primaria_escura']};'>📈 Evolução Mensal</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        df_m = df_ano[df_ano["status"] == "Confirmada"].groupby(["mes_num", "mes_nome"]).agg({"mrr": "sum", "cliente": "count"}).reset_index().sort_values("mes_num")
        fig = px.bar(
            df_m, x="mes_nome", y="mrr", text="cliente",
            title="MRR Conquistado",
            color_discrete_sequence=[CORES["verde"]]
        )
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(
            xaxis_title=None, yaxis_title=None,
            plot_bgcolor=CORES["cinza_claro"],
            paper_bgcolor=CORES["branco"],
            font=dict(color=CORES["primaria_escura"])
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_u = df_ano[df_ano["upgrade"] > 0].groupby(["mes_num", "mes_nome"]).agg({"upgrade": "sum", "cliente": "count"}).reset_index().sort_values("mes_num")
        fig = px.bar(
            df_u, x="mes_nome", y="upgrade", text="cliente",
            title="Evolução de Upsell",
            color_discrete_sequence=[CORES["laranja"]]
        )
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(
            xaxis_title=None, yaxis_title=None,
            plot_bgcolor=CORES["cinza_claro"],
            paper_bgcolor=CORES["branco"],
            font=dict(color=CORES["primaria_escura"])
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        df_c = df_ano[df_ano["status"] == "Cancelada"].groupby(["mes_num", "mes_nome"]).agg({"mrr": "sum", "cliente": "count"}).reset_index().sort_values("mes_num")
        df_c = df_c[df_c["mrr"] > 0]
        fig = px.bar(
            df_c, x="mes_nome", y="mrr", text="cliente",
            title="Churn Mensal",
            color_discrete_sequence=[CORES["vermelho"]]
        )
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(
            xaxis_title=None, yaxis_title=None,
            plot_bgcolor=CORES["cinza_claro"],
            paper_bgcolor=CORES["branco"],
            font=dict(color=CORES["primaria_escura"])
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SEÇÃO 4: PERFORMANCE VS. METAS ====================
    st.markdown(f"<h2 style='color: {CORES['primaria_escura']};'>🎯 Performance vs. Metas</h2>", unsafe_allow_html=True)
    
    col4, col5 = st.columns(2)
    
    df_meta = df_f[df_f["status"] == "Confirmada"].groupby(["mes_num", "mes_nome"]).agg({"mrr": "sum", "cliente": "count"}).reset_index().sort_values("mes_num")
    df_meta["mrr_a"] = df_meta["mrr"].cumsum()
    df_meta["cont_a"] = df_meta["cliente"].cumsum()
    df_meta["meta_m"] = [8000 * (i + 1) for i in range(len(df_meta))]
    df_meta["meta_c"] = [17 * (i + 1) for i in range(len(df_meta))]

    with col4:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["mrr_a"], name="Real", marker_color=CORES["verde"]))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_m"], name="Meta (8k/mês)", line=dict(color=CORES["laranja"], width=4)))
        fig.update_layout(
            title="MRR Acumulado vs. Meta",
            xaxis_title=None, yaxis_title=None,
            plot_bgcolor=CORES["cinza_claro"],
            paper_bgcolor=CORES["branco"],
            font=dict(color=CORES["primaria_escura"]),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["cont_a"], name="Real", marker_color=CORES["primaria_media"]))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_c"], name="Meta (17/mês)", line=dict(color=CORES["laranja"], width=4)))
        fig.update_layout(
            title="Contratos Acumulados vs. Meta",
            xaxis_title=None, yaxis_title=None,
            plot_bgcolor=CORES["cinza_claro"],
            paper_bgcolor=CORES["branco"],
            font=dict(color=CORES["primaria_escura"]),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SEÇÃO 5: ANÁLISES ADICIONAIS ====================
    st.markdown(f"<h2 style='color: {CORES['primaria_escura']};'>📊 Análises Adicionais</h2>", unsafe_allow_html=True)
    
    col6, col7 = st.columns(2)
    
    with col6:
        df_s = df_f[df_f["status"] == "Confirmada"].groupby("inicio_semana")["mrr"].sum().reset_index().sort_values("inicio_semana")
        df_s["data_s"] = df_s["inicio_semana"].dt.strftime("%d/%m/%Y")
        fig = go.Figure(go.Scatter(
            x=df_s["data_s"], y=df_s["mrr"],
            mode="lines+markers+text",
            text=df_s["mrr"].apply(lambda x: f"R$ {x:,.0f}"),
            textposition="top center",
            line=dict(color=CORES["primaria_media"], width=4),
            fill="tozeroy",
            fillcolor=f"rgba(91, 163, 208, 0.2)"
        ))
        fig.update_layout(
            title="MRR Semanal",
            xaxis_title=None, yaxis_title=None,
            showlegend=False,
            plot_bgcolor=CORES["cinza_claro"],
            paper_bgcolor=CORES["branco"],
            font=dict(color=CORES["primaria_escura"]),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col7:
        fig = px.pie(
            df_f, names="produto", values="mrr",
            title="Receita por Produto",
            color_discrete_sequence=[CORES["primaria_clara"], CORES["verde"], CORES["laranja"], CORES["primaria_media"]]
        )
        fig.update_layout(
            xaxis_title=None, yaxis_title=None,
            paper_bgcolor=CORES["branco"],
            font=dict(color=CORES["primaria_escura"])
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SEÇÃO 6: TABELA DE DETALHAMENTO ====================
    st.markdown(f"<h2 style='color: {CORES['primaria_escura']};'>📋 Detalhamento de Vendas</h2>", unsafe_allow_html=True)
    
    # Preparar dados para tabela
    df_table = df_f[["data", "cliente", "vendedor", "sdr", "produto", "status", "mrr", "upgrade", "adesao"]].sort_values("data", ascending=False).copy()
    df_table["data"] = df_table["data"].dt.strftime("%d/%m/%Y")
    df_table.columns = ["Data", "Cliente", "Vendedor", "SDR", "Produto", "Status", "MRR (R$)", "Upgrade (R$)", "Adesão (R$)"]
    
    # Formatar valores monetários
    for col in ["MRR (R$)", "Upgrade (R$)", "Adesão (R$)"]:
        df_table[col] = df_table[col].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # ==================== RODAPÉ COM INFORMAÇÕES ====================
    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns([2, 2, 2])
    
    with col_footer1:
        st.markdown(f"<p style='color: {CORES['cinza_medio']}; font-size: 12px;'>Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>", unsafe_allow_html=True)
    
    with col_footer2:
        # Botão para download dos dados
        csv = df_table.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Baixar Relatório (CSV)",
            data=csv,
            file_name=f"relatorio_vendas_{datetime.now().strftime('%d%m%Y')}.csv",
            mime="text/csv"
        )
    
    with col_footer3:
        st.markdown(f"<p style='color: {CORES['cinza_medio']}; font-size: 12px; text-align: right;'>© 2025 Acelerar.tech - Dashboard Comercial</p>", unsafe_allow_html=True)

else:
    st.error("❌ Erro ao carregar os dados. Verifique as planilhas do Google Sheets.")
