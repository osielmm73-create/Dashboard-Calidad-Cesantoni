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

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #121921;
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
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
    
    uploaded_file = st.file_uploader("📂 Cargar archivo Excel (.xlsx)", type=["xlsx", "xls"])
    
    st.markdown("---")
    opcion_menu = st.radio(
        "Navegación principal:",
        [
            "📌 RESUMEN",
            "📊 INDICADORES",
            "📋 DEFECTOS",
            "🏭 PROCESOS",
            "📦 EMBARQUES",
            "⚙️ ACCIONES",
            "👥 AUDITORÍAS"
        ]
    )
    
    st.markdown("---")
    fecha_sel = st.date_input("Fecha de Consulta", pd.to_datetime("2026-05-19"))
    filtro_linea = st.selectbox("Filtro de Línea", ["Todos", "Línea 1", "Línea 2", "Línea 3"])

# ---------------------------------------------------------
# CONTROL DE FLUJO: SI NO HAY ARCHIVO, NO MUESTRA NADA
# ---------------------------------------------------------
if uploaded_file is None:
    st.markdown("""
    <div style="text-align: center; padding: 60px; background-color: #F8FAFC; border-radius: 12px; border: 2px dashed #CBD5E1; margin-top: 20px;">
        <h2 style="color: #475569; margin-bottom: 10px;">📊 Dashboard Sistema de Calidad</h2>
        <p style="color: #64748B; font-size: 16px;">Por favor, carga un archivo de Excel (.xlsx) en el menú lateral para habilitar todos los apartados.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# CARGA DE HOJAS
# ---------------------------------------------------------
try:
    excel_file = pd.ExcelFile(uploaded_file)
    hojas_disponibles = excel_file.sheet_names
    
    def cargar_hoja(nombre_hoja, df_backup):
        if nombre_hoja in hojas_disponibles:
            df = pd.read_excel(uploaded_file, sheet_name=nombre_hoja)
            return df if not df.empty else df_backup
        return df_backup

    df_kpis = cargar_hoja("KPIs", pd.DataFrame())
    df_def = cargar_hoja("Defectos", pd.DataFrame())
    df_tendencia = cargar_hoja("Tendencia", pd.DataFrame())
    df_acciones = cargar_hoja("Acciones", pd.DataFrame())
    df_procesos = cargar_hoja("Procesos", pd.DataFrame())
    df_embarques = cargar_hoja("Embarques", pd.DataFrame())
    df_auditorias = cargar_hoja("Auditorias", pd.DataFrame())

    # Aplicar Filtro de Línea si existe la columna en el DataFrame
    if filtro_linea != "Todos":
        for df in [df_kpis, df_def, df_tendencia, df_acciones, df_procesos, df_embarques, df_auditorias]:
            if "Linea" in df.columns:
                df = df[df["Linea"] == filtro_linea]

except Exception as e:
    st.error(f"Error al leer el archivo Excel: {e}")
    st.stop()

# ---------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------
st.markdown(f"""
<div class="header-container">
    <div>
        <h2 style="margin:0; font-size:22px;">DASHBOARD – SISTEMA DE CALIDAD</h2>
        <span style="font-size:13px; color:#94A3B8;">PRODUCTO TERMINADO – PISO CERÁMICO | {opcion_menu}</span>
    </div>
    <div style="text-align:right;">
        <span style="font-size:14px; background:#334155; padding:6px 12px; border-radius:6px;">📅 {fecha_sel.strftime('%d/%m/%Y')} | 🌪️ Línea: {filtro_linea}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# NAVEGACIÓN Y VISTAS FUNCIONALES
# ---------------------------------------------------------

# --- 1. RESUMEN (Vista Completa Unificada) ---
if opcion_menu == "📌 RESUMEN":
    # KPIs Cards
    if not df_kpis.empty:
        cols_kpi = st.columns(min(len(df_kpis), 6))
        for i, kpi in enumerate(df_kpis.to_dict('records')[:6]):
            with cols_kpi[i]:
                val_historicos = [float(x) for x in str(kpi.get('historico', '0,0,0')).split(',')]
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">{kpi.get('title', 'KPI')}</div>
                    <div class="kpi-value" style="color:{kpi.get('color', '#1E293B')}">{kpi.get('val', '-')}</div>
                    <div class="kpi-meta">{kpi.get('meta', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                fig_spark = px.line(x=range(len(val_historicos)), y=val_historicos)
                fig_spark.update_traces(line_color=kpi.get('color', '#1E293B'), line_width=2)
                fig_spark.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=35, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})
    
    st.write("")
    c1, c2, c3 = st.columns([1.1, 1, 1.1])
    
    with c1:
        st.markdown("##### PARETO DE DEFECTOS")
        if not df_def.empty and {"Defecto", "Porcentaje"}.issubset(df_def.columns):
            df_pareto = df_def.groupby("Defecto", as_index=False)["Porcentaje"].sum().sort_values(by="Porcentaje", ascending=True)
            fig_pareto = px.bar(df_pareto, y="Defecto", x="Porcentaje", orientation='h', text="Porcentaje", color_discrete_sequence=['#1E3A8A'])
            fig_pareto.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_pareto.update_layout(height=260, margin=dict(l=10, r=30, t=10, b=10), xaxis=dict(showgrid=True, gridcolor='#E2E8F0', title=""), yaxis=dict(title=""))
            st.plotly_chart(fig_pareto, use_container_width=True)
        else:
            st.info("Sin datos de defectos.")

    with c2:
        st.markdown("##### DISTRIBUCIÓN DE DEFECTOS")
        if not df_def.empty and {"Defecto", "Cantidad"}.issubset(df_def.columns):
            df_pie = df_def.groupby("Defecto", as_index=False)["Cantidad"].sum()
            total_defectos = df_pie["Cantidad"].sum()
            fig_pie = px.pie(df_pie, values='Cantidad', names='Defecto', hole=0.6, color_discrete_sequence=['#1E3A8A', '#3B82F6', '#F59E0B', '#E11D48', '#8B5CF6', '#64748B'])
            fig_pie.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), annotations=[dict(text=f'<b>Total<br>{total_defectos:,}</b>', x=0.5, y=0.5, font_size=14, showarrow=False)], showlegend=True, legend=dict(font=dict(size=10)))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sin datos para distribución.")

    with c3:
        st.markdown("##### CALIDAD POR PROCESO (%)")
        if not df_procesos.empty:
            col_p1, col_p2 = st.columns(2)
            for idx, p in enumerate(df_procesos.to_dict('records')):
                target_col = col_p1 if idx % 2 == 0 else col_p2
                with target_col:
                    st.markdown(f"""
                    <div style="border:1px solid #E2E8F0; padding:8px; border-radius:6px; margin-bottom:8px; text-align:center; background:#FAFAFA;">
                        <span style="font-size:10px; font-weight:bold; color:#475569;">{p.get('nombre', '')}</span><br>
                        <span style="font-size:16px;">{p.get('icon', '⚙️')}</span><br>
                        <span style="font-size:13px; font-weight:bold; color:#1E293B;">{p.get('status', '')} {p.get('val', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Sin datos de procesos.")

    st.write("")
    b1, b2, b3 = st.columns([1, 1.2, 1.1])
    
    with b1:
        st.markdown("##### TENDENCIA DE RECHAZO (%)")
        if not df_tendencia.empty and {"Mes", "Rechazo"}.issubset(df_tendencia.columns):
            fig_tend = px.line(df_tendencia, x="Mes", y="Rechazo", markers=True, text="Rechazo")
            fig_tend.update_traces(line_color="#DC2626", textposition="top center")
            fig_tend.add_hline(y=2.0, line_dash="dash", line_color="#64748B", annotation_text="Meta (2.0 %)")
            fig_tend.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(title=""), xaxis=dict(title=""))
            st.plotly_chart(fig_tend, use_container_width=True)
        else:
            st.info("Sin datos de tendencia.")

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

    with b3:
        st.markdown("##### ACCIONES CORRECTIVAS")
        if not df_acciones.empty:
            st.dataframe(df_acciones, hide_index=True, use_container_width=True)
        else:
            st.info("Sin acciones pendientes.")

# --- 2. INDICADORES ---
elif opcion_menu == "📊 INDICADORES":
    st.markdown("### 📊 Análisis Detallado de KPIs e Indicadores")
    if not df_kpis.empty:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_kpis, use_container_width=True, hide_index=True)
        with col2:
            if "val" in df_kpis.columns and "title" in df_kpis.columns:
                df_kpis_num = df_kpis.copy()
                df_kpis_num["val_clean"] = pd.to_numeric(df_kpis_num["val"].astype(str).str.replace("%", "").str.replace("$", "").str.replace(",", ""), errors='coerce')
                fig_kpis = px.bar(df_kpis_num, x="title", y="val_clean", title="Métricas Comparativas", text="val")
                fig_kpis.update_layout(xaxis_title="", yaxis_title="Valor")
                st.plotly_chart(fig_kpis, use_container_width=True)
    else:
        st.warning("No se encontró la hoja 'KPIs' en el Excel cargado.")

# --- 3. DEFECTOS ---
elif opcion_menu == "📋 DEFECTOS":
    st.markdown("### 📋 Análisis Profundo de Defectos de Calidad")
    if not df_def.empty:
        col1, col2 = st.columns([1.2, 1])
        with col1:
            fig_def_bar = px.bar(df_def, x="Defecto", y="Cantidad", color="Defecto", title="Frecuencia por Tipo de Defecto", text="Cantidad")
            st.plotly_chart(fig_def_bar, use_container_width=True)
        with col2:
            st.markdown("#### Registro Tabular")
            st.dataframe(df_def, use_container_width=True, hide_index=True)
    else:
        st.warning("No se encontró la hoja 'Defectos' en el Excel cargado.")

# --- 4. PROCESOS ---
elif opcion_menu == "🏭 PROCESOS":
    st.markdown("### 🏭 Estado y Desempeño de Procesos Productivos")
    if not df_procesos.empty:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_procesos, use_container_width=True, hide_index=True)
        with col2:
            if "val" in df_procesos.columns and "nombre" in df_procesos.columns:
                df_p_num = df_procesos.copy()
                df_p_num["val_clean"] = pd.to_numeric(df_p_num["val"].astype(str).str.replace("%", ""), errors='coerce')
                fig_proc = px.bar(df_p_num, x="nombre", y="val_clean", color="status", title="Rendimiento de Primera por Etapa (%)")
                st.plotly_chart(fig_proc, use_container_width=True)
    else:
        st.warning("No se encontró la hoja 'Procesos' en el Excel cargado.")

# --- 5. EMBARQUES ---
elif opcion_menu == "📦 EMBARQUES":
    st.markdown("### 📦 Control de Embarques y Despachos")
    if not df_embarques.empty:
        st.dataframe(df_embarques, use_container_width=True, hide_index=True)
        if {"Fecha", "Cajas"}.issubset(df_embarques.columns):
            fig_emb = px.line(df_embarques, x="Fecha", y="Cajas", markers=True, title="Volumen de Cajas Embarcadas por Día")
            st.plotly_chart(fig_emb, use_container_width=True)
    else:
        st.info("Para habilitar este apartado, agrega una hoja llamada **'Embarques'** a tu archivo de Excel.")

# --- 6. ACCIONES ---
elif opcion_menu == "⚙️ ACCIONES":
    st.markdown("### ⚙️ Plan de Acciones Correctivas y Preventivas")
    if not df_acciones.empty:
        st.dataframe(df_acciones, use_container_width=True, hide_index=True)
        if "ESTADO" in df_acciones.columns:
            fig_acc = px.pie(df_acciones, names="ESTADO", title="Distribución de Estatus de Acciones")
            st.plotly_chart(fig_acc, use_container_width=True)
    else:
        st.warning("No se encontró la hoja 'Acciones' en el Excel cargado.")

# --- 7. AUDITORÍAS ---
elif opcion_menu == "👥 AUDITORÍAS":
    st.markdown("### 👥 Registro y Cumplimiento de Auditorías")
    if not df_auditorias.empty:
        st.dataframe(df_auditorias, use_container_width=True, hide_index=True)
        if {"Auditor", "Calificacion"}.issubset(df_auditorias.columns):
            fig_aud = px.bar(df_auditorias, x="Auditor", y="Calificacion", title="Calificación por Auditor")
            st.plotly_chart(fig_aud, use_container_width=True)
    else:
        st.info("Para habilitar este apartado, agrega una hoja llamada **'Auditorias'** a tu archivo de Excel.")

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
