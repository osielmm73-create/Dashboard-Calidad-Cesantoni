import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Calidad Cesantoni",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Ejecutivo de Calidad")

archivo = st.file_uploader(
    "Sube tu archivo Excel",
    type=["xlsx"]
)

if archivo:

    excel = pd.ExcelFile(archivo)

    st.success("Archivo cargado correctamente")

    st.write("Hojas encontradas:")
    st.write(excel.sheet_names)

    try:

        df = pd.read_excel(
            archivo,
            sheet_name="REPORTE DE CALIDAD",
            header=8
        )

        st.subheader("Diagnóstico")

        st.write("Columnas detectadas:")

        st.write(df.columns.tolist())

        st.write(df.head(10))

    except Exception as e:

        st.error(f"Error leyendo REPORTE DE CALIDAD: {e}")
