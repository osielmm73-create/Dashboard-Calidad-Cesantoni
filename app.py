import io
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. Configuración de la página en modo ancho
st.set_page_config(
    page_title="CALIDAD P1&P3 - Sistema de Calidad", page_icon="🏭", layout="wide"
)

# Estilos CSS mejorados: Fondo claro profesional y legibilidad total en tarjetas
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stMetric label {
        color: #374151 !important;
        font-weight: 600 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #111827 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BARRA LATERAL: LOGOTIPO Y ACCESO ADMINISTRATIVO ---
with st.sidebar:
  if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
  else:
    st.markdown("### **CESANTONI**")

  st.markdown("---")
  st.subheader("Panel de Control")

  if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

  if not st.session_state["autenticado"]:
    with st.expander("🔐 Acceso Administrador (Subir/Modificar)"):
      usuario = st.text_input("Usuario")
      password = st.text_input("Contraseña", type="password")
      if st.button("Iniciar Sesión"):
        if usuario == "calidad" and password == "cesantoni2026":
          st.session_state["autenticado"] = True
          st.success("¡Acceso concedido!")
          st.rerun()
        else:
          st.error("Credenciales incorrectas")
  else:
    st.success("Modo Edición Activado 🔓")
    if st.button("Cerrar Sesión"):
      st.session_state["autenticado"] = False
      st.rerun()

# --- CARGAR ARCHIVO EXCEL ---
archivo_cargado = None
if st.session_state["autenticado"]:
  st.sidebar.markdown("---")
  st.sidebar.subheader("📤 Actualizar Base de Datos")
  archivo_subido = st.sidebar.file_uploader(
      "Sube tu archivo Excel actualizado", type=["xlsx"]
  )
  if archivo_subido is not None:
    with open("temp_excel.xlsx", "wb") as f:
      f.write(archivo_subido.getbuffer())
    archivo_cargado = "temp_excel.xlsx"
    st.sidebar.success("¡Archivo cargado con éxito!")

if not archivo_cargado:
  if os.path.exists("temp_excel.xlsx"):
    archivo_cargado = "temp_excel.xlsx"
  else:
    import glob

    xls_list = glob.glob("*.xlsx")
    if xls_list:
      archivo_cargado = xls_list[0]

# --- ENCABEZADO PRINCIPAL ---
st.markdown(
    """
    <div style="background-color: #1e293b; padding: 22px; border-radius: 10px; margin-bottom: 25px; border-left: 6px solid #2563eb;">
        <h2 style="color: white; margin: 0; font-weight: 700;">CALIDAD P1&P3</h2>
        <p style="color: #94a3b8; margin: 0; font-size: 15px; font-weight: 500;">Todos somos calidad | Planta Zacatecas</p>
    </div>
""",
    unsafe_allow_html=True,
)


# 2. Función optimizada para leer las tablas de la hoja 'DASHBOARD'
@st.cache_data
def cargar_todas_las_tablas(path_archivo):
  # Tabla 1: Calidad y Metros (Cols A:G)
  df_t1 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="A:G",
      skiprows=1,
      names=[
          "FECHA",
          "PRIMERA",
          "SEGUNDA",
          "TERCERA",
          "QUINTA",
          "MTS2_DIA",
          "CALIDAD_META",
      ],
  )
  # Limpiar filas vacías o mal formateadas en la fecha
  df_t1["FECHA"] = pd.to_datetime(df_t1["FECHA"], errors="coerce")
  df_t1 = df_t1.dropna(subset=["FECHA"])

  for col in ["PRIMERA", "SEGUNDA", "TERCERA", "QUINTA", "MTS2_DIA", "CALIDAD_META"]:
    df_t1[col] = pd.to_numeric(df_t1[col], errors="coerce").fillna(0)

  # Tabla 2: Garantías (Cols I:J) - Ordenadas estrictamente de Enero a Diciembre
  df_t2 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="I:J",
      skiprows=1,
      names=["MES_GARANTIAS", "GARANTIAS"],
  )
  df_t2 = df_t2.dropna(subset=["MES_GARANTIAS"])
  df_t2 = df_t2[
      ~df_t2["MES_GARANTIAS"].astype(str).str.upper().str.contains("TOTAL")
  ]
  df_t2["MES_GARANTIAS"] = (
      df_t2["MES_GARANTIAS"].astype(str).str.strip().str.upper()
  )
  df_t2["GARANTIAS"] = pd.to_numeric(df_t2["GARANTIAS"], errors="coerce").fillna(0)

  meses_orden = [
      "ENERO",
      "FEBRERO",
      "MARZO",
      "ABRIL",
      "MAYO",
      "JUNIO",
      "JULIO",
      "AGOSTO",
      "SEPTIEMBRE",
      "OCTUBRE",
      "NOVIEMBRE",
      "DICIEMBRE",
  ]
  df_t2["MES_GARANTIAS"] = pd.Categorical(
      df_t2["MES_GARANTIAS"], categories=meses_orden, ordered=True
  )
  df_t2 = df_t2.sort_values("MES_GARANTIAS").reset_index(drop=True)

  # Tabla 3: Modelos en prueba (Cols L:M)
  df_t3 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="L:M",
      skiprows=1,
      names=["MODELO_PRUEBA", "HORNO_PRUEBAS"],
  ).dropna(how="all")

  # Tabla 4: Modelos autorizados (Cols O:P)
  df_t4 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="O:P",
      skiprows=1,
      names=["MODELOS_AUTORIZADOS", "HORNO_AUTORIZADOS"],
  ).dropna(how="all")

  # Tabla 5: Defectos (Cols R:Y)
  df_t5 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="R:Y",
      skiprows=1,
      names=[
          "FECHA_DEFECTO",
          "MODELO_DEFECTO",
          "FORMATO_DEFECTO",
          "HORNO_DEFECTO",
          "DEFECTO",
          "MTS2_DEFECTO",
          "RESPONSABLE_DEFECTO",
          "PORCENTAJE_DEFECTO",
      ],
  ).dropna(how="all")

  # Tabla 6: Cumplimiento a tonos (Cols AA:AD)
  df_t6 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="AA:AD",
      skiprows=1,
      names=["FECHA_TONO", "TONO_P1", "TONO_P3", "TONO_ACUMULADO"],
  ).dropna(how="all")

  # Tabla 7: Liberación de pallet (Cols AF:AK)
  df_t7 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="AF:AK",
      skiprows=1,
      names=[
          "PALLET_FECHA",
          "PALLET_1RA",
          "PALLET_2DA",
          "PALLET_3RA",
          "PALLET_RECHAZADO",
          "PRINCIPAL_RECHAZO",
      ],
  ).dropna(how="all")

  return df_t1, df_t2, df_t3, df_t4, df_t5, df_t6, df_t7


if archivo_cargado:
  try:
    t1, t2, t3, t4, t5, t6, t7 = cargar_todas_las_tablas(archivo_cargado)

    # --- CÁLCULOS DE MÉTRICAS (KPIs) ---
    calidad_dia = t1["PRIMERA"].iloc[-1] if not t1.empty else 0
    calidad_acumulada = t1["PRIMERA"].mean() if not t1.empty else 0

    mts_dia = t1["MTS2_DIA"].iloc[-1] if not t1.empty else 0
    mts_acumulados = t1["MTS2_DIA"].sum() if not t1.empty else 0
    total_garantias = t2["GARANTIAS"].sum() if not t2.empty else 0

    # --- SECCIÓN 1: TARJETAS DE INDICADORES PRINCIPALES ---
    st.subheader("📊 Indicadores de Producción y Calidad")
    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
      st.metric(
          label="Calidad del Día (1ra)",
          value=(
              f"{calidad_dia*100:.2f}%"
              if calidad_dia <= 1
              else f"{calidad_dia:.2f}%"
          ),
      )
    with k2:
      st.metric(
          label="Calidad Acumulada (1ra)",
          value=(
              f"{calidad_acumulada*100:.2f}%"
              if calidad_acumulada <= 1
              else f"{calidad_acumulada:.2f}%"
          ),
      )
    with k3:
      st.metric(label="Metros del Día", value=f"{mts_dia:,.2f} m²")
    with k4:
      st.metric(label="Metros Acumulados", value=f"{mts_acumulados:,.2f} m²")
    with k5:
      st.metric(label="Total Garantías Anual", value=int(total_garantias))

    st.divider()

    # --- SECCIÓN 2: GRÁFICAS PRINCIPALES CON ETIQUETAS DE DATOS ---
    col_izq, col_der = st.columns(2)

    with col_izq:
      st.subheader("📈 Calidad Diaria vs Calidad Meta")
      if not t1.empty and "FECHA" in t1.columns:
        # Usamos Plotly para permitir etiquetas de datos claras
        fig_calidad = px.line(
            t1,
            x="FECHA",
            y=["PRIMERA", "CALIDAD_META"],
            markers=True,
            labels={
                "value": "Porcentaje",
                "variable": "Métrica",
                "FECHA": "Fecha",
            },
        )
        fig_calidad.update_traces(
            textposition="top center",
            texttemplate="%{y:.1%}",
            mode="lines+markers",
        )
        st.plotly_chart(fig_calidad, use_container_width=True)
      else:
        st.info("Sin datos suficientes para la gráfica de calidad.")

    with col_der:
      st.subheader("📦 Garantías por Mes")
      if not t2.empty and "MES_GARANTIAS" in t2.columns:
        # Gráfica de barras con Plotly para asegurar etiquetas de datos y orden exacto
        fig_garantias = px.bar(
            t2,
            x="MES_GARANTIAS",
            y="GARANTIAS",
            text="GARANTIAS",
            labels={
                "MES_GARANTIAS": "Mes",
                "GARANTIAS": "Total Garantías",
            },
        )
        fig_garantias.update_traces(
            texttemplate="%{text}",
            textposition="outside",
            marker_color="rgb(31, 119, 182)",
        )
        fig_garantias.update_layout(
            xaxis={
                "categoryorder": "array",
                "categoryarray": [
                    "ENERO",
                    "FEBRERO",
                    "MARZO",
                    "ABRIL",
                    "MAYO",
                    "JUNIO",
                    "JULIO",
                    "AGOSTO",
                    "SEPTIEMBRE",
                    "OCTUBRE",
                    "NOVIEMBRE",
                    "DICIEMBRE",
                ],
            }
        )
        st.plotly_chart(fig_garantias, use_container_width=True)
      else:
        st.info("Sin registros de garantías.")

    st.divider()

    # --- SECCIÓN 3: TENDENCIA DE METROS Y CUMPLIMIENTO A TONOS ---
    col_a, col_b = st.columns(2)

    with col_a:
      st.subheader("🏭 Tendencia de Metros Cuadrados Diarios")
      if not t1.empty and "FECHA" in t1.columns:
        st.line_chart(t1.set_index("FECHA")["MTS2_DIA"])
      else:
        st.info("Sin datos de metros diarios.")

    with col_b:
      st.subheader("🎨 Cumplimiento a Tonos (Datos Actuales)")
      if not t6.empty:
        st.dataframe(t6.tail(5), use_container_width=True)
        if "TONO_ACUMULADO" in t6.columns:
          ultimo_tono = t6["TONO_ACUMULADO"].iloc[-1]
          st.metric(label="Cumplimiento Tono Acumulado", value=f"{ultimo_tono}")
      else:
        st.info("No hay datos capturados en Cumplimiento a Tonos.")

    st.divider()

    # --- SECCIÓN 4: MODELOS EN PRUEBA Y AUTORIZADOS ---
    col_c, col_d = st.columns(2)
    with col_c:
      st.subheader("🔬 Modelos en Prueba (Tabla L:M)")
      if not t3.empty:
        st.dataframe(t3, use_container_width=True)
      else:
        st.info("Sin modelos en prueba registrados.")

    with col_d:
      st.subheader("✅ Modelos Autorizados (Tabla O:P)")
      if not t4.empty:
        st.dataframe(t4, use_container_width=True)
      else:
        st.info("Sin modelos autorizados registrados.")

    # --- EXPANSOR DE DATOS EN BRUTO ---
    with st.expander("📂 Ver todas las tablas de datos (Hoja DASHBOARD)"):
      st.write("### 1. Calidad y Metros (A:G)")
      st.dataframe(t1)
      st.write("### 2. Garantías (I:J)")
      st.dataframe(t2)
      st.write("### 3. Defectos (R:Y)")
      st.dataframe(t5)

  except Exception as e:
    st.error(
        f"⚠️ Error al procesar el archivo. Verifica que contenga la hoja"
        f" 'DASHBOARD' y el formato correcto. Detalle: {e}"
    )
else:
  st.warning(
      "⚠️ **Bienvenido.** Inicia sesión en la barra lateral para subir tu"
      " archivo Excel de calidad."
  )
