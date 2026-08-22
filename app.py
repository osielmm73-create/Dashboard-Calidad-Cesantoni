import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Calidad P1 y P3", layout="wide")

st.title("📊 Dashboard de Control de Calidad (P1 / P3)")

# Cargador de archivos
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Cargar datos omitiendo las filas de encabezado secundario
        df = pd.read_excel(uploaded_file, sheet_name='REPORTE DE CALIDAD', skiprows=8)
        
        # Limpiar nombres de columnas (quitar espacios en blanco)
        df.columns = df.columns.str.strip()
        
        # Filtrar columnas esenciales
        df = df.dropna(subset=['PLANTA', 'CALIDAD', 'M2'])
        
        # Convertir tipos de datos
        df['M2'] = pd.to_numeric(df['M2'], errors='coerce').fillna(0)
        df['PLANTA'] = df['PLANTA'].astype(str)
        df['HORNO'] = df['HORNO'].astype(str)
        df['DIA'] = pd.to_datetime(df['DIA'], errors='coerce')

        # --- FILTROS DE SIDEBAR ---
        st.sidebar.header("Filtros")
        
        plantas = st.sidebar.multiselect("Planta:", options=df['PLANTA'].unique(), default=df['PLANTA'].unique())
        meses = st.sidebar.multiselect("Mes:", options=df['MES'].dropna().unique(), default=df['MES'].dropna().unique())
        
        # Aplicar filtros
        df_filtered = df[(df['PLANTA'].isin(plantas)) & (df['MES'].isin(meses))]

        # --- MÉTRICAS CLAVE ---
        total_m2 = df_filtered['M2'].sum()
        m2_primera = df_filtered[df_filtered['CALIDAD'].astype(str).str.upper() == 'PRIMERA']['M2'].sum()
        pct_calidad = (m2_primera / total_m2 * 100) if total_m2 > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Producción Total (m²)", f"{total_m2:,.2f}")
        col2.metric("Producción Primera (m²)", f"{m2_primera:,.2f}")
        col3.metric("% Calidad (Primera)", f"{pct_calidad:.2f}%")

        st.markdown("---")

        # --- GRÁFICOS ---
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("Distribución por Calidad")
            fig_calidad = px.pie(
                df_filtered, 
                values='M2', 
                names='CALIDAD', 
                title='Proporción de Metros Cuadrados por Calidad',
                hole=0.4
            )
            st.plotly_chart(fig_calidad, use_container_width=True)

        with g2:
            st.subheader("Producción por Horno")
            df_horno = df_filtered.groupby(['HORNO', 'CALIDAD'])['M2'].sum().reset_index()
            fig_horno = px.bar(
                df_horno, 
                x='HORNO', 
                y='M2', 
                color='CALIDAD', 
                barmode='stack',
                title='Volumen de Producción por Horno'
            )
            st.plotly_chart(fig_horno, use_container_width=True)

        # Gráfico de tendencia diaria
        st.subheader("Tendencia Diaria de Producción (m²)")
        df_diario = df_filtered.groupby(['DIA', 'CALIDAD'])['M2'].sum().reset_index()
        fig_line = px.line(
            df_diario, 
            x='DIA', 
            y='M2', 
            color='CALIDAD', 
            markers=True,
            title='Evolución Diaria por Calidad'
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # --- TABLA DE DATOS DETALLADA ---
        with st.expander("Ver tabla de datos procesados"):
            st.dataframe(df_filtered[['PLANTA', 'MES', 'HORNO', 'MODELO', 'FORMATO', 'CALIDAD', 'M2', 'DIA']])

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube el archivo Excel .xlsx para cargar la información automáticamente.")
