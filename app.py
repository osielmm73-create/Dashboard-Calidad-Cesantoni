import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📊 Resumen",
                "🔥 Hornos",
                "🚨 Defectivos",
                "📞 Reclamaciones y Tonos"
            ]
        )

       with tab1:

    brecha = calidad - 94.5

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

    st.divider()

    planta = (
        df.groupby("PLANTA")
        .apply(
            lambda x:
            (
                x.loc[
                    x["CALIDAD"]=="PRIMERA",
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
        color="PLANTA",
        title="Calidad Acumulada por Planta"
    )

    fig3.update_traces(
        texttemplate='%{text:.2f}%',
        textposition='outside'
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

    st.header("🔥 Calidad y Producción por Horno")

    horno_resumen = (
        df.groupby(["HORNO", "CALIDAD"])["M2"]
        .sum()
        .reset_index()
    )

    pivot = horno_resumen.pivot_table(
        index="HORNO",
        columns="CALIDAD",
        values="M2",
        aggfunc="sum",
        fill_value=0
    )

    if "PRIMERA" not in pivot.columns:
        pivot["PRIMERA"] = 0

    pivot["TOTAL"] = pivot.sum(axis=1)

    pivot["CALIDAD"] = (
        pivot["PRIMERA"] /
        pivot["TOTAL"]
    ) * 100

    st.subheader("Calidad por Horno")

    cols = st.columns(len(pivot))

    for i, (horno, row) in enumerate(pivot.iterrows()):

        calidad_horno = row["CALIDAD"]

        if calidad_horno >= 94.5:
            color = "🟢"
        elif calidad_horno >= 92:
            color = "🟡"
        else:
            color = "🔴"

        cols[i].metric(
            f"Horno {horno}",
            f"{calidad_horno:.2f}%"
        )

        cols[i].write(color)

    st.divider()

    produccion = (
        df.groupby("HORNO")["M2"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        produccion,
        x="HORNO",
        y="M2",
        text="M2",
        color="HORNO",
        title="Producción Acumulada por Horno"
    )

    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=600,
        showlegend=False,
        yaxis_title="M²",
        xaxis_title="Horno"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    calidad_horno = (
        pivot.reset_index()
    )

    fig2 = px.bar(
        calidad_horno,
        x="HORNO",
        y="CALIDAD",
        text="CALIDAD",
        color="CALIDAD",
        title="Calidad Acumulada por Horno (%)"
    )

    fig2.update_traces(
        texttemplate='%{text:.2f}%',
        textposition='outside'
    )

    fig2.add_hline(
        y=94.5,
        line_dash="dash",
        line_color="red",
        annotation_text="Meta 94.5%"
    )

    fig2.update_layout(
        height=600,
        yaxis_title="% Calidad"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )
        with tab3:

            st.info(
                "Próximo paso: Pareto de defectos"
            )

        with tab4:

            st.info(
                "Próximo paso: Reclamaciones y tonos"
            )

    except Exception as e:

        st.error(
            f"Error al procesar archivo: {e}"
        )
