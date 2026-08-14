# Dashboard Ejecutivo Calidad V5
# Ajustes solicitados por Leonardo
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Dashboard Ejecutivo Calidad',layout='wide')
META=94.5

@st.cache_data
def cargar(f):
    df=pd.read_excel(f,sheet_name='REPORTE DE CALIDAD',header=8)
    df.columns=[str(c).strip().upper() for c in df.columns]
    df=df.loc[:,~df.columns.str.contains('UNNAMED',na=False)]
    df=df[df['CALIDAD'].isin(['PRIMERA','SEGUNDA','TERCERA','QUINTA'])]
    df['M2']=pd.to_numeric(df['M2'],errors='coerce').fillna(0)
    return df

st.title('📊 Dashboard Ejecutivo de Calidad')
file=st.file_uploader('Cargar Excel',type='xlsx')
if file:
    df=cargar(file)
    meses=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
    disp=[m for m in meses if m in df['MES'].astype(str).unique()]

    with st.sidebar:
        mes=st.selectbox('Mes',disp,index=max(0,len(disp)-1))
        vista=st.radio('Vista',['MES','ACUMULADO'])

    dff=df[df['MES']==mes] if vista=='MES' else df[df['MES'].isin(meses[:meses.index(mes)+1])]

    total=dff.M2.sum(); primera=dff[dff.CALIDAD=='PRIMERA'].M2.sum()
    segunda=dff[dff.CALIDAD=='SEGUNDA'].M2.sum(); tercera=dff[dff.CALIDAD=='TERCERA'].M2.sum(); quinta=dff[dff.CALIDAD=='QUINTA'].M2.sum()
    calidad=(primera/total*100) if total else 0

    a,b,c,d,e,f=st.columns(6)
    a.metric('🎯 Calidad',f'{calidad:.2f}%')
    b.metric('🏆 Meta','94.50%')
    c.metric('🟡 Segunda',f'{segunda:,.0f}')
    d.metric('🟠 Tercera',f'{tercera:,.0f}')
    e.metric('🔴 Quinta',f'{quinta:,.0f}')
    f.metric('🏭 Producción',f'{total:,.0f}')

    t1,t2,t3,t4,t5=st.tabs(['Plantas y Hornos','Modelos','Formatos','Defectivos','Tendencia'])

    with t1:
        planta=dff.groupby('PLANTA').apply(lambda x:(x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100).reset_index(name='CALIDAD')
        planta['PLANTA']=planta['PLANTA'].apply(lambda x:f'PLANTA {x}')
        st.plotly_chart(px.bar(planta,x='PLANTA',y='CALIDAD',text=planta['CALIDAD'].round(2).astype(str)+'%'),use_container_width=True)

        horn=dff[(dff['HORNO'].notna())&(dff['HORNO'].astype(str).str.strip()!='')]
        if len(horn):
            h=horn.groupby('HORNO').apply(lambda x:(x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100).reset_index(name='CALIDAD')
            st.plotly_chart(px.bar(h,x='HORNO',y='CALIDAD',text=h['CALIDAD'].round(2).astype(str)+'%'),use_container_width=True)

    with t2:
        modelos=dff.pivot_table(index='MODELO',columns='CALIDAD',values='M2',aggfunc='sum',fill_value=0).reset_index()
        st.plotly_chart(px.bar(modelos.sort_values('PRIMERA',ascending=False).head(15),x='MODELO',y=['PRIMERA','SEGUNDA','TERCERA','QUINTA'],title='Comportamiento por Modelo'),use_container_width=True)

    with t3:
        fmt=dff.groupby('FORMATO').apply(lambda x:(x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100).reset_index(name='CALIDAD')
        fmt=fmt.sort_values('CALIDAD',ascending=False)
        st.plotly_chart(px.bar(fmt,x='FORMATO',y='CALIDAD',text=fmt['CALIDAD'].round(2).astype(str)+'%'),use_container_width=True)

    with t4:
        for cal in ['SEGUNDA','TERCERA','QUINTA']:
            st.subheader(f'Top Modelos {cal}')
            tmp=dff[dff['CALIDAD']==cal].groupby('MODELO')['M2'].sum().reset_index().sort_values('M2',ascending=False).head(10)
            st.plotly_chart(px.bar(tmp,x='MODELO',y='M2',text='M2'),use_container_width=True)

    with t5:
        datos=[]
        for m in disp:
            x=df[df['MES']==m]
            datos.append([m,
                x[x.CALIDAD=='PRIMERA'].M2.sum(),
                x[x.CALIDAD=='SEGUNDA'].M2.sum(),
                x[x.CALIDAD=='TERCERA'].M2.sum(),
                x[x.CALIDAD=='QUINTA'].M2.sum(),
                x.M2.sum()])
        td=pd.DataFrame(datos,columns=['MES','PRIMERA','SEGUNDA','TERCERA','QUINTA','TOTAL'])
        st.plotly_chart(px.line(td,x='MES',y=['PRIMERA','SEGUNDA','TERCERA','QUINTA','TOTAL'],markers=True,title='Tendencia M² por Calidad'),use_container_width=True)
        st.dataframe(td,use_container_width=True)
