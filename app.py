import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="Dashboard - Control de Calidad",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; }
    .dashboard-header {
        background-color: #0f172a;
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .kpi-title { 
        font-size: 11px; 
        font-weight: 700; 
        color: #64748b; 
        text-transform: uppercase;
    }
    .kpi-value { 
        font-size: 20px; 
        font-weight: 800; 
        margin-top: 4px;
    }
    .val-green { color: #10b981; }
    .val-red { color: #ef4444; }
    .val-blue { color: #2563eb; }
    .val-amber { color: #f59e0b; }
    .val-purple { color: #8b5cf6; }

    .section-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 13px;
        font-weight: 700;
        color: #1e293b;
        text-transform: uppercase;
        margin-bottom: 12px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

ADMIN_PASSWORD = "admin123"

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'excel_bytes' not in st.session_state:
    st.session_state['excel_bytes'] = None

# Función auxiliar para encontrar filas de encabezado por nombre exacto
def read_table_by_header(df_raw, header_names):
    for r in range(len(df_raw)):
        row_vals = [str(val).strip().upper() for val in df_raw.iloc[r].values]
        if all(h in row_vals for h in header_names):
            col_indices = [row_vals.index(h) for h in header_names]
            df_sub = df_raw.iloc[r+1:, col_indices].copy()
            df_sub.columns = header_names
            return df_sub.dropna(subset=[header_names[0]])
    return pd.DataFrame(columns=header_names)

def parse_excel_data(file_bytes):
    xl = pd.ExcelFile(io.BytesIO(file_bytes))
    sheet_names = xl.sheet_names
    selected_sheet = next((s for s in sheet_names if "DASH" in s.strip().upper() or "CALIDAD" in s.strip().upper()), sheet_names[0])
    
    df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=selected_sheet, header=None)
    
    # 1. Calidad y Metros
    df_calidad = read_table_by_header(df_raw, ['FECHA', 'PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'CALIDAD META'])
    if not df_calidad.empty:
        df_calidad['FECHA'] = pd.to_datetime(df_calidad['FECHA'], errors='coerce')
        df_calidad = df_calidad.dropna(subset=['FECHA'])
        for col in ['PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2', 'CALIDAD META']:
            df_calidad[col] = pd.to_numeric(df_calidad[col], errors='coerce').fillna(0)
        if df_calidad['PRIMERA'].max() <= 1.0 and df_calidad['PRIMERA'].max() > 0:
            df_calidad['PRIMERA'] *= 100
        df_calidad['MES'] = df_calidad['FECHA'].dt.strftime('%B %Y').str.capitalize()

    # 2. Pallets
    df_pallets = read_table_by_header(df_raw, ['FECHA', 'PALLET DE 1RA', 'PALLET DE 2DA', 'PALLET DE 3RA', 'PALLET RECHAZADO', 'PRINCIPAL RECHAZO'])
    if not df_pallets.empty:
        df_pallets['FECHA'] = pd.to_datetime(df_pallets['FECHA'], errors='coerce')
        df_pallets = df_pallets.dropna(subset=['FECHA'])
        for col in ['PALLET DE 1RA', 'PALLET DE 2DA', 'PALLET DE 3RA', 'PALLET RECHAZADO']:
            df_pallets[col] = pd.to_numeric(df_pallets[col], errors='coerce').fillna(0)
        df_pallets['MES'] = df_pallets['FECHA'].dt.strftime('%B %Y').str.capitalize()

    # 3. Garantías
    df_garantias = read_table_by_header(df_raw, ['MES', 'CANTIDAD'])
    if not df_garantias.empty:
        df_garantias['CANTIDAD'] = pd.to_numeric(df_garantias['CANTIDAD'], errors='coerce').fillna(0)

    # 4. Modelos en Prueba y Autorizados
    df_pruebas = read_table_by_header(df_raw, ['MODELO', 'HORNO'])
    
    # 5. Defectos
    df_def = read_table_by_header(df_raw, ['FECHA', 'MODELO', 'FORMATO', 'HORNO', 'DEFECTO', 'MTS2', 'RESPONSABLE', 'PORCENTAJE DE DEFECTO DEL ÁREA'])
    if not df_def.empty:
        df_def['FECHA'] = pd.to_datetime(df_def['FECHA'], errors='coerce').dt.floor('D')
        df_def = df_def.dropna(subset=['FECHA', 'DEFECTO'])
        df_def['MTS2'] = pd.to_numeric(df_def['MTS2'], errors='coerce').fillna(0)
        df_def['PORCENTAJE DE DEFECTO DEL ÁREA'] = pd.to_numeric(df_def['PORCENTAJE DE DEFECTO DEL ÁREA'], errors='coerce').fillna(0)
        df_def['MES'] = df_def['FECHA'].dt.strftime('%B %Y').str.capitalize()

    # 6. Cumplimiento a Tono (Celdas AA:AF -> Columnas 26 a 31, Filas 2 a 13)
    cumplimiento_tono = 0.0
    try:
        df_tono = df_raw.iloc[1:13, 26:32].select_dtypes(include=[np.number])
        if not df_tono.empty:
            cumplimiento_tono = float(df_tono.mean().mean())
            if cumplimiento_tono <= 1.0 and cumplimiento_tono > 0:
                cumplimiento_tono *= 100
    except Exception:
        cumplimiento_tono = 0.0

    return df_calidad, df_pallets, df_garantias, df_pruebas, df_def, cumplimiento_tono

# Sidebar
with st.sidebar:
    st.markdown("### 🟢 CONTROL DE CALIDAD")
    if not st.session_state['logged_in']:
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if pwd == ADMIN_PASSWORD:
                st.session_state['logged_in'] = True
                st.rerun()
    else:
        st.success("Modo Admin Activo")
        uploaded_file = st.file_uploader("Subir Archivo Excel", type=["xlsx", "xls"])
        if uploaded_file is not None:
            st.session_state['excel_bytes'] = uploaded_file.getvalue()
            st.success("Cargado correctamente")
            
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.rerun()

if st.session_state['excel_bytes'] is None:
    st.warning("⚠️ Sube tu archivo Excel desde la barra lateral para visualizar el dashboard.")
    st.stop()

try:
    df_calidad, df_pallets, df_garantias, df_pruebas, df_def, cumplimiento_tono = parse_excel_data(st.session_state['excel_bytes'])
except Exception as e:
    st.error(f"Error procesando el Excel: {e}")
    st.stop()

# Filtros
meses_opciones = ["Todos los Meses"] + list(df_calidad['MES'].unique()) if not df_calidad.empty else ["Todos los Meses"]
mes_seleccionado = st.sidebar.selectbox("🗓️ Seleccionar Mes:", options=meses_opciones)
meta_calidad = st.sidebar.number_input("🎯 Meta Calidad (%):", value=94.50, step=0.5)

# Filtrado por mes
df_calidad_f = df_calidad[df_calidad['MES'] == mes_seleccionado].copy() if mes_seleccionado != "Todos los Meses" else df_calidad.copy()
df_pallets_f = df_pallets[df_pallets['MES'] == mes_seleccionado].copy() if mes_seleccionado != "Todos los Meses" else df_pallets.copy()
df_def_f = df_def[df_def['MES'] == mes_seleccionado].copy() if mes_seleccionado != "Todos los Meses" else df_def.copy()

# Último día registrado
ultimo_dia = df_calidad_f['FECHA'].max() if not df_calidad_f.empty else None
df_ultimo_dia = df_calidad_f[df_calidad_f['FECHA'] == ultimo_dia] if ultimo_dia else pd.DataFrame()
df_pallets_ultimo = df_pallets_f[df_pallets_f['FECHA'] == ultimo_dia] if ultimo_dia else pd.DataFrame()
df_def_ultimo = df_def_f[df_def_f['FECHA'] == ultimo_dia] if ultimo_dia else pd.DataFrame()

# Métricas Calculadas
calidad_dia = df_ultimo_dia['PRIMERA'].values[0] if not df_ultimo_dia.empty else 0.0
calidad_acum = df_calidad_f['PRIMERA'].mean() if not df_calidad_f.empty else 0.0

mts2_def_dia = df_def_ultimo['MTS2'].sum() if not df_def_ultimo.empty else 0.0
mts2_def_acum = df_def_f['MTS2'].sum() if not df_def_f.empty else 0.0

# Pallets (Suma real de columnas indicadas)
pallets_1ra_dia = int(df_pallets_ultimo['PALLET DE 1RA'].sum()) if not df_pallets_ultimo.empty else 0
pallets_1ra_acum = int(df_pallets_f['PALLET DE 1RA'].sum()) if not df_pallets_f.empty else 0

pallets_rech_dia = int(df_pallets_ultimo['PALLET RECHAZADO'].sum()) if not df_pallets_ultimo.empty else 0
pallets_rech_acum = int(df_pallets_f['PALLET RECHAZADO'].sum()) if not df_pallets_f.empty else 0

garantias_total = int(df_garantias['CANTIDAD'].sum()) if not df_garantias.empty else 0

# Visualización Header
st.markdown(f"""
<div class="dashboard-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h3 style="margin:0;">PRODUCTO TERMINADO - PISO CERÁMICO</h3>
            <p style="margin:0; font-size:12px; color:#94a3b8;">Monitoreo Operativo de Calidad</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size:12px; color:#94a3b8;">Último Día:</span><br>
            <span style="font-size:14px; color:#10b981; font-weight:bold;">{ultimo_dia.strftime('%d/%m/%Y') if pd.notnull(ultimo_dia) else 'N/A'}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tarjetas KPI Fila 1
c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Día</div><div class="kpi-value val-green">{calidad_dia:.2f}%</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Acum</div><div class="kpi-value val-green">{calidad_acum:.2f}%</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><div class="kpi-title">Defectos Día</div><div class="kpi-value val-red">{mts2_def_dia:,.2f} m²</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Defectos Acum</div><div class="kpi-value val-red">{mts2_def_acum:,.2f} m²</div></div>', unsafe_allow_html=True)
c5.markdown(f'<div class="kpi-card"><div class="kpi-title">Cumplimiento Tono</div><div class="kpi-value val-blue">{cumplimiento_tono:.1f}%</div></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# Tarjetas KPI Fila 2 (Pallets corregidos y Garantías)
p1, p2, p3, p4, p5 = st.columns(5)
p1.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets 1ra Día</div><div class="kpi-value val-amber">{pallets_1ra_dia:,}</div></div>', unsafe_allow_html=True)
p2.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets 1ra Acum</div><div class="kpi-value val-amber">{pallets_1ra_acum:,}</div></div>', unsafe_allow_html=True)
p3.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Rech. Día</div><div class="kpi-value val-red">{pallets_rech_dia:,}</div></div>', unsafe_allow_html=True)
p4.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Rech. Acum</div><div class="kpi-value val-red">{pallets_rech_acum:,}</div></div>', unsafe_allow_html=True)
p5.markdown(f'<div class="kpi-card"><div class="kpi-title">Garantías Total</div><div class="kpi-value val-purple">{garantias_total:,}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gráficas
g1, g2 = st.columns(2)

with g1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚨 Principales Defectos Afectados (m²)</div>', unsafe_allow_html=True)
    if not df_def_f.empty:
        df_top_def = df_def_f.groupby('DEFECTO')['MTS2'].sum().reset_index().sort_values('MTS2', ascending=True).tail(5)
        fig_bar = px.bar(df_top_def, x='MTS2', y='DEFECTO', orientation='h', text_auto='.2f')
        fig_bar.update_traces(marker_color='#ef4444')
        fig_bar.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sin registros de defectos.")
    st.markdown('</div>', unsafe_allow_html=True)

with g2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 % Afectación por Responsable del Defecto</div>', unsafe_allow_html=True)
    if not df_def_f.empty and 'RESPONSABLE' in df_def_f.columns:
        df_resp = df_def_f.groupby('RESPONSABLE')['PORCENTAJE DE DEFECTO DEL ÁREA'].mean().reset_index()
        fig_pie = px.pie(df_resp, values='PORCENTAJE DE DEFECTO DEL ÁREA', names='RESPONSABLE', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Sin datos de responsables o porcentajes.")
    st.markdown('</div>', unsafe_allow_html=True)
