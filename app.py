import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

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
    .kpi-value { font-size: 24px; font-weight: 800; margin: 5px 0; }
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

# ---------------------------------------------------------
# FUNCION PARA CARGAR DATOS DEL EXCEL (CON DETECCIÓN FLEXIBLE DE PESTAÑA)
# ---------------------------------------------------------
@st.cache_data
def load_excel_data(file_source):
    xl = pd.ExcelFile(file_source)
    sheet_names = xl.sheet_names
    
    # Buscar pestaña 'DASHBOARD' sin importar espacios vacíos o mayúsculas
    selected_sheet = None
    for s in sheet_names:
        if s.strip().upper() == "DASHBOARD":
            selected_sheet = s
            break
            
    if not selected_sheet:
        for s in sheet_names:
            if "DASH" in s.strip().upper():
                selected_sheet = s
                break
    if not selected_sheet:
        selected_sheet = sheet_names[0]

    df_raw = pd.read_excel(file_source, sheet_name=selected_sheet, header=None)
    
    # 1. Calidades y Mts2 (Columnas A:G)
    df_calidad = df_raw.iloc[2:, 0:7].copy()
    df_calidad.columns = ['FECHA', 'PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'META']
    df_calidad['FECHA'] = pd.to_datetime(df_calidad['FECHA'], errors='coerce')
    df_calidad = df_calidad.dropna(subset=['FECHA'])
    for col in ['PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'META']:
        df_calidad[col] = pd.to_numeric(df_calidad[col], errors='coerce').fillna(0)
    df_calidad['MES'] = df_calidad['FECHA'].dt.strftime('%B %Y').str.capitalize()
    
    # 2. Garantías por Mes (Columnas I:J)
    df_garantias = df_raw.iloc[2:14, 8:10].copy()
    df_garantias.columns = ['MES', 'CANTIDAD']
    df_garantias['CANTIDAD'] = pd.to_numeric(df_garantias['CANTIDAD'], errors='coerce').fillna(0)
    df_garantias = df_garantias[df_garantias['MES'] != 'TOTAL']

    # 3. Modelos en Prueba (Columnas L:M)
    df_pruebas = df_raw.iloc[2:10, 11:13].copy()
    df_pruebas.columns = ['MODELO', 'HORNO']
    df_pruebas = df_pruebas.dropna(subset=['MODELO'])

    # 4. Modelos Autorizados (Columnas O:P)
    df_autorizados = df_raw.iloc[2:10, 14:16].copy()
    df_autorizados.columns = ['MODELO', 'HORNO']
    df_autorizados = df_autorizados.dropna(subset=['MODELO'])

    # 5. Defectos (Columnas R:Y)
    df_def = df_raw.iloc[2:, 17:25].copy()
    df_def.columns = ['DIA', 'MODELO', 'FORMATO', 'HORNO', 'DEFECTO', 'MTS2', 'RESPONSABLE', 'PCT_AREA']
    df_def['DIA'] = pd.to_datetime(df_def['DIA'], errors='coerce')
    df_def = df_def.dropna(subset=['DIA', 'DEFECTO'])
    df_def['MTS2'] = pd.to_numeric(df_def['MTS2'], errors='coerce').fillna(0)
    df_def['MES'] = df_def['DIA'].dt.strftime('%B %Y').str.capitalize()

    return df_calidad, df_garantias, df_pruebas, df_autorizados, df_def

# Intentar cargar desde archivo guardado o default
target_file = None
if os.path.exists("REPORTE_ACTUAL.xlsx"):
    target_file = "REPORTE_ACTUAL.xlsx"
elif os.path.exists("REPORTE P1 Y P3 AGOSTO 2026.xlsx"):
    target_file = "REPORTE P1 Y P3 AGOSTO 2026.xlsx"

# Barra Lateral (Control de Acceso + Carga de Archivos)
with st.sidebar:
    st.markdown("### 🟢 SISTEMA DE CALIDAD")
    menu = st.radio(
        "MENÚ PRINCIPAL",
        ["RESUMEN", "MODELOS Y GARANTÍAS", "DEFECTOS", "PROCESOS", "EMBARQUES", "ACCIONES", "AUDITORÍAS"]
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
            st.cache_data.clear()
            st.success("¡Datos actualizados para el público!")
            st.rerun()

# Cargar datos si existe archivo
if target_file:
    df_calidad, df_garantias, df_pruebas, df_autorizados, df_def = load_excel_data(target_file)
else:
    st.error("⚠️ No se encontró el archivo de Excel en el servidor.")
    st.stop()

# Filtro por Mes en Barra Lateral
st.sidebar.divider()
meses_opciones = ["Todos los Meses"] + list(df_calidad['MES'].unique())
mes_seleccionado = st.sidebar.selectbox("🗓️ Filtro de Mes:", options=meses_opciones, index=0)

if mes_seleccionado != "Todos los Meses":
    df_calidad_f = df_calidad[df_calidad['MES'] == mes_seleccionado]
    df_def_f = df_def[df_def['MES'] == mes_seleccionado]
else:
    df_calidad_f = df_calidad.copy()
    df_def_f = df_def.copy()

# Header Principal
st.markdown(f"""
<div class="dashboard-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; font-weight:800; font-size:22px;">DASHBOARD – SISTEMA DE CALIDAD</h2>
            <p style="margin:0; font-size:12px; color:#bdc3c7; font-weight:600;">PRODUCTO TERMINADO – PISO CERÁMICO</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size:13px; font-weight:bold;">📅 Mes Activo</span> &nbsp;|&nbsp; 
            <span style="font-size:12px; color:#27ae60; font-weight:bold;">{mes_seleccionado}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Cálculo de KPIs desde Excel
total_m2 = df_calidad_f['MTS2'].sum()
p1_pct = ((df_calidad_f['PRIMERA'] * df_calidad_f['MTS2']).sum() / total_m2 * 100) if total_m2 > 0 else 0
p2_pct = ((df_calidad_f['SEGUNDA'] * df_calidad_f['MTS2']).sum() / total_m2 * 100) if total_m2 > 0 else 0
p5_pct = ((df_calidad_f['QUINTA'] * df_calidad_f['MTS2']).sum() / total_m2 * 100) if total_m2 > 0 else 0
garantias_total = int(df_garantias['CANTIDAD'].sum())

if menu == "RESUMEN":
    # Fila 1: KPIs Superiores Integrados
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad de Primera</div><div class="kpi-value val-green">{p1_pct:.1f}%</div><div class="kpi-meta">Meta ≥ 94.5%</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad 2ª</div><div class="kpi-value val-orange">{p2_pct:.1f}%</div><div class="kpi-meta">Seguimiento</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-title">Rechazo (5ª)</div><div class="kpi-value val-red">{p5_pct:.1f}%</div><div class="kpi-meta">Meta ≤ 1.5%</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-title">Mts² Producidos</div><div class="kpi-value val-blue">{total_m2/1000:.1f}k</div><div class="kpi-meta">Volumen Total</div></div>', unsafe_allow_html=True)
    k5.markdown('<div class="kpi-card"><div class="kpi-title">Cumplimiento Tonos</div><div class="kpi-value val-green">98.2%</div><div class="kpi-meta">Conforme Norma</div></div>', unsafe_allow_html=True)
    k6.markdown(f'<div class="kpi-card"><div class="kpi-title">Garantías (Año)</div><div class="kpi-value val-red">{garantias_total}</div><div class="kpi-meta">Reclamaciones</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    # Fila 2: Pareto, Distribución y Calidad por Proceso
    col_p, col_d, col_pr = st.columns([1.2, 1, 1.3])
    
    with col_p:
        st.markdown("##### PARETO DE DEFECTOS (m²)")
        if not df_def_f.empty:
            df_p = df_def_f.groupby('DEFECTO')['MTS2'].sum().reset_index().sort_values(by='MTS2', ascending=True)
            fig_p = px.bar(df_p, x="MTS2", y="DEFECTO", orientation='h', text_auto='.0f', color_discrete_sequence=["#1b365d"])
            fig_p.update_layout(height=240, margin=dict(l=5, r=5, t=10, b=10), yaxis_title="", xaxis_title="")
            st.plotly_chart(fig_p, use_container_width=True)

    with col_d:
        st.markdown("##### DISTRIBUCIÓN DE DEFECTOS")
        if not df_def_f.empty:
            fig_d = px.pie(df_def_f, values="MTS2", names="DEFECTO", hole=0.5, color_discrete_sequence=px.colors.qualitative.Set2)
            fig_d.add_annotation(text=f"<b>Total<br>{df_def_f['MTS2'].sum():,.0f} m²</b>", showarrow=False, font_size=11)
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

    # Fila 3: Tendencia Diaria, Indicadores Clave y Acciones
    f3_1, f3_2, f3_3 = st.columns([1, 1.2, 1.3])
    
    with f3_1:
        st.markdown("##### TENDENCIA DIARIA (% PRIMERA)")
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(x=df_calidad_f['FECHA'], y=df_calidad_f['PRIMERA']*100, mode='lines+markers', line=dict(color='#27ae60', width=2)))
        fig_t.add_trace(go.Scatter(x=df_calidad_f['FECHA'], y=[94.5]*len(df_calidad_f), mode='lines', line=dict(color='#e74c3c', dash='dash')))
        fig_t.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10), yaxis_range=[70, 100], showlegend=False)
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

elif menu == "MODELOS Y GARANTÍAS":
    st.subheader("📋 Control de Modelos y Garantías")
    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1:
        st.markdown("##### 🧪 MODELOS EN PRUEBA")
        st.dataframe(df_pruebas, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("##### ✅ MODELOS AUTORIZADOS")
        st.dataframe(df_autorizados, use_container_width=True, hide_index=True)
    with c3:
        st.markdown("##### 🛡️ GARANTÍAS POR MES")
        fig_g = px.bar(df_garantias, x="MES", y="CANTIDAD", text_auto=True, color_discrete_sequence=["#8b5cf6"])
        fig_g.update_layout(height=300, margin=dict(l=5, r=5, t=10, b=10))
        st.plotly_chart(fig_g, use_container_width=True)

else:
    st.subheader(f"Módulo: {menu}")
    st.info(f"Desglose en desarrollo para la sección {menu}.")
