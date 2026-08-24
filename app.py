import glob
import io
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuración de la página en modo ancho
st.set_page_config(
    page_title="CALIDAD P1&P3 - Sistema de Calidad", page_icon="🏭", layout="wide"
)

# Estilos CSS mejorados para tarjetas y tablas ejecutivas
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 10px;
        position: relative;
    }
    .metric-title {
        color: #64748b;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #1e293b;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .metric-footer {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 500;
    }
    .defect-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #e11d48;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BARRA LATERAL: CONTROL Y ACCESO ADMINISTRATIVO ---
with st.sidebar:
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

    # EL BOTÓN DE REINICIAR SOLO APARECE SI ESTÁS AUTENTICADO
    st.markdown("---")
    if st.button("🔄 Reiniciar / Limpiar Sesión"):
      if os.path.exists("temp_excel.xlsx"):
        os.remove("temp_excel.xlsx")
      st.cache_data.clear()
      for key in list(st.session_state.keys()):
        del st.session_state[key]
      st.success("¡Datos reseteados con éxito!")
      st.rerun()

# --- CARGAR ARCHIVO EXCEL ---
archivo_cargado = None
if st.session_state.get("autenticado", False):
  st.sidebar.markdown("---")
  st.sidebar.subheader("📤 Actualizar Base de Datos")
  archivo_subido = st.sidebar.file_uploader(
      "Sube tu archivo Excel actualizado", type=["xlsx"]
  )
  if archivo_subido is not None:
    with open("temp_excel.xlsx", "wb") as f:
      f.write(archivo_subido.getbuffer())
    st.cache_data.clear()
    archivo_cargado = "temp_excel.xlsx"
    st.sidebar.success("¡Archivo cargado y actualizado con éxito!")

if not archivo_cargado:
  if os.path.exists("temp_excel.xlsx"):
    archivo_cargado = "temp_excel.xlsx"
  else:
    xls_list = glob.glob("*.xlsx")
    if xls_list:
      archivo_cargado = xls_list[0]


# Función para leer todas las tablas de la hoja 'DASHBOARD'
@st.cache_data
def cargar_todas_las_tablas(path_archivo):
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
  df_t1["FECHA"] = pd.to_datetime(df_t1["FECHA"], errors="coerce")
  df_t1 = df_t1.dropna(subset=["FECHA"])
  for col in ["PRIMERA", "SEGUNDA", "TERCERA", "QUINTA", "MTS2_DIA", "CALIDAD_META"]:
    df_t1[col] = pd.to_numeric(df_t1[col], errors="coerce").fillna(0)

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

  df_t3 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="L:M",
      skiprows=1,
      names=["MODELO_PRUEBA", "HORNO_PRUEBAS"],
  )
  df_t3 = df_t3.dropna(subset=["MODELO_PRUEBA"])

  df_t4 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="O:P",
      skiprows=1,
      names=["MODELOS_AUTORIZADOS", "HORNO_AUTORIZADOS"],
  )
  df_t4 = df_t4.dropna(subset=["MODELOS_AUTORIZADOS"])

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
  )
  df_t5["FECHA_DEFECTO"] = pd.to_datetime(df_t5["FECHA_DEFECTO"], errors="coerce")
  df_t5 = df_t5.dropna(subset=["FECHA_DEFECTO", "DEFECTO"], how="any")
  df_t5["MTS2_DEFECTO"] = pd.to_numeric(
      df_t5["MTS2_DEFECTO"], errors="coerce"
  ).fillna(0)
  df_t5["PORCENTAJE_DEFECTO"] = pd.to_numeric(
      df_t5["PORCENTAJE_DEFECTO"], errors="coerce"
  ).fillna(0)

  df_t6 = pd.read_excel(
      path_archivo,
      sheet_name="DASHBOARD",
      usecols="AA:AD",
      skiprows=1,
      names=["FECHA_TONO", "TONO_P1", "TONO_P3", "TONO_ACUMULADO"],
  )
  df_t6["FECHA_TONO"] = pd.to_datetime(df_t6["FECHA_TONO"], errors="coerce")
  df_t6 = df_t6.dropna(subset=["FECHA_TONO"])
  for col in ["TONO_P1", "TONO_P3", "TONO_ACUMULADO"]:
    df_t6[col] = pd.to_numeric(df_t6[col], errors="coerce")

  # Lectura de Liberación de Pallet (Columnas AF:AK)
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
  )
  df_t7["PALLET_FECHA"] = pd.to_datetime(df_t7["PALLET_FECHA"], errors="coerce")
  df_t7 = df_t7.dropna(subset=["PALLET_FECHA", "PRINCIPAL_RECHAZO"], how="any")
  for col in ["PALLET_1RA", "PALLET_2DA", "PALLET_3RA", "PALLET_RECHAZADO"]:
    df_t7[col] = pd.to_numeric(df_t7[col], errors="coerce").fillna(0)

  return df_t1, df_t2, df_t3, df_t4, df_t5, df_t6, df_t7


if archivo_cargado:
  try:
    t1, t2, t3, t4, t5, t6, t7 = cargar_todas_las_tablas(archivo_cargado)

    # Determinar la fecha de última actualización en base a los datos de la tabla 1 o fecha actual del archivo
    ultima_fecha_datos = (
        t1["FECHA"].max().strftime("%d/%m/%Y")
        if not t1.empty
        else "Sin fecha"
    )

    # --- ENCABEZADO PRINCIPAL CON FECHA DE ACTUALIZACIÓN A LA DERECHA ---
    col_logo, col_titulo, col_fecha = st.columns([1, 4, 2])

    with col_logo:
      if os.path.exists("logo_cesantoni.png"):
        st.image("logo_cesantoni.png", use_container_width=True)
      else:
        st.markdown("### 🏭 Cesantoni")

    with col_titulo:
      st.markdown(
          """
            <div style="background-color: #1e293b; padding: 22px; border-radius: 10px; margin-bottom: 25px; border-left: 6px solid #2563eb;">
                <h2 style="color: white; margin: 0; font-weight: 700;">CALIDAD P1&P3</h2>
                <p style="color: #94a3b8; margin: 0; font-size: 15px; font-weight: 500;">Todos somos calidad | Planta Zacatecas</p>
            </div>
        """,
          unsafe_allow_html=True,
      )

    with col_fecha:
      st.markdown(
          f"""
            <div style="background-color: #1e293b; padding: 18px; border-radius: 10px; text-align: right; margin-bottom: 25px;">
                <span style="color: #94a3b8; font-size: 12px; display: block; text-transform: uppercase;">Última Actualización</span>
                <span style="color: #ffffff; font-size: 18px; font-weight: 700;">📅 {ultima_fecha_datos}</span>
            </div>
        """,
          unsafe_allow_html=True,
      )

    # --- CÁLCULOS DE MÉTRICAS (KPIs) ---
    calidad_dia = t1["PRIMERA"].iloc[-1] if not t1.empty else 0

    if not t1.empty and t1["MTS2_DIA"].sum() > 0:
      calidad_acumulada = (
          t1["PRIMERA"] * t1["MTS2_DIA"]
      ).sum() / t1["MTS2_DIA"].sum()
    else:
      calidad_acumulada = t1["PRIMERA"].mean() if not t1.empty else 0

    mts_dia = t1["MTS2_DIA"].iloc[-1] if not t1.empty else 0
    mts_acumulados = t1["MTS2_DIA"].sum() if not t1.empty else 0
    total_garantias = t2["GARANTIAS"].sum() if not t2.empty else 0
    meta_actual = (
        (t1["CALIDAD_META"].iloc[-1] * 100) if not t1.empty else 95.0
    )

    # --- SECCIÓN 1: TARJETAS DE INDICADORES ---
    st.subheader("📊 Indicadores de Producción y Calidad")
    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
      st.markdown(
          f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-title">Calidad del Día (1ra)</span>
                    <span style="font-size: 20px;">✅</span>
                </div>
                <div class="metric-value">{calidad_dia * 100:.2f}%</div>
                <div class="metric-footer">Meta ≥ {meta_actual:.1f}%</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with k2:
      st.markdown(
          f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-title">Calidad Acumulada</span>
                    <span style="font-size: 20px;">📈</span>
                </div>
                <div class="metric-value">{calidad_acumulada * 100:.2f}%</div>
                <div class="metric-footer">Rendimiento Global 1ra</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with k3:
      st.markdown(
          f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-title">Metros del Día</span>
                    <span style="font-size: 20px;">🏭</span>
                </div>
                <div class="metric-value" style="font-size: 24px;">{mts_dia:,.2f} m²</div>
                <div class="metric-footer">Producción Diaria</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with k4:
      st.markdown(
          f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-title">Metros Acumulados</span>
                    <span style="font-size: 20px;">📦</span>
                </div>
                <div class="metric-value" style="font-size: 24px;">{mts_acumulados:,.2f} m²</div>
                <div class="metric-footer">Total Fabricado</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with k5:
      st.markdown(
          f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-title">Total Garantías</span>
                    <span style="font-size: 20px;">⚠️</span>
                </div>
                <div class="metric-value">{int(total_garantias)}</div>
                <div class="metric-footer">Reclamos del Año</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.divider()

    # --- SECCIÓN 2: GRÁFICA DE CALIDAD DIARIA GRANDE (A TODO EL ANCHO) ---
    st.subheader("📈 Calidad Diaria vs Calidad Meta")
    if not t1.empty and "FECHA" in t1.columns:
      t1_grafica = t1.copy()
      t1_grafica["PRIMERA_PCT"] = t1_grafica["PRIMERA"] * 100
      t1_grafica["CALIDAD_META_PCT"] = t1_grafica["CALIDAD_META"] * 100

      fig_calidad = go.Figure()

      # Línea de Calidad Diaria CON etiquetas de datos
      fig_calidad.add_trace(
          go.Scatter(
              x=t1_grafica["FECHA"],
              y=t1_grafica["PRIMERA_PCT"],
              mode="lines+markers+text",
              name="PRIMERA_PCT",
              text=[f"{v:.1f}%" for v in t1_grafica["PRIMERA_PCT"]],
              textposition="top center",
              line=dict(color="#1f77b4", width=3),
          )
      )

      # Línea de Meta SIN etiquetas de datos para evitar saturación
      fig_calidad.add_trace(
          go.Scatter(
              x=t1_grafica["FECHA"],
              y=t1_grafica["CALIDAD_META_PCT"],
              mode="lines",
              name="CALIDAD_META_PCT",
              line=dict(color="#ff7f0e", width=2, dash="dash"),
          )
      )

      fig_calidad.update_layout(
          height=500,
          margin=dict(l=20, r=20, t=30, b=20),
          legend=dict(
              orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
          ),
          xaxis_title="Fecha",
          yaxis_title="Porcentaje (%)",
      )
      st.plotly_chart(fig_calidad, use_container_width=True)
    else:
      st.info("Sin datos suficientes para la gráfica de calidad.")

    st.divider()

    # --- SECCIÓN 3: TENDENCIA DE METROS Y GARANTÍAS ABAJO ---
    col_a, col_b = st.columns(2)

    with col_a:
      st.subheader("🏭 Tendencia de Metros Cuadrados Diarios")
      if not t1.empty and "FECHA" in t1.columns:
        fig_mts = px.line(
            t1,
            x="FECHA",
            y="MTS2_DIA",
            markers=True,
            labels={"MTS2_DIA": "Metros (m²)", "FECHA": "Fecha"},
            height=380,
        )
        fig_mts.update_traces(
            textposition="top center",
            texttemplate="%{y:,.0f} m²",
            mode="lines+markers+text",
        )
        st.plotly_chart(fig_mts, use_container_width=True)
      else:
        st.info("Sin datos de metros diarios.")

    with col_b:
      st.subheader("📦 Garantías por Mes")
      if not t2.empty and "MES_GARANTIAS" in t2.columns:
        fig_garantias = px.bar(
            t2,
            x="MES_GARANTIAS",
            y="GARANTIAS",
            text="GARANTIAS",
            labels={
                "MES_GARANTIAS": "Mes",
                "GARANTIAS": "Total Garantías",
            },
            height=380,
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

    # --- SECCIÓN 4: CUMPLIMIENTO A TONOS ---
    st.subheader("🎨 Cumplimiento a Tonos (Valores Actuales)")
    if not t6.empty:
      t6_validos = t6.dropna(subset=["TONO_P1", "TONO_P3", "TONO_ACUMULADO"])

      if not t6_validos.empty:
        ultimo_p1 = t6_validos["TONO_P1"].iloc[-1] * 100
        ultimo_p3 = t6_validos["TONO_P3"].iloc[-1] * 100
        ultimo_acum = t6_validos["TONO_ACUMULADO"].iloc[-1] * 100
        fecha_ultimo = t6_validos["FECHA_TONO"].iloc[-1].strftime("%d/%m/%Y")
      else:
        ultimo_p1, ultimo_p3, ultimo_acum, fecha_ultimo = (
            0,
            0,
            0,
            "Sin datos recientes",
        )

      sub_c1, sub_c2, sub_c3 = st.columns(3)
      with sub_c1:
        st.metric(label="Tono P1 (Último)", value=f"{ultimo_p1:.2f}%")
      with sub_c2:
        st.metric(label="Tono P3 (Último)", value=f"{ultimo_p3:.2f}%")
      with sub_c3:
        st.metric(label="Tono Acumulado", value=f"{ultimo_acum:.2f}%")

      st.caption(f"📅 Última actualización de tonos: {fecha_ultimo}")
    else:
      st.info("No hay datos capturados en Cumplimiento a Tonos.")

    st.divider()

    # --- SECCIÓN 5: REGISTRO DE DEFECTOS ---
    st.subheader("⚠️ Registro de Defectos, Porcentajes y Responsables")
    if not t5.empty:
      for index, row in t5.iterrows():
        fec = (
            row["FECHA_DEFECTO"].strftime("%d/%m/%Y")
            if pd.notnull(row["FECHA_DEFECTO"])
            else ""
        )
        def_nombre = row["DEFECTO"]
        mod = row["MODELO_DEFECTO"]
        fmt = row["FORMATO_DEFECTO"]
        mts = row["MTS2_DEFECTO"]
        resp = row["RESPONSABLE_DEFECTO"]
        pct = (
            row["PORCENTAJE_DEFECTO"] * 100
            if pd.notnull(row["PORCENTAJE_DEFECTO"])
            else 0
        )

        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 5px solid #e11d48; padding: 15px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 16px; color: #1e293b;">{def_nombre}</strong>
                        <span style="color: #64748b; font-size: 13px; margin-left: 10px;">({mod} - {fmt})</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 18px; font-weight: 700; color: #e11d48;">{pct:.2f}%</span>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 13px; color: #64748b;">
                    <span>📅 Fecha: {fec} | 🏭 Metros: {mts:,.2f} m²</span>
                    <span>👤 Responsable: <strong style="color: #0f172a;">{resp}</strong></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
      st.info("Sin registros de defectos capturados.")

    st.divider()

    # --- SECCIÓN 6: LIBERACIÓN DE PALLET (AF:AK) ---
    st.subheader("📦 Registro de Liberación de Pallets")
    if not t7.empty:
      for index, row in t7.iterrows():
        fec_pallet = (
            row["PALLET_FECHA"].strftime("%d/%m/%Y")
            if pd.notnull(row["PALLET_FECHA"])
            else ""
        )
        p_1ra = row["PALLET_1RA"]
        p_2da = row["PALLET_2DA"]
        p_3ra = row["PALLET_3RA"]
        p_rech = row["PALLET_RECHAZADO"]
        motivo_rech = row["PRINCIPAL_RECHAZO"]

        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 5px solid #2563eb; padding: 15px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 15px; color: #1e293b;">📅 Fecha de Liberación: {fec_pallet}</strong>
                    </div>
                    <div style="font-size: 13px; color: #64748b;">
                        Principal Rechazo: <strong style="color: #e11d48;">{motivo_rech}</strong>
                    </div>
                </div>
                <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 13px; color: #334155;">
                    <span>🥇 1ra: <strong>{p_1ra:,.0f}</strong></span>
                    <span>🥈 2da: <strong>{p_2da:,.0f}</strong></span>
                    <span>🥉 3ra: <strong>{p_3ra:,.0f}</strong></span>
                    <span>❌ Rechazado: <strong style="color: #e11d48;">{p_rech:,.0f}</strong></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
      st.info("Sin registros de liberación de pallets.")

    st.divider()

    # --- SECCIÓN 7: MODELOS EN PRUEBA Y AUTORIZADOS ---
    col_c, col_d = st.columns(2)
    with col_c:
      st.subheader("🔬 Modelos en Prueba")
      if not t3.empty:
        st.dataframe(t3, use_container_width=True, hide_index=True)
      else:
        st.info("Sin modelos en prueba registrados.")

    with col_d:
      st.subheader("✅ Modelos Autorizados")
      if not t4.empty:
        st.dataframe(t4, use_container_width=True, hide_index=True)
      else:
        st.info("Sin modelos autorizados registrados.")

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
