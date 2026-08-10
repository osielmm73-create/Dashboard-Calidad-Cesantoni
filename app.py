import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Calidad",
    layout="wide"
)

st.title("📊 Dashboard de Calidad")

archivo = st.file_uploader(
    "Arrastra tu archivo Excel aquí",
    type=["xlsx"]
)

if archivo:

    try:
        excel = pd.ExcelFile(archivo)

        st.write("Hojas encontradas:")
        st.write(excel.sheet_names)

        hoja = excel.sheet_names[0]

        df = pd.read_excel(
            archivo,
            sheet_name=hoja
        )

        st.success(f"Hoja cargada: {hoja}")

        st.write("Columnas detectadas:")
        st.write(df.columns.tolist())

        st.write(df.head())

    except Exception as e:
        st.error(f"Error al leer archivo: {e}")
