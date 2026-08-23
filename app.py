import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from PIL import Image

# ==========================================
# CONFIGURACION GENERAL
# ==========================================

st.set_page_config(
    page_title="CALIDAD P1 & P3",
    layout="wide"
)

st.markdown("""
<style>

.main{
    background-color:#F4F6F9;
}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

[data-testid="stMetric"]{
    background:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.10);
}

h1,h2,h3,h4{
    font-family:Arial, Helvetica, sans-serif;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# RUTAS
# ==========================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_FILE = DATA_DIR / "dashboard.xlsx"

ADMIN_USER = "admin"
ADMIN_PASSWORD = "Calidad2026"

# ==========================================
# LOGIN
# ==========================================

if "admin" not in st.session_state:
    st.session_state.admin = False

with st.sidebar:

    st.title("🔐 Acceso")

    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        st.session_state.admin = (
            user == ADMIN_USER and
            password == ADMIN_PASSWORD
        )

    if st.session_state.admin:

        st.success("Administrador")

        archivo = st.file_uploader(
            "Cargar archivo Excel",
            type=["xlsx"]
        )

        if archivo:
            DB_FILE.write_bytes(archivo.read())
            st.success("Archivo actualizado correctamente")

# ==========================================
# VALIDACION
# ==========================================

if not DB_FILE.exists():
    st.warning(
        "Ingrese como administrador y cargue un archivo Excel."
    )
    st.stop()

# ==========================================
# ENCABEZADO
# ==========================================

col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        logo = Image.open("logo_cesantoni.png")
        st.image(logo, width=230)
    except:
        pass

with col_titulo:

    st.markdown("""
    <div style="padding-top:15px;">

    <h1 style="
        color:#1F4E79;
        font-size:48px;
        font-weight:700;
        margin-bottom:0px;">
        CALIDAD P1 & P3
    </h1>

    <h3 style="
        color:#6C757D;
        margin-top:0px;
        font-weight:400;">
        Todos somos calidad
    </h3>

    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# LECTURA EXCEL
# ==========================================

raw = pd.read_excel(
    DB_FILE,
    sheet_name="DASHBOARD",
    header=1
)

raw.columns = [str(c).strip() for c in raw.columns]

# ==========================================
# CALIDAD
# ==========================================

cal = raw[
    [
        "FECHA CALIDAD Y MTS2",
        "PRIMERA",
        "MTS2 DEL DIA",
        "CALIDAD META"
    ]
].copy()

cal["FECHA CALIDAD Y MTS2"] = pd.to_datetime(
    cal["FECHA CALIDAD Y MTS2"],
    errors="coerce"
)

cal = cal.dropna(
    subset=["FECHA CALIDAD Y MTS2"]
)

ult = cal.iloc[-1]

# ==========================================
# GARANTIAS
# ==========================================

if "MES GARANTIAS" in raw.columns:

    gar = raw[
        ["MES GARANTIAS", "GARANTIAS"]
    ].dropna(subset=["MES GARANTIAS"])

    gar_plot = gar[
        gar["MES GARANTIAS"]
        .astype(str)
        .str.upper() != "TOTAL"
    ]

    total_garantias = pd.to_numeric(
        gar["GARANTIAS"],
        errors="coerce"
    ).max()

else:

    gar_plot = pd.DataFrame()
    total_garantias = 0

# ==========================================
# DEFECTOS
# ==========================================

req = [
    "DEFECTO",
    "MTS2 DEFECTO",
    "RESPONSABLE DE DEFECTO",
    "PORCENTAJE DE DEFECTO DEL AREA"
]

if all(c in raw.columns for c in req):
    defects = raw[req].dropna(subset=["DEFECTO"])
else:
    defects = pd.DataFrame()

# ==========================================
# KPI'S
# ==========================================

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric(
    "Calidad de Primera Día",
    f"{ult['PRIMERA']*100:.2f}%"
)

c2.metric(
    "Calidad Promedio Acumulada",
    f"{cal['PRIMERA'].mean()*100:.2f}%"
)

c3.metric(
    "Producción del Día (m²)",
    f"{ult['MTS2 DEL DIA']:,.0f}"
)

c4.metric(
    "Producción Acumulada (m²)",
    f"{cal['MTS2 DEL DIA'].sum():,.0f}"
)

c5.metric(
    "Garantías Acumuladas",
    f"{total_garantias:,.0f}"
)

c6.metric(
    "Meta de Calidad",
    f"{ult['CALIDAD META']*100:.2f}%"
)

st.write("")

# ==========================================
# GRAFICA CALIDAD
# ==========================================

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=cal["FECHA CALIDAD Y MTS2"],
        y=cal["PRIMERA"] * 100,
        mode="lines+markers+text",
        name="Calidad de Primera",
        text=[
            f"{v:.2f}%"
            for v in cal["PRIMERA"] * 100
        ],
        textposition="top center",
        line=dict(
            color="#1F4E79",
            width=4
        ),
        marker=dict(size=8)
    )
)

fig.add_trace(
    go.Scatter(
        x=cal["FECHA CALIDAD Y MTS2"],
        y=cal["CALIDAD META"] * 100,
        mode="lines",
        name="Meta",
        line=dict(
            color="#DC3545",
            width=3,
            dash="dash"
        )
    )
)

fig.update_layout(
    title="Tendencia de Calidad (%)",
    title_x=0.5,
    template="plotly_white",
    height=500,
    legend=dict(
        orientation="h",
        y=1.1,
        x=0.5,
        xanchor="center"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# GARANTIAS
# ==========================================

if not gar_plot.empty:

    fig_gar = px.bar(
        gar_plot,
        x="MES GARANTIAS",
        y="GARANTIAS",
        text="GARANTIAS",
        color="GARANTIAS",
        color_continuous_scale="Reds",
        title="Tendencia Mensual de Garantías"
    )

    fig_gar.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_gar.update_layout(
        title_x=0.5,
        template="plotly_white",
        showlegend=False,
        height=450
    )

    st.plotly_chart(
        fig_gar,
        use_container_width=True
    )

# ==========================================
# DEFECTOS
# ==========================================

if not defects.empty:

    col1, col2 = st.columns(2)

    topm = (
        defects.groupby("DEFECTO")
        ["MTS2 DEFECTO"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    topp = (
        defects.groupby("DEFECTO")
        ["PORCENTAJE DE DEFECTO DEL AREA"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig_topm = px.bar(
        topm,
        text_auto=".2f",
        color=topm,
        color_continuous_scale="Blues",
        title="Principales Defectos por m²"
    )

    fig_topm.update_layout(
        title_x=0.5,
        template="plotly_white"
    )

    fig_topm.update_traces(
        textposition="outside"
    )

    col1.plotly_chart(
        fig_topm,
        use_container_width=True
    )

    fig_topp = px.bar(
        topp,
        text_auto=".2f",
        color=topp,
        color_continuous_scale="Oranges",
        title="Participación de Defectos (%)"
    )

    fig_topp.update_layout(
        title_x=0.5,
        template="plotly_white"
    )

    fig_topp.update_traces(
        textposition="outside"
    )

    col2.plotly_chart(
        fig_topp,
        use_container_width=True
    )

    resp = (
        defects.groupby("RESPONSABLE DE DEFECTO")
        ["MTS2 DEFECTO"]
        .sum()
    )

    fig_pie = px.pie(
        values=resp.values,
        names=resp.index,
        hole=0.55,
        title="Distribución de Defectos por Responsable"
    )

    fig_pie.update_traces(
        textinfo="percent+label"
    )

    fig_pie.update_layout(
        title_x=0.5,
        height=500
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )
