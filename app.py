import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(
    page_title="Dashboard - Sistema de Calidad",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; }
    .dashboard-header {
        background-color: #1a252f;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e1e8ed;
        text-align: center;
    }
    .kpi-title { font-size: 11px; font-weight: 700; color: #5a6578; text-transform: uppercase; }
    .kpi-value { font-size: 26px; font-weight: 800; margin: 5px 0; }
    .kpi-meta { font-size: 11px; color: #7f8c8d; }
    .val-green { color: #27ae60; }
    .val-red { color: #e74c3c; }
    .val-orange { color: #e67e22; }
    .val-blue { color: #2980b9; }

    .process-card {
        background: white;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #e1e8ed;
        text-align: center;
    }
    .process-name { font-size: 10px; font-weight: 700; color: #34495e; text-transform: uppercase; }
    .process-val { font-size: 13px; font-weight: bold; margin-top: 4px; }

    .ind-card {
        background: white;
        border-radius: 8px;
        padding: 10px 4px;
        border: 1px solid #e1e8ed;
        text-align: center;
        font-size: 10px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 6px;
    }
    .footer-banner {
        background-color: white;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #e1e8ed;
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 15px;
        font-size: 11px;
        font-weight: 800;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

ADMIN_PASSWORD = "admin123"

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Barra Lateral (Control de Acceso + Carga de Archivos)
with st.sidebar:
    st.markdown("### 🟢 SISTEMA DE CALIDAD")
    menu = st.radio(
        "MENÚ PRINCIPAL",
        ["RESUMEN", "INDICADORES", "DEFECTOS", "PROCESOS", "EMBARQUES", "ACCIONES", "AUDITORÍAS"]
    )
    
    st.divider()
    st.subheader("🔑 Acceso Administrador")
    if not st.session_state['logged_in']:
        pwd = st.text_input("Contraseña Admin", type="password")
        if st.button("Iniciar Sesión"):
            if pwd == ADMIN_PASSWORD:
                st.session_state['logged_in'] = True
                st.success("Acceso Admin concedido")
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    else:
        st.success("Modo Admin Activo")
        if st.button("Cerrar Sesión Admin"):
            st.session_state['logged_in'] = False
            st.rerun()

    if st.session_state['logged_in']:
        st.divider()
        st.subheader("📤 Cargar Nuevo Excel")
        uploaded_file = st.file_uploader("Subir REPORTE P1 Y P3", type=["xlsx", "xls"])
        if uploaded_file is not None:
            with open("REPORTE_ACTUAL.xlsx", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("¡Datos actualizados para el público!")

# Header Principal
st.markdown("""
<div class="dashboard-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; font-weight:800; font-size:22px;">DASHBOARD – SISTEMA DE CALIDAD</h2>
            <p style="margin:0; font-size:12px; color:#bdc3c7; font-weight:600;">PRODUCTO TERMINADO – PISO CERÁMICO</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size:13px; font-weight:bold;">📅 19/05/2026</span> &nbsp;|&nbsp; 
            <span style="font-size:12px; color:#bdc3c7;">Filtro: Todos</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if menu == "RESUMEN":
    # Fila 1: KPIs Superiores
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.markdown('<div class="kpi-card"><div class="kpi-title">Calidad de Primera</div><div class="kpi-value val-green">96.8 %</div><div class="kpi-meta">Meta ≥ 95 %</div></div>', unsafe_allow_html=True)
    k2.markdown('<div class="kpi-card"><div class="kpi-title">Rechazo</div><div class="kpi-value val-red">2.1 %</div><div class="kpi-meta">Meta ≤ 2 %</div></div>', unsafe_allow_html=True)
    k3.markdown('<div class="kpi-card"><div class="kpi-title">Retrabajo</div><div class="kpi-value val-orange">1.1 %</div><div class="kpi-meta">Meta ≤ 1 %</div></div>', unsafe_allow_html=True)
    k4.markdown('<div class="kpi-card"><div class="kpi-title">Producto Liberado</div><div class="kpi-value val-blue">98.4 %</div><div class="kpi-meta">Meta ≥ 98 %</div></div>', unsafe_allow_html=True)
    k5.markdown('<div class="kpi-card"><div class="kpi-title">Reclamos Cliente</div><div class="kpi-value val-red">4</div><div class="kpi-meta">Meta ≤ 3</div></div>', unsafe_allow_html=True)
    k6.markdown('<div class="kpi-card"><div class="kpi-title">Auditorías Cumplidas</div><div class="kpi-value val-green">94 %</div><div class="kpi-meta">Meta ≥ 95 %</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    # Fila 2: Pareto, Distribución y Calidad por Proceso
    col_p, col_d, col_pr = st.columns([1.2, 1, 1.3])
    
    with col_p:
        st.markdown("##### PARETO DE DEFECTOS (MES ACTUAL)")
        df_p = pd.DataFrame({
            "Defecto": ["Mancha sup.", "Planitud", "Var. tono", "Canto/escuadra", "Ruptura", "Otros"],
            "Pct": [32, 24, 18, 12, 8, 6]
        }).sort_values("Pct", ascending=True)
        fig_p = px.bar(df_p, x="Pct", y="Defecto", orientation='h', text=[f"{v}%" for v in df_p["Pct"]], color_discrete_sequence=["#1b365d"])
        fig_p.update_layout(height=240, margin=dict(l=5, r=5, t=10, b=10), yaxis_title="", xaxis_title="")
        st.plotly_chart(fig_p, use_container_width=True)

    with col_d:
        st.markdown("##### DISTRIBUCIÓN DE DEFECTOS")
        fig_d = px.pie(df_p, values="Pct", names="Defecto", hole=0.5, color_discrete_sequence=["#1b365d", "#3498db", "#f39c12", "#e67e22", "#9b59b6", "#95a5a6"])
        fig_d.add_annotation(text="<b>Total<br>1,248</b>", showarrow=False, font_size=11)
        fig_d.update_layout(height=240, margin=dict(l=5, r=5, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_d, use_container_width=True)

    with col_pr:
        st.markdown("##### CALIDAD POR PROCESO (% PRIMERA)")
        procs = [
            ("PRENSADO", "🟢 98.2 %"), ("SECADO", "🟢 97.6 %"),
            ("ESMALTADO", "🟠 94.8 %"), ("DECORACIÓN", "🟠 95.1 %"),
            ("HORNO", "🔴 91.7 %"), ("SELECCIÓN", "🟢 98.5 %"),
            ("EMPAQUE", "🟢 99.1 %"), ("EMBARQUES", "🟢 98.7 %")
        ]
        p_c1 = st.columns(4)
        for i, (name, val) in enumerate(procs[:4]):
            p_c1[i].markdown(f'<div class="process-card"><div class="process-name">{name}</div><div class="process-val">{val}</div></div>', unsafe_allow_html=True)
            
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
        p_c2 = st.columns(4)
        for i, (name, val) in enumerate(procs[4:]):
            p_c2[i].markdown(f'<div class="process-card"><div class="process-name">{name}</div><div class="process-val">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    # Fila 3: Tendencia, Indicadores Clave y Acciones
    f3_1, f3_2, f3_3 = st.columns([1, 1.2, 1.3])
    
    with f3_1:
        st.markdown("##### TENDENCIA DE RECHAZO (%)")
        trend_df = pd.DataFrame({"Mes": ["Dic", "Ene", "Feb", "Mar", "Abr", "May"], "Rechazo": [2.6, 2.4, 2.2, 1.8, 1.7, 2.1]})
        fig_t = px.line(trend_df, x="Mes", y="Rechazo", text="Rechazo", markers=True, color_discrete_sequence=["#c0392b"])
        fig_t.add_hline(y=2.0, line_dash="dash", line_color="gray")
        fig_t.update_traces(textposition="top center")
        fig_t.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10), yaxis_range=[0, 3.5])
        st.plotly_chart(fig_t, use_container_width=True)

    with f3_2:
        st.markdown("##### INDICADORES CLAVE DEL PRODUCTO")
        ind1 = ["Planitud", "Curvatura Central", "Curvatura Lateral", "Alabeo", "Dimensiones"]
        ind2 = ["Absorción/Peso", "Módulo Ruptura", "Resistencia Impacto", "Tono/Apariencia", "DCOF/Superficie"]
        ic1 = st.columns(5)
        for i, item in enumerate(ind1):
            ic1[i].markdown(f'<div class="ind-card">{item}</div>', unsafe_allow_html=True)
        ic2 = st.columns(5)
        for i, item in enumerate(ind2):
            ic2[i].markdown(f'<div class="ind-card">{item}</div>', unsafe_allow_html=True)

    with f3_3:
        st.markdown("##### ACCIONES CORRECTIVAS ABIERTAS")
        acciones_df = pd.DataFrame({
            "ACCIÓN": ["Corregir planitud modelo X", "Revisar tono línea 3", "Auditoría de empaque", "Disminuir manchas modelo Y"],
            "RESPONSABLE": ["Producción", "Esmaltes", "Calidad", "Decoración"],
            "VENCIMIENTO": ["22/05/2026", "23/05/2026", "24/05/2026", "26/05/2026"],
            "ESTADO": ["🔴", "🟠", "🟢", "🟠"]
        })
        st.dataframe(acciones_df, use_container_width=True, hide_index=True)

    # Banner Inferior
    st.markdown("""
    <div class="footer-banner">
        <span>👥 ENFOQUE AL CLIENTE</span>
        <span>📈 MEJORA CONTINUA</span>
        <span>🤝 TRABAJO EN EQUIPO</span>
        <span>🛡️ INTEGRIDAD</span>
        <span>⚙️ DISCIPLINA OPERATIVA</span>
        <span>✅ CALIDAD SIEMPRE</span>
    </div>
    """, unsafe_allow_html=True)

else:
    st.subheader(f"Módulo: {menu}")
    st.info(f"Desglose en desarrollo para la sección {menu}.")
