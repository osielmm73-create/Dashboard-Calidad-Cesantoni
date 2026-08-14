import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Dashboard Calidad Cesantoni V3',page_icon='📊',layout='wide')
META=94.5

@st.cache_data
def cargar(archivo):
    df=pd.read_excel(archivo,sheet_name='REPORTE DE CALIDAD',header=8)
    df.columns=[str(c).strip().upper() for c in df.columns]
    df=df.loc[:,~df.columns.str.contains('UNNAMED',na=False)]
    df=df[df['CALIDAD'].isin(['PRIMERA','SEGUNDA','TERCERA','QUINTA'])]
    df['M2']=pd.to_numeric(df['M2'],errors='coerce')
    return df

def calidad(df):
    t=df['M2'].sum()
    p=df.loc[df['CALIDAD']=='PRIMERA','M2'].sum()
    return (p/t*100) if t>0 else 0

st.title('📊 Dashboard Ejecutivo Calidad V3')
archivo=st.file_uploader('Sube tu archivo Excel',type=['xlsx'])

if archivo:
    df=cargar(archivo)
    meses_orden=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
    disponibles=[m for m in meses_orden if m in df['MES'].astype(str).unique()]
    c1,c2=st.columns([2,1])
    mes=c1.selectbox('MES',disponibles,index=max(0,len(disponibles)-1))
    vista=c2.radio('VISTA',['MES','ACUMULADO'])

    if vista=='MES':
        dff=df[df['MES']==mes].copy()
    else:
        idx=meses_orden.index(mes)
        dff=df[df['MES'].isin(meses_orden[:idx+1])].copy()

    tabs=st.tabs(['Resumen','Plantas y Hornos','Modelos','Formatos','Defectivos','Tendencia'])

    with tabs[0]:
        total=dff['M2'].sum()
        seg=dff.loc[dff['CALIDAD']=='SEGUNDA','M2'].sum()
        ter=dff.loc[dff['CALIDAD']=='TERCERA','M2'].sum()
        qui=dff.loc[dff['CALIDAD']=='QUINTA','M2'].sum()
        cal=calidad(dff)
        a,b,c,d,e=st.columns(5)
        a.metric('Calidad General',f'{cal:.2f}%')
        b.metric('Meta','94.50%')
        c.metric('Brecha',f'{cal-META:.2f}%')
        d.metric('M² Totales',f'{total:,.0f}')
        e.metric('Defectivos',f'{seg+ter+qui:,.0f}')
        pie=dff.groupby('CALIDAD')['M2'].sum().reset_index()
        st.plotly_chart(px.pie(pie,names='CALIDAD',values='M2',title='Distribución Calidad'),use_container_width=True)

    with tabs[1]:
        planta=dff.groupby('PLANTA').apply(lambda x:(x.loc[x['CALIDAD']=='PRIMERA','M2'].sum()/x['M2'].sum())*100).reset_index(name='CALIDAD')
        fig=px.bar(planta,x='PLANTA',y='CALIDAD',text='CALIDAD',title='Calidad por Planta')
        fig.add_hline(y=META,line_dash='dash')
        st.plotly_chart(fig,use_container_width=True)

        horno=dff.groupby(['HORNO','CALIDAD'])['M2'].sum().reset_index()
        pv=horno.pivot_table(index='HORNO',columns='CALIDAD',values='M2',fill_value=0)
        if 'PRIMERA' not in pv: pv['PRIMERA']=0
        pv['TOTAL']=pv.sum(axis=1)
        pv['CALIDAD_PCT']=pv['PRIMERA']/pv['TOTAL']*100
        cols=st.columns(max(1,len(pv)))
        for i,(h,r) in enumerate(pv.iterrows()):
            sem='🟢' if r['CALIDAD_PCT']>=94.5 else '🟡' if r['CALIDAD_PCT']>=92 else '🔴'
            cols[i].metric(f'Horno {h}',f"{r['CALIDAD_PCT']:.2f}%")
            cols[i].markdown(sem)
        st.plotly_chart(px.bar(pv.reset_index(),x='HORNO',y='CALIDAD_PCT',text='CALIDAD_PCT',title='Calidad por Horno'),use_container_width=True)
        prod=dff.groupby('HORNO')['M2'].sum().reset_index()
        st.plotly_chart(px.bar(prod,x='HORNO',y='M2',text='M2',title='Producción por Horno'),use_container_width=True)

    with tabs[2]:
        mod=dff.groupby('MODELO')['M2'].sum().reset_index().sort_values('M2',ascending=False)
        st.plotly_chart(px.bar(mod.head(20),x='M2',y='MODELO',orientation='h',title='Top 20 Modelos'),use_container_width=True)
        st.dataframe(mod,use_container_width=True)

    with tabs[3]:
        fmt=dff.groupby('FORMATO').apply(lambda x:(x.loc[x['CALIDAD']=='PRIMERA','M2'].sum()/x['M2'].sum())*100).reset_index(name='CALIDAD')
        st.plotly_chart(px.bar(fmt,x='FORMATO',y='CALIDAD',title='Calidad por Formato'),use_container_width=True)
        st.dataframe(fmt,use_container_width=True)

    with tabs[4]:
        defect=dff[dff['CALIDAD'].isin(['SEGUNDA','TERCERA','QUINTA'])]
        top=defect.groupby('MODELO')['M2'].sum().reset_index().sort_values('M2',ascending=False)
        st.plotly_chart(px.bar(top.head(20),x='M2',y='MODELO',orientation='h',title='Top Defectivos'),use_container_width=True)
        st.dataframe(defect,use_container_width=True)

    with tabs[5]:
        datos=[]
        for m in disponibles:
            tmp=df[df['MES']==m]
            datos.append([m,calidad(tmp)])
        ten=pd.DataFrame(datos,columns=['MES','CALIDAD'])
        fig=px.line(ten,x='MES',y='CALIDAD',markers=True,title='Tendencia Mensual')
        fig.add_hline(y=META,line_dash='dash')
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(ten,use_container_width=True)
