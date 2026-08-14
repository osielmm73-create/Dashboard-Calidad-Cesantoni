import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Dashboard Calidad V2', page_icon='📊', layout='wide')
META = 94.5

@st.cache_data
def cargar_datos(archivo):
    df = pd.read_excel(archivo, sheet_name='REPORTE DE CALIDAD', header=8)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('UNNAMED', na=False)]
    df = df[df['CALIDAD'].isin(['PRIMERA','SEGUNDA','TERCERA','QUINTA'])]
    df['M2'] = pd.to_numeric(df['M2'], errors='coerce')
    return df

def calidad_pct(df):
    total = df['M2'].sum()
    primera = df.loc[df['CALIDAD']=='PRIMERA','M2'].sum()
    return (primera/total*100) if total>0 else 0

st.title('📊 Dashboard Ejecutivo Calidad V2')
archivo = st.file_uploader('Sube archivo Excel', type=['xlsx'])

if archivo:
    df = cargar_datos(archivo)
    meses = sorted(df['MES'].dropna().unique())
    mes = st.selectbox('MES', meses)
    df = df[df['MES'] == mes]

    tab1,tab2,tab3,tab4,tab5 = st.tabs(['Resumen','Plantas y Hornos','Modelos','Formatos','Defectivos'])

    with tab1:
        total = df['M2'].sum()
        segunda = df.loc[df['CALIDAD']=='SEGUNDA','M2'].sum()
        tercera = df.loc[df['CALIDAD']=='TERCERA','M2'].sum()
        quinta = df.loc[df['CALIDAD']=='QUINTA','M2'].sum()
        calidad = calidad_pct(df)
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric('Calidad', f'{calidad:.2f}%')
        c2.metric('Meta', f'{META:.2f}%')
        c3.metric('Brecha', f'{calidad-META:.2f}%')
        c4.metric('M² Totales', f'{total:,.0f}')
        c5.metric('Defectivo', f'{segunda+tercera+quinta:,.0f}')

    with tab2:
        planta = df.groupby('PLANTA').apply(lambda x:(x.loc[x['CALIDAD']=='PRIMERA','M2'].sum()/x['M2'].sum())*100).reset_index(name='CALIDAD')
        st.plotly_chart(px.bar(planta,x='PLANTA',y='CALIDAD'), use_container_width=True)
        horno = df.groupby('HORNO').apply(lambda x:(x.loc[x['CALIDAD']=='PRIMERA','M2'].sum()/x['M2'].sum())*100).reset_index(name='CALIDAD')
        st.plotly_chart(px.bar(horno,x='HORNO',y='CALIDAD'), use_container_width=True)

    with tab3:
        modelos = df.groupby('MODELO')['M2'].sum().reset_index().sort_values('M2', ascending=False)
        st.dataframe(modelos)

    with tab4:
        formatos = df.groupby('FORMATO').apply(lambda x:(x.loc[x['CALIDAD']=='PRIMERA','M2'].sum()/x['M2'].sum())*100).reset_index(name='CALIDAD')
        st.dataframe(formatos)

    with tab5:
        defectivos = df[df['CALIDAD'].isin(['SEGUNDA','TERCERA','QUINTA'])]
        st.dataframe(defectivos)
