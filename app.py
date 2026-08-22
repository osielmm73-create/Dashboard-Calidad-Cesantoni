import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(page_title="DASHBOARD - SISTEMA DE CALIDAD", layout="wide")

# CSS Personalizado para estilo Dashboard Industrial
st.markdown("""
<style>
    .main {
        background-color: #f4f6f9;
    }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        text-align: center;
        border-top: 4px solid #10b981;
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 13px;
        font-weight: 700;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        margin: 5px 0;
    }
    .kpi-sub {
        font-size: 11px;
        color: #6b7280;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado principal estilo corporativo
st.markdown("""
<div style="background-color: #111827; padding: 15px 25px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h2 style="color: #ffffff; margin: 0; font-weight: 800; font-size: 22px;">DASHBOARD - SISTEMA DE CALIDAD</h2>
        <p style="color: #9ca3af; margin: 0; font-size: 13px;">PRODUCTO TERMINADO – PISO CERÁMICO (PLANTA 1 Y 3)</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Cargar archivo Excel
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel para actualizar los datos:", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df_calidad = pd.read_excel(uploaded_file, sheet_name='REPORTE DE CALIDAD', skiprows=8)
        df_calidad.columns = df_calidad.columns.str.strip()
        df_calidad = df_calidad.dropna(subset=['PLANTA', 'CALIDAD', 'M2'])
        
        df_calidad['M2'] = pd.to_numeric(df_calidad['M2'], errors='coerce').fillna(0)
        df_calidad['PLANTA'] = df_calidad['PLANTA'].astype(str)
        df_calidad['HORNO'] = df_calidad['HORNO'].astype(str)
        df_calidad['DIA'] = pd.to_datetime(df_calidad['DIA'], errors='coerce')

        # Sidebar Filtros
        st.sidebar.markdown("### 🔍 FILTROS")
        plantas_sel = st.sidebar.multiselect("Planta:", options=df_calidad['PLANTA'].unique(), default=df_calidad['PLANTA'].unique())
        meses_sel = st.sidebar.multiselect("Mes:", options=df_calidad['MES'].dropna().unique(), default=df_calidad['MES'].dropna().unique())

        df_filtered = df_calidad[(df_calidad['PLANTA'].isin(plantas_sel)) & (df_calidad['MES'].isin(meses_sel))]

        # Cálculos de Métricas principales
        total_m2 = df_filtered['M2'].sum()
        m2_primera = df_filtered[df_filtered['CALIDAD'].astype(str).str.upper() == 'PRIMERA']['M2'].sum()
        m2_segunda = df_filtered[df_filtered['CALIDAD'].astype(str).str.upper() == 'SEGUNDA']['M2'].sum()
        m2_tercera = df_filtered[df_filtered['CALIDAD'].astype(str).str.upper() == 'TERCERA']['M2'].sum()
        m2_quinta = df_filtered[df_filtered['CALIDAD'].astype(str).str.upper() == 'QUINTA']['M2'].sum()
        
        pct_primera = (m2_primera / total_m2 * 100) if total_m2 > 0 else 0
        pct_segunda = (m2_segunda / total_m2 * 100) if total_m2 > 0 else 0
        pct_tercera = (m2_tercera / total_m2 * 100) if total_m2 > 0 else 0
        pct_quinta = (m2_quinta / total_m2 * 100) if total_m2 > 0 else 0

        # --- FILA 1: KPIs Estilo Dashboard Imagen ---
        k1, k2, k3, k4, k5 = st.columns(5)

        with k1:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #10b981;">
                <div class="kpi-title">Calidad de Primera</div>
                <div class="kpi-value" style="color: #10b981;">{pct_primera:.1f}%</div>
                <div class="kpi-sub">Meta ≥ 95% ({m2_primera:,.0f} m²)</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #ef4444;">
                <div class="kpi-title">Segunda Calidad</div>
                <div class="kpi-value" style="color: #ef4444;">{pct_segunda:.1f}%</div>
                <div class="kpi-sub">Meta ≤ 3% ({m2_segunda:,.0f} m²)</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #f59e0b;">
                <div class="kpi-title">Tercera Calidad</div>
                <div class="kpi-value" style="color: #f59e0b;">{pct_tercera:.1f}%</div>
                <div class="kpi-sub">Meta ≤ 1% ({m2_tercera:,.0f} m²)</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #3b82f6;">
                <div class="kpi-title">Quinta Calidad</div>
                <div class="kpi-value" style="color: #3b82f6;">{pct_quinta:.1f}%</div>
                <div class="kpi-sub">Rechazo ({m2_quinta:,.0f} m²)</div>
            </div>
            """, unsafe_allow_html=True)

        with k5:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #8b5cf6;">
                <div class="kpi-title">Producción Total</div>
                <div class="kpi-value" style="color: #8b5cf6;">{total_m2:,.0f}</div>
                <div class="kpi-sub">Metros Cuadrados (m²)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- FILA 2: GRÁFICOS PRINCIPALES ---
        col_g1, col_g2 = st.columns([1, 1])

        with col_g1:
            st.subheader("📊 Distribución de Calidad por Modelo")
            df_mod = df_filtered.groupby(['MODELO', 'CALIDAD'])['M2'].sum().reset_index()
            fig_bar = px.bar(
                df_mod, 
                x='M2', 
                y='MODELO', 
                color='CALIDAD', 
                orientation='h',
                color_discrete_map={'PRIMERA': '#10b981', 'SEGUNDA': '#f59e0b', 'TERCERA': '#ef4444', 'QUINTA': '#6b7280'},
                title="Volumen Producido por Modelo y Calidad"
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            st.subheader("🎯 Proporción Global de Calidad")
            df_pie = df_filtered.groupby('CALIDAD')['M2'].sum().reset_index()
            fig_pie = px.pie(
                df_pie, 
                values='M2', 
                names='CALIDAD', 
                hole=0.6,
                color='CALIDAD',
                color_discrete_map={'PRIMERA': '#10b981', 'SEGUNDA': '#f59e0b', 'TERCERA': '#ef4444', 'QUINTA': '#6b7280'}
            )
            fig_pie.update_layout(
                annotations=[dict(text=f"Total<br>{total_m2:,.0f} m²", x=0.5, y=0.5, font_size=16, showarrow=False)],
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- FILA 3: TENDENCIA Y RENDIMIENTO POR HORNO ---
        col_g3, col_g4 = st.columns([1, 1])

        with col_g3:
            st.subheader("📈 Tendencia Diaria de Calidad de Primera (%)")
            df_diario_primera = df_filtered.groupby(['DIA', 'CALIDAD'])['M2'].sum().unstack(fill_value=0)
            if 'PRIMERA' in df_diario_primera.columns:
                df_diario_primera['% Primera'] = (df_diario_primera['PRIMERA'] / df_diario_primera.sum(axis=1)) * 100
                fig_line = px.line(
                    df_diario_primera.reset_index(), 
                    x='DIA', 
                    y='% Primera', 
                    markers=True,
                    title="Evolución % Primera Calidad por Día"
                )
                fig_line.update_traces(line_color='#10b981', line_width=3)
                fig_line.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Meta (95%)")
                fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
                st.plotly_chart(fig_line, use_container_width=True)

        with col_g4:
            st.subheader("🔥 Rendimiento de Calidad por Horno")
            df_horno = df_filtered.groupby(['HORNO', 'CALIDAD'])['M2'].sum().reset_index()
            fig_horno = px.bar(
                df_horno, 
                x='HORNO', 
                y='M2', 
                color='CALIDAD', 
                barmode='group',
                color_discrete_map={'PRIMERA': '#10b981', 'SEGUNDA': '#f59e0b', 'TERCERA': '#ef4444', 'QUINTA': '#6b7280'},
                title="Producción por Horno y Calidad"
            )
            fig_horno.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_horno, use_container_width=True)

        # --- TABLA DETALLADA DE REGISTROS ---
        with st.expander("📋 Ver Registro Completo de Producción"):
            st.dataframe(df_filtered[['PLANTA', 'MES', 'HORNO', 'MODELO', 'FORMATO', 'CALIDAD', 'M2', 'DIA']], use_container_width=True)

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("👋 Por favor sube tu archivo Excel en el botón superior para actualizar el tablero interactivo.")
