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
    .kpi-value { font-size: 22px; font-weight: 800; margin: 5px 0; }
    .kpi-meta { font-size: 11px; color: #7f8c8d; }
    .val-green { color: #27ae60; }
    .val-red { color: #e74c3c; }
    .val-orange { color: #e67e22; }
    .val-blue { color: #2980b9; }

    .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #1a252f;
        margin-bottom: 10px;
        text-transform: uppercase;
        border-bottom: 2px solid #e1e8ed;
        padding-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

ADMIN_PASSWORD = "admin123"

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# FUNCION PARA CARGAR Y CALCULAR DATOS DEL EXCEL
def load_excel_data(file_source):
    xl = pd.ExcelFile(file_source)
    sheet_names = xl.sheet_names
    
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
    
    # 1. Calidades, Mts2 y Pallets (Cols A:G)
    df_calidad = df_raw.iloc[2:, 0:7].copy()
    df_calidad.columns = ['FECHA', 'PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'PALLETS_LIB']
    df_calidad['FECHA'] = pd.to_datetime(df_calidad['FECHA'], errors='coerce')
    df_calidad = df_calidad.dropna(subset=['FECHA'])
    
    for col in ['PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'PALLETS_LIB']:
        df_calidad[col] = pd.to_numeric(df_calidad[col], errors='coerce').fillna(0)
        
    df_calidad['MES'] = df_calidad['FECHA'].dt.strftime('%B %Y').str.capitalize()
    
    # 2. Garantías por Mes (Cols I:J)
    df_garantias = df_raw.iloc[2:14, 8:10].copy()
    df_garantias.columns = ['MES', 'CANTIDAD']
    df_garantias['CANTIDAD'] = pd.to_numeric(df_garantias['CANTIDAD'], errors='coerce').fillna(0)
    df_garantias = df_garantias[df_garantias['MES'] != 'TOTAL']

    # 3. Modelos en Prueba (Cols L:M)
    df_pruebas = df_raw.iloc[2:15, 11:13].copy()
    df_pruebas.columns = ['MODELO', 'HORNO']
    df_pruebas = df_pruebas.dropna(subset=['MODELO'])

    # 4. Modelos Autorizados (Cols O:P)
    df_autorizados = df_raw.iloc[2:15, 14:16].copy()
    df_autorizados.columns = ['MODELO', 'HORNO']
    df_autorizados = df_autorizados.dropna(subset=['MODELO'])

    # 5. Defectos y Rechazos (Cols R:Y)
    df_def = df_raw.iloc[2:, 17:25].copy()
    df_def.columns = ['DIA', 'MODELO', 'FORMATO', 'HORNO', 'DEFECTO', 'MTS2', 'RESPONSABLE', 'PCT_AREA']
    df_def['DIA'] = pd.to_datetime(df_def['DIA'], errors='coerce')
    df_def = df_def.dropna(subset=['DIA', 'DEFECTO'])
    df_def['MTS2'] = pd.to_numeric(df_def['MTS2'], errors='coerce').fillna(0)
    df_def['MES'] = df_def['DIA'].dt.strftime('%B %Y').str.capitalize()

    cumplimiento_tonos = 98.2

    return df_calidad, df_garantias, df_pruebas, df_autorizados, df_def, cumplimiento_tonos

# Barra Lateral
with st.sidebar:
    st.markdown("### 🟢 SISTEMA DE CALIDAD")
    st.divider()
    
    st.subheader("🔑 Administrador")
    if not st.session_state['logged_in']:
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if pwd == ADMIN_PASSWORD:
                st.session_state['logged_in'] = True
                st.success("Sesión iniciada")
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    else:
        st.success("Modo Admin Activo")
        uploaded_file = st.file_uploader("Subir / Actualizar Excel", type=["xlsx", "xls"])
        if uploaded_file is not None:
            st.session_state['excel_file'] = uploaded_file
            st.success("¡Archivo cargado con éxito!")
            st.rerun()
            
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.rerun()

# SI NO HAY NINGÚN ARCHIVO CARGADO EN SESIÓN: PANTALLA TOTALMENTE EN BLANCO
if 'excel_file' not in st.session_state or st.session_state['excel_file'] is None:
    st.warning("⚠️ Sin datos para mostrar. Inicia sesión como Administrador en la barra lateral para subir el archivo de reporte Excel.")
    st.stop()

# Cargar los datos únicamente desde la sesión activa
df_calidad, df_garantias, df_pruebas, df_autorizados, df_def, cumplimiento_tonos = load_excel_data(st.session_state['excel_file'])

# Filtro lateral de Mes
st.sidebar.divider()
meses_opciones = ["Todos los Meses"] + list(df_calidad['MES'].unique())
mes_seleccionado = st.sidebar.selectbox("🗓️ Filtrar Mes:", options=meses_opciones, index=0)

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
            <h2 style="margin:0; font-weight:800; font-size:22px;">DASHBOARD – CONTROL DE CALIDAD</h2>
            <p style="margin:0; font-size:12px; color:#bdc3c7; font-weight:600;">RESUMEN OPERATIVO</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size:13px; font-weight:bold;">📅 Período:</span> 
            <span style="font-size:12px; color:#27ae60; font-weight:bold;">{mes_seleccionado}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# CÁLCULOS Y RENDERIZADO DE PANTALLA
ultimo_dia = df_calidad_f['FECHA'].max()
df_ultimo_dia = df_calidad_f[df_calidad_f['FECHA'] == ultimo_dia]
df_def_ultimo_dia = df_def_f[df_def_f['DIA'] == ultimo_dia]

calidad_dia = (df_ultimo_dia['PRIMERA'].mean() * 100) if not df_ultimo_dia.empty else 0
total_m2_acum = df_calidad_f['MTS2'].sum()
calidad_acumulada = ((df_calidad_f['PRIMERA'] * df_calidad_f['MTS2']).sum() / total_m2_acum * 100) if total_m2_acum > 0 else 0

mts2_dia = df_ultimo_dia['MTS2'].sum() if not df_ultimo_dia.empty else 0
pallets_dia = df_ultimo_dia['PALLETS_LIB'].sum() if not df_ultimo_dia.empty else 0
pallets_acum = df_calidad_f['PALLETS_LIB'].sum()
total_garantias = int(df_garantias['CANTIDAD'].sum())

rechazo_dia = df_def_ultimo_dia.groupby('DEFECTO')['MTS2'].sum().idxmax() if not df_def_ultimo_dia.empty else "N/A"
rechazo_acum = df_def_f.groupby('DEFECTO')['MTS2'].sum().idxmax() if not df_def_f.empty else "N/A"

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad de Primera</div><div class="kpi-value val-green">{calidad_dia:.1f}% <span style="font-size:12px; color:#7f8c8d;">(Día)</span></div><div class="kpi-meta">Acum. Mes: <b>{calidad_acumulada:.1f}%</b></div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Volumen Mts²</div><div class="kpi-value val-blue">{mts2_dia:,.0f} <span style="font-size:12px; color:#7f8c8d;">m² (Día)</span></div><div class="kpi-meta">Acum. Mes: <b>{total_m2_acum:,.0f} m²</b></div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Liberados</div><div class="kpi-value val-green">{pallets_dia:,.0f} <span style="font-size:12px; color:#7f8c8d;">(Día)</span></div><div class="kpi-meta">Acum. Mes: <b>{pallets_acum:,.0f}</b></div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Cumplimiento Tonos</div><div class="kpi-value val-green">{cumplimiento_tonos:.1f}%</div><div class="kpi-meta">Garantías Año: <b style="color:#e74c3c;">{total_garantias}</b></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">📌 Principales Motivos de Rechazo</div>', unsafe_allow_html=True)
r1, r2 = st.columns(2)
r1.info(f"**Principal Rechazo del Día:** {rechazo_dia}")
r2.warning(f"**Principal Rechazo Acumulado:** {rechazo_acum}")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">🧪 Control de Modelos</div>', unsafe_allow_html=True)
m1, m2 = st.columns(2)

with m1:
    st.markdown("##### LISTA DE MODELOS EN PRUEBA")
    st.dataframe(df_pruebas, use_container_width=True, hide_index=True)

with m2:
    st.markdown("##### LISTA DE MODELOS AUTORIZADOS")
    st.dataframe(df_autorizados, use_container_width=True, hide_index=True)
