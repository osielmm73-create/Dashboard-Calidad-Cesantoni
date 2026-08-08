import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Calidad P1/P3", layout="wide")
st.title("📊 Dashboard de Calidad P1 / P3")

archivo = st.file_uploader("Arrastra o selecciona tu Excel", type=['xlsx'])

if archivo:
    xls = pd.ExcelFile(archivo)
    hoja = 'REPORTE DE CALIDAD' if 'REPORTE DE CALIDAD' in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(archivo, sheet_name=hoja)

    df.columns = [str(c).strip().upper() for c in df.columns]

    st.success(f'Hoja utilizada: {hoja}')

    if 'HORNO' in df.columns:
        hornos = sorted(df['HORNO'].dropna().astype(str).unique())
        seleccion = st.multiselect('Hornos', hornos, default=hornos)
        df = df[df['HORNO'].astype(str).isin(seleccion)]

    if 'M2' in df.columns:
        total = pd.to_numeric(df['M2'], errors='coerce').fillna(0).sum()
        primera = 0
        if 'CALIDAD' in df.columns:
            primera = pd.to_numeric(df.loc[df['CALIDAD'].astype(str).str.upper()=='PRIMERA','M2'], errors='coerce').fillna(0).sum()

        c1,c2,c3=st.columns(3)
        c1.metric('M² Totales',f'{total:,.0f}')
        c2.metric('M² Primera',f'{primera:,.0f}')
        c3.metric('Calidad %',f'{(primera/total*100) if total else 0:.2f}%')

    if all(c in df.columns for c in ['HORNO','M2']):
        datos=df.groupby('HORNO',dropna=True)['M2'].sum().reset_index()
        st.plotly_chart(px.bar(datos,x='HORNO',y='M2',title='Metros por Horno'),use_container_width=True)

    if all(c in df.columns for c in ['HORNO','CALIDAD','M2']):
        p=df.pivot_table(values='M2',index='HORNO',columns='CALIDAD',aggfunc='sum',fill_value=0)
        if 'PRIMERA' in p.columns:
            p['CALIDAD_%']=p['PRIMERA']/p.sum(axis=1)*100
            st.plotly_chart(px.bar(p.reset_index(),x='HORNO',y='CALIDAD_%',title='Calidad por Horno %'),use_container_width=True)

    if 'MODELO' in df.columns and 'M2' in df.columns:
        top=df.groupby('MODELO')['M2'].sum().reset_index().sort_values('M2',ascending=False).head(10)
        st.plotly_chart(px.bar(top,x='MODELO',y='M2',title='Top Modelos'),use_container_width=True)
