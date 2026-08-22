import streamlit as st
import pandas as pd
import plotly.express as px

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
# DATOS POR DEFECTO (DEMO / MOCK DATA)
# ---------------------------------------------------------
demo_kpis = pd.DataFrame([
    {"title": "Calidad Primera", "val": "94.2%", "meta": "Meta: 95.0%", "color": "#16A34A", "historico": "91,92,93,94.2"},
    {"title": "Rechazo Total", "val": "1.8%", "meta": "Meta: < 2.0%", "color": "#DC2626", "historico": "2.5,2.1,1.9,1.8"},
    {"title": "Efectividad (OEE)", "val": "88.5%", "meta": "Meta: 90.0%", "color": "#2563EB", "historico": "85,86,87,88.5"},
    {"title": "Acciones Cerradas", "val": "92%", "meta": "12 de 13 abiertas", "color": "#D97706", "historico": "80,85,90,92"},
    {"title": "Piezas Inspeccionadas", "val": "45,200", "meta": "Turno Actual", "color": "#475569", "historico": "10,20,30,45.2"},
    {"title": "Auditorías 5S", "val": "96%", "meta": "Planta General", "color": "#9333EA", "historico": "90,92,94,96"}
])

demo_def = pd.DataFrame([
    {"Defecto": "Curvatura / Deformación", "Cantidad": 450, "Porcentaje": 35.0, "Linea": "Línea 1"},
    {"Defecto": "Esmalte / Gotas", "Cantidad": 280, "Porcentaje": 22.0, "Linea": "Línea 1"},
    {"Defecto": "Tono / Variación", "Cantidad": 210, "Porcentaje": 16.0, "Linea": "Línea 2"},
    {"Defecto": "Despostillado", "Cantidad": 180, "Porcentaje": 14.0, "Linea": "Línea 2"},
    {"Defecto": "Dimensiones / Cajas", "Cantidad": 110, "Porcentaje": 8.0, "Linea": "Línea 3"},
    {"Defecto": "Otros / Varios", "Cantidad": 70, "Porcentaje": 5.0, "Linea": "Línea 3"}
])

demo_tendencia = pd.DataFrame([
    {"Mes": "Ene", "Rechazo": 2.8, "Linea": "Línea 1"},
    {"Mes": "Feb", "Rechazo": 2.5, "Linea": "Línea 1"},
    {"Mes": "Mar", "Rechazo": 2.2, "Linea": "Línea 1"},
    {"Mes": "Abr", "Rechazo": 2.0, "Linea": "Línea 1"},
    {"Mes": "May", "Rechazo": 1.8, "Linea": "Línea 1"}
])

demo_procesos = pd.DataFrame([
    {"nombre": "Prensado", "val": "98.5%", "status": "✅ OK", "icon": "⚙️", "Linea": "Línea 1"},
    {"nombre": "Secado", "val": "99.1%", "status": "✅ OK", "icon": "🔥", "Linea": "Línea 1"},
    {"nombre": "Esmaltado", "val": "95.2%", "status": "⚠️ Alerta", "icon": "🎨", "Linea": "Línea 1"},
    {"nombre": "Cocción (Horno)", "val": "96.8%", "status": "✅ OK", "icon": "🌡️", "Linea": "Línea 1"},
    {"nombre": "Rectificado", "val": "97.4%", "status": "✅ OK", "icon": "📐", "Linea": "Línea 1"},
    {"nombre": "Empaque", "val": "99.8%", "status": "✅ OK", "icon": "📦", "Linea": "Línea 1"}
])

demo_acciones = pd.DataFrame([
    {"ID": "AC-01", "DESCRIPCIÓN": "Ajuste de curva de temperatura Horno 2", "RESPONSABLE": "Mantenimiento", "ESTADO": "En Proceso", "Linea": "Línea 2"},
    {"ID": "AC-02", "DESCRIPCIÓN": "Cambio de boquillas en cabina de esmalte", "RESPONSABLE": "Producción", "ESTADO": "Cerrado", "Linea": "Línea 1"},
    {"ID": "AC-03", "DESCRIPCIÓN": "Calibración del sensor de espesor", "RESPONSABLE": "Calidad", "ESTADO": "Cerrado", "Linea": "Línea 3"}
])

demo_embarques = pd.DataFrame([
    {"Fecha": "2026-05-15", "Cajas": 1200, "Destino": "Norte", "Linea": "Línea 1"},
    {"Fecha": "2026-05-16", "Cajas": 1500, "Destino": "Centro", "Linea": "Línea 1"},
    {"Fecha": "2026-05-17", "Cajas": 1100, "Destino": "Sur", "Linea": "Línea 2"},
    {"Fecha": "2026-05-18", "Cajas": 1800, "Destino": "Exportación", "Linea": "Línea 3"}
])

demo_auditorias = pd.DataFrame([
    {"Fecha": "2026-05-10", "Auditor": "Juan Pérez", "Área": "Hornos", "Calificacion": 95, "Linea": "Línea 1"},
    {"Fecha": "2026-05-12", "Auditor": "María López", "Área": "Esmaltado", "Calificacion": 88, "Linea": "Línea 2"},
    {"Fecha": "2026-05-14", "Auditor": "Carlos Ruiz", "Área": "Empaque", "Calificacion": 98, "Linea": "Línea 3"}
])

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
# CARGA DE DATOS (CON FALLBACK A DATOS DEMO)
# ---------------------------------------------------------
df_kpis = demo_kpis.copy()
df_def = demo_def.copy()
df_tendencia = demo_tendencia.copy()
df_acciones = demo_acciones.copy()
df_procesos = demo_procesos.copy()
df_embarques = demo_embarques.copy()
df_auditorias = demo_auditorias.copy()

if uploaded_file is not None:
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        hojas = excel_file.sheet_names
        
        if "KPIs" in hojas: df_kpis = pd.read_excel(uploaded_file, sheet_name="KPIs")
        if "Defectos" in hojas: df_def = pd.read_excel(uploaded_file, sheet_name="Defectos")
        if "Tendencia" in hojas: df_tendencia = pd.read_excel(uploaded_file, sheet_name="Tendencia")
        if "Acciones" in hojas: df_acciones = pd.read_excel(uploaded_file, sheet_name="Acciones")
        if "Procesos" in hojas: df_procesos = pd.read_excel(uploaded_file, sheet_name="Procesos")
        if "Embarques" in hojas: df_embarques = pd.read_excel(uploaded_file, sheet_name="Embarques")
        if "Auditorias" in hojas: df_auditorias = pd.read_excel(uploaded_file, sheet_name="Auditorias")
        
        st.sidebar.success("✅ Archivo cargado correctamente")
    except Exception as e:
        st.sidebar.error(f"Error al leer Excel: {e}")

# Aplicar filtro de línea
if filtro_linea != "Todos":
    for df in [df_def, df_tendencia, df_acciones, df_procesos, df_embarques, df_auditorias]:
        if isinstance(df, pd.DataFrame) and "Linea" in df.columns:
            df = df[df["Linea"] == filtro_linea]

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
# NAVEGACIÓN Y VISTAS
# ---------------------------------------------------------

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

    with c2:
        st.markdown("##### DISTRIBUCIÓN DE DEFECTOS")
        if not df_def.empty and {"Defecto", "Cantidad"}.issubset(df_def.columns):
            df_pie = df_def.groupby("Defecto", as_index=False)["Cantidad"].sum()
            total_defectos = df_pie["Cantidad"].sum()
            fig_pie = px.pie(df_pie, values='Cantidad', names='Defecto', hole=0.6, color_discrete_sequence=['#1E3A8A', '#3B82F6', '#F59E0B', '#E11D48', '#8B5CF6', '#64748B'])
            fig_pie.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), annotations=[dict(text=f'<b>Total<br>{total_defectos:,}</b>', x=0.5, y=0.5, font_size=14, showarrow=False)], showlegend=True, legend=dict(font=dict(size=10)))
            st.plotly_chart(fig_pie, use_container_width=True)

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

elif opcion_menu == "📊 INDICADORES":
    st.markdown("### 📊 Análisis Detallado de KPIs e Indicadores")
    st.dataframe(df_kpis, use_container_width=True, hide_index=True)

elif opcion_menu == "📋 DEFECTOS":
    st.markdown("### 📋 Análisis Profundo de Defectos de Calidad")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        fig_def_bar = px.bar(df_def, x="Defecto", y="Cantidad", color="Defecto", title="Frecuencia por Tipo de Defecto", text="Cantidad")
        st.plotly_chart(fig_def_bar, use_container_width=True)
    with col2:
        st.dataframe(df_def, use_container_width=True, hide_index=True)

elif opcion_menu == "🏭 PROCESOS":
    st.markdown("### 🏭 Estado y Desempeño de Procesos Productivos")
    st.dataframe(df_procesos, use_container_width=True, hide_index=True)

elif opcion_menu == "📦 EMBARQUES":
    st.markdown("### 📦 Control de Embarques y Despachos")
    st.dataframe(df_embarques, use_container_width=True, hide_index=True)

elif opcion_menu == "⚙️ ACCIONES":
    st.markdown("### ⚙️ Plan de Acciones Correctivas y Preventivas")
    st.dataframe(df_acciones, use_container_width=True, hide_index=True)

elif opcion_menu == "👥 AUDITORÍAS":
    st.markdown("### 👥 Registro y Cumplimiento de Auditorías")
    st.dataframe(df_auditorias, use_container_width=True, hide_index=True)

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
