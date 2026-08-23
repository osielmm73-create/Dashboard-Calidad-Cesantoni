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

def extract_column_by_keyword(df_raw, keywords):
    for r in range(len(df_raw)):
        for c in range(len(df_raw.columns)):
            val = str(df_raw.iloc[r, c]).strip().upper()
            if any(kw.upper() == val or kw.upper() in val for kw in keywords):
                col_data = df_raw.iloc[r+1:, c].values
                return pd.Series(col_data)
    return pd.Series(dtype=object)

def parse_excel_data(file_bytes):
    xl = pd.ExcelFile(io.BytesIO(file_bytes))
    sheet_names = xl.sheet_names
    selected_sheet = next((s for s in sheet_names if "DASH" in s.strip().upper() or "CALIDAD" in s.strip().upper()), sheet_names[0])
    
    df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=selected_sheet, header=None)
    
    # 1. Calidad y Metros
    fechas = extract_column_by_keyword(df_raw, ['FECHA'])
    primera = extract_column_by_keyword(df_raw, ['PRIMERA'])
    segunda = extract_column_by_keyword(df_raw, ['SEGUNDA'])
    tercera = extract_column_by_keyword(df_raw, ['TERCERA'])
    quinta = extract_column_by_keyword(df_raw, ['QUINTA'])
    mts2 = extract_column_by_keyword(df_raw, ['MTS2'])
    calidad_meta = extract_column_by_keyword(df_raw, ['CALIDAD META'])
    
    df_calidad = pd.DataFrame()
    if not fechas.empty:
        max_len = len(fechas)
        df_calidad['FECHA'] = pd.to_datetime(fechas.iloc[:max_len], errors='coerce')
        df_calidad['PRIMERA'] = pd.to_numeric(primera.iloc[:max_len], errors='coerce').fillna(0) if not primera.empty else 0
        df_calidad['SEGUNDA'] = pd.to_numeric(segunda.iloc[:max_len], errors='coerce').fillna(0) if not segunda.empty else 0
        df_calidad['TERCERA'] = pd.to_numeric(tercera.iloc[:max_len], errors='coerce').fillna(0) if not tercera.empty else 0
        df_calidad['QUINTA'] = pd.to_numeric(quinta.iloc[:max_len], errors='coerce').fillna(0) if not quinta.empty else 0
        df_calidad['MTS2'] = pd.to_numeric(mts2.iloc[:max_len], errors='coerce').fillna(0) if not mts2.empty else 0
        df_calidad['CALIDAD META'] = pd.to_numeric(calidad_meta.iloc[:max_len], errors='coerce').fillna(94.5) if not calidad_meta.empty else 94.5
        
        df_calidad = df_calidad.dropna(subset=['FECHA'])
        if df_calidad['PRIMERA'].max() <= 1.0 and df_calidad['PRIMERA'].max() > 0:
            df_calidad['PRIMERA'] *= 100
        df_calidad['MES'] = df_calidad['FECHA'].dt.strftime('%B %Y').str.capitalize()

    # 2. Pallets
    p_fechas = extract_column_by_keyword(df_raw, ['FECHA'])
    p_1ra = extract_column_by_keyword(df_raw, ['PALLET DE 1RA'])
    p_2da = extract_column_by_keyword(df_raw, ['PALLET DE 2DA'])
    p_3ra = extract_column_by_keyword(df_raw, ['PALLET DE 3RA'])
    p_rech = extract_column_by_keyword(df_raw, ['PALLET RECHAZADO'])
    
    df_pallets = pd.DataFrame()
    if not p_fechas.empty:
        max_len = len(p_fechas)
        df_pallets['FECHA'] = pd.to_datetime(p_fechas.iloc[:max_len], errors='coerce')
        df_pallets['PALLET DE 1RA'] = pd.to_numeric(p_1ra.iloc[:max_len], errors='coerce').fillna(0) if not p_1ra.empty else 0
        df_pallets['PALLET DE 2DA'] = pd.to_numeric(p_2da.iloc[:max_len], errors='coerce').fillna(0) if not p_2da.empty else 0
        df_pallets['PALLET DE 3RA'] = pd.to_numeric(p_3ra.iloc[:max_len], errors='coerce').fillna(0) if not p_3ra.empty else 0
        df_pallets['PALLET RECHAZADO'] = pd.to_numeric(p_rech.iloc[:max_len], errors='coerce').fillna(0) if not p_rech.empty else 0
        
        df_pallets = df_pallets.dropna(subset=['FECHA'])
        df_pallets['MES'] = df_pallets['FECHA'].dt.strftime('%B %Y').str.capitalize()

    # 3. Garantías (Lectura estricta de la columna CANTIDAD de garantías)
    g_cant = extract_column_by_keyword(df_raw, ['CANTIDAD'])
    df_garantias = pd.DataFrame()
    if not g_cant.empty:
        # Filtramos solo valores numéricos válidos y cortamos antes de basura vacía
        vals = pd.to_numeric(g_cant, errors='coerce').dropna()
        df_garantias['CANTIDAD'] = vals[vals > 0]

    # 4. Defectos que influyen en calidad
    d_fecha = extract_column_by_keyword(df_raw, ['FECHA'])
    d_def = extract_column_by_keyword(df_raw, ['DEFECTO'])
    d_mts2 = extract_column_by_keyword(df_raw, ['MTS2'])
    d_resp = extract_column_by_keyword(df_raw, ['RESPONSABLE'])
    d_pct = extract_column_by_keyword(df_raw, ['PORCENTAJE DE DEFECTO DEL ÁREA'])
    
    df_def = pd.DataFrame()
    if not d_def.empty:
        max_len = len(d_def)
        df_def['FECHA'] = pd.to_datetime(d_fecha.iloc[:max_len], errors='coerce').dt.floor('D') if not d_fecha.empty else pd.NaT
        df_def['DEFECTO'] = d_def.iloc[:max_len].astype(str).str.strip()
        df_def['MTS2'] = pd.to_numeric(d_mts2.iloc[:max_len], errors='coerce').fillna(0) if not d_mts2.empty else 0
        df_def['RESPONSABLE'] = d_resp.iloc[:max_len].astype(str).str.strip().fillna("SIN ASIGNAR") if not d_resp.empty else "SIN ASIGNAR"
        df_def['PORCENTAJE'] = pd.to_numeric(d_pct.iloc[:max_len], errors='coerce').fillna(0) if not d_pct.empty else 0
        
        df_def = df_def.dropna(subset=['DEFECTO'])
        df_def = df_def[(df_def['DEFECTO'] != 'nan') & (df_def['DEFECTO'] != '')]
        df_def['MES'] = df_def['FECHA'].dt.strftime('%B %Y').str.capitalize()

    # 5. Cumplimiento a Tono
    t_fecha = extract_column_by_keyword(df_raw, ['FECHA'])
    t_acum = extract_column_by_keyword(df_raw, ['%CUMPLIMIENTO A TONO ACUMULADO'])
    
    df_tono = pd.DataFrame()
    if not t_acum.empty:
        max_len = len(t_acum)
        df_tono['FECHA'] = pd.to_datetime(t_fecha.iloc[:max_len], errors='coerce').dt.floor('D') if not t_fecha.empty else pd.NaT
        df_tono['ACUMULADO'] = pd.to_numeric(t_acum.iloc[:max_len], errors='coerce').fillna(0)
        if df_tono['ACUMULADO'].max() <= 1.0 and df_tono['ACUMULADO'].max() > 0:
            df_tono['ACUMULADO'] *= 100
        df_tono['MES'] = df_tono['FECHA'].dt.strftime('%B %Y').str.capitalize()

    return df_calidad, df_pallets, df_garantias, df_def, df_tono

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
    df_calidad, df_pallets, df_garantias, df_def, df_tono = parse_excel_data(st.session_state['excel_bytes'])
except Exception as e:
    st.error(f"Error procesando el Excel: {e}")
    st.stop()

# Filtros
meses_opciones = ["Todos los Meses"] + list(df_calidad['MES'].unique()) if not df_calidad.empty else ["Todos los Meses"]
mes_seleccionado = st.sidebar.selectbox("🗓️ Seleccionar Mes:", options=meses_opciones)
meta_calidad = st.sidebar.number_input("🎯 Meta Calidad (%):", value=94.50, step=0.5)

# Filtrado
df_calidad_f = df_calidad[df_calidad['MES'] == mes_seleccionado].copy() if mes_seleccionado != "Todos los Meses" else df_calidad.copy()
df_pallets_f = df_pallets[df_pallets['MES'] == mes_seleccionado].copy() if mes_seleccionado != "Todos los Meses" else df_pallets.copy()
df_def_f = df_def[df_def['MES'] == mes_seleccionado].copy() if mes_seleccionado != "Todos los Meses" else df_def.copy()
df_tono_f = df_tono[df_tono['MES'] == mes_seleccionado].copy() if not df_tono.empty and mes_seleccionado != "Todos los Meses" else df_tono.copy()

# Último día registrado
ultimo_dia = df_calidad_f['FECHA'].max() if not df_calidad_f.empty else None
df_ultimo_dia = df_calidad_f[df_calidad_f['FECHA'] == ultimo_dia] if ultimo_dia else pd.DataFrame()
df_pallets_ultimo = df_pallets_f[df_pallets_f['FECHA'] == ultimo_dia] if ultimo_dia else pd.DataFrame()
df_def_ultimo = df_def_f[df_def_f['FECHA'] == ultimo_dia] if ultimo_dia else pd.DataFrame()
df_tono_ultimo = df_tono_f[df_tono_f['FECHA'] == ultimo_dia] if ultimo_dia and not df_tono_f.empty else pd.DataFrame()

# Métricas Calculadas
calidad_dia = df_ultimo_dia['PRIMERA'].values[0] if not df_ultimo_dia.empty else 0.0
calidad_acum = df_calidad_f['PRIMERA'].mean() if not df_calidad_f.empty else 0.0

mts2_def_dia = df_def_ultimo['MTS2'].sum() if not df_def_ultimo.empty else 0.0
mts2_def_acum = df_def_f['MTS2'].sum() if not df_def_f.empty else 0.0

cumplimiento_tono = df_tono_ultimo['ACUMULADO'].values[0] if not df_tono_ultimo.empty and df_tono_ultimo['ACUMULADO'].values[0] > 0 else (df_tono_f['ACUMULADO'].mean() if not df_tono_f.empty else 0.0)

pallets_total_dia = int(df_pallets_ultimo[['PALLET DE 1RA', 'PALLET DE 2DA', 'PALLET DE 3RA']].sum().sum()) if not df_pallets_ultimo.empty else 0
pallets_total_acum = int(df_pallets_f[['PALLET DE 1RA', 'PALLET DE 2DA', 'PALLET DE 3RA']].sum().sum()) if not df_pallets_f.empty else 0

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

# Tarjetas KPI Fila 2
p1, p2, p3, p4, p5 = st.columns(5)
p1.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Totales Día</div><div class="kpi-value val-amber">{pallets_total_dia:,}</div></div>', unsafe_allow_html=True)
p2.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Totales Acum</div><div class="kpi-value val-amber">{pallets_total_acum:,}</div></div>', unsafe_allow_html=True)
p3.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Rech. Día</div><div class="kpi-value val-red">{pallets_rech_dia:,}</div></div>', unsafe_allow_html=True)
p4.markdown(f'<div class="kpi-card"><div class="kpi-title">Pallets Rech. Acum</div><div class="kpi-value val-red">{pallets_rech_acum:,}</div></div>', unsafe_allow_html=True)
p5.markdown(f'<div class="kpi-card"><div class="kpi-title">Garantías Total</div><div class="kpi-value val-purple">{garantias_total:,}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gráfica 1: Comportamiento Diario de Calidad
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📈 Comportamiento Diario de Calidad (Primera %) vs Meta</div>', unsafe_allow_html=True)
if not df_calidad_f.empty:
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_calidad_f['FECHA'], y=df_calidad_f['PRIMERA'], mode='lines+markers', name='Calidad 1ra (%)', line=dict(color='#10b981', width=3)))
    fig_line.add_trace(go.Scatter(x=df_calidad_f['FECHA'], y=df_calidad_f['CALIDAD META'], mode='lines', name='Meta', line=dict(color='#ef4444', width=2, dash='dash')))
    fig_line.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None, yaxis_title=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Sin datos de calidad para mostrar.")
st.markdown('</div>', unsafe_allow_html=True)

# Gráficas de Defectos y Responsables
g1, g2 = st.columns(2)

with g1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚨 Principales Defectos Afectados (m²)</div>', unsafe_allow_html=True)
    if not df_def_f.empty and 'DEFECTO' in df_def_f.columns:
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
        df_resp = df_def_f.groupby('RESPONSABLE')['PORCENTAJE'].sum().reset_index()
        fig_pie = px.pie(df_resp, values='PORCENTAJE', names='RESPONSABLE', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Sin datos de responsables o porcentajes.")
    st.markdown('</div>', unsafe_allow_html=True)
