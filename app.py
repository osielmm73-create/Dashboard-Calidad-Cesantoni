import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard - Sistema de Calidad",
    page_icon="🟩",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Fondo General */
    .main { background-color: #0F172A; color: #F8FAFC; font-family: 'Segoe UI', Roboto, sans-serif; }
    .block-container { padding: 1.5rem 2rem 2rem 2rem; }

    /* BARRA LATERAL */
    [data-testid="stSidebar"] { 
        background-color: #1E293B !important; 
        border-right: 1px solid #334155; 
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #E2E8F0 !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Header del Dashboard */
    .dashboard-header { 
        background: linear-gradient(90deg, #1E293B 0%, #0F172A 100%); 
        padding: 20px 24px; 
        border-radius: 12px; 
        border-left: 6px solid #10B981; 
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .header-title { font-size: 26px; font-weight: 800; color: #FFFFFF; margin: 0; }
    .header-subtitle { font-size: 13px; color: #94A3B8; margin-top: 4px; }

    /* Tarjetas KPI Generales */
    .kpi-section-title {
        font-size: 12px;
        font-weight: 800;
        color: #38BDF8;
        text-transform: uppercase;
        margin-top: 14px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }

    .kpi-card { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        border-radius: 10px; 
        padding: 18px 16px; 
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value { font-size: 28px; font-weight: 800; margin-bottom: 2px; }
    .kpi-subtext { font-size: 11px; color: #64748B; }

    /* Cajas de Gráficos y Tablas */
    .section-box { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px;
    }
    .section-title { font-size: 14px; font-weight: 700; color: #F1F5F9; margin-bottom: 16px; text-transform: uppercase; }

    /* TARJETAS KPI ILUSTRADAS ESTILO CUADRÍCULA (ÁREAS RESPONSABLES) */
    .grid-kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 16px 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
    }
    .grid-kpi-title {
        font-size: 11px;
        font-weight: 800;
        color: #1E293B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .grid-kpi-icon {
        font-size: 34px;
        margin: 6px 0;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 48px;
    }
    .grid-kpi-footer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin-top: 6px;
    }
    .grid-kpi-val {
        font-size: 18px;
        font-weight: 800;
    }
    .dot-green { color: #22C55E; font-size: 14px; }
    .dot-yellow { color: #F59E0B; font-size: 14px; }
    .dot-red { color: #EF4444; font-size: 14px; }

    /* Estilo de Tablas Integradas */
    div[data-testid="stDataFrame"] {
        background-color: #0F172A;
        border-radius: 8px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PROCESAMIENTO Y CACHÉ PERSISTENTE DE DATOS EXCEL
# -----------------------------------------------------------------------------
ADMIN_USER = "admin"
ADMIN_PASSWORD = "calidad2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def process_excel(file_source):
    xls = pd.ExcelFile(file_source)
    sheet_name = 'DASHBOARD' if 'DASHBOARD' in xls.sheet_names else xls.sheet_names[0]
    df_raw = pd.read_excel(xls, sheet_name=sheet_name)

    # 1. Tabla Anual (Cols A:D)
    t1 = df_raw.iloc[:, 0:4].copy()
    t1.columns = ['MES', 'P1_ANUAL', 'P3_ANUAL', 'P1_P3_ANUAL']
    t1['P1_ANUAL'] = pd.to_numeric(t1['P1_ANUAL'], errors='coerce')
    t1['P3_ANUAL'] = pd.to_numeric(t1['P3_ANUAL'], errors='coerce')
    t1['P1_P3_ANUAL'] = pd.to_numeric(t1['P1_P3_ANUAL'], errors='coerce')
    
    total_gen_row = t1[t1['MES'].astype(str).str.contains("Total general", case=False, na=False)]
    t1_meses = t1[~t1['MES'].astype(str).str.contains("Total general", case=False, na=False)].dropna(subset=['P1_P3_ANUAL'])

    # 2. Tabla Diaria / Mensual (Cols F:J)
    t2 = df_raw.iloc[:, 5:10].copy()
    t2.columns = ['DIA', 'P1_DIARIA', 'P3_DIARIA', 'P1_P3_DIARIA', 'MTS2_DIA']
    t2['P1_DIARIA'] = pd.to_numeric(t2['P1_DIARIA'], errors='coerce')
    t2['P3_DIARIA'] = pd.to_numeric(t2['P3_DIARIA'], errors='coerce')
    t2['P1_P3_DIARIA'] = pd.to_numeric(t2['P1_P3_DIARIA'], errors='coerce')
    t2['MTS2_DIA'] = pd.to_numeric(t2['MTS2_DIA'], errors='coerce')
    
    resumen_mensual_row = t2[t2['DIA'].astype(str).str.contains("Total|Mensual|Promedio", case=False, na=False)]
    t2_dias = t2[~t2['DIA'].astype(str).str.contains("Total|Mensual|Promedio", case=False, na=False)].dropna(subset=['P1_P3_DIARIA'])

    # 3. Otras Tablas
    t3 = df_raw.iloc[:, 11:13].dropna(how='all'); t3.columns = ['MES_GARANTIAS', 'GARANTIAS']
    
    # Tabla 4: Modelos de Prueba en Horno (Cols O:P)
    t4 = df_raw.iloc[:, 14:16].dropna(how='all')
    t4.columns = ['MODELO_PRUEBA', 'HORNO_PRUEBAS']
    t4 = t4.dropna(subset=['MODELO_PRUEBA'])

    # Tabla 5: Modelos Autorizados (Cols R:S)
    t5 = df_raw.iloc[:, 17:19].dropna(how='all')
    t5.columns = ['MODELOS_AUTORIZADOS', 'HORNO_AUTORIZADOS']
    t5 = t5.dropna(subset=['MODELOS_AUTORIZADOS'])

    # Tabla 6: Cumplimiento de Tono (Cols U:X)
    t6 = df_raw.iloc[:, 20:24].dropna(how='all')
    t6.columns = ['FECHA', 'CUMP_P1', 'CUMP_P3', 'CUMP_ACUMULADO']
    t6['CUMP_P1'] = pd.to_numeric(t6['CUMP_P1'], errors='coerce')
    t6['CUMP_P3'] = pd.to_numeric(t6['CUMP_P3'], errors='coerce')
    t6['CUMP_ACUMULADO'] = pd.to_numeric(t6['CUMP_ACUMULADO'], errors='coerce')
    t6_clean = t6.dropna(subset=['FECHA']).copy()

    t7 = df_raw.iloc[:, 25:27].dropna(how='all'); t7.columns = ['DEFECTO', 'PORC_DEFECTO']
    t8 = df_raw.iloc[:, 28:30].dropna(how='all'); t8.columns = ['DEFECTO_P1', 'PORC_DEFECTO_P1']
    t9 = df_raw.iloc[:, 31:33].dropna(how='all'); t9.columns = ['DEFECTO_P3', 'PORC_DEFECTO_P3']
    t10 = df_raw.iloc[:, 34:36].dropna(how='all'); t10.columns = ['AREA_RESPONSABLE', 'PORC_AREA']

    # 4. Tabla 11: Calidad por Horno (Cols AL:AP)
    t11 = df_raw.iloc[:, 37:42].copy()
    t11.columns = ['DIA_HORNO', 'H1', 'H4', 'H5', 'H6']
    t11['H1'] = pd.to_numeric(t11['H1'], errors='coerce')
    t11['H4'] = pd.to_numeric(t11['H4'], errors='coerce')
    t11['H5'] = pd.to_numeric(t11['H5'], errors='coerce')
    t11['H6'] = pd.to_numeric(t11['H6'], errors='coerce')
    t11_clean = t11.dropna(subset=['H1', 'H4', 'H5', 'H6'], how='all')

    return (t1_meses, total_gen_row, t2_dias, resumen_mensual_row, t3, t4, t5, t6_clean, t7, t8, t9, t10, t11_clean)

@st.cache_data(show_spinner=False)
def load_and_process(file_bytes):
    return process_excel(io.BytesIO(file_bytes))

def fmt_pct(val):
    if pd.isna(val) or val is None:
        return "0.00%"
    return f"{val * 100:.2f}%" if val <= 1.0 else f"{val:.2f}%"

def fmt_num(val):
    if pd.isna(val) or val is None:
        return "0.00"
    return f"{val:,.2f}"

# -----------------------------------------------------------------------------
# 3. PANEL LATERAL DE NAVEGACIÓN
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🟩 **SISTEMA DE CALIDAD**")
    st.caption("PISO CERÁMICO P1 & P3")
    st.markdown("---")
    
    menu = st.radio("NAVEGACIÓN", ["CALIDAD", "DEFECTIVOS", "TONOS", "GARANTÍAS"])
    st.markdown("---")
    
    planta_sel = st.selectbox("Seleccionar Planta / Línea", ["Todas (P1 & P3)", "Planta 1 (P1)", "Planta 3 (P3)"])
    st.markdown("---")
    
    st.markdown("### 🔒 **Gestión de Archivo**")
    
    if not st.session_state.authenticated:
        with st.expander("🔑 Iniciar Sesión Admin"):
            u_in = st.text_input("Usuario")
            p_in = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", type="primary"):
                if u_in == ADMIN_USER and p_in == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credenciales erróneas")
    else:
        st.success("🟢 Sesión Admin Activa")
        uploaded_file = st.file_uploader("Cargar Reporte Excel", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            st.session_state["stored_file"] = uploaded_file.getvalue()

        if "stored_file" in st.session_state:
            try:
                st.session_state.tables = load_and_process(st.session_state["stored_file"])
                st.session_state.data_loaded = True
            except Exception as err:
                st.error(f"Error al procesar el archivo: {err}")
        
        if st.session_state.get("data_loaded", False):
            if st.button("🗑️ Resetear Datos Cargados"):
                if "stored_file" in st.session_state:
                    del st.session_state["stored_file"]
                st.session_state.data_loaded = False
                st.session_state.tables = None
                st.cache_data.clear()
                st.rerun()
                
        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()

# -----------------------------------------------------------------------------
# 4. DASHBOARD PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="dashboard-header">
    <div class="header-title">DASHBOARD - SISTEMA DE CALIDAD</div>
    <div class="header-subtitle">MONITORIZACIÓN Y CONTROL DE PRODUCCIÓN CERÁMICA</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("data_loaded", False):
    st.info("ℹ️ **Por favor, ingresa tu reporte en Excel desde el panel lateral para visualizar el dashboard.**")
    st.stop()

t1_meses, total_gen_row, t2_dias, resumen_mensual_row, t3, t4, t5, t6, t7, t8, t9, t10, t11 = st.session_state.tables

# =============================================================================
# HOJA 1: CALIDAD
# =============================================================================
if menu == "CALIDAD":

    # --- DATOS KPI ---
    if not total_gen_row.empty:
        v_anual_ac = total_gen_row['P1_P3_ANUAL'].values[0]
        v_anual_p1 = total_gen_row['P1_ANUAL'].values[0]
        v_anual_p3 = total_gen_row['P3_ANUAL'].values[0]
    else:
        v_anual_ac = t1_meses['P1_P3_ANUAL'].iloc[-1] if not t1_meses.empty else 0
        v_anual_p1 = t1_meses['P1_ANUAL'].iloc[-1] if not t1_meses.empty else 0
        v_anual_p3 = t1_meses['P3_ANUAL'].iloc[-1] if not t1_meses.empty else 0

    if not resumen_mensual_row.empty:
        v_mensual_ac = resumen_mensual_row['P1_P3_DIARIA'].values[0]
        v_mensual_p1 = resumen_mensual_row['P1_DIARIA'].values[0]
        v_mensual_p3 = resumen_mensual_row['P3_DIARIA'].values[0]
    else:
        v_mensual_ac = v_mensual_p1 = v_mensual_p3 = 0

    if not t2_dias.empty:
        ult_dia = t2_dias.iloc[-1]
        v_diaria_ac = ult_dia['P1_P3_DIARIA']
        v_diaria_p1 = ult_dia['P1_DIARIA']
        v_diaria_p3 = ult_dia['P3_DIARIA']
        fecha_ult = str(ult_dia['DIA']).split()[0]
    else:
        v_diaria_ac = v_diaria_p1 = v_diaria_p3 = 0
        fecha_ult = "N/A"

    # --- KPI CARDS SUPERIORES ---
    st.markdown('<div class="kpi-section-title">📊 Calidad Anual</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Anual Acumulada</div><div class="kpi-value" style="color: #10B981;">{fmt_pct(v_anual_ac)}</div><div class="kpi-subtext">Global P1 & P3</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Anual P1</div><div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_anual_p1)}</div><div class="kpi-subtext">Planta 1</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Anual P3</div><div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_anual_p3)}</div><div class="kpi-subtext">Planta 3</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kpi-section-title">📅 Calidad Mensual</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Mensual Acumulada</div><div class="kpi-value" style="color: #10B981;">{fmt_pct(v_mensual_ac)}</div><div class="kpi-subtext">Global P1 & P3</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Mensual P1</div><div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_mensual_p1)}</div><div class="kpi-subtext">Planta 1</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Mensual P3</div><div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_mensual_p3)}</div><div class="kpi-subtext">Planta 3</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kpi-section-title">⏱️ Calidad Diaria (Día: ' + fecha_ult + ')</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Diaria Acumulada</div><div class="kpi-value" style="color: #10B981;">{fmt_pct(v_diaria_ac)}</div><div class="kpi-subtext">Global Día P1 & P3</div></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Diaria P1</div><div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_diaria_p1)}</div><div class="kpi-subtext">Día P1</div></div>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Diaria P3</div><div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_diaria_p3)}</div><div class="kpi-subtext">Día P3</div></div>', unsafe_allow_html=True)

    # --- CALIDAD POR HORNO (TABLA 11 AL:AP) ---
    st.markdown('<div class="kpi-section-title">🔥 Calidad por Horno (Último Registro)</div>', unsafe_allow_html=True)
    if not t11.empty:
        ult_horno_row = t11.iloc[-1]
        v_h1 = ult_horno_row['H1']
        v_h4 = ult_horno_row['H4']
        v_h5 = ult_horno_row['H5']
        v_h6 = ult_horno_row['H6']
        
        h1, h2, h3, h4_col = st.columns(4)
        with h1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Horno 1 (H1)</div><div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_h1)}</div><div class="kpi-subtext">Columna AM</div></div>', unsafe_allow_html=True)
        with h2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Horno 4 (H4)</div><div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_h4)}</div><div class="kpi-subtext">Columna AN</div></div>', unsafe_allow_html=True)
        with h3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Horno 5 (H5)</div><div class="kpi-value" style="color: #10B981;">{fmt_pct(v_h5)}</div><div class="kpi-subtext">Columna AO</div></div>', unsafe_allow_html=True)
        with h4_col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Horno 6 (H6)</div><div class="kpi-value" style="color: #EC4899;">{fmt_pct(v_h6)}</div><div class="kpi-subtext">Columna AP</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- GRÁFICA COMBINADA ---
    st.markdown('<div class="section-box"><div class="section-title">EVOLUCIÓN DIARIA: CALIDAD (%) VS PRODUCCIÓN DE METROS CUADRADOS (M²)</div>', unsafe_allow_html=True)
    if not t2_dias.empty:
        t2_dias['DIA_STR'] = t2_dias['DIA'].astype(str).str.split().str[0]
        y_calidad = t2_dias['P1_P3_DIARIA'] * 100 if t2_dias['P1_P3_DIARIA'].max() <= 1.0 else t2_dias['P1_P3_DIARIA']
        y_mts2 = t2_dias['MTS2_DIA']

        fig_mix = make_subplots(specs=[[{"secondary_y": True}]])

        # 1. Columnas m² (Gris tenue con borde marcado)
        fig_mix.add_trace(
            go.Bar(
                x=t2_dias['DIA_STR'],
                y=y_mts2,
                name="m² Producidos",
                marker_color="#64748B",
                marker_line_color="#1E293B",
                marker_line_width=1.5,
                text=[f"{v:,.2f}" if pd.notna(v) else "0.00" for v in y_mts2],
                texttemplate="%{text}",
                textposition="inside",
                textfont=dict(color="#FFFFFF", size=9, family="sans-serif")
            ),
            secondary_y=True
        )

        # 2. Línea Calidad Diaria (%) 
        fig_mix.add_trace(
            go.Scatter(
                x=t2_dias['DIA_STR'],
                y=y_calidad,
                mode="lines+markers",
                name="Calidad Diaria (%)",
                line=dict(color="#000000", width=3),
                marker=dict(size=7, color="#000000", line=dict(color="#FFFFFF", width=1))
            ),
            secondary_y=False
        )

        # Agregar etiquetas de texto por encima de los puntos
        for x_val, y_val in zip(t2_dias['DIA_STR'], y_calidad):
            if pd.notna(y_val):
                fig_mix.add_annotation(
                    x=x_val,
                    y=y_val,
                    text=f"<b>{y_val:.2f}%</b>",
                    showarrow=False,
                    textangle=-90,
                    yshift=40,
                    font=dict(color="#000000", size=18, family="sans-serif"),
                    yref="y"
                )

        # 3. Línea Meta 94.50%
        fig_mix.add_trace(
            go.Scatter(
                x=t2_dias['DIA_STR'],
                y=[94.50] * len(t2_dias),
                mode="lines",
                name="Meta Calidad (94.50%)",
                line=dict(color="#EF4444", width=2, dash="dash")
            ),
            secondary_y=False
        )

        min_val = float(y_calidad.min()) if not y_calidad.empty and pd.notna(y_calidad.min()) else 70.0
        y_min_bound = float(min(min_val - 5.0, 70.0))
        max_mts2 = float(y_mts2.max()) if not y_mts2.empty and pd.notna(y_mts2.max()) else 20000.0

        fig_mix.update_layout(
            height=650,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94A3B8",
            margin=dict(l=15, r=15, t=50, b=15),
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1)
        )

        fig_mix.update_xaxes(
            type="category",
            tickangle=-45,
            showgrid=False,
            title_text="Días del Mes"
        )

        fig_mix.update_yaxes(
            title_text="% Calidad",
            showgrid=False,
            tickformat=".1f",
            range=[y_min_bound, 118.0],
            secondary_y=False
        )

        fig_mix.update_yaxes(
            title_text="Metros Cuadrados (m²)",
            showgrid=False,
            tickformat=",.2f",
            range=[0, max_mts2 * 3.2],
            secondary_y=True
        )

        st.plotly_chart(fig_mix, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# HOJA 2: DEFECTIVOS
# =============================================================================
elif menu == "DEFECTIVOS":
    st.markdown('<div class="kpi-section-title">📉 Análisis de Defectos y Áreas Responsables</div>', unsafe_allow_html=True)
    
    # 1. PARETO DE DEFECTOS GENERAL
    st.markdown('<div class="section-box"><div class="section-title">PARETO DE DEFECTOS GENERAL</div>', unsafe_allow_html=True)
    
    if planta_sel == "Planta 1 (P1)":
        df_def = t8.rename(columns={'DEFECTO_P1': 'DEFECTO', 'PORC_DEFECTO_P1': 'PORC_DEFECTO'}).copy()
    elif planta_sel == "Planta 3 (P3)":
        df_def = t9.rename(columns={'DEFECTO_P3': 'DEFECTO', 'PORC_DEFECTO_P3': 'PORC_DEFECTO'}).copy()
    else:
        df_def = t7.copy()
        
    if not df_def.empty:
        df_def = df_def.dropna(subset=['DEFECTO', 'PORC_DEFECTO']).copy()
        df_def['VAL_PCT'] = df_def['PORC_DEFECTO'].apply(lambda x: x * 100 if x <= 1.0 else x)
        df_def = df_def.sort_values(by='VAL_PCT', ascending=False)
        
        fig_def = px.bar(
            df_def, 
            x='DEFECTO', 
            y='VAL_PCT', 
            text=df_def['VAL_PCT'].apply(lambda x: f"{x:.2f}%"), 
            color_discrete_sequence=['#475569']
        )
        fig_def.update_traces(
            textposition='outside',
            textangle=-90,
            textfont=dict(color='#000000', size=20, family="sans-serif", weight="bold"),
            marker_line_color='#334155',
            marker_line_width=1
        )
        
        max_val = df_def['VAL_PCT'].max() if not df_def.empty else 100.0
        fig_def.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='#FFFFFF', 
            margin=dict(l=10, r=10, t=70, b=10)
        )
        fig_def.update_xaxes(
            showgrid=False, 
            tickangle=-45, 
            tickfont=dict(color='#000000', size=20, family="sans-serif", weight="bold"), 
            title=dict(text="DEFECTO", font=dict(color='#000000', size=20, family="sans-serif", weight="bold"))
        )
        fig_def.update_yaxes(showgrid=False, showticklabels=False, title=None, range=[0, max_val * 1.35])
        st.plotly_chart(fig_def, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. TARJETAS KPI ILUSTRADAS A COLOR (ESTILO INDUSTRIA CERÁMICA - SVG VECTORIAL)
    st.markdown('<div class="section-box"><div class="section-title">DISTRIBUCIÓN POR ÁREA RESPONSABLE</div>', unsafe_allow_html=True)
    
    SVG_PRENSAS = """
    <svg width="44" height="44" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="27" y="4" width="10" height="16" rx="2" fill="#475569"/>
        <rect x="29" y="4" width="6" height="16" rx="1" fill="#64748B"/>
        <path d="M16 20 C16 18, 48 18, 48 20 L48 26 C48 28, 16 28, 16 26 Z" fill="#334155"/>
        <rect x="18" y="21" width="28" height="4" rx="1" fill="#475569"/>
        <rect x="22" y="28" width="20" height="6" rx="1" fill="#CBD5E1" stroke="#94A3B8" stroke-width="1"/>
        <rect x="10" y="34" width="44" height="14" rx="3" fill="#1E293B"/>
        <rect x="12" y="36" width="40" height="4" fill="#334155"/>
        <rect x="14" y="48" width="8" height="4" fill="#0F172A"/>
        <rect x="42" y="48" width="8" height="4" fill="#0F172A"/>
    </svg>
    """

    SVG_ESMALTADO = """
    <svg width="44" height="44" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="16" y="8" width="6" height="20" rx="1" fill="#EF4444"/>
        <rect x="26" y="14" width="6" height="14" rx="1" fill="#EF4444"/>
        <path d="M14 8 H24 V11 H14 Z" fill="#B91C1C"/>
        <path d="M24 14 H34 V17 H24 Z" fill="#B91C1C"/>
        <path d="M8 28 L24 20 L40 28 V52 H8 Z" fill="#94A3B8"/>
        <path d="M40 28 L56 34 V52 H40 Z" fill="#64748B"/>
        <rect x="14" y="36" width="10" height="16" rx="1" fill="#38BDF8"/>
        <rect x="30" y="36" width="6" height="6" rx="1" fill="#F1F5F9"/>
        <rect x="44" y="40" width="8" height="12" rx="1" fill="#334155"/>
    </svg>
    """

    ICONOS_AREAS = {
        "LINEAS DE ESMALTADO": SVG_ESMALTADO,
        "LÍNEAS DE ESMALTADO": SVG_ESMALTADO,
        "HORNOS": "🔥",
        "RECTIFICADO": "📐",
        "TMA": "⚙️",
        "SELECCIÓN & EMPAQUE": "📦",
        "SELECCION & EMPAQUE": "📦",
        "PRENSAS": SVG_PRENSAS,
        "PRENSADO": SVG_PRENSAS,
        "MTTO": "🛠️",
        "MANTENIMIENTO": "🛠️",
        "PULIDO": "✨",
        "MOLIENDA Y PREPARACIÓN DE ESMALTES": "🧪",
        "PREPARACIÓN DE ESMALTES": "🧪",
        "CARACTERÍSTICAS DEL PRODUCTO": "🔍",
        "CARACTERISTICAS DEL PRODUCTO": "🔍"
    }

    if not t10.empty:
        df_area = t10.dropna(subset=['AREA_RESPONSABLE', 'PORC_AREA']).copy()
        df_area['VAL_PCT'] = df_area['PORC_AREA'].apply(lambda x: x * 100 if x <= 1.0 else x)
        df_area = df_area[df_area['VAL_PCT'] > 0].sort_values(by='VAL_PCT', ascending=False)
        
        cols = st.columns(4)
        for idx, (_, row) in enumerate(df_area.iterrows()):
            area_name = str(row['AREA_RESPONSABLE']).strip().upper()
            val_num = row['VAL_PCT']
            val_pct = f"{val_num:.2f}%"
            icon = ICONOS_AREAS.get(area_name, "🏭")
            
            if val_num < 5.0:
                dot_class = "dot-green"
                text_color = "#15803D"
            elif val_num < 15.0:
                dot_class = "dot-yellow"
                text_color = "#D97706"
            else:
                dot_class = "dot-red"
                text_color = "#B91C1C"

            col_target = cols[idx % 4]
            with col_target:
                st.markdown(f"""
                <div class="grid-kpi-card">
                    <div class="grid-kpi-title">{area_name}</div>
                    <div class="grid-kpi-icon">{icon}</div>
                    <div class="grid-kpi-footer">
                        <span class="{dot_class}">●</span>
                        <span class="grid-kpi-val" style="color: {text_color};">{val_pct}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. DETALLE DE PARETOS P1 Y P3
    st.markdown('<div class="section-box"><div class="section-title">ANÁLISIS COMPARATIVO DE DEFECTOS: PLANTA 1 VS PLANTA 3</div>', unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    
    with c_a:
        st.subheader("Pareto Defectos Planta 1 (P1)")
        if not t8.empty:
            df_p1 = t8.dropna(subset=['DEFECTO_P1', 'PORC_DEFECTO_P1']).copy()
            df_p1['VAL_PCT'] = df_p1['PORC_DEFECTO_P1'].apply(lambda x: x * 100 if x <= 1.0 else x)
            df_p1 = df_p1.sort_values(by='VAL_PCT', ascending=False)
            
            fig_p1 = px.bar(
                df_p1, 
                x='DEFECTO_P1', 
                y='VAL_PCT', 
                text=df_p1['VAL_PCT'].apply(lambda x: f"{x:.2f}%"),
                color_discrete_sequence=['#475569']
            )
            fig_p1.update_traces(
                textposition='outside',
                textangle=-90,
                textfont=dict(color='#000000', size=14, family="sans-serif", weight="bold"),
                marker_line_color='#334155',
                marker_line_width=1
            )
            max_p1 = df_p1['VAL_PCT'].max() if not df_p1.empty else 100.0
            fig_p1.update_layout(
                height=520, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color='#FFFFFF',
                margin=dict(l=5, r=5, t=60, b=10)
            )
            fig_p1.update_xaxes(
                showgrid=False, 
                tickangle=-45, 
                tickfont=dict(color='#000000', size=14, family="Segoe UI, sans-serif", weight="bold"), 
                title=None
            )
            fig_p1.update_yaxes(showgrid=False, showticklabels=False, title=None, range=[0, max_p1 * 1.35])
            st.plotly_chart(fig_p1, use_container_width=True)

    with c_b:
        st.subheader("Pareto Defectos Planta 3 (P3)")
        if not t9.empty:
            df_p3 = t9.dropna(subset=['DEFECTO_P3', 'PORC_DEFECTO_P3']).copy()
            df_p3['VAL_PCT'] = df_p3['PORC_DEFECTO_P3'].apply(lambda x: x * 100 if x <= 1.0 else x)
            df_p3 = df_p3.sort_values(by='VAL_PCT', ascending=False)
            
            fig_p3 = px.bar(
                df_p3, 
                x='DEFECTO_P3', 
                y='VAL_PCT', 
                text=df_p3['VAL_PCT'].apply(lambda x: f"{x:.2f}%"),
                color_discrete_sequence=['#475569']
            )
            fig_p3.update_traces(
                textposition='outside',
                textangle=-90,
                textfont=dict(color='#000000', size=14, family="sans-serif", weight="bold"),
                marker_line_color='#334155',
                marker_line_width=1
            )
            max_p3 = df_p3['VAL_PCT'].max() if not df_p3.empty else 100.0
            fig_p3.update_layout(
                height=520, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color='#FFFFFF',
                margin=dict(l=5, r=5, t=60, b=10)
            )
            fig_p3.update_xaxes(
                showgrid=False, 
                tickangle=-45, 
                tickfont=dict(color='#000000', size=14, family="Segoe UI, sans-serif", weight="bold"), 
                title=None
            )
            fig_p3.update_yaxes(showgrid=False, showticklabels=False, title=None, range=[0, max_p3 * 1.35])
            st.plotly_chart(fig_p3, use_container_width=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# HOJA 3: TONOS
# =============================================================================
elif menu == "TONOS":
    st.markdown('<div class="kpi-section-title">🎨 Cumplimiento y Control de Tonos</div>', unsafe_allow_html=True)
    
    # Obtener valores del último registro disponible
    if not t6.empty:
        ult_row = t6.iloc[-1]
        v_cump_p1 = ult_row['CUMP_P1']
        v_cump_p3 = ult_row['CUMP_P3']
        v_cump_acum = ult_row['CUMP_ACUMULADO']
        fecha_val = str(ult_row['FECHA']).split()[0]
    else:
        v_cump_p1 = v_cump_p3 = v_cump_acum = 0
        fecha_val = "N/A"

    # Tarjetas KPI de Cumplimiento de Tono
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">CUMP_P1</div>
            <div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_cump_p1)}</div>
            <div class="kpi-subtext">Planta 1 ({fecha_val})</div>
        </div>
        ''', unsafe_allow_html=True)
    with k2:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">CUMP_P3</div>
            <div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_cump_p3)}</div>
            <div class="kpi-subtext">Planta 3 ({fecha_val})</div>
        </div>
        ''', unsafe_allow_html=True)
    with k3:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">CUMP_ACUMULADO</div>
            <div class="kpi-value" style="color: #10B981;">{fmt_pct(v_cump_acum)}</div>
            <div class="kpi-subtext">Global ({fecha_val})</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Tablas de Modelos en Horno
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown('<div class="section-box"><div class="section-title">🧪 MODELOS DE PRUEBA EN HORNO</div>', unsafe_allow_html=True)
        if not t4.empty:
            st.dataframe(
                t4, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "MODELO_PRUEBA": "Modelo en Prueba",
                    "HORNO_PRUEBAS": "Horno"
                }
            )
        else:
            st.caption("No hay registros disponibles de modelos de prueba.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_m2:
        st.markdown('<div class="section-box"><div class="section-title">✅ MODELOS AUTORIZADOS</div>', unsafe_allow_html=True)
        if not t5.empty:
            st.dataframe(
                t5, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "MODELOS_AUTORIZADOS": "Modelo Autorizado",
                    "HORNO_AUTORIZADOS": "Horno"
                }
            )
        else:
            st.caption("No hay registros disponibles de modelos autorizados.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# HOJA 4: GARANTÍAS
# =============================================================================
elif menu == "GARANTÍAS":
    st.markdown('<div class="kpi-section-title">🛡️ Reclamaciones y Garantías</div>', unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        st.markdown('<div class="section-box"><div class="section-title">GARANTÍAS RECLAMADAS POR MES</div>', unsafe_allow_html=True)
        if not t3.empty:
            fig_gar = px.bar(t3, x='MES_GARANTIAS', y='GARANTIAS', text='GARANTIAS', color_discrete_sequence=['#EF4444'])
            fig_gar.update_layout(
                height=450,
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color='#94A3B8'
            )
            fig_gar.update_xaxes(showgrid=False)
            fig_gar.update_yaxes(showgrid=True, gridcolor='#334155')
            st.plotly_chart(fig_gar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_g2:
        st.markdown('<div class="section-box"><div class="section-title">DATOS DE GARANTÍAS</div>', unsafe_allow_html=True)
        st.dataframe(t3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
