import os
import pandas as pd
import streamlit as st

# 1. Configuración inicial de la página (Debe ser lo primero)
st.set_page_config(
    page_title="CALIDAD P1&P3 - CESANTONI", page_icon="📊", layout="wide"
)

# 2. Inicializar variables de sesión para autenticación y datos
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "df_dashboard" not in st.session_state:
    st.session_state["df_dashboard"] = None
if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None

# 3. Estilos CSS personalizados para simular la interfaz de la imagen
st.markdown(
    """
    <style>
        /* Ocultar elementos predeterminados de Streamlit para limpieza visual */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Estilo general del fondo */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        /* Tarjetas de métricas superiores estilo dashboard */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }
        
        /* Estilos de títulos de sección */
        .section-title {
            font-size: 1.1rem;
            font-weight: bold;
            color: #333333;
            margin-bottom: 10px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# 4. BARRA LATERAL (Sidebar)
with st.sidebar:
    # Logo corporativo
    logo_path = "logo_cesantoni.png"
    if os.path.exists(logo_path):
        st.image(
            logo_path, width=160
        )  # Tamaño bien proporcionado para la barra
    else:
        st.warning("⚠️ No se encontró 'logo_cesantoni.png' en la carpeta.")

    st.markdown("---")
    st.markdown("### 🎛️ MENÚ DE NAVEGACIÓN")
    menu_opcion = st.radio(
        "Ir a:",
        [
            "RESUMEN",
            "INDICADORES",
            "DEFECTOS",
            "PROCESOS",
            "EMBARQUES",
            "ACCIONES",
            "AUDITORÍAS",
        ],
    )

    st.markdown("---")
    st.markdown("### 🔐 PANEL DE ADMINISTRACIÓN")

    # Sistema de Login / Logout
    if not st.session_state["authenticated"]:
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Iniciar Sesión")

            if submit_login:
                # Credenciales de ejemplo (cámbialas por las tuyas de seguridad)
                if usuario == "admin" and password == "cesantoni2026":
                    st.session_state["authenticated"] = True
                    st.success("¡Sesión iniciada con éxito!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    else:
        st.success("🟢 Modo Administrador Activo")

        # Botón de reinicio de sesión (Solo activo si inició sesión)
        if st.button("Cerrar Sesión / Reiniciar"):
            st.session_state["authenticated"] = False
            st.session_state["df_dashboard"] = None
            st.session_state["uploaded_file_name"] = None
            st.success("Sesión cerrada correctamente.")
            st.rerun()

        st.markdown("---")
        st.markdown("### 📁 CARGA DE ARCHIVO EXCEL")
        archivo_subido = st.file_uploader(
            "Subir reporte de calidad", type=["xlsx", "xls"]
        )

        if archivo_subido is not None:
            try:
                # Leer el archivo buscando específicamente la hoja "DASHBOARD"
                xls = pd.ExcelFile(archivo_subido)
                if "DASHBOARD" in xls.sheet_names:
                    df = pd.read_excel(archivo_subido, sheet_name="DASHBOARD")
                    st.session_state["df_dashboard"] = df
                    st.session_state["uploaded_file_name"] = (
                        archivo_subido.name
                    )
                    st.success(
                        f"Hoja 'DASHBOARD' cargada desde: {archivo_subido.name}"
                    )
                else:
                    st.error(
                        "El archivo Excel no contiene una hoja llamada 'DASHBOARD'."
                    )
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

# 5. CUERPO PRINCIPAL DEL DASHBOARD
# Encabezado principal solicitado
st.title("CALIDAD P1&P3")
st.markdown("##### Todos somos calidad | CESANTONI SA de CV")
st.markdown("---")

# Indicador del archivo activo actual para espectadores y admin
if st.session_state["uploaded_file_name"]:
    st.info(
        f"📄 Mostrando datos basados en el archivo del administrador: **{st.session_state['uploaded_file_name']}**"
    )
else:
    st.warning(
        "⚠️ Ningún archivo cargado por el administrador. Mostrando datos de ejemplo/vacíos."
    )

# 6. DISTRIBUCIÓN DE CONTENIDO SEGÚN LA PESTAÑA SELECCIONADA
if menu_opcion == "RESUMEN":

    # Fila 1: Tarjetas de Métricas Superiores (Simulando la referencia visual)
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(
            """<div class="metric-card">
            <span style="font-size: 0.8rem; color: gray;">CALIDAD DE PRIMERA</span><br>
            <span style="font-size: 1.3rem; font-weight: bold; color: #2e7d32;">96.8 %</span><br>
            <span style="font-size: 0.7rem; color: gray;">Meta ≥ 95%</span>
        </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """<div class="metric-card">
            <span style="font-size: 0.8rem; color: gray;">RECHAZO</span><br>
            <span style="font-size: 1.3rem; font-weight: bold; color: #c62828;">2.1 %</span><br>
            <span style="font-size: 0.7rem; color: gray;">Meta ≤ 2%</span>
        </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """<div class="metric-card">
            <span style="font-size: 0.8rem; color: gray;">RETRABAJO</span><br>
            <span style="font-size: 1.3rem; font-weight: bold; color: #ef6c00;">1.1 %</span><br>
            <span style="font-size: 0.7rem; color: gray;">Meta ≤ 1%</span>
        </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            """<div class="metric-card">
            <span style="font-size: 0.8rem; color: gray;">PRODUCTO LIBERADO</span><br>
            <span style="font-size: 1.3rem; font-weight: bold; color: #1565c0;">98.4 %</span><br>
            <span style="font-size: 0.7rem; color: gray;">Meta ≥ 98%</span>
        </div>""",
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            """<div class="metric-card">
            <span style="font-size: 0.8rem; color: gray;">RECLAMOS CLIENTE</span><br>
            <span style="font-size: 1.3rem; font-weight: bold; color: #c62828;">4</span><br>
            <span style="font-size: 0.7rem; color: gray;">Meta ≤ 3</span>
        </div>""",
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            """<div class="metric-card">
            <span style="font-size: 0.8rem; color: gray;">AUDITORÍAS CUMPLIDAS</span><br>
            <span style="font-size: 1.3rem; font-weight: bold; color: #2e7d32;">94 %</span><br>
            <span style="font-size: 0.7rem; color: gray;">Meta ≥ 95%</span>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Fila 2: Visualización de datos de la hoja de Excel si existe
    if st.session_state["df_dashboard"] is not None:
        st.markdown("### 📊 Datos procesados de la hoja 'DASHBOARD'")
        st.dataframe(
            st.session_state["df_dashboard"], use_container_width=True
        )

        # Ejemplo de gráfico rápido basado en las columnas del Excel cargado
        df_data = st.session_state["df_dashboard"]
        if len(df_data.columns) >= 2:
            st.markdown("### 📈 Gráfico Rápido Generado del Archivo")
            try:
                # Intenta graficar las dos primeras columnas si son numéricas/texto
                st.bar_chart(df_data.set_index(df_data.columns[0]))
            except Exception:
                st.info(
                    "No se pudo generar un gráfico automático, asegúrate de que la estructura de la hoja tenga datos numéricos y categóricos."
                )
    else:
        # Contenedor visual estático simbiótico a la imagen mientras no haya archivo
        col_A, col_B = st.columns([2, 1])
        with col_A:
            st.markdown(
                """
                <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
                    <h4>PARETO DE DEFECTOS (MES ACTUAL)</h4>
                    <p style="color: gray; font-size: 0.9rem;">Esperando archivo de Excel del Administrador para mapear defectos...</p>
                    <ul>
                        <li>Mancha superficial: 32%</li>
                        <li>Planitud: 24%</li>
                        <li>Variación de tono: 18%</li>
                        <li>Canto / escuadra: 12%</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_B:
            st.markdown(
                """
                <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
                    <h4>ESTADO DEL SISTEMA</h4>
                    <p>🔒 <b>Modo Espectador:</b> Solo lectura.</p>
                    <p>🔑 Inicia sesión en el panel lateral como administrador para actualizar los registros mediante tu archivo Excel.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

else:
    # Secciones adicionales correspondientes al menú lateral
    st.markdown(
        f"### Sección: {menu_opcion}"
    )
    st.info(
        f"Apartado de {menu_opcion} en desarrollo. Aquí se mostrarán los detalles específicos de este módulo utilizando la información de la hoja DASHBOARD."
    )
    if st.session_state["df_dashboard"] is not None:
        st.dataframe(
            st.session_state["df_dashboard"], use_container_width=True
        )
