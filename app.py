import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página - Estilo Sênior Limpo
st.set_page_config(layout="wide", page_title="Dashboard Comercial Estratégico", page_icon="📊")

# IDs e GIDs das planilhas Google Sheets (agora referenciando VMC Tech)
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M" # Vendas Realizadas_VMC Tech
VENDAS_GID = "1202307787"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw" # Cancelados_VMC Tech
CANCELADOS_GID = "606807719"

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid: url += f"&gid={gid}"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def parse_currency(series):
    def clean_val(val):
        if pd.isna(val) or val == "": return 0.0
        if isinstance(val, (int, float)): return float(val)
        s = str(val).replace("R$", "").strip()
        if not s: return 0.0
        if "," in s: s = s.replace(".", "").replace(",", ".")
        elif "." in s:
            parts = s.split(".")
            if len(parts[-1]) != 2: s = s.replace(".", "")
        try: return float(s)
        except: return 0.0
    return series.apply(clean_val)

def processar_dados():
    df_v = load_data(VENDAS_ID, VENDAS_GID)
    df_c = load_data(CANCELADOS_ID, CANCELADOS_GID)
    if df_v.empty: return None

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

    # Padronização para Formato Americano (Mês/Dia/Ano)
    df["data_h"] = pd.to_datetime(df_v["Data de Ativação"], errors="coerce", dayfirst=False)
    df["data_x"] = pd.to_datetime(df_v["Data alteração de CNPJ"], errors="coerce", dayfirst=False)
    
    df["data"] = df["data_h"]
    df.loc[df["upgrade"] > 0, "data"] = df["data_x"]
    
    df = df.dropna(subset=["data"])
    df["ano"] = df["data"].dt.year.astype(int)
    df["mes_num"] = df["data"].dt.month.astype(int)
    meses_pt = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
                7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
    df["mes_nome"] = df["mes_num"].map(meses_pt)
    df["inicio_semana"] = df["data"].apply(lambda x: x - pd.Timedelta(days=x.weekday()))

    df["status"] = "Confirmada"
    if not df_c.empty:
        canc_cnpjs = df_c["CNPJ do Cliente"].astype(str).str.replace(r"\D", "", regex=True).unique()
        df.loc[df["cnpj"].isin(canc_cnpjs), "status"] = "Cancelada"
    
    return df

# --- UI ---
df = processar_dados()
if df is not None:
    st.title("📊 Dashboard Comercial Estratégico")
    
    st.sidebar.header("🔍 Filtros")
    anos = sorted(df["ano"].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano", anos)
    df_ano = df[df["ano"] == ano_sel]
    
    meses_ordem = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    meses_disp = [m for m in meses_ordem if m in df_ano["mes_nome"].unique()]
    meses_sel = st.sidebar.multiselect("Meses", meses_disp, default=meses_disp)
    
    prod_sel = st.sidebar.selectbox("Produto", ["Todos"] + sorted(df["produto"].unique().tolist()))
    vend_sel = st.sidebar.selectbox("Vendedor", ["Todos"] + sorted(df["vendedor"].unique().tolist()))
    sdr_sel = st.sidebar.selectbox("SDR", ["Todos"] + sorted(df["sdr"].unique().tolist()))

    df_f = df_ano[df_ano["mes_nome"].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f["produto"] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f["vendedor"] == vend_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f["sdr"] == sdr_sel]

    # KPIs
    mrr_conq = df_f[df_f["status"] == "Confirmada"]["mrr"].sum()
    mrr_perd = df_f[df_f["status"] == "Cancelada"]["mrr"].sum()
    upsell_v = df_f["upgrade"].sum()
    upsell_q = len(df_f[df_f["upgrade"] > 0])
    cl_fech = len(df_f[(df_f["status"] == "Confirmada") & (df_f["mrr"] > 0)])
    cl_canc = len(df_f[df_f["status"] == "Cancelada"])
    tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
    base_ativa = len(df[df["status"] == "Confirmada"]) - len(df[df["status"] == "Cancelada"])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("MRR Conquistado", f"R$ {mrr_conq:,.2f}")
    c2.metric("MRR Ativo (Net)", f"R$ {mrr_conq - mrr_perd:,.2f}")
    c3.metric("MRR Perdido (Churn)", f"R$ {mrr_perd:,.2f}", delta=f"{churn_p:.1f}%", delta_color="inverse")
    
    c4, c5, c6 = st.columns(3)
    c4.metric("Total de Upsell", f"R$ {upsell_v:,.2f}", delta=f"{upsell_q} eventos")
    c5.metric("Ticket Médio", f"R$ {tkt_med:,.2f}")
    c6.metric("Adesão Total", f"R$ {df_f["adesao"].sum():,.2f}")
    
    c7, c8, c9 = st.columns(3)
    c7.metric("Clientes fechado (no periodo)", cl_fech)
    c8.metric("Clientes Cancelados (no periodo)", cl_canc)
    c9.metric("Total Clientes Ativos (Base)", base_ativa)

    st.divider()
    
    st.subheader("📈 Evolução Mensal")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        df_m = df_ano[df_ano["status"] == "Confirmada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        fig = px.bar(df_m, x="mes_nome", y="mrr", text="cliente", title="MRR Conquistado", color_discrete_sequence=["#2ECC71"])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_u = df_ano[df_ano["upgrade"] > 0].groupby(["mes_num","mes_nome"]).agg({"upgrade":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        fig = px.bar(df_u, x="mes_nome", y="upgrade", text="cliente", title="Evolução de Upsell", color_discrete_sequence=["#9B59B6"])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        df_c = df_ano[df_ano["status"] == "Cancelada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        df_c = df_c[df_c["mrr"] > 0]
        fig = px.bar(df_c, x="mes_nome", y="mrr", text="cliente", title="Churn Mensal", color_discrete_sequence=["#E74C3C"])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    st.subheader("🎯 Performance vs. Metas")
    col4, col5 = st.columns(2)
    
    df_meta = df_f[df_f["status"] == "Confirmada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
    df_meta["mrr_a"] = df_meta["mrr"].cumsum()
    df_meta["cont_a"] = df_meta["cliente"].cumsum()
    df_meta["meta_m"] = [8000 * (i+1) for i in range(len(df_meta))]
    df_meta["meta_c"] = [17 * (i+1) for i in range(len(df_meta))]

    with col4:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["mrr_a"], name="Real", marker_color="#2ECC71"))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_m"], name="Meta (8k/mês)", line=dict(color="#F1C40F", width=4)))
        fig.update_layout(title="MRR Acumulado vs. Meta", xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["cont_a"], name="Real", marker_color="#3498DB"))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_c"], name="Meta (17/mês)", line=dict(color="#F39C12", width=4)))
        fig.update_layout(title="Contratos Acumulados vs. Meta", xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    col6, col7 = st.columns(2)
    with col6:
        df_s = df_f[df_f["status"] == "Confirmada"].groupby("inicio_semana")["mrr"].sum().reset_index().sort_values("inicio_semana")
        df_s["data_s"] = df_s["inicio_semana"].dt.strftime("%d/%m/%Y")
        fig = go.Figure(go.Scatter(x=df_s["data_s"], y=df_s["mrr"], mode="lines+markers+text", text=df_s["mrr"].apply(lambda x: f"{x:,.0f}"), textposition="top center", line=dict(color="#1A3A5A", width=4)))
        fig.update_layout(title="MRR SEMANA", xaxis_title=None, yaxis_title=None, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col7:
        fig = px.pie(df_f, names="produto", values="mrr", title="Receita por Produto", hole=0.4)
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Detalhamento")
    st.dataframe(df_f[["data", "cliente", "vendedor", "produto", "status", "mrr", "upgrade", "adesao"]].sort_values("data", ascending=False), use_container_width=True)
