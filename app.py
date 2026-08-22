import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Calidad Planta 1 y 3", layout="wide")

st.title("📊 Dashboard de Control de Calidad y Reclamaciones (P1 y P3)")

# Cargar archivo de forma dinámica
uploaded_file = st.file_uploader("Sube tu reporte Excel aquí:", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Cargar hoja de Calidad
        df_calidad = pd.read_excel(uploaded_file, sheet_name='REPORTE DE CALIDAD', skiprows=8)
        df_calidad.columns = df_calidad.columns.str.strip()
        df_calidad = df_calidad.dropna(subset=['PLANTA', 'CALIDAD', 'M2'])
        
        df_calidad['M2'] = pd.to_numeric(df_calidad['M2'], errors='coerce').fillna(0)
        df_calidad['PLANTA'] = df_calidad['PLANTA'].astype(str)
        df_calidad['HORNO'] = df_calidad['HORNO'].astype(str)
        df_calidad['DIA'] = pd.to_datetime(df_calidad['DIA'], errors='coerce')

        # Intentar cargar hoja de Reclamaciones
        try:
            df_reclamaciones = pd.read_excel(uploaded_file, sheet_name='RECLAMACIONES')
        except Exception:
            df_reclamaciones = pd.DataFrame()

        # Sidebar con Filtros
        st.sidebar.header("🔍 Filtros de Búsqueda")
        
        plantas_sel = st.sidebar.multiselect(
            "Planta:", 
            options=df_calidad['PLANTA'].unique(), 
            default=df_calidad['PLANTA'].unique()
        )
        
        meses_sel = st.sidebar.multiselect(
            "Mes:", 
            options=df_calidad['MES'].dropna().unique(), 
            default=df_calidad['MES'].dropna().unique()
        )

        # Aplicar filtros
        df_filtered = df_calidad[
            (df_calidad['PLANTA'].isin(plantas_sel)) & 
            (df_calidad['MES'].isin(meses_sel))
        ]

        # Creación de Pestañas
        tab1, tab2, tab3 = st.tabs(["📊 Métricas de Calidad", "🔥 Análisis por Horno y Modelo", "📋 Reclamaciones y Registro"])

        with tab1:
            # Métricas
            total_m2 = df_filtered['M2'].sum()
            m2_primera = df_filtered[df_filtered['CALIDAD'].astype(str).str.upper() == 'PRIMERA']['M2'].sum()
            pct_calidad = (m2_primera / total_m2 * 100) if total_m2 > 0 else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("Producción Total (m²)", f"{total_m2:,.2f}")
            c2.metric("Producción Primera (m²)", f"{m2_primera:,.2f}")
            c3.metric("% Calidad (Primera)", f"{pct_calidad:.2f}%")

            st.markdown("---")

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.subheader("Distribución por Calidad")
                fig_calidad = px.pie(
                    df_filtered, 
                    values='M2', 
                    names='CALIDAD', 
                    title='Proporción por Tipo de Calidad',
                    hole=0.4
                )
                st.plotly_chart(fig_calidad, use_container_width=True)

            with col_g2:
                st.subheader("Tendencia Diaria de Producción")
                df_diario = df_filtered.groupby(['DIA', 'CALIDAD'])['M2'].sum().reset_index()
                fig_line = px.line(
                    df_diario, 
                    x='DIA', 
                    y='M2', 
                    color='CALIDAD', 
                    markers=True,
                    title='Evolución Diaria (m²)'
                )
                st.plotly_chart(fig_line, use_container_width=True)

        with tab2:
            st.subheader("Producción por Horno y Tipo de Calidad")
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

            st.subheader("Top 10 Modelos Producidos")
            df_modelo = df_filtered.groupby('MODELO')['M2'].sum().reset_index().sort_values(by='M2', ascending=False).head(10)
            fig_modelo = px.bar(
                df_modelo, 
                x='M2', 
                y='MODELO', 
                orientation='h',
                title='Top Modelos por Volumen (m²)'
            )
            st.plotly_chart(fig_modelo, use_container_width=True)

        with tab3:
            st.subheader("Registro Detallado de Calidad")
            st.dataframe(df_filtered[['PLANTA', 'MES', 'HORNO', 'MODELO', 'FORMATO', 'CALIDAD', 'M2', 'DIA']])

            if not df_reclamaciones.empty:
                st.subheader("Reclamaciones Mensuales")
                st.dataframe(df_reclamaciones)

    except Exception as e:
        st.error(f"Error al procesar el archivo Excel: {e}")
else:
    st.info("👋 Por favor sube tu archivo Excel en el cargador para refrescar los datos automáticamente.")
