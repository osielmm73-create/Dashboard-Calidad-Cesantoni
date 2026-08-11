import streamlit as st
import pandas as pd
import plotly.express as px

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

        df = df[
            df["CALIDAD"].isin(
                ["PRIMERA", "SEGUNDA", "TERCERA", "QUINTA"]
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
            if total > 0 else 0
        )

        brecha = calidad - 94.5

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📊 Resumen",
                "🔥 Hornos",
                "🚨 Defectivos",
                "📞 Reclamaciones y Tonos"
            ]
        )

        with tab1:

            c1, c2, c3, c4, c5, c6 = st.columns(6)

            c1.metric(
                "Calidad General",
                f"{calidad:.2f}%"
            )

            c2.metric(
                "Meta",
                "94.5%"
            )

            c3.metric(
                "Brecha",
                f"{brecha:.2f}%"
            )

            c4.metric(
                "M² Totales",
                f"{total:,.0f}"
            )

            c5.metric(
                "M² Segunda",
                f"{segunda:,.0f}"
            )

            c6.metric(
                "M² Quinta",
                f"{quinta:,.0f}"
            )

            planta = (
                df.groupby("PLANTA")
                .apply(
                    lambda x:
                    (
                        x.loc[
                            x["CALIDAD"] == "PRIMERA",
                            "M2"
                        ].sum()
                        /
                        x["M2"].sum()
                    ) * 100
                )
                .reset_index(name="CALIDAD")
            )

            fig3 = px.bar(
                planta,
                x="PLANTA",
                y="CALIDAD",
                text="CALIDAD",
                title="Calidad Acumulada por Planta"
            )

            fig3.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside"
            )

            fig3.add_hline(
                y=94.5,
                line_dash="dash",
                line_color="red"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        with tab2:

            horno_resumen = (
                df.groupby(
                    ["HORNO", "CALIDAD"]
                )["M2"]
                .sum()
                .reset_index()
            )

            pivot = horno_resumen.pivot_table(
                index="HORNO",
                columns="CALIDAD",
                values="M2",
                fill_value=0
            )

            if "PRIMERA" not in pivot.columns:
                pivot["PRIMERA"] = 0

            pivot["TOTAL"] = pivot.sum(axis=1)

            pivot["CALIDAD_%"] = (
                pivot["PRIMERA"]
                /
                pivot["TOTAL"]
            ) * 100

            st.subheader(
                "Calidad Acumulada por Horno"
            )

            cols = st.columns(
                len(pivot)
            )

            for i, (horno, row) in enumerate(
                pivot.iterrows()
            ):

                valor = row["CALIDAD_%"]

                if valor >= 94.5:
                    semaforo = "🟢"
                elif valor >= 92:
                    semaforo = "🟡"
                else:
                    semaforo = "🔴"

                cols[i].metric(
                    f"Horno {horno}",
                    f"{valor:.2f}%"
                )

                cols[i].write(
                    semaforo
                )

            produccion = (
                df.groupby("HORNO")["M2"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                produccion,
                x="HORNO",
      
