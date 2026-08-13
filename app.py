import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Calidad Cesantoni", page_icon="📊", layout="wide")
st.title("📊 Dashboard Ejecutivo de Calidad")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo, sheet_name="REPORTE DE CALIDAD", header=8)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.loc[:, ~df.columns.str.contains("UNNAMED", na=False)]

        df = df[df["CALIDAD"].isin(["PRIMERA", "SEGUNDA", "TERCERA", "QUINTA"])]
        df["M2"] = pd.to_numeric(df["M2"], errors="coerce")

        total = df["M2"].sum()
        primera = df.loc[df["CALIDAD"] == "PRIMERA", "M2"].sum()
        segunda = df.loc[df["CALIDAD"] == "SEGUNDA", "M2"].sum()
        quinta = df.loc[df["CALIDAD"] == "QUINTA", "M2"].sum()

        calidad = (primera / total * 100) if total else 0
        brecha = calidad - 94.5

        t1, t2 = st.tabs(["📊 Resumen", "🏭 Plantas y Hornos"])

        with t1:
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Calidad General", f"{calidad:.2f}%")
            c2.metric("Meta", "94.50%")
            c3.metric("Brecha", f"{brecha:.2f}%")
            c4.metric("M² Totales", f"{total:,.0f}")
            c5.metric("M² Segunda + Quinta", f"{(segunda+quinta):,.0f}")

            planta = (
                df.groupby("PLANTA")
                .apply(lambda x:(x.loc[x['CALIDAD']=='PRIMERA','M2'].sum()/x['M2'].sum())*100)
                .reset_index(name='CALIDAD')
            )

            fig = px.bar(planta,x='PLANTA',y='CALIDAD',text='CALIDAD',title='Calidad Acumulada por Planta')
            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig.add_hline(y=94.5,line_dash='dash',line_color='red',annotation_text='Meta 94.5%')
            st.plotly_chart(fig,use_container_width=True)

        with t2:
            produccion = df.groupby('HORNO')['M2'].sum().reset_index()
            fig2 = px.bar(produccion,x='HORNO',y='M2',text='M2',title='Producción Acumulada por Horno')
            fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig2,use_container_width=True)

    except Exception as e:
        st.error(f'Error: {e}')
