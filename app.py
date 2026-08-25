import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard - Sistema de Calidad",
    page_icon="🟩",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0E131F; color: #FFFFFF; font-family: 'Segoe UI', Roboto, sans-serif; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; padding-left: 2rem; padding-right: 2rem; }
    [data-testid="stSidebar"] { background-color: #080B11; border-right: 1px solid #1E293B; }
    .dashboard-header { background-color: #131B2E; padding: 16px 24px; border-radius: 12px; border-left: 5px solid #10B981; margin-bottom: 20px; }
    .header-title { font-size: 24px; font-weight: 700; color: #FFFFFF; margin: 0; }
    .header-subtitle { font-size: 13px; color: #94A3B8; margin: 2px 0 0 0; }
    .kpi-card { background-color: #131B2E; border: 1px solid #1E293B; border-radius: 12px; padding: 16px; text-align: center; }
    .kpi-title { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 8px; }
    .kpi-value { font-size: 26px; font-weight: 800; margin-bottom: 4px; }
    .kpi-subtext { font-size: 11px; color: #64748B; }
    .section-box { background-color: #131B2E; border: 1px solid #1E293B; border-radius: 12px; padding: 18px; margin-bottom: 15px; }
    .section-title { font-size: 14px; font-weight: 700; color: #E2E8F0; margin-bottom: 15px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CREDENCIALES Y PROCESAMIENTO
# -----------------------------------------------------------------------------
ADMIN_USER = "admin"
ADMIN_PASSWORD = "calidad2026"
DATA_FILE = "data_actual.xlsx"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def process_data(file_source):
    xls = pd.ExcelFile(file_source)
    sheet_name = 'DASHBOARD' if 'DASHBOARD' in xls.sheet_names else xls.sheet_names[0]
    df_raw = pd.read_excel(xls, sheet_name=sheet_name)
    
    t1 = df_raw.iloc[:, 0:4].dropna(how='all'); t1.columns = ['MES', 'P1_ANUAL', 'P3_ANUAL', 'P1_P3_ANUAL']
    t2 = df_raw.iloc[:, 5:10].dropna(how='all'); t2.columns = ['DIA', 'P1_DIARIA', 'P3_DIARIA', 'P1_P3_DIARIA', 'MTS2_DIA']
    t3 = df_raw.iloc[:, 11:13].dropna(how='all'); t3.columns = ['MES_GARANTIAS', 'GARANTIAS']
    t4 = df_raw.iloc[:, 14:16].dropna(how='all'); t4.columns = ['MODELO_PRUEBA', 'HORNO_PRUEBAS']
    t5 = df_raw.iloc[:, 17:19].dropna(how='all'); t5.columns = ['MODELOS_AUTORIZADOS', 'HORNO_AUTORIZADOS']
    t6 = df_raw.iloc[:, 20:24].dropna(how='all'); t6.columns = ['FECHA', 'CUMP_P1', 'CUMP_P3', 'CUMP_ACUMULADO']
    t7 = df_raw.iloc[:, 25:27].dropna(how='all'); t7.columns = ['DEFECTO', 'PORC_DEFECTO']
    t8 = df_raw.iloc[:, 28:30].dropna(how='all'); t8.columns = ['DEFECTO_P1', 'PORC_DEFECTO_P1']
    t9 = df_raw.iloc[:, 31:33].dropna(how='all'); t9.columns = ['DEFECTO_P3', 'PORC_DEFECTO_P3']
    t10 = df_raw.iloc[:, 34:36].dropna(how='all'); t10.columns = ['AREA_RESPONSABLE', 'PORC_AREA']
    
    return t1, t2, t3, t4, t5, t6, t7, t8, t9, t10

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (AUTENTICACIÓN Y GESTIÓN)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🟩 **SISTEMA DE CALIDAD**")
    st.caption("PISO CERÁMICO P1 & P3")
    st.markdown("---")
    
    menu = st.radio("NAVEGACIÓN", ["RESUMEN", "INDICADORES", "DEFECTOS", "MODELOS Y HORNOS"])
    st.markdown("---")
    planta_sel = st.selectbox("Seleccionar Planta / Línea", ["Todas (P1 & P3)", "Planta 1 (P1)", "Planta 3 (P3)"])
    st.markdown("---")
    
    st.markdown("### 🔒 **Gestión de Archivo**")
    if not st.session_state.authenticated:
        with st.expander("Iniciar Sesión"):
            user_input = st.text_input("Usuario", key="u_input")
            pass_input = st.text_input("Contraseña", type="password", key="p_input")
            if st.button("Ingresar"):
                if user_input == ADMIN_USER and pass_input == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("Sesión iniciada")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    else:
        st.success("🟢 Sesión Admin Activa")
        
        # Carga de archivo
        uploaded_file = st.file_uploader("Subir Excel", type=["xlsx", "xls"])
        if uploaded_file is not None:
            if st.button("Guardar y Aplicar"):
                with open(DATA_FILE, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Archivo subido con éxito.")
                st.rerun()
                
        # Eliminación / Reseteo de archivo
        if os.path.exists(DATA_FILE):
            if st.button("🗑️ Eliminar/Resetear Datos"):
                os.remove(DATA_FILE)
                st.warning("Archivo eliminado.")
                st.rerun()

        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()

# -----------------------------------------------------------------------------
# 4. CARGA Y DESPLIEGUE
# -----------------------------------------------------------------------------
st.markdown("""
<div class="dashboard-header">
    <div class="header-title">DASHBOARD - SISTEMA DE CALIDAD</div>
    <div class="header-subtitle">MONITORIZACIÓN Y CONTROL DE PRODUCCIÓN CERÁMICA</div>
</div>
""", unsafe_allow_html=True)

data_loaded = False
if os.path.exists(DATA_FILE):
    try:
        t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = process_data(DATA_FILE)
        data_loaded = True
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

if not data_loaded:
    st.warning("⚠️ No hay datos cargados.")
    st.info("Inicia sesión en la barra lateral para subir o actualizar el archivo Excel.")
    st.stop()

# (Se mantiene la lógica de visualización de gráficos previa en el menú RESUMEN, INDICADORES, etc.)
