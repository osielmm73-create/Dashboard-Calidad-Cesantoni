import streamlit as st
import pandas as pd

st.title("Explorador de Excel")

archivo = st.file_uploader("Sube el Excel", type=["xlsx"])

if archivo:

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

    st.write(df.head(50))
