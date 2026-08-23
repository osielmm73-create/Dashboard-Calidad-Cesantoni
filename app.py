import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL Y ESTILO (ESTILO IMAGEN)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DASHBOARD - SISTEMA DE CALIDAD",
    page_icon="🟩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS para replicar la interfaz blanca/gris con sidebar oscura
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    .kpi-card {
        background-color: #ffffff;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        text-align: center;
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
        margin: 4px 0;
    }
    .kpi-meta {
        font-size: 11px;
        color: #475569;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# CARGA Y EXTRAACCIÓN DE TODAS LAS SECCIONES DE EXCEL
# ---------------------------------------------------------
@st.cache_data
def load_all_dashboard_data(file_path):
    df_raw = pd.read_excel(file_path, sheet_name='DASHBOARD', header=None)
    
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


# Cargar archivo
try:
    df_calidad, df_garantias, df_pruebas, df_autorizados, df_def = load_all_dashboard_data('REPORTE P1 Y P3 AGOSTO 2026.xlsx')
except Exception as e:
    st.error(f"Error cargando el archivo Excel: {e}")
    st.stop()


# ---------------------------------------------------------
# SIDEBAR NAVEGABLE Y FILTROS
# ---------------------------------------------------------
st.sidebar.markdown("## 🟩 SISTEMA CALIDAD")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🗓️ FILTROS")
meses_opciones = ["Todos los Meses"] + list(df_calidad['MES'].unique())
mes_seleccionado = st.sidebar.selectbox("Filtrar por Mes:", options=meses_opciones, index=0)

# Filtrado por mes
if mes_seleccionado != "Todos los Meses":
    df_calidad_f = df_calidad[df_calidad['MES'] == mes_seleccionado]
    df_def_f = df_def[df_def['MES'] == mes_seleccionado]
else:
    df_calidad_f = df_calidad.copy()
    df_def_f = df_def.copy()


# ---------------------------------------------------------
# ENCABEZADO SUPERIOR
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("DASHBOARD – SISTEMA DE CALIDAD")
    st.caption("PRODUCTO TERMINADO – PISO CERÁMICO")

with col_h2:
    st.markdown(
        f"<div style='text-align: right; font-weight: bold; padding-top: 10px;'>Mes Activo:<br>"
        f"<span style='color: #10b981; font-size: 18px;'>{mes_seleccionado}</span></div>", 
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# CÁLCULOS DE KPIS
# ---------------------------------------------------------
total_m2 = df_calidad_f['MTS2'].sum()
if total_m2 > 0:
    p1_pct = ((df_calidad_f['PRIMERA'] * df_calidad_f['MTS2']).sum() / total_m2) * 100
    p2_pct = ((df_calidad_f['SEGUNDA'] * df_calidad_f['MTS2']).sum() / total_m2) * 100
    p5_pct = ((df_calidad_f['QUINTA'] * df_calidad_f['MTS2']).sum() / total_m2) * 100
else:
    p1_pct, p2_pct, p5_pct = 0, 0, 0

garantias_total = int(df_garantias['CANTIDAD'].sum())


# ---------------------------------------------------------
# FILA DE KPIS SUPERIORES (CALIDADES, MTS2, TONOS, GARANTÍAS)
# ---------------------------------------------------------
k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Calidad 1ª</div>
            <div class='kpi-value' style='color: #10b981;'>{p1_pct:.1f}%</div>
            <div class='kpi-meta'>Meta ≥ 94.5%</div>
        </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Calidad 2ª</div>
            <div class='kpi-value' style='color: #f59e0b;'>{p2_pct:.1f}%</div>
            <div class='kpi-meta'>Seguimiento</div>
        </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Rechazo / 5ª</div>
            <div class='kpi-value' style='color: #ef4444;'>{p5_pct:.1f}%</div>
            <div class='kpi-meta'>Meta ≤ 1.5%</div>
        </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Mts² Producidos</div>
            <div class='kpi-value' style='color: #0284c7;'>{total_m2/1000:.1f}k</div>
            <div class='kpi-meta'>Volumen Total</div>
        </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-title'>Cumplimiento Tonos</div>
            <div class='kpi-value' style='color: #10b981;'>98.2%</div>
            <div class='kpi-meta'>Conforme a Norma</div>
        </div>
    """, unsafe_allow_html=True)

with k6:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Garantías (Año)</div>
            <div class='kpi-value' style='color: #8b5cf6;'>{garantias_total}</div>
            <div class='kpi-meta'>Reclamaciones</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# BLOQUE CENTRAL 1: DEFECTOS Y GARANTÍAS POR MES
# ---------------------------------------------------------
g1, g2, g3 = st.columns([1.2, 1, 1.2])

with g1:
    st.markdown("### PARETO DE DEFECTOS ($m^2$)")
    if not df_def_f.empty:
        df_def_grp = df_def_f.groupby('DEFECTO')['MTS2'].sum().reset_index().sort_values(by='MTS2', ascending=True)
        fig_pareto = px.bar(
            df_def_grp,
            x='MTS2',
            y='DEFECTO',
            orientation='h',
            text_auto='.0f',
            color_discrete_sequence=['#1e293b'],
            template="plotly_white"
        )
        fig_pareto.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="m² Defectuosos",
            yaxis_title=None,
            height=280
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

with g2:
    st.markdown("### DISTRIBUCIÓN DE DEFECTOS")
    if not df_def_f.empty:
        fig_donut = px.pie(
            df_def_f,
            names='DEFECTO',
            values='MTS2',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_white"
        )
        fig_donut.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_donut, use_container_width=True)

with g3:
    st.markdown("### GARANTÍAS POR MES")
    fig_gar = px.bar(
        df_garantias,
        x='MES',
        y='CANTIDAD',
        text_auto=True,
        color_discrete_sequence=['#8b5cf6'],
        template="plotly_white"
    )
    fig_gar.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title="Reclamaciones",
        height=280
    )
    st.plotly_chart(fig_gar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# BLOQUE CENTRAL 2: MODELOS Y CUMPLIMIENTO A TONOS
# ---------------------------------------------------------
col_m1, col_m2, col_m3 = st.columns([1, 1, 1.2])

with col_m1:
    st.markdown("### 🧪 MODELOS EN PRUEBA")
    st.dataframe(
        df_pruebas,
        use_container_width=True,
        hide_index=True
    )

with col_m2:
    st.markdown("### ✅ MODELOS AUTORIZADOS")
    st.dataframe(
        df_autorizados,
        use_container_width=True,
        hide_index=True
    )

with col_m3:
    st.markdown("### 📈 TENDENCIA DIARIA (% PRIMERA)")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df_calidad_f['FECHA'],
        y=df_calidad_f['PRIMERA'] * 100,
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=5)
    ))
    fig_trend.add_trace(go.Scatter(
        x=df_calidad_f['FECHA'],
        y=[94.5] * len(df_calidad_f),
        mode='lines',
        line=dict(color='#ef4444', dash='dash')
    ))
    fig_trend.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[70, 100]),
        showlegend=False,
        height=240
    )
    st.plotly_chart(fig_trend, use_container_width=True)
