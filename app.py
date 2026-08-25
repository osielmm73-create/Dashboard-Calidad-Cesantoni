import os
import pandas as pd
import streamlit as st

# 1. Configuración de página en modo wide
st.set_page_config(
    page_title="CALIDAD P1&P3 - CESANTONI", page_icon="📊", layout="wide"
)

# 2. Inicializar estado de sesión
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "df_dashboard" not in st.session_state:
    st.session_state["df_dashboard"] = None
if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None
if "menu_activo" not in st.session_state:
    st.session_state["menu_activo"] = "RESUMEN"

# 3. Estilos CSS Avanzados para replicar el diseño de la imagen exacta
st.markdown(
    """
    <style>
        /* Ocultar elementos predeterminados de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Fondo general de la aplicación */
        .stApp {
            background-color: #f4f6f9;
        }

        /* Forzar un diseño compacto en el contenedor principal */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Simular la barra lateral oscura de la imagen mediante inyección o diseño compacto */
        section[data-testid="stSidebar"] {
            background-color: #1a2228 !important;
            color: white !important;
            width: 220px !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] span {
            color: #ffffff !important;
        }

        /* Tarjetas de métricas superiores idénticas a la referencia */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 12px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            text-align: center;
            margin-bottom: 5px;
        }
        
        .metric-title {
            font-size: 0.70rem;
            font-weight: bold;
            color: #64748b;
            letter-spacing: 0.5px;
        }

        .metric-value-green { font-size: 1.4rem; font-weight: 800; color: #16a34a; }
        .metric-value-red { font-size: 1.4rem; font-weight: 800; color: #dc2626; }
        .metric-value-orange { font-size: 1.4rem; font-weight: 800; color: #d97706; }
        .metric-value-blue { font-size: 1.4rem; font-weight: 800; color: #2563eb; }

        .metric-meta {
            font-size: 0.65rem;
            color: #94a3b8;
        }

        /* Contenedores de paneles (Paneles blancos con bordes sutiles) */
        .dashboard-panel {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        
        .panel-title {
            font-size: 0.85rem;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# 4. BARRA LATERAL (Simulando el menú vertical oscuro de la imagen)
with st.sidebar:
    logo_path = "logo_cesantoni.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    else:
        st.markdown(
            "### **CESANTONI**"
        )  # Texto de respaldo si falta la imagen

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.75rem; color:#94a3b8;'>NAVEGACIÓN</p>",
        unsafe_allow_html=True,
    )

    # Botones de navegación estilo menú lateral de la imagen
    opciones = [
        "🏠 RESUMEN",
        "📊 INDICADORES",
        "📋 DEFECTOS",
        "🏭 PROCESOS",
        "📦 EMBARQUES",
        "⚙️ ACCIONES",
        "👥 AUDITORÍAS",
    ]

    seleccion = st.radio("Menú principal", opciones, label_visibility="collapsed")
    st.session_state["menu_activo"] = seleccion.split(" ")[1]

    st.markdown("---")
    st.markdown("### 🔐 ACCESO ADMIN")

    if not st.session_state["authenticated"]:
        with st.form("login_admin"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            entrar = st.form_submit_button("Entrar")
            if entrar:
                if user == "admin" and pwd == "cesantoni2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
    else:
        st.success("✔ Modo Administrador")
        # Botón de reinicio que solo se activa al iniciar sesión
        if st.button("🔄 Reiniciar Sesión"):
            st.session_state["authenticated"] = False
            st.session_state["df_dashboard"] = None
            st.session_state["uploaded_file_name"] = None
            st.rerun()

        st.markdown("---")
        archivo = st.file_uploader(
            "Subir Excel (.xlsx)", type=["xlsx"], key="excel_uploader"
        )
        if archivo is not None:
            try:
                xls = pd.ExcelFile(archivo)
                if "DASHBOARD" in xls.sheet_names:
                    st.session_state["df_dashboard"] = pd.read_excel(
                        archivo, sheet_name="DASHBOARD"
                    )
                    st.session_state["uploaded_file_name"] = archivo.name
                    st.success("Hoja 'DASHBOARD' cargada.")
                else:
                    st.error("El archivo no tiene la hoja 'DASHBOARD'.")
            except Exception as e:
                st.error(f"Error: {e}")

# 5. ENCABEZADO PRINCIPAL DE LA VISTA (Header superior estilo barra gris clara)
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.markdown(
        """
        <div style="background-color: #1e293b; color: white; padding: 12px 20px; border-radius: 6px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: white;">CALIDAD P1&P3</h3>
            <p style="margin: 0; font-size: 0.75rem; color: #cbd5e1;">Todos somos calidad | CESANTONI SA de CV</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
with col_head2:
    st.markdown(
        """
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; text-align: center; margin-bottom: 15px;">
            <span style="font-size: 0.7rem; color: #64748b;">📅 19/05/2026 &nbsp;|&nbsp; 🔍 Filtro: Todos</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Indicador de archivo activo
if st.session_state["uploaded_file_name"]:
    st.caption(
        f"📂 Archivo activo en uso: **{st.session_state['uploaded_file_name']}**"
    )

# 6. CONTENIDO SEGÚN LA PESTAÑA ACTIVA
pestana = st.session_state["menu_activo"]

if pestana == "RESUMEN":
    # FILA 1: Las 6 tarjetas superiores de métricas exactas a la imagen
    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">CALIDAD DE PRIMERA</div>
                <div class="metric-value-green">96.8 %</div>
                <div class="metric-meta">Meta ≥ 95%</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">RECHAZO</div>
                <div class="metric-value-red">2.1 %</div>
                <div class="metric-meta">Meta ≤ 2%</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">RETRABAJO</div>
                <div class="metric-value-orange">1.1 %</div>
                <div class="metric-meta">Meta ≤ 1%</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">PRODUCTO LIBERADO</div>
                <div class="metric-value-blue">98.4 %</div>
                <div class="metric-meta">Meta ≥ 98%</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with m5:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">RECLAMOS CLIENTE</div>
                <div class="metric-value-red">4</div>
                <div class="metric-meta">Meta ≤ 3</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with m6:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">AUDITORÍAS CUMPLIDAS</div>
                <div class="metric-value-green">94 %</div>
                <div class="metric-meta">Meta ≥ 95%</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # FILA 2: Paneles centrales (Si hay datos de Excel los muestra, sino muestra la estructura visual limpia)
    if st.session_state["df_dashboard"] is not None:
        st.markdown(
            '<div class="dashboard-panel">', unsafe_allow_html=True
        )
        st.markdown(
            '<div class="panel-title">📊 DATOS DE LA HOJA "DASHBOARD"</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            st.session_state["df_dashboard"], use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        c_p1, c_p2, c_p3 = st.columns([1.2, 1, 1.2])

        with c_p1:
            st.markdown(
                """
                <div class="dashboard-panel">
                    <div class="panel-title">Pareto de Defectos (Mes Actual)</div>
                    <p style="font-size:0.75rem; color:#64748b;">(Sube tu archivo Excel para poblar automáticamente)</p>
                    <ul style="font-size:0.8rem; padding-left: 15px; color:#334155;">
                        <li><b>Mancha superficial:</b> 32%</li>
                        <li><b>Planitud:</b> 24%</li>
                        <li><b>Variación de tono:</b> 18%</li>
                        <li><b>Canto / escuadra:</b> 12%</li>
                        <li><b>Ruptura:</b> 8%</li>
                    </ul>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with c_p2:
            st.markdown(
                """
                <div class="dashboard-panel" style="text-align: center;">
                    <div class="panel-title">Distribución de Defectos</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1e293b; margin-top: 20px;">1,248</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 20px;">Total Defectos Detectados</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with c_p3:
            st.markdown(
                """
                <div class="dashboard-panel">
                    <div class="panel-title">Calidad por Proceso (% Primera)</div>
                    <table style="width:100%; font-size:0.75rem; text-align:center;">
                        <tr><td>Prensado: <b>98.2%</b></td><td>Secado: <b>97.6%</b></td></tr>
                        <tr><td>Esmaltado: <b>94.8%</b></td><td>Decoración: <b>95.1%</b></td></tr>
                        <tr><td>Horno: <span style="color:red;">91.7%</span></td><td>Selección: <b>98.5%</b></td></tr>
                    </table>
                </div>
            """,
                unsafe_allow_html=True,
            )
else:
    st.markdown(f"### Módulo: {pestana}")
    st.info(
        "Sección configurada para reflejar los datos de tu archivo de calidad."
    )
    if st.session_state["df_dashboard"] is not None:
        st.dataframe(
            st.session_state["df_dashboard"], use_container_width=True
        )
