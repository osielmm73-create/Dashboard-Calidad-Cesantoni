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

        excel = pd.ExcelFile(archivo)

        st.success("Archivo cargado correctamente")

        st.write("Hojas encontradas:")

        st.write(excel.sheet_names)

    except Exception as e:

        st.error(str(e))
