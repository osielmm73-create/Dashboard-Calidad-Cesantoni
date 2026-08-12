import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Calidad",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Calidad")

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

        # Limpiar nombres de columnas
        df.columns = [
            str(c).strip().upper()
            for c in df.columns
        ]

        # Eliminar columnas UNNAMED
        df = df.loc[
            :,
            ~df.columns.str.contains("UNNAMED")
        ]

        st.write("Columnas encontradas:")

        st.write(df.columns.tolist())

        columnas = [
            "PLANTA",
            "MES",
            "HORNO",
            "DIA",
            "MODELO",
            "FORMATO",
            "CALIDAD",
            "M2"
        ]

        df = df[
            [c for c in columnas if c in df.columns]
        ].copy()

        st.success(
            "Datos limpiados correctamente"
        )

        st.subheader("Vista previa")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Error: {e}"
        )
