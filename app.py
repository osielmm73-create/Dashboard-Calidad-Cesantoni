import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# Configuración de página
st.set_page_config(
    page_title="Dashboard - Sistema de Calidad",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS - Estilo Tarjetas Dashboard
st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; }
    
    .dashboard-header {
        background-color: #0f172a;
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px 0 rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        text-align: center;
        height: 100%;
    }
    
    .kpi-title { 
        font-size: 11px; 
        font-weight: 700; 
        color: #64748b; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value { 
        font-size: 24px; 
        font-weight: 800; 
        margin: 8px 0 2px 0; 
    }
    
    .val-green { color: #10b981; }
    .val-red { color: #ef4444; }
    .val-blue { color: #2563eb; }
    .val-amber { color: #f59e0b; }

    .section-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 13px;
        font-weight: 700;
        color: #1e293b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

ADMIN_PASSWORD = "admin123"

# Inicialización de Estados
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'excel_bytes' not in st.session_state:
    st.session_state['excel_bytes'] = None

# ---------------------------------------------------------
# FUNCIÓN PARA CARGAR Y PARSEAR DATOS DESDE EXCEL
# ---------------------------------------------------------
def parse_excel_data(file_bytes):
    xl = pd.ExcelFile(io.BytesIO(file_bytes))
    sheet_names = xl.sheet_names
    
    # 1. Búsqueda o lectura directa de la pestaña DASHBOARD o DEFECTIVOS
    selected_sheet = next((s for s in sheet_names if s.strip().upper() == "DASHBOARD"), None)
    if not selected_sheet:
        selected_sheet = next((s for s in sheet_names if "DASH" in s.strip().upper()), sheet_names[0])

    df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=selected_sheet, header=None)
    
    # Lectura Tabla Calidad, Metrajes y Pallets (Cols A a G)
    df_calidad = df_raw.iloc[2:, 0:7].copy()
    df_calidad.columns = ['FECHA', 'PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'PALLETS_LIB']
    df_calidad['FECHA'] = pd.to_datetime(df_calidad['FECHA'], errors='coerce')
    df_calidad = df_calidad.dropna(subset=['FECHA'])
    
    for col in ['PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'PALLETS_LIB']:
        df_calidad[col] = pd.to_numeric(df_calidad[col], errors='coerce').fillna(0)
        
    df_calidad['MES'] = df_calidad['FECHA'].dt.strftime('%B %Y').str.capitalize()
    
    # Lectura Garantías (Cols I a J)
    df_garantias = df_raw.iloc[2:14, 8:10].copy()
    df_garantias.columns = ['MES', 'CANTIDAD']
    df_garantias['CANTIDAD'] = pd.to_numeric(df_garantias['CANTIDAD'], errors='coerce').fillna(0)
    df_garantias = df_garantias[df_garantias['MES'] != 'TOTAL']

    # Lectura Modelos en Prueba y Autorizados
    df_pruebas = df_raw.iloc[2:15, 11:13].copy()
    df_pruebas.columns = ['MODELO', 'HORNO']
    df_pruebas = df_pruebas.dropna(subset=['MODELO'])

    df_autorizados = df_raw.iloc[2:15, 14:16].copy()
    df_autorizados.columns = ['MODELO', 'HORNO']
    df_autorizados = df_autorizados.dropna(subset=['MODELO'])

    # Lectura Tabla de Defectos (Cols Q a Y - Rango 16 al 24 en índice base 0)
    df_def = df_raw.iloc[2:, 16:25].copy()
    df_def.columns = ['DIA', 'MODELO', 'FORMATO', 'HORNO', 'DEFECTO', 'MTS2', 'RESPONSABLE', 'PCT_AREA', 'EXTRA']
    df_def['DIA'] = pd.to_datetime(df_def['DIA'], errors='coerce')
    df_def = df_def.dropna(subset=['DIA', 'DEFECTO'])
    df_def['MTS2'] = pd.to_numeric(df_def['MTS2'], errors='coerce').fillna(0)
    df_def['PCT_AREA'] = pd.to_numeric(df_def['PCT_AREA'], errors='coerce').fillna(0)
    df_def['MES'] = df_def['DIA'].dt.strftime('%B %Y').str.capitalize()

    return df_calidad, df_garantias, df_pruebas, df_autorizados, df_def

# ---------------------------------------------------------
# BARRA LATERAL (ADMINISTRADOR Y CONFIGURACIÓN)
# ---------------------------------------------------------
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
        uploaded_file = st.file_uploader("Subir / Actualizar Excel", type=["xlsx", "xls"], key="uploader")
        
        if uploaded_file is not None:
            st.session_state['excel_bytes'] = uploaded_file.getvalue()
            st.success("¡Archivo cargado correctamente!")
            
        if st.session_state['excel_bytes'] is not None:
            if st.button("🗑️ Eliminar Reporte Actual"):
                st.session_state['excel_bytes'] = None
                st.rerun()

        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.rerun()

# ---------------------------------------------------------
# VERIFICACIÓN DE DATOS
# ---------------------------------------------------------
if st.session_state['excel_bytes'] is None:
    st.warning("⚠️ Sin datos para mostrar. Inicia sesión como Administrador en la barra lateral para subir el archivo de reporte Excel.")
    st.stop()

try:
    df_calidad, df_garantias, df_pruebas, df_autorizados, df_def = parse_excel_data(st.session_state['excel_bytes'])
except Exception as e:
    st.error(f"Error al procesar el archivo Excel: {e}")
    st.stop()

# Filtros en Barra Lateral
st.sidebar.divider()
meses_opciones = ["Todos los Meses"] + list(df_calidad['MES'].unique())
mes_seleccionado = st.sidebar.selectbox("🗓️ Filtrar Mes:", options=meses_opciones, index=0)
meta_calidad = st.sidebar.number_input("🎯 Meta de Calidad (%):", min_value=0.0, max_value=100.0, value=95.0, step=0.5)

if mes_seleccionado != "Todos los Meses":
    df_calidad_f = df_calidad[df_calidad['MES'] == mes_seleccionado].copy()
    df_def_f = df_def[df_def['MES'] == mes_seleccionado].copy()
else:
    df_calidad_f = df_calidad.copy()
    df_def_f = df_def.copy()

# ---------------------------------------------------------
# CÁLCULOS DÍA ACTUAL Y ACUMULADO MES
# ---------------------------------------------------------
ultimo_dia = df_calidad_f['FECHA'].max()
df_ultimo_dia = df_calidad_f[df_calidad_f['FECHA'] == ultimo_dia]
df_def_ultimo_dia = df_def_f[df_def_f['DIA'] == ultimo_dia]

# Métricas de Calidad
calidad_dia = (df_ultimo_dia['PRIMERA'].mean() * 100) if not df_ultimo_dia.empty else 0.0
total_m2_acum = df_calidad_f['MTS2'].sum()
calidad_acum = ((df_calidad_f['PRIMERA'] * df_calidad_f['MTS2']).sum() / total_m2_acum * 100) if total_m2_acum > 0 else 0.0

# Métricas de Volumen y Defectos
mts2_dia = df_ultimo_dia['MTS2'].sum() if not df_ultimo_dia.empty else 0.0
mts2_def_dia = df_def_ultimo_dia['MTS2'].sum()
mts2_def_acum = df_def_f['MTS2'].sum()

pallets_dia = df_ultimo_dia['PALLETS_LIB'].sum() if not df_ultimo_dia.empty else 0.0
pallets_acum = df_calidad_f['PALLETS_LIB'].sum()

dias_evaluados = df_calidad_f.copy()
dias_evaluados['PRIMERA_PCT'] = dias_evaluados['PRIMERA'] * 100
dias_cumple = (dias_evaluados['PRIMERA_PCT'] >= meta_calidad).sum()
dias_no_cumple = (dias_evaluados['PRIMERA_PCT'] < meta_calidad).sum()

# ---------------------------------------------------------
# RENDERIZADO DEL DASHBOARD
# ---------------------------------------------------------
st.markdown(f"""
<div class="dashboard-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; font-weight:800; font-size:20px; letter-spacing:0.5px;">DASHBOARD – CONTROL DE CALIDAD</h2>
            <p style="margin:2px 0 0 0; font-size:12px; color:#94a3b8; font-weight:600;">PRODUCTO TERMINADO – PISO CERÁMICO</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size:12px; color:#94a3b8;">Última Captura:</span><br>
            <span style="font-size:14px; color:#10b981; font-weight:bold;">{ultimo_dia.strftime('%d/%m/%Y') if pd.notnull(ultimo_dia) else 'N/A'}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# TARJETAS KPI
k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)

with k1:
    col_class = "val-green" if calidad_dia >= meta_calidad else "val-red"
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Día</div><div class="kpi-value {col_class}">{calidad_dia:.2f}%</div></div>', unsafe_allow_html=True)
with k2:
    col_class_ac = "val-green" if calidad_acum >= meta_calidad else "val-red"
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Acum</div><div class="kpi-value {col_class_ac}">{calidad_acum:.2f}%</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Defecto Día</div><div class="kpi-value val-red">{mts2_def_dia:,.2f}<span style="font-size:10px;"> m²</span></div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Defectos Acum</div><div class="kpi-value val-red">{mts2_def_acum:,.2f}<span style="font-size:10px;"> m²</span></div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Día</div><div class="kpi-value val-amber">{pallets_dia:,.2f}</div></div>', unsafe_allow_html=True)
with k6:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Acum</div><div class="kpi-value val-amber">{pallets_acum:,.2f}</div></div>', unsafe_allow_html=True)
with k7:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Días Cumple</div><div class="kpi-value val-green">{dias_cumple}</div></div>', unsafe_allow_html=True)
with k8:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Días No Cumple</div><div class="kpi-value val-red">{dias_no_cumple}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# GRÁFICAS
g1, g2 = st.columns([1, 1])

with g1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Tendencia Diaria de Calidad de Primera (%) vs Meta</div>', unsafe_allow_html=True)
    
    df_trend = df_calidad_f.sort_values('FECHA').copy()
    df_trend['PRIMERA_PCT'] = df_trend['PRIMERA'] * 100
    df_trend['CUMPLE_META'] = df_trend['PRIMERA_PCT'] >= meta_calidad
    
    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=df_trend['FECHA'],
        y=[meta_calidad] * len(df_trend),
        mode='lines',
        name=f'Meta ({meta_calidad:.2f}%)',
        line=dict(color='#ef4444', width=2, dash='dash')
    ))

    fig_line.add_trace(go.Scatter(
        x=df_trend['FECHA'],
        y=df_trend['PRIMERA_PCT'],
        mode='lines+markers+text',
        name='Calidad Real',
        text=df_trend['PRIMERA_PCT'].map('{:.2f}%'.format),
        textposition="top center",
        line=dict(color='#2563eb', width=3),
        marker=dict(
            size=9,
            color=np.where(df_trend['CUMPLE_META'], '#10b981', '#ef4444')
        )
    ))

    fig_line.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=25, b=10),
        xaxis_title=None,
        yaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚨 Principales Defectos Afectados (m²)</div>', unsafe_allow_html=True)
    
    df_top_def = df_def_f.groupby('DEFECTO')['MTS2'].sum().reset_index()
    df_top_def = df_top_def.sort_values('MTS2', ascending=True).tail(5)
    
    if not df_top_def.empty:
        fig_bar = px.bar(
            df_top_def, x='MTS2', y='DEFECTO', orientation='h',
            text=df_top_def['MTS2'].map('{:,.2f} m²'.format)
        )
        fig_bar.update_traces(marker_color='#ef4444', textposition='outside')
        fig_bar.update_layout(
            height=300, margin=dict(l=10, r=10, t=25, b=10),
            xaxis_title=None, yaxis_title=None,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No se registraron defectos para el período seleccionado.")
    st.markdown('</div>', unsafe_allow_html=True)

# DETALLE DEL ÚLTIMO DÍA Y MODELOS
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-title">📋 Registro Detallado de Defectos del Día ({ultimo_dia.strftime("%d/%m/%Y") if pd.notnull(ultimo_dia) else "N/A"})</div>', unsafe_allow_html=True)

if not df_def_ultimo_dia.empty:
    df_show_def = df_def_ultimo_dia[['DIA', 'MODELO', 'FORMATO', 'HORNO', 'DEFECTO', 'MTS2', 'RESPONSABLE', 'PCT_AREA']].copy()
    df_show_def['DIA'] = df_show_def['DIA'].dt.strftime('%d/%m/%Y')
    df_show_def['PCT_AREA'] = df_show_def['PCT_AREA'].apply(lambda x: f"{x*100:.2f}%" if x < 1 else f"{x:.2f}%")
    st.dataframe(df_show_def, use_container_width=True, hide_index=True)
else:
    st.info("No hay eventos de defectos registrados en la última fecha.")

st.markdown('</div>', unsafe_allow_html=True)

# TABLAS DE CONTROL DE MODELOS
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🧪 Control de Modelos Cerámicos</div>', unsafe_allow_html=True)
m1, m2 = st.columns(2)

with m1:
    st.markdown("##### MODELOS EN PRUEBA")
    st.dataframe(df_pruebas, use_container_width=True, hide_index=True)

with m2:
    st.markdown("##### MODELOS AUTORIZADOS")
    st.dataframe(df_autorizados, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)
