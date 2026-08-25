import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
# =============================================================================
st.set_page_config(
    page_title="Dashboard de Calidad",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Estilos generales */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Contenedores y Secciones */
    .section-box {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    .section-title {
        color: #F8FAFC;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .kpi-section-title {
        color: #38BDF8;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 15px;
    }

    /* Tarjetas KPI Estilo Cuadrícula */
    .grid-kpi-card {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
    }
    .grid-kpi-title {
        color: #94A3B8;
        font-size: 11px;
        font-weight: bold;
        min-height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .grid-kpi-icon {
        font-size: 32px;
        margin: 10px 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 50px;
    }
    .grid-kpi-footer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .grid-kpi-val {
        font-size: 20px;
        font-weight: bold;
    }
    
    /* Indicadores de estado */
    .dot-green { color: #22C55E; font-size: 14px; }
    .dot-yellow { color: #F59E0B; font-size: 14px; }
    .dot-red { color: #EF4444; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MANEJO DE SESIÓN Y CARGA DE DATOS
# =============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "custom_file" not in st.session_state:
    st.session_state.custom_file = None

st.sidebar.title("🔐 Sesión & Archivo")

if not st.session_state.logged_in:
    with st.sidebar.expander("Iniciar Sesión"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            st.session_state.logged_in = True
            st.rerun()
else:
    st.sidebar.success("Sesión Activa")
    uploaded_file = st.sidebar.file_uploader("Cargar Excel Personalizado", type=["xlsx", "xls"])
    if uploaded_file:
        st.session_state.custom_file = uploaded_file
    
    if st.sidebar.button("Restablecer Datos por Defecto"):
        st.session_state.custom_file = None
        st.rerun()

@st.cache_data
def load_data(file_source):
    excel_obj = pd.ExcelFile(file_source)
    sheet_names = excel_obj.sheet_names
    t_dict = {}
    
    for i in range(1, 11):
        s_name = f'T{i}'
        if s_name in sheet_names:
            t_dict[s_name] = pd.read_excel(file_source, sheet_name=s_name)
        else:
            t_dict[s_name] = pd.DataFrame()
            
    return t_dict['T1'], t_dict['T2'], t_dict['T3'], t_dict['T4'], t_dict['T5'], \
           t_dict['T6'], t_dict['T7'], t_dict['T8'], t_dict['T9'], t_dict['T10']

try:
    source = st.session_state.custom_file if st.session_state.custom_file else 'DATOS_DASHBOARD.xlsx'
    t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = load_data(source)
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.info("Asegúrate de tener el archivo 'DATOS_DASHBOARD.xlsx' en la misma carpeta o inicia sesión para subir uno.")
    st.stop()

# =============================================================================
# BARRA LATERAL (FILTROS Y NAVEGACIÓN)
# =============================================================================
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Seleccione Pestaña", ["GENERAL", "DEFECTIVOS"])

st.sidebar.title("Filtros")
planta_sel = st.sidebar.selectbox("Planta", ["Todas", "Planta 1 (P1)", "Planta 3 (P3)"])

# =============================================================================
# HOJA 1: GENERAL
# =============================================================================
if menu == "GENERAL":
    st.markdown('<div class="kpi-section-title">📊 Resumen General de Calidad</div>', unsafe_allow_html=True)
    
    # 1. METRICAS PRINCIPALES / RESUMEN
    st.markdown('<div class="section-box"><div class="section-title">INDICADORES CLAVE DE RENDIMIENTO (KPIs)</div>', unsafe_allow_html=True)
    
    if not t1.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        df_t1 = t1.copy()
        if planta_sel == "Planta 1 (P1)":
            df_t1 = df_t1[df_t1['PLANTA'] == 'P1'] if 'PLANTA' in df_t1.columns else df_t1
        elif planta_sel == "Planta 3 (P3)":
            df_t1 = df_t1[df_t1['PLANTA'] == 'P3'] if 'PLANTA' in df_t1.columns else df_t1

        with col1:
            val_prod = df_t1['PRODUCCION'].sum() if 'PRODUCCION' in df_t1.columns else 0
            st.metric("Producción Total", f"{val_prod:,.0f} m²")
            
        with col2:
            val_prim = df_t1['PRIMERA'].mean() if 'PRIMERA' in df_t1.columns else 0
            st.metric("% Primera Calidad", f"{val_prim:.2f}%")
            
        with col3:
            val_def = df_t1['DEFECTIVO'].mean() if 'DEFECTIVO' in df_t1.columns else 0
            st.metric("% Defectivo", f"{val_def:.2f}%")
            
        with col4:
            val_rot = df_t1['ROTURA'].mean() if 'ROTURA' in df_t1.columns else 0
            st.metric("% Rotura", f"{val_rot:.2f}%")
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. TENDENCIAS TEMPORALES
    st.markdown('<div class="section-box"><div class="section-title">TENDENCIA HISTÓRICA DE CALIDAD</div>', unsafe_allow_html=True)
    if not t2.empty:
        df_t2 = t2.copy()
        fig_tend = px.line(
            df_t2, 
            x='FECHA' if 'FECHA' in df_t2.columns else df_t2.columns[0],
            y=['PRIMERA', 'DEFECTIVO', 'ROTURA'] if all(c in df_t2.columns for c in ['PRIMERA', 'DEFECTIVO', 'ROTURA']) else df_t2.columns[1:],
            markers=True,
            color_discrete_sequence=['#22C55E', '#EF4444', '#F59E0B']
        )
        fig_tend.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#94A3B8',
            legend_title_text='Métrica'
        )
        fig_tend.update_xaxes(showgrid=False)
        fig_tend.update_yaxes(showgrid=True, gridcolor='#334155')
        st.plotly_chart(fig_tend, use_container_width=True)
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
            color_discrete_sequence=['#64748B']
        )
        fig_def.update_traces(
            textposition='outside',
            textangle=-90,
            textfont=dict(color='#94A3B8', size=20, family="sans-serif", weight="bold"),
            marker_line_color='#334155',
            marker_line_width=1
        )
        
        max_val = df_def['VAL_PCT'].max() if not df_def.empty else 100.0
        fig_def.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='#94A3B8', 
            margin=dict(l=10, r=10, t=70, b=10)
        )
        fig_def.update_xaxes(
            showgrid=False, 
            tickangle=-45, 
            tickfont=dict(color='#FFFFFF', size=11, weight="bold"), 
            title=dict(text="DEFECTO", font=dict(color='#FFFFFF', size=13, weight="bold"))
        )
        fig_def.update_yaxes(showgrid=False, visible=False, range=[0, max_val * 1.35])
        st.plotly_chart(fig_def, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. TARJETAS KPI ILUSTRADAS A COLOR
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
                color_discrete_sequence=['#64748B']
            )
            fig_p1.update_traces(
                textposition='outside',
                textangle=-90,
                textfont=dict(color='#94A3B8', size=20, family="sans-serif", weight="bold"),
                marker_line_color='#334155',
                marker_line_width=1
            )
            max_p1 = df_p1['VAL_PCT'].max() if not df_p1.empty else 100.0
            fig_p1.update_layout(
                height=480, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color='#94A3B8',
                margin=dict(l=5, r=5, t=60, b=10)
            )
            fig_p1.update_xaxes(
                showgrid=False, 
                tickangle=-45, 
                tickfont=dict(color='#FFFFFF', size=11, weight="bold"), 
                title=dict(text="DEFECTO", font=dict(color='#FFFFFF', size=13, weight="bold"))
            )
            fig_p1.update_yaxes(showgrid=False, visible=False, range=[0, max_p1 * 1.35])
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
                color_discrete_sequence=['#64748B']
            )
            fig_p3.update_traces(
                textposition='outside',
                textangle=-90,
                textfont=dict(color='#94A3B8', size=20, family="sans-serif", weight="bold"),
                marker_line_color='#334155',
                marker_line_width=1
            )
            max_p3 = df_p3['VAL_PCT'].max() if not df_p3.empty else 100.0
            fig_p3.update_layout(
                height=480, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color='#94A3B8',
                margin=dict(l=5, r=5, t=60, b=10)
            )
            fig_p3.update_xaxes(
                showgrid=False, 
                tickangle=-45, 
                tickfont=dict(color='#FFFFFF', size=11, weight="bold"), 
                title=dict(text="DEFECTO", font=dict(color='#FFFFFF', size=13, weight="bold"))
            )
            fig_p3.update_yaxes(showgrid=False, visible=False, range=[0, max_p3 * 1.35])
            st.plotly_chart(fig_p3, use_container_width=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
