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

        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.loc[:, ~df.columns.str.contains("UNNAMED", na=False)]

        df = df[df["CALIDAD"].isin(["PRIMERA","SEGUNDA","TERCERA","QUINTA"])]
        df["M2"] = pd.to_numeric(df["M2"], errors="coerce")

        total = df["M2"].sum()
        primera = df.loc[df["CALIDAD"]=="PRIMERA","M2"].sum()
        segunda = df.loc[df["CALIDAD"]=="SEGUNDA","M2"].sum()
        quinta = df.loc[df["CALIDAD"]=="QUINTA","M2"].sum()

        calidad = primera / total * 100 if total > 0 else 0
        brecha = calidad - 94.5

        st.header("📊 Resumen Ejecutivo")

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Calidad General", f"{calidad:.2f}%")
        c2.metric("Meta", "94.50%")
        c3.metric("Brecha", f"{brecha:.2f}%")
        c4.metric("M² Totales", f"{total:,.0f}")
        c5.metric("M² Segunda + Quinta", f"{(segunda + quinta):,.0f}")

        st.divider()

        st.header("🏭 Calidad por Planta")

        planta = (
            df.groupby("PLANTA")
            .apply(lambda x:(x.loc[x["CALIDAD"]=="PRIMERA","M2"].sum()/x["M2"].sum())*100)
            .reset_index(name="CALIDAD")
        )

        fig_planta = px.bar(planta,x="PLANTA",y="CALIDAD",text="CALIDAD",title="Calidad Acumulada por Planta")
        fig_planta.update_traces(texttemplate="%{text:.2f}%",textposition="outside")
        fig_planta.add_hline(y=94.5,line_dash="dash",line_color="red",annotation_text="Meta 94.5%")
        st.plotly_chart(fig_planta,use_container_width=True)

        st.divider()

        st.header("🔥 Calidad por Horno")

        horno_resumen = df.groupby(["HORNO","CALIDAD"])["M2"].sum().reset_index()
        pivot = horno_resumen.pivot_table(index="HORNO",columns="CALIDAD",values="M2",fill_value=0)

        if "PRIMERA" not in pivot.columns:
            pivot["PRIMERA"] = 0

        pivot["TOTAL"] = pivot.sum(axis=1)
        pivot["CALIDAD_PCT"] = (pivot["PRIMERA"] / pivot["TOTAL"]) * 100
        pivot = pivot[pivot["TOTAL"] > 0]

        cols = st.columns(len(pivot))

        for i,(horno,row) in enumerate(pivot.iterrows()):
            valor = row["CALIDAD_PCT"]
            if valor >= 94.5:
                semaforo = "🟢"
            elif valor >= 92:
                semaforo = "🟡"
            else:
                semaforo = "🔴"

            cols[i].metric(f"Horno {horno}", f"{valor:.2f}%")
            cols[i].markdown(f"## {semaforo}")

        fig_calidad = px.bar(pivot.reset_index(),x="HORNO",y="CALIDAD_PCT",text="CALIDAD_PCT",title="Calidad Acumulada por Horno (%)")
        fig_calidad.update_traces(texttemplate="%{text:.2f}%",textposition="outside")
        fig_calidad.add_hline(y=94.5,line_dash="dash",line_color="red",annotation_text="Meta 94.5%")
        st.plotly_chart(fig_calidad,use_container_width=True)

        st.divider()

        st.header("📈 Producción por Horno")

        produccion = df.groupby("HORNO")["M2"].sum().reset_index()
        produccion = produccion[produccion["M2"] > 0]

        fig_horno = px.bar(produccion,x="HORNO",y="M2",text="M2",title="Producción Acumulada por Horno")
        fig_horno.update_traces(texttemplate="%{text:,.0f}",textposition="outside")
        fig_horno.update_layout(height=600)
        st.plotly_chart(fig_horno,use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
