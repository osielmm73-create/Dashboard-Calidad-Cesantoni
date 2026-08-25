import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    /* Tarjetas KPI */
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
        padding: 14px 16px; 
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value { font-size: 24px; font-weight: 800; margin-bottom: 2px; }
    .kpi-subtext { font-size: 10px; color: #64748B; }

    /* Cajas de Gráficos y Tablas */
    .section-box { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px;
    }
    .section-title { font-size: 14px; font-weight: 700; color: #F1F5F9; margin-bottom: 16px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PROCESAMIENTO Y LECTURA DE DATOS EXCEL
# -----------------------------------------------------------------------------
ADMIN_USER = "admin"
ADMIN_PASSWORD = "calidad2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.tables = None

def process_excel(file):
    xls = pd.ExcelFile(file)
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
    t4 = df_raw.iloc[:, 14:16].dropna(how='all'); t4.columns = ['MODELO_PRUEBA', 'HORNO_PRUEBAS']
    t5 = df_raw.iloc[:, 17:19].dropna(how='all'); t5.columns = ['MODELOS_AUTORIZADOS', 'HORNO_AUTORIZADOS']
    t6 = df_raw.iloc[:, 20:24].dropna(how='all'); t6.columns = ['FECHA', 'CUMP_P1', 'CUMP_P3', 'CUMP_ACUMULADO']
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

    return (t1_meses, total_gen_row, t2_dias, resumen_mensual_row, t3, t4, t5, t6, t7, t8, t9, t10, t11_clean)

def fmt_pct(val):
    if pd.isna(val) or val is None:
        return "0.00%"
    return f"{val * 100:.2f}%" if val <= 1.0 else f"{val:.2f}%"

def fmt_num(val):
    if pd.isna(val) or val is None:
        return "0"
    return f"{val:,.0f}"

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
                    st.success("Sesión activa")
                    st.rerun()
                else:
                    st.error("Credenciales erróneas")
    else:
        st.success("🟢 Sesión Admin Activa")
        uploaded_file = st.file_uploader("Cargar Reporte Excel", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                st.session_state.tables = process_excel(uploaded_file)
                st.session_state.data_loaded = True
                st.success("¡Datos procesados correctamente!")
            except Exception as err:
                st.error(f"Error al leer estructura: {err}")
        
        if st.session_state.data_loaded:
            if st.button("🗑️ Resetear Datos Cargados"):
                st.session_state.data_loaded = False
                st.session_state.tables = None
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

if not st.session_state.data_loaded:
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

    # --- GRÁFICA AMPLIADA Y CORREGIDA: CALIDAD DIARIA (%) VS M² ---
    st.markdown('<div class="section-box"><div class="section-title">EVOLUCIÓN DIARIA: CALIDAD (%) VS PRODUCCIÓN DE METROS CUADRADOS (M²)</div>', unsafe_allow_html=True)
    if not t2_dias.empty:
        t2_dias['DIA_STR'] = t2_dias['DIA'].astype(str).str.split().str[0]
        y_calidad = t2_dias['P1_P3_DIARIA'] * 100 if t2_dias['P1_P3_DIARIA'].max() <= 1.0 else t2_dias['P1_P3_DIARIA']
        y_mts2 = t2_dias['MTS2_DIA']

        fig_mix = make_subplots(specs=[[{"secondary_y": True}]])

        # 1. Columnas m² (Eje Y2)
        fig_mix.add_trace(
            go.Bar(
                x=t2_dias['DIA_STR'],
                y=y_mts2,
                name="m² Producidos",
                marker_color="rgba(56, 189, 248, 0.45)",
                marker_line_color="#38BDF8",
                marker_line_width=1,
                text=[fmt_num(v) for v in y_mts2],
                textposition="inside",
                textfont=dict(color="#F8FAFC", size=10)
            ),
            secondary_y=True
        )

        # 2. Línea Calidad Diaria (Eje Y1)
        fig_mix.add_trace(
            go.Scatter(
                x=t2_dias['DIA_STR'],
                y=y_calidad,
                mode="lines+markers+text",
                name="Calidad Diaria (%)",
                text=[f"{v:.2f}%" for v in y_calidad],
                textposition="top center",
                textfont=dict(color="#10B981", size=11),
                line=dict(color="#10B981", width=3.5),
                marker=dict(size=8, color="#10B981", symbol="circle")
            ),
            secondary_y=False
        )

        # 3. Línea Meta 94.50% (Eje Y1)
        fig_mix.add_trace(
            go.Scatter(
                x=t2_dias['DIA_STR'],
                y=[94.50] * len(t2_dias),
                mode="lines",
                name="Meta Calidad (94.50%)",
                line=dict(color="#EF4444", width=2.5, dash="dash")
            ),
            secondary_y=False
        )

        # Rango seguro para evitar errores de tipo en Plotly
        min_y = float(y_calidad.min()) if not y_calidad.empty and pd.notna(y_calidad.min()) else 70.0
        y_min_bound = float(min(min_y - 4.0, 70.0))

        fig_mix.update_layout(
            height=520,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94A3B8"),
            margin=dict(l=15, r=15, t=30, b=15),
            xaxis=dict(
                type="category",
                tickangle=-45,
                showgrid=True,
                gridcolor="#334155",
                title="Días del Mes",
                titlefont=dict(color="#F8FAFC", size=12)
            ),
            yaxis=dict(
                title="% Calidad",
                titlefont=dict(color="#10B981", size=12),
                showgrid=True,
                gridcolor="#334155",
                tickformat=".1f",
                range=[y_min_bound, 105.0]
            ),
            yaxis2=dict(
                title="Metros Cuadrados (m²)",
                titlefont=dict(color="#38BDF8", size=12),
                showgrid=False,
                tickformat=",d"
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_mix, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# HOJA 2: DEFECTIVOS
# =============================================================================
elif menu == "DEFECTIVOS":
    st.markdown('<div class="kpi-section-title">📉 Análisis de Defectos y Áreas Responsables</div>', unsafe_allow_html=True)
    
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        st.markdown('<div class="section-box"><div class="section-title">PARETO DE DEFECTOS</div>', unsafe_allow_html=True)
        df_def = t8.rename(columns={'DEFECTO_P1': 'DEFECTO', 'PORC_DEFECTO_P1': 'PORC_DEFECTO'}) if planta_sel == "Planta 1 (P1)" else (t9.rename(columns={'DEFECTO_P3': 'DEFECTO', 'PORC_DEFECTO_P3': 'PORC_DEFECTO'}) if planta_sel == "Planta 3 (P3)" else t7)
        if not df_def.empty:
            df_def = df_def.sort_values(by='PORC_DEFECTO', ascending=True)
            fig_def = px.bar(
                df_def, 
                x='PORC_DEFECTO', 
                y='DEFECTO', 
                orientation='h', 
                text=df_def['PORC_DEFECTO'].apply(lambda x: fmt_pct(x)), 
                color_discrete_sequence=['#3B82F6']
            )
            fig_def.update_layout(
                height=500,
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='#94A3B8'), 
                margin=dict(l=10, r=10, t=10, b=10), 
                xaxis=dict(showgrid=False, visible=False), 
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_def, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_sub2:
        st.markdown('<div class="section-box"><div class="section-title">DISTRIBUCIÓN POR ÁREA RESPONSABLE</div>', unsafe_allow_html=True)
        if not t10.empty:
            fig_donut = px.pie(
                t10, 
                names='AREA_RESPONSABLE', 
                values='PORC_AREA', 
                hole=0.45, 
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_donut.update_layout(
                height=500,
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='#94A3B8'), 
                margin=dict(l=5, r=5, t=5, b=5), 
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box"><div class="section-title">DETALLE DE TABLAS DE DEFECTOS</div>', unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("Defectos Planta 1 (P1)")
        st.dataframe(t8, use_container_width=True)
    with c_b:
        st.subheader("Defectos Planta 3 (P3)")
        st.dataframe(t9, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# HOJA 3: TONOS
# =============================================================================
elif menu == "TONOS":
    st.markdown('<div class="kpi-section-title">🎨 Cumplimiento y Control de Tonos</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-box"><div class="section-title">CUMPLIMIENTO DE TONO EN PRODUCCIÓN (%)</div>', unsafe_allow_html=True)
    if not t6.empty:
        fig_tono = px.bar(
            t6, 
            x='FECHA', 
            y=['CUMP_P1', 'CUMP_P3', 'CUMP_ACUMULADO'], 
            barmode='group', 
            color_discrete_sequence=['#3B82F6', '#F59E0B', '#10B981']
        )
        fig_tono.update_layout(
            height=480,
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#94A3B8'), 
            xaxis=dict(showgrid=False), 
            yaxis=dict(showgrid=True, gridcolor='#334155')
        )
        st.plotly_chart(fig_tono, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown('<div class="section-box"><div class="section-title">MODELOS DE PRUEBA EN HORNO</div>', unsafe_allow_html=True)
        st.dataframe(t4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown('<div class="section-box"><div class="section-title">MODELOS AUTORIZADOS</div>', unsafe_allow_html=True)
        st.dataframe(t5, use_container_width=True)
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
                font=dict(color='#94A3B8'), 
                xaxis=dict(showgrid=False), 
                yaxis=dict(showgrid=True, gridcolor='#334155')
            )
            st.plotly_chart(fig_gar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_g2:
        st.markdown('<div class="section-box"><div class="section-title">DATOS DE GARANTÍAS</div>', unsafe_allow_html=True)
        st.dataframe(t3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
