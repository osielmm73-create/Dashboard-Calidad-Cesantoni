import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title='Dashboard Calidad P1&P3 - Cesantoni', layout='wide'
)

# ==========================================
# PANEL DE CONTROL Y AUTENTICACIÓN
# ==========================================
st.sidebar.title('Panel de Control')

# Sistema de autenticación para modo edición
if 'authenticated' not in st.session_state:
  st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
  st.sidebar.subheader('Modo Edición / Acceso')
  user_password = st.sidebar.text_input('Contraseña', type='password')
  if st.sidebar.button('Iniciar Sesión'):
    # Aquí puedes cambiar la contraseña por la que uses en tu app
    if user_password == 'cesantoni2026':
      st.session_state['authenticated'] = True
      st.sidebar.success('¡Acceso concedido!')
      st.rerun()
    else:
      st.sidebar.error('Contraseña incorrecta')
else:
  st.sidebar.success('Modo Edición Activado 🔓')
  if st.sidebar.button('Cerrar Sesión'):
    st.session_state['authenticated'] = False
    st.rerun()

st.sidebar.markdown('---')
st.sidebar.subheader('Actualizar Base de Datos')
uploaded_file = st.sidebar.file_uploader(
    'Sube tu archivo Excel actualizado', type=['xlsx', 'xls']
)

# Título principal
st.title('CALIDAD P1&P3 - Sistema de Calidad Cesantoni')
st.markdown('**Todos somos calidad | Planta Zacatecas**')

if uploaded_file is not None:
  # Leer la hoja DASHBOARD
  df_dash = pd.read_excel(uploaded_file, sheet_name='DASHBOARD', header=None)

  # 1. Procesar la tabla de Calidad Diaria
  df_calidad = df_dash.iloc[2:25, 0:7].copy()
  df_calidad.columns = [
      'FECHA',
      'PRIMERA',
      'SEGUNDA',
      'TERCERA',
      'QUINTA',
      'MTS2_DIA',
      'CALIDAD_META',
  ]

  # Limpiar filas vacías o de totales
  df_calidad['FECHA'] = pd.to_datetime(df_calidad['FECHA'], errors='coerce')
  df_calidad = df_calidad.dropna(subset=['FECHA'])

  # Asegurar formato estrictamente numérico para evitar errores en Plotly
  for col in ['PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2_DIA', 'CALIDAD_META']:
    df_calidad[col] = pd.to_numeric(df_calidad[col], errors='coerce').fillna(0)

  # 2. Procesar la tabla de Garantías por Mes
  df_garantias = df_dash.iloc[2:14, 8:10].copy()
  df_garantias.columns = ['MES', 'GARANTIAS']

  meses_orden = [
      'ENERO',
      'FEBRERO',
      'MARZO',
      'ABRIL',
      'MAYO',
      'JUNIO',
      'JULIO',
      'AGOSTO',
      'SEPTIEMBRE',
      'OCTUBRE',
      'NOVIEMBRE',
      'DICIEMBRE',
  ]

  df_garantias['MES'] = (
      df_garantias['MES'].astype(str).str.strip().str.upper()
  )
  df_garantias['GARANTIAS'] = pd.to_numeric(
      df_garantias['GARANTIAS'], errors='coerce'
  ).fillna(0)

  df_garantias['MES'] = pd.Categorical(
      df_garantias['MES'], categories=meses_orden, ordered=True
  )
  df_garantias = df_garantias.sort_values('MES').reset_index(drop=True)

  st.success('¡Archivo cargado con éxito!')

  # ==========================================
  # VISUALIZACIÓN DE GRÁFICAS
  # ==========================================
  col1, col2 = st.columns(2)

  with col1:
    st.subheader('Calidad Diaria vs Calidad Meta')
    fig_calidad = px.line(
        df_calidad,
        x='FECHA',
        y=['PRIMERA', 'CALIDAD_META'],
        markers=True,
        labels={'value': 'Porcentaje', 'variable': 'Métrica', 'FECHA': 'Fecha'},
    )
    # Etiquetas de datos para la línea de calidad
    fig_calidad.update_traces(
        textposition='top center',
        texttemplate='%{y:.1%}',
        mode='lines+markers+text',
    )
    st.plotly_chart(fig_calidad, use_container_width=True)

  with col2:
    st.subheader('Garantías por Mes')
    fig_garantias = px.bar(
        df_garantias,
        x='MES',
        y='GARANTIAS',
        text='GARANTIAS',
        labels={'MES': 'Mes', 'GARANTIAS': 'Total Garantías'},
    )
    # Etiquetas de datos visibles sobre las barras y orden cronológico
    fig_garantias.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        marker_color='rgb(31, 119, 182)',
    )
    fig_garantias.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': meses_orden}
    )
    st.plotly_chart(fig_garantias, use_container_width=True)

else:
  st.info(
      'Por favor, sube tu archivo Excel actualizado en el panel de la'
      ' izquierda para visualizar el dashboard.'
  )
