import pandas as pd
import streamlit as st

# 1. Configuración de la página en modo ancho (Panel Industrial)
st.set_page_config(
    page_title="Dashboard - Sistema de Calidad",
    page_icon="🏭",
    layout="wide",
)

# Estilos CSS para el fondo oscuro y tarjetas de métricas limpias
st.markdown(
    """
    <style>
    .main {
        background-color: #0b131a;
    }
    .stMetric {
        background-color: #161f28;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown(
    """
    <div style="background-color: #161f28; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">DASHBOARD - SISTEMA DE CALIDAD</h2>
        <p style="color: #8b949e; margin: 0;">PRODUCTO TERMINADO – PISO CERÁMICO</p>
    </div>
""",
    unsafe_allow_html=True,
)


# 2. Carga de las 7 tablas desde la hoja 'DASHBOARD' del Excel
@st.cache_data
def cargar_todas_las_tablas():
  # REEMPLAZA 'tu_archivo.xlsx' por el nombre real de tu archivo en GitHub
  archivo = "tu_archivo.xlsx"

  # Tabla 1: Calidad y Metros (Cols A:G)
  df_t1 = pd.read_excel(
      archivo,
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

  # Tabla 2: Garantías (Cols I:J)
  df_t2 = pd.read_excel(
      archivo,
      sheet_name="DASHBOARD",
      usecols="I:J",
      skiprows=1,
      names=["MES_GARANTIAS", "GARANTIAS"],
  )

  # Tabla 3: Modelos en prueba (Cols L:M)
  df_t3 = pd.read_excel(
      archivo,
      sheet_name="DASHBOARD",
      usecols="L:M",
      skiprows=1,
      names=["MODELO_PRUEBA", "HORNO_PRUEBAS"],
  )

  # Tabla 4: Modelos autorizados (Cols O:P)
  df_t4 = pd.read_excel(
      archivo,
      sheet_name="DASHBOARD",
      usecols="O:P",
      skiprows=1,
      names=["MODELOS_AUTORIZADOS", "HORNO_AUTORIZADOS"],
  )

  # Tabla 5: Defectos (Cols R:Y)
  df_t5 = pd.read_excel(
      archivo,
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
  )

  # Tabla 6: Cumplimiento a tonos (Cols AA:AD)
  df_t6 = pd.read_excel(
      archivo,
      sheet_name="DASHBOARD",
      usecols="AA:AD",
      skiprows=1,
      names=[
          "FECHA_TONO",
          "TONO_P1",
          "TONO_P3",
          "TONO_ACUMULADO",
      ],
  )

  # Tabla 7: Liberación de pallet (Cols AF:AK)
  df_t7 = pd.read_excel(
      archivo,
      sheet_name="DASHBOARD",
      usecols="AF:AK",
      skiprows=1,
      names=[
          "FECHA_PALLET",
          "PALLET_1RA",
          "PALLET_2DA",
          "PALLET_3RA",
          "PALLET_RECHAZADO",
          "PRINCIPAL_RECHAZO",
      ],
  )

  return (
      df_t1.dropna(how="all"),
      df_t2.dropna(how="all"),
      df_t3.dropna(how="all"),
      df_t4.dropna(how="all"),
      df_t5.dropna(how="all"),
      df_t6.dropna(how="all"),
      df_t7.dropna(how="all"),
  )


try:
  t1, t2, t3, t4, t5, t6, t7 = cargar_todas_las_tablas()

  # --- SECCIÓN DE TARJETAS DE KPIs SUPERIORES ---
  st.subheader("📊 Indicadores Generales")
  total_mts = t1["MTS2_DIA"].sum() if not t1.empty else 0
  prom_primera = t1["PRIMERA"].mean() if not t1.empty else 0
  total_garantias = t2["GARANTIAS"].sum() if not t2.empty else 0
  total_defectos_mts = t5["MTS2_DEFECTO"].sum() if not t5.empty else 0

  kpi1, kpi2, kpi3, kpi4 = st.columns(4)
  with kpi1:
    st.metric(label="Metros Producidos (Día)", value=f"{total_mts:,.2f} m²")
  with kpi2:
    st.metric(label="Promedio Calidad 1ra", value=f"{prom_primera:.1f}%")
  with kpi3:
    st.metric(label="Total Garantías", value=int(total_garantias))
  with kpi4:
    st.metric(label="Metros con Defecto", value=f"{total_defectos_mts:,.2f} m²")

  st.divider()

  # --- SECCIÓN: GRÁFICOS Y ANÁLISIS PRINCIPAL ---
  col_izq, col_der = st.columns(2)

  with col_izq:
    st.subheader("📈 Tendencia de Metros Cuadrados (Tabla A:G)")
    if not t1.empty and "FECHA" in t1.columns:
      st.line_chart(t1.set_index("FECHA")["MTS2_DIA"])
    else:
      st.info("No hay datos suficientes para graficar la producción diaria.")

  with col_der:
    st.subheader("🛑 Defectos por Responsable / Área (Tabla R:Y)")
    if not t5.empty and "RESPONSABLE_DEFECTO" in t5.columns:
      defectos_resp = t5["RESPONSABLE_DEFECTO"].value_counts()
      st.bar_chart(defectos_resp)
    else:
      st.info("No hay registros de defectos en la tabla.")

  st.divider()

  # --- SECCIÓN: SEGUIMIENTO DE PROCESOS Y PRUEBAS ---
  col_a, col_b = st.columns(2)

  with col_a:
    st.subheader("🔬 Modelos en Prueba (Tabla L:M)")
    if not t3.empty:
      st.dataframe(t3, use_container_width=True)
    else:
      st.info("Sin modelos en prueba registrados.")

  with col_b:
    st.subheader("✅ Modelos Autorizados (Tabla O:P)")
    if not t4.empty:
      st.dataframe(t4, use_container_width=True)
    else:
      st.info("Sin modelos autorizados registrados.")

  st.divider()

  # --- SECCIÓN: CUMPLIMIENTO DE TONOS Y PALLETS ---
  col_c, col_d = st.columns(2)

  with col_c:
    st.subheader("🎨 Cumplimiento a Tonos Acumulado (Tabla AA:AD)")
    if not t6.empty and "FECHA_TONO" in t6.columns:
      st.line_chart(t6.set_index("FECHA_TONO")["TONO_ACUMULADO"])
    else:
      st.info("Sin datos de cumplimiento a tonos.")

  with col_d:
    st.subheader("📦 Liberación y Rechazo de Pallets (Tabla AF:AK)")
    if not t7.empty:
      st.dataframe(t7.head(10), use_container_width=True)

  # --- EXPANSOR GENERAL PARA REVISAR TODAS LAS TABLAS ---
  with st.expander("📂 Ver todas las tablas de datos en bruto (Hoja DASHBOARD)"):
    st.write("### 1. Calidad y Metros (A:G)")
    st.dataframe(t1)
    st.write("### 2. Garantías (I:J)")
    st.dataframe(t2)
    st.write("### 3. Modelos en Prueba (L:M)")
    st.dataframe(t3)
    st.write("### 4. Modelos Autorizados (O:P)")
    st.dataframe(t4)
    st.write("### 5. Defectos (R:Y)")
    st.dataframe(t5)
    st.write("### 6. Cumplimiento a Tonos (AA:AD)")
    st.dataframe(t6)
    st.write("### 7. Liberación de Pallet (AF:AK)")
    st.dataframe(t7)

except FileNotFoundError:
  st.error(
      "⚠️ No se encontró el archivo Excel. Sube tu archivo con el nombre"
      " correcto a GitHub junto al código."
  )
except Exception as e:
  st.error(
      f"⚠️ Ocurrió un error leyendo los rangos de la hoja DASHBOARD: {e}"
  )
