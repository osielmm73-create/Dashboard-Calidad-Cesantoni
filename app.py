import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Calidad",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Ejecutivo de Calidad")

archivo = st.file_uploader(
    "Sube tu archivo Excel",
    type=["xlsx"]
)

if archivo:

    try:

        df = pd.read_excel(
            archivo,
            sheet_name="REPORTE DE CALIDAD",
            header=8
        )

        df.columns = [
            str(c).strip().upper()
            for c in df.columns
        ]

        st.success("Archivo cargado correctamente")

        st.write("Columnas detectadas:")

        st.write(df.columns.tolist())

        st.write("Primeras filas:")

        st.dataframe(df.head(10))

    except Exception as e:

        st.error(f"Error: {e}")
