import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Explorador de Excel")

archivo = st.file_uploader(
    "Sube el Excel",
    type=["xlsx"]
)

if archivo is not None:

    try:

        excel = pd.ExcelFile(archivo)

        hoja = st.selectbox(
            "Hoja",
            excel.sheet_names
        )

        df = pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=None
        )

        st.write(f"Filas: {df.shape[0]}")
        st.write(f"Columnas: {df.shape[1]}")

        st.subheader("Primeras 50 filas")

        st.dataframe(
            df.head(50),
            use_container_width=True
        )

    except Exception as e:

        st.error(str(e))
