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

    df = pd.read_excel(
        archivo,
        sheet_name="REPORTE DE CALIDAD",
        header=8
    )

    df.columns = [
        str(c).strip().upper()
        for c in df.columns
    ]

    df = df.loc[
        :,
        ~df.columns.str.contains("UNNAMED")
    ]

    df = df[
        df["CALIDAD"].isin(
            [
                "PRIMERA",
                "SEGUNDA",
                "TERCERA",
                "QUINTA"
            ]
        )
    ]

    df["M2"] = pd.to_numeric(
        df["M2"],
        errors="coerce"
    )

    total = df["M2"].sum()

    primera = df.loc[
        df["CALIDAD"] == "PRIMERA",
        "M2"
    ].sum()

    segunda = df.loc[
        df["CALIDAD"] == "SEGUNDA",
        "M2"
    ].sum()

    quinta = df.loc[
        df["CALIDAD"] == "QUINTA",
        "M2"
    ].sum()

    calidad = (
        primera / total * 100
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Calidad General",
        f"{calidad:.2f}%"
    )

    c2.metric(
        "M² Totales",
        f"{total:,.0f}"
    )

    c3.metric(
        "M² Segunda",
        f"{segunda:,.0f}"
    )

    c4.metric(
        "M² Quinta",
        f"{quinta:,.0f}"
    )

    st.dataframe(
        df.head(20),
        use_container_width=True
    )
