import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    .main { background-color: #0F172A; color: #F8FAFC; font-family: 'Segoe UI', Roboto, sans-serif; }
    .block-container { padding: 1.5rem 2rem 2rem 2rem; }

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

    .kpi-card { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        border-radius: 10px; 
        padding: 12px 14px; 
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 10px;
    }
    .kpi-title { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value { font-size: 24px; font-weight: 800; margin-bottom: 2px; }
    .kpi-subtext { font-size: 10px; color: #64748B; }

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

    # 1. Tabla Anual
    t1 = df_raw.iloc[:, 0:4].copy()
    t1.columns = ['MES', 'P1_ANUAL', 'P3_ANUAL', 'P1_P3_ANUAL']
    t1['P1_ANUAL'] = pd.to_numeric(t1['P1_ANUAL'], errors='coerce')
    t1['P3_ANUAL'] = pd.to_numeric(t1['P3_ANUAL'], errors='coerce')
    t1['P1_P3_ANUAL'] = pd.to_numeric(t1['P1_P3_ANUAL'], errors='coerce')
    
    total_gen_row = t1[t1['MES'].astype(str).str.contains("Total general", case=False, na=False)]
    t1_meses = t1[~t1['MES'].astype(str).str.contains("Total general", case=False, na=False)].dropna(subset=['P1_P3_ANUAL'])

    # 2. Tabla Diaria / Mensual
    t2 = df_raw.iloc[:, 5:10].copy()
    t2.columns = ['DIA', 'P1_DIARIA', 'P3_DIARIA', 'P1_P3_DIARIA', 'MTS2_DIA']
    t2['P1_DIARIA'] = pd.to_numeric(t2['P1_DIARIA'], errors='coerce')
    t2['P3_DIARIA'] = pd.to_numeric(t2['P3_DIARIA'], errors='coerce')
    t2['P1_P3_DIARIA'] = pd.to_numeric(t2['P1_P3_DIARIA'], errors='coerce')
    t2['MTS2_DIA'] = pd.to_numeric(t2['MTS2_DIA'], errors='coerce')
    
    # Limpiar filas nulas o vacías
    t2 = t2.dropna(subset=['DIA', 'P1_P3_DIARIA'])

    # 3. Resto de Tablas
    t3 = df_raw.iloc[:, 11:13].dropna(how='all'); t3.columns = ['MES_GARANTIAS', 'GARANTIAS']
    t4 = df_raw.iloc[:, 14:16].dropna(how='all'); t4.columns = ['MODELO_PRUEBA', 'HORNO_PRUEBAS']
    t5 = df_raw.iloc[:, 17:19].dropna(how='all'); t5.columns = ['MODELOS_AUTORIZADOS', 'HORNO_AUTORIZADOS']
    t6 = df_raw.iloc[:, 20:24].dropna(how='all'); t6.columns = ['FECHA', 'CUMP_P1', 'CUMP_P3', 'CUMP_ACUMULADO']
    t7 = df_raw.iloc[:, 25:27].dropna(how='all'); t7.columns = ['DEFECTO', 'PORC_DEFECTO']
    t8 = df_raw.iloc[:, 28:30].dropna(how='all'); t8.columns = ['DEFECTO_P1', 'PORC_DEFECTO_P1']
    t9 = df_raw.iloc[:, 31:33].dropna(how='all'); t9.columns = ['DEFECTO_P3', 'PORC_DEFECTO_P3']
    t10 = df_raw.iloc[:, 34:36].dropna(how='all'); t10.columns = ['AREA_RESPONSABLE', 'PORC_AREA']

    return (t1_meses, total_gen_row, t2, t3, t4, t5, t6, t7, t8, t9, t10)

def fmt_pct(val):
    if pd.isna(val) or val is None:
        return "0.00%"
    return f"{val * 100:.2f}%" if val <= 1.0 else f"{val:.2f}%"

# -----------------------------------------------------------------------------
# 3. NAVEGACIÓN Y PANEL LATERAL
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🟩 **SISTEMA DE CALIDAD**")
    st.caption("PISO CERÁMICO P1 & P3")
    st.markdown("---")
    
    menu = st.radio("NAVEGACIÓN", ["RESUMEN", "INDICADORES", "DEFECTOS", "MODELOS Y HORNOS"])
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
# 4. VISTA PRINCIPAL Y LÓGICA DE CALIDAD
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

t1_meses, total_gen_row, t2, t3, t4, t5, t6, t7, t8, t9, t10 = st.session_state.tables

if menu == "RESUMEN":

    # A) CALIDAD ANUAL (Total General de la Tabla 1 del Excel)
    if not total_gen_row.empty:
        v_anual_ac = total_gen_row['P1_P3_ANUAL'].values[0]
        v_anual_p1 = total_gen_row['P1_ANUAL'].values[0]
        v_anual_p3 = total_gen_row['P3_ANUAL'].values[0]
    else:
        v_anual_ac = t1_meses['P1_P3_ANUAL'].iloc[-1] if not t1_meses.empty else 0
        v_anual_p1 = t1_meses['P1_ANUAL'].iloc[-1] if not t1_meses.empty else 0
        v_anual_p3 = t1_meses['P3_ANUAL'].iloc[-1] if not t1_meses.empty else 0

    # B) CALIDAD MENSUAL (Media Ponderada por m² producidos)
    total_mts2 = t2['MTS2_DIA'].sum() if 'MTS2_DIA' in t2.columns else 0
    
    if total_mts2 > 0:
        v_mensual_ac = (t2['P1_P3_DIARIA'] * t2['MTS2_DIA']).sum() / total_mts2
        v_mensual_p1 = (t2['P1_DIARIA'] * t2['MTS2_DIA']).sum() / total_mts2
        v_mensual_p3 = (t2['P3_DIARIA'] * t2['MTS2_DIA']).sum() / total_mts2
    else:
        # En caso de no tener m², tomar el promedio directo filtrado
        v_mensual_ac = t2['P1_P3_DIARIA'].mean() if not t2.empty else 0
        v_mensual_p1 = t2['P1_DIARIA'].mean() if not t2.empty else 0
        v_mensual_p3 = t2['P3_DIARIA'].mean() if not t2.empty else 0

    # C) CALIDAD DIARIA (Última fila activa de la Tabla Diaria)
    if not t2.empty:
        ult_reg = t2.iloc[-1]
        v_diaria_ac = ult_reg['P1_P3_DIARIA']
        v_diaria_p1 = ult_reg['P1_DIARIA']
        v_diaria_p3 = ult_reg['P3_DIARIA']
        fecha_ult = str(ult_reg['DIA']).split()[0]
    else:
        v_diaria_ac = v_diaria_p1 = v_diaria_p3 = 0
        fecha_ult = "N/A"

    # -----------------------------------------------------------------------------
    # TARJETAS DE MÉTRICAS
    # -----------------------------------------------------------------------------
    col_kpis, col_charts = st.columns([1, 2.3])

    with col_kpis:
        # --- BLOQUE ACUMULADO / GLOBAL ---
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Anual Acumulada</div><div class="kpi-value" style="color: #10B981;">{fmt_pct(v_anual_ac)}</div><div class="kpi-subtext">Global P1 & P3</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Mensual Acumulada</div><div class="kpi-value" style="color: #10B981;">{fmt_pct(v_mensual_ac)}</div><div class="kpi-subtext">Ponderada P1 & P3</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Diaria Acumulada</div><div class="kpi-value" style="color: #10B981;">{fmt_pct(v_diaria_ac)}</div><div class="kpi-subtext">Día: {fecha_ult}</div></div>', unsafe_allow_html=True)
        
        # --- BLOQUE PLANTA 1 ---
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Anual P1</div><div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_anual_p1)}</div><div class="kpi-subtext">Planta 1</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Mensual P1</div><div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_mensual_p1)}</div><div class="kpi-subtext">Planta 1</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Diaria P1</div><div class="kpi-value" style="color: #3B82F6;">{fmt_pct(v_diaria_p1)}</div><div class="kpi-subtext">Día: {fecha_ult} (P1)</div></div>', unsafe_allow_html=True)
        
        # --- BLOQUE PLANTA 3 ---
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Anual P3</div><div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_anual_p3)}</div><div class="kpi-subtext">Planta 3</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Mensual P3</div><div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_mensual_p3)}</div><div class="kpi-subtext">Planta 3</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Calidad Diaria P3</div><div class="kpi-value" style="color: #F59E0B;">{fmt_pct(v_diaria_p3)}</div><div class="kpi-subtext">Día: {fecha_ult} (P3)</div></div>', unsafe_allow_html=True)

    with col_charts:
        st.markdown('<div class="section-box"><div class="section-title">EVOLUCIÓN DIARIA DE LA CALIDAD ACUMULADA (%)</div>', unsafe_allow_html=True)
        if not t2.empty:
            fig_line = go.Figure()
            
            # Convierte porcentajes a escala 0-100 para el eje Y
            val_y = t2['P1_P3_DIARIA'] * 100 if t2['P1_P3_DIARIA'].max() <= 1.0 else t2['P1_P3_DIARIA']

            # 1. Calidad Diaria Acumulada
            fig_line.add_trace(go.Scatter(
                x=t2['DIA'], 
                y=val_y, 
                mode='lines+markers', 
                name='Calidad Diaria Acumulada', 
                line=dict(color='#10B981', width=3)
            ))

            # 2. Línea de Meta en 94.50%
            fig_line.add_trace(go.Scatter(
                x=t2['DIA'], 
                y=[94.50] * len(t2), 
                mode='lines', 
                name='Meta (94.50%)', 
                line=dict(color='#EF4444', width=2, dash='dash')
            ))

            fig_line.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='#94A3B8'), 
                margin=dict(l=10, r=10, t=10, b=10), 
                xaxis=dict(showgrid=True, gridcolor='#334155', title="Día"), 
                yaxis=dict(showgrid=True, gridcolor='#334155', title="% Calidad", tickformat=".2f"), 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            st.markdown('<div class="section-box"><div class="section-title">PARETO DE DEFECTOS</div>', unsafe_allow_html=True)
            df_def = t8.rename(columns={'DEFECTO_P1': 'DEFECTO', 'PORC_DEFECTO_P1': 'PORC_DEFECTO'}) if planta_sel == "Planta 1 (P1)" else (t9.rename(columns={'DEFECTO_P3': 'DEFECTO', 'PORC_DEFECTO_P3': 'PORC_DEFECTO'}) if planta_sel == "Planta 3 (P3)" else t7)
            if not df_def.empty:
                df_def = df_def.sort_values(by='PORC_DEFECTO', ascending=True)
                fig_def = px.bar(df_def, x='PORC_DEFECTO', y='DEFECTO', orientation='h', text=df_def['PORC_DEFECTO'].apply(lambda x: fmt_pct(x)), color_discrete_sequence=['#3B82F6'])
                fig_def.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'), margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False))
                st.plotly_chart(fig_def, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_sub2:
            st.markdown('<div class="section-box"><div class="section-title">DISTRIBUCIÓN POR ÁREA</div>', unsafe_allow_html=True)
            if not t10.empty:
                fig_donut = px.pie(t10, names='AREA_RESPONSABLE', values='PORC_AREA', hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
                fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'), margin=dict(l=5, r=5, t=5, b=5), legend=dict(orientation="h", yanchor="bottom", y=-0.3))
                st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# OTRAS VISTAS
# -----------------------------------------------------------------------------
elif menu == "INDICADORES":
    col_ind1, col_ind2 = st.columns(2)
    with col_ind1:
        st.markdown('<div class="section-box"><div class="section-title">HISTÓRICO DE CALIDAD MES A MES</div>', unsafe_allow_html=True)
        if not t1_meses.empty:
            fig_anual = px.line(t1_meses, x='MES', y=['P1_ANUAL', 'P3_ANUAL', 'P1_P3_ANUAL'], markers=True, color_discrete_map={'P1_ANUAL': '#3B82F6', 'P3_ANUAL': '#F59E0B', 'P1_P3_ANUAL': '#10B981'})
            fig_anual.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'), xaxis=dict(showgrid=True, gridcolor='#334155'), yaxis=dict(showgrid=True, gridcolor='#334155', tickformat=".2f"))
            st.plotly_chart(fig_anual, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_ind2:
        st.markdown('<div class="section-box"><div class="section-title">GARANTÍAS RECLAMADAS POR MES</div>', unsafe_allow_html=True)
        if not t3.empty:
            fig_gar = px.bar(t3, x='MES_GARANTIAS', y='GARANTIAS', text='GARANTIAS', color_discrete_sequence=['#EF4444'])
            fig_gar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#334155'))
            st.plotly_chart(fig_gar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box"><div class="section-title">CUMPLIMIENTO DE TONO EN PRODUCCIÓN</div>', unsafe_allow_html=True)
    if not t6.empty:
        fig_tono = px.bar(t6, x='FECHA', y=['CUMP_P1', 'CUMP_P3', 'CUMP_ACUMULADO'], barmode='group', color_discrete_sequence=['#3B82F6', '#F59E0B', '#10B981'])
        fig_tono.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#334155'))
        st.plotly_chart(fig_tono, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "DEFECTOS":
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown('<div class="section-box"><div class="section-title">DEFECTOS EN PLANTA 1 (P1)</div>', unsafe_allow_html=True)
        st.dataframe(t8, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_d2:
        st.markdown('<div class="section-box"><div class="section-title">DEFECTOS EN PLANTA 3 (P3)</div>', unsafe_allow_html=True)
        st.dataframe(t9, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box"><div class="section-title">DEFECTOS GLOBALES Y RESPONSABILIDAD DE ÁREA</div>', unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("Defectos Consolidados (P1 & P3)")
        st.dataframe(t7, use_container_width=True)
    with c_b:
        st.subheader("% Defectos por Área Responsable")
        st.dataframe(t10, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "MODELOS Y HORNOS":
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown('<div class="section-box"><div class="section-title">MODELOS DE PRUEBA EN HORNO</div>', unsafe_allow_html=True)
        st.dataframe(t4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown('<div class="section-box"><div class="section-title">MODELOS AUTORIZADOS</div>', unsafe_allow_html=True)
        st.dataframe(t5, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
