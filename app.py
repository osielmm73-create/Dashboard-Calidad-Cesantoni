import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Cargar el archivo Excel
file_path = 'REPORTE P1 Y P3 AGOSTO 2026.xlsx'

# Leer la hoja DASHBOARD
df_dash = pd.read_excel(file_path, sheet_name='DASHBOARD', header=None)

# 1. Procesar la tabla de Calidad Diaria (Columnas 0 a 6, filas desde la 2 en adelante)
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

# Asegurar formato numérico
for col in ['PRIMERA', 'SEGUNDA', 'TERCERA', 'QUINTA', 'MTS2_DIA']:
  df_calidad[col] = pd.to_numeric(df_calidad[col], errors='coerce').fillna(0)

# 2. Procesar la tabla de Garantías por Mes (Columnas 8 y 9, filas 2 a 13)
df_garantias = df_dash.iloc[2:14, 8:10].copy()
df_garantias.columns = ['MES', 'GARANTIAS']

# Definir orden cronológico estricto de meses
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

# Ordenar según el orden cronológico
df_garantias['MES'] = pd.Categorical(
    df_garantias['MES'], categories=meses_orden, ordered=True
)
df_garantias = df_garantias.sort_values('MES').reset_index(drop=True)

# ==========================================
# 3. CONSTRUCCIÓN DE GRÁFICAS CON ETIQUETAS
# ==========================================

st.subheader('Calidad Diaria vs Calidad Meta')
fig_calidad = px.line(
    df_calidad,
    x='FECHA',
    y=['PRIMERA', 'CALIDAD_META'],
    markers=True,
    labels={'value': 'Porcentaje', 'variable': 'Métrica', 'FECHA': 'Fecha'},
)
# Agregar etiquetas de datos en la línea de primera calidad
fig_calidad.update_traces(
    textposition='top center',
    texttemplate='%{y:.2%}',
    mode='lines+markers+text',
)
st.plotly_chart(fig_calidad, use_container_width=True)

st.subheader('Garantías por Mes (Ordenado)')
fig_garantias = px.bar(
    df_garantias,
    x='MES',
    y='GARANTIAS',
    text='GARANTIAS',
    labels={'MES', 'Mes', 'GARANTIAS', 'Total Garantías'},
)
# Mostrar etiquetas de datos sobre las barras y asegurar el orden correcto de los meses
fig_garantias.update_traces(
    texttemplate='%{text}', textposition='outside', marker_color='rgb(31, 119, 182)'
)
fig_garantias.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': meses_orden})
st.plotly_chart(fig_garantias, use_container_width=True)
