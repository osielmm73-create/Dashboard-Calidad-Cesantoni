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

    st.divider()

# CALIDAD POR PLANTA

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

import plotly.express as px

fig_planta = px.bar(
    planta,
    x="PLANTA",
    y="CALIDAD",
    text="CALIDAD",
    color="PLANTA",
    title="Calidad Acumulada por Planta"
)

fig_planta.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_planta.add_hline(
    y=94.5,
    line_dash="dash",
    line_color="red",
    annotation_text="Meta 94.5%"
)

st.plotly_chart(
    fig_planta,
    use_container_width=True
)

st.divider()

# CALIDAD POR HORNO

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

pivot["CALIDAD"] = (
    pivot["PRIMERA"]
    /
    pivot["TOTAL"]
) * 100

st.subheader(
    "Calidad por Horno"
)

cols = st.columns(
    len(pivot)
)

for i, (horno, row) in enumerate(
    pivot.iterrows()
):

    valor = row["CALIDAD"]

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

st.divider()

# PRODUCCION POR HORNO

produccion = (
    df.groupby("HORNO")["M2"]
    .sum()
    .reset_index()
)

fig_horno = px.bar(
    produccion,
    x="HORNO",
    y="M2",
    text="M2",
    color="HORNO",
    title="Producción Acumulada por Horno"
)

fig_horno.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig_horno.update_layout(
    showlegend=False,
    height=600
)

st.plotly_chart(
    fig_horno,
    use_container_width=True
)
