import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# CONFIGURACIÓN PÁGINA Y ESTILOS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard - Sistema de Calidad",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS personalizado para emular la interfaz
st.markdown("""
<style>
    /* Estilo del Sidebar */
    [data-testid="stSidebar"] {
        background-color: #121921;
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    
    /* Encabezado Principal */
    .header-container {
        background-color: #1E293B;
        padding: 18px 25px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Contenedores tipo Tarjeta (Cards) */
    .kpi-card {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.04);
        text-align: center;
        margin-bottom: 10px;
    }
    
    .kpi-title {
        font-size: 11px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        margin: 5px 0;
    }
    .kpi-meta {
        font-size: 11px;
        color: #64748B;
    }

    /* Grillas para Indicadores Clave */
    .icon-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        margin-top: 10px;
    }
    .icon-box {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 5px;
        text-align: center;
        background-color: #F8FAFC;
    }
    .icon-box-title {
        font-size: 10px;
        font-weight: 600;
        color: #334155;
    }

    /* Footer / Valores */
    .footer-bar {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 12px;
        border-radius: 8px;
        display: flex;
        justify-content: space-around;
        text-align: center;
        font-size: 11px;
        font-weight: bold;
        color: #334155;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ❖ SISTEMA DE CALIDAD")
    st.markdown("---")
    
    opciones = [
        "📌 RESUMEN",
        "📊 INDICADORES",
        "📋 DEFECTOS",
        "🏭 PROCESOS",
        "📦 EMBARQUES",
        "⚙️ ACCIONES",
        "👥 AUDITORÍAS"
    ]
    st.radio("Navegación principal:", opciones, label_visibility="collapsed")
    
    st.markdown("---")
    st.date_input("Fecha de Consulta", pd.to_datetime("2026-05-19"))
    st.selectbox("Filtro de Línea", ["Todos", "Línea 1", "Línea 2", "Línea 3"])

# ---------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------
st.markdown("""
<div class="header-container">
    <div>
        <h2 style="margin:0; font-size:22px;">DASHBOARD – SISTEMA DE CALIDAD</h2>
        <span style="font-size:13px; color:#94A3B8;">PRODUCTO TERMINADO – PISO CERÁMICO</span>
    </div>
    <div style="text-align:right;">
        <span style="font-size:14px; background:#334155; padding:6px 12px; border-radius:6px;">📅 19/05/2026 | 🌪️ Filtro: Todos</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECCIÓN 1: KPI CARDS (6 Columnas)
# ---------------------------------------------------------
cols_kpi = st.columns(6)

kpis = [
    {"title": "CALIDAD DE PRIMERA", "val": "96.8 %", "meta": "Meta ≥ 95 %", "color": "#16A34A", "data": [95, 96, 94, 97, 96.8]},
    {"title": "RECHAZO", "val": "2.1 %", "meta": "Meta ≤ 2 %", "color": "#DC2626", "data": [2.6, 2.4, 2.2, 1.8, 2.1]},
    {"title": "RETRABAJO", "val": "1.1 %", "meta": "Meta ≤ 1 %", "color": "#D97706", "data": [1.5, 1.2, 1.0, 1.3, 1.1]},
    {"title": "PRODUCTO LIBERADO", "val": "98.4 %", "meta": "Meta ≥ 98 %", "color": "#2563EB", "data": [97, 98, 98.2, 98.5, 98.4]},
    {"title": "RECLAMOS CLIENTE", "val": "4", "meta": "Meta ≤ 3", "color": "#DC2626", "data": [2, 3, 5, 3, 4]},
    {"title": "AUDITORÍAS CUMPLIDAS", "val": "94 %", "meta": "Meta ≥ 95 %", "color": "#16A34A", "data": [90, 92, 95, 93, 94]}
]

for i, kpi in enumerate(kpis):
    with cols_kpi[i]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{kpi['title']}</div>
            <div class="kpi-value" style="color:{kpi['color']}">{kpi['val']}</div>
            <div class="kpi-meta">{kpi['meta']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sparkline mini gráfico para cada KPI
        fig_spark = px.line(x=range(5), y=kpi['data'])
        fig_spark.update_traces(line_color=kpi['color'], line_width=2)
        fig_spark.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=35,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})

st.write("")

# ---------------------------------------------------------
# SECCIÓN 2: PARETO | DISTRIBUCIÓN | CALIDAD POR PROCESO
# ---------------------------------------------------------
c1, c2, c3 = st.columns([1.1, 1, 1.1])

# --- Pareto de Defectos ---
with c1:
    st.markdown("##### PARETO DE DEFECTOS (MES ACTUAL)")
    df_pareto = pd.DataFrame({
        "Defecto": ["Mancha superficial", "Planitud", "Variación de tono", "Canto / escuadra", "Ruptura", "Otros"],
        "Porcentaje": [32, 24, 18, 12, 8, 6]
    }).sort_values(by="Porcentaje", ascending=True)

    fig_pareto = px.bar(
        df_pareto, y="Defecto", x="Porcentaje", orientation='h', text="Porcentaje",
        color_discrete_sequence=['#1E3A8A']
    )
    fig_pareto.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_pareto.update_layout(
        height=260, margin=dict(l=10, r=30, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor='#E2E8F0', title=""),
        yaxis=dict(title="")
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

# --- Donut / Distribución de Defectos ---
with c2:
    st.markdown("##### DISTRIBUCIÓN DE DEFECTOS")
    df_pie = pd.DataFrame({
        "Defecto": ["Mancha superficial", "Planitud", "Variación de tono", "Canto / escuadra", "Ruptura", "Otros"],
        "Cantidad": [400, 300, 224, 150, 100, 74]
    })
    
    fig_pie = px.pie(
        df_pie, values='Cantidad', names='Defecto', hole=0.6,
        color_discrete_sequence=['#1E3A8A', '#3B82F6', '#F59E0B', '#E11D48', '#8B5CF6', '#64748B']
    )
    fig_pie.update_layout(
        height=260, margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(text='<b>Total<br>1,248</b>', x=0.5, y=0.5, font_size=14, showarrow=False)],
        showlegend=True, legend=dict(font=dict(size=10))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- Calidad por Proceso (8 Tarjetas en Grid) ---
with c3:
    st.markdown("##### CALIDAD POR PROCESO (CALIDAD DE PRIMERA %)")
    
    procesos = [
        {"nombre": "PRENSADO", "val": "98.2 %", "status": "🟢", "icon": "🔩"},
        {"nombre": "SECADO", "val": "97.6 %", "status": "🟢", "icon": "♨️"},
        {"nombre": "ESMALTADO", "val": "94.8 %", "status": "🟡", "icon": "🖌️"},
        {"nombre": "DECORACIÓN", "val": "95.1 %", "status": "🟡", "icon": "🎨"},
        {"nombre": "HORNO", "val": "91.7 %", "status": "🔴", "icon": "🔥"},
        {"nombre": "SELECCIÓN", "val": "98.5 %", "status": "🟢", "icon": "🔍"},
        {"nombre": "EMPAQUE", "val": "99.1 %", "status": "🟢", "icon": "📦"},
        {"nombre": "EMBARQUES", "val": "98.7 %", "status": "🟢", "icon": "🚚"},
    ]
    
    col_p1, col_p2 = st.columns(2)
    for idx, p in enumerate(procesos):
        target_col = col_p1 if idx % 2 == 0 else col_p2
        with target_col:
            st.markdown(f"""
            <div style="border:1px solid #E2E8F0; padding:8px; border-radius:6px; margin-bottom:8px; text-align:center; background:#FAFAFA;">
                <span style="font-size:10px; font-weight:bold; color:#475569;">{p['nombre']}</span><br>
                <span style="font-size:16px;">{p['icon']}</span><br>
                <span style="font-size:13px; font-weight:bold; color:#1E293B;">{p['status']} {p['val']}</span>
            </div>
            """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# SECCIÓN 3: TENDENCIA | INDICADORES CLAVE | ACCIONES
# ---------------------------------------------------------
b1, b2, b3 = st.columns([1, 1.2, 1.1])

# --- Tendencia de Rechazo ---
with b1:
    st.markdown("##### TENDENCIA DE RECHAZO (%)")
    df_tendencia = pd.DataFrame({
        "Mes": ["Dic", "Ene", "Feb", "Mar", "Abr", "May"],
        "Rechazo": [2.6, 2.4, 2.2, 1.8, 1.7, 2.1]
    })
    
    fig_tend = px.line(df_tendencia, x="Mes", y="Rechazo", markers=True, text="Rechazo")
    fig_tend.update_traces(line_color="#DC2626", textposition="top center")
    fig_tend.add_hline(y=2.0, line_dash="dash", line_color="#64748B", annotation_text="Meta (2.0 %)")
    fig_tend.update_layout(
        height=250, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[0, 3.5], title=""), xaxis=dict(title="")
    )
    st.plotly_chart(fig_tend, use_container_width=True)

# --- Indicadores Clave del Producto ---
with b2:
    st.markdown("##### INDICADORES CLAVE DEL PRODUCTO")
    
    st.markdown("""
    <div class="icon-grid">
        <div class="icon-box">📐<br><span class="icon-box-title">Planitud</span></div>
        <div class="icon-box">🛡️<br><span class="icon-box-title">Curvatura Central</span></div>
        <div class="icon-box">〰️<br><span class="icon-box-title">Curvatura Lateral</span></div>
        <div class="icon-box">📐<br><span class="icon-box-title">Alabeo</span></div>
        <div class="icon-box">📏<br><span class="icon-box-title">Dimensiones</span></div>
        <div class="icon-box">💧<br><span class="icon-box-title">Absorción / Peso</span></div>
        <div class="icon-box">🏛️<br><span class="icon-box-title">Módulo Ruptura</span></div>
        <div class="icon-box">💥<br><span class="icon-box-title">Resistencia Impacto</span></div>
        <div class="icon-box">👁️<br><span class="icon-box-title">Tono y Apariencia</span></div>
        <div class="icon-box">👟<br><span class="icon-box-title">DCOF / Superficie</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- Acciones Correctivas Abiertas ---
with b3:
    st.markdown("##### ACCIONES CORRECTIVAS ABIERTAS")
    
    df_acciones = pd.DataFrame({
        "ACCIÓN": ["Corregir planitud modelo X", "Revisar tono línea 3", "Auditoría de empaque", "Disminuir manchas modelo Y"],
        "RESPONSABLE": ["Producción", "Esmaltes", "Calidad", "Decoración"],
        "VENCIMIENTO": ["22/05/2026", "23/05/2026", "24/05/2026", "26/05/2026"],
        "ESTADO": ["🔴", "🟡", "🟢", "🟡"]
    })
    
    st.dataframe(df_acciones, hide_index=True, use_container_width=True)

# ---------------------------------------------------------
# FOOTER VALORES
# ---------------------------------------------------------
st.markdown("""
<div class="footer-bar">
    <div>👥 ENFOQUE AL CLIENTE</div>
    <div>📈 MEJORA CONTINUA</div>
    <div>🤝 TRABAJO EN EQUIPO</div>
    <div>🛡️ INTEGRIDAD</div>
    <div>⚙️ DISCIPLINA OPERATIVA</div>
    <div>✅ CALIDAD SIEMPRE</div>
</div>
""", unsafe_allow_html=True)
