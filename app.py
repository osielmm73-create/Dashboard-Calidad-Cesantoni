import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Calidad y Defectos",
    layout="wide"
)

st.title("📊 Panel de Control: Calidad y Defectos")

# 1. Cargar Datos desde el Excel
@st.cache_data(ttl=60)
def cargar_datos():
    # Reemplaza con la ruta real o el nombre de tu archivo de Excel
    archivo_excel = "REPORTE_CALIDAD.xlsx" 
    
    # Lectura de la pestaña de DEFECTOS
    df_def = pd.read_excel(archivo_excel, sheet_name="DEFECTIVOS")
    
    # Lectura de la pestaña de CALIDAD / DASHBOARD
    df_cal = pd.read_excel(archivo_excel, sheet_name="REPORTE DE CALIDAD")
    
    # Limpieza de nombres de columnas
    df_def.columns = df_def.columns.str.strip().str.upper()
    df_cal.columns = df_cal.columns.str.strip().str.upper()
    
    # Asegurar formato de fecha
    df_def['DIA'] = pd.to_datetime(df_def['DIA'], errors='coerce')
    df_cal['DIA'] = pd.to_datetime(df_cal['DIA'], errors='coerce')
    
    # Filtrar filas sin fecha
    df_def = df_def.dropna(subset=['DIA'])
    df_cal = df_cal.dropna(subset=['DIA'])
    
    return df_def, df_cal

try:
    df_defectos, df_calidad = cargar_datos()

    # 2. Identificar el Último Día Capturado
    ultimo_dia = df_defectos['DIA'].max()
    mes_actual = ultimo_dia.month
    anio_actual = ultimo_dia.year

    st.sidebar.info(f"📅 **Último día capturado:** {ultimo_dia.strftime('%d/%m/%Y')}")

    # 3. Filtrado de Datos (Día Actual vs Acumulado Mes)
    # Día Actual
    df_dia = df_defectos[df_defectos['DIA'] == ultimo_dia]
    df_cal_dia = df_calidad[df_calidad['DIA'] == ultimo_dia]

    # Acumulado Mes
    df_mes = df_defectos[(df_defectos['DIA'].dt.month == mes_actual) & (df_defectos['DIA'].dt.year == anio_actual)]
    df_cal_mes = df_calidad[(df_calidad['DIA'].dt.month == mes_actual) & (df_calidad['DIA'].dt.year == anio_actual)]

    # 4. Cálculos de Métricas
    # A. M2 Afectados
    mts2_dia = df_dia['MTS²'].sum() if 'MTS²' in df_dia.columns else 0.0
    mts2_mes = df_mes['MTS²'].sum() if 'MTS²' in df_mes.columns else 0.0

    # B. Principal Rechazo (Pallet con mayor causa de rechazo)
    if 'DEFECTO2' in df_mes.columns and not df_mes.empty:
        principal_rechazo_dia = df_dia.groupby('DEFECTO2')['MTS²'].sum().idxmax() if not df_dia.empty else "N/A"
        principal_rechazo_mes = df_mes.groupby('DEFECTO2')['MTS²'].sum().idxmax()
    else:
        principal_rechazo_dia, principal_rechazo_mes = "N/A", "N/A"

    # C. Pallets Liberados
    pallets_lib_dia = df_cal_dia['PALLETS_LIBERADOS'].sum() if 'PALLETS_LIBERADOS' in df_cal_dia.columns else 0
    pallets_lib_mes = df_cal_mes['PALLETS_LIBERADOS'].sum() if 'PALLETS_LIBERADOS' in df_cal_mes.columns else 0

    # D. Garantías y Cumplimiento a Tono
    cumplimiento_tono = df_cal_mes['CUMPLIMIENTO_TONO_%'].mean() if 'CUMPLIMIENTO_TONO_%' in df_cal_mes.columns else 0.0
    garantias_total = df_cal_mes['GARANTIAS_CANTIDAD'].sum() if 'GARANTIAS_CANTIDAD' in df_cal_mes.columns else 0

    # 5. Despliegue de KPIs en Pantalla
    st.subheader(f"📌 Métricas al Día: {ultimo_dia.strftime('%d/%m/%Y')} | Acumulado del Mes")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Principal Rechazo (Mes)", 
            value=str(principal_rechazo_mes),
            delta=f"Día: {principal_rechazo_dia}",
            delta_color="off"
        )

    with col2:
        st.metric(
            label="M² Afectados (Acumulado)", 
            value=f"{mts2_mes:,.2f} m²", 
            delta=f"Día: {mts2_dia:,.2f} m²"
        )

    with col3:
        st.metric(
            label="Pallets Liberados (Acumulado)", 
            value=f"{int(pallets_lib_mes):,}", 
            delta=f"Día: {int(pallets_lib_dia):,}"
        )

    with col4:
        st.metric(
            label="Cumplimiento a Tono", 
            value=f"{cumplimiento_tono:.1f}%", 
            delta=f"Garantías: {garantias_total}"
        )

    st.markdown("---")

    # 6. Tabla de Registros del Día Capturado
    st.subheader(f"📋 Registros de Defectos del Día ({ultimo_dia.strftime('%d/%m/%Y')})")
    
    # Formatear la vista de la tabla
    columnas_mostrar = ['DIA', 'MODELO', 'FORMATO', 'HORNO', 'DEFECTO2', 'MTS²', 'RESPONSABLE', 'PORCENTAJE DEL AREA']
    columnas_existentes = [col for col in columnas_mostrar if col in df_dia.columns]

    df_vista_dia = df_dia[columnas_existentes].copy()
    if 'DIA' in df_vista_dia.columns:
        df_vista_dia['DIA'] = df_vista_dia['DIA'].dt.strftime('%d/%m/%Y')
        
    st.dataframe(df_vista_dia, use_container_width=True)

    # 7. Resumen de Defectos por Responsable / Área (Acumulado Mes)
    st.subheader("📉 Acumulado de M² Afectados por Área / Responsable (Mes)")
    if 'RESPONSABLE' in df_mes.columns and 'MTS²' in df_mes.columns:
        resumen_area = df_mes.groupby('RESPONSABLE')['MTS²'].sum().reset_index()
        resumen_area = resumen_area.sort_values(by='MTS²', ascending=False)
        st.bar_chart(data=resumen_area, x='RESPONSABLE', y='MTS²')

except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo de Excel. Verifica la ruta en la función `cargar_datos()`.")
except Exception as e:
    st.error(f"❌ Ocurrió un error al procesar los datos: {e}")
