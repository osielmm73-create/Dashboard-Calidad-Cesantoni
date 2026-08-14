import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Dashboard Ejecutivo Calidad V4',layout='wide',page_icon='📊')
META=94.5
GREEN='#00A65A';YELLOW='#F4B400';RED='#DB4437';BLUE='#005A9C'

@st.cache_data
def load(f):
    df=pd.read_excel(f,sheet_name='REPORTE DE CALIDAD',header=8)
    df.columns=[str(c).strip().upper() for c in df.columns]
    df=df.loc[:,~df.columns.str.contains('UNNAMED',na=False)]
    df=df[df['CALIDAD'].isin(['PRIMERA','SEGUNDA','TERCERA','QUINTA'])]
    df['M2']=pd.to_numeric(df['M2'],errors='coerce').fillna(0)
    return df


def q(df):
    t=df['M2'].sum(); p=df.loc[df['CALIDAD']=='PRIMERA','M2'].sum()
    return 0 if t==0 else p/t*100

st.title('📊 Dashboard Ejecutivo de Calidad')
f=st.file_uploader('Excel Calidad',type='xlsx')
if f:
    df=load(f)
    meses=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
    disp=[m for m in meses if m in df['MES'].astype(str).unique()]
    c1,c2=st.columns([4,1])
    mes=c1.selectbox('Mes',disp,index=max(0,len(disp)-1))
    vista=c2.radio('Vista',['MES','ACUMULADO'])
    dff=df[df['MES']==mes] if vista=='MES' else df[df['MES'].isin(meses[:meses.index(mes)+1])]

    tabs=st.tabs(['Resumen Ejecutivo','Plantas y Hornos','Calidad por Modelo','Formatos','Defectivos','Tendencia'])

    with tabs[0]:
      total=dff['M2'].sum(); primera=dff[dff.CALIDAD=='PRIMERA']['M2'].sum(); defect=total-primera; cal=q(dff)
      a,b,c,d,e,f1=st.columns(6)
      a.metric('Calidad %',f'{cal:.2f}%')
      b.metric('Meta %','94.50%')
      c.metric('Brecha %',f'{cal-META:.2f}%')
      d.metric('M² Totales',f'{total:,.0f}')
      e.metric('M² Primera',f'{primera:,.0f}')
      f1.metric('M² Defectivo',f'{defect:,.0f}')

    with tabs[1]:
      planta=dff.groupby('PLANTA').apply(lambda x:(x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100).reset_index(name='CALIDAD')
      planta=planta.dropna().sort_values('CALIDAD')
      fig=px.bar(planta,x='CALIDAD',y='PLANTA',orientation='h',text=planta['CALIDAD'].map(lambda x:f'{x:.2f}%'))
      fig.add_hline(y=None)
      st.plotly_chart(fig,use_container_width=True)

      hd=dff.copy()
      hd=hd[(hd['HORNO'].notna()) & (hd['HORNO'].astype(str).str.strip()!='')]
      if len(hd):
        h=hd.groupby('HORNO').apply(lambda x:(x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100).reset_index(name='CALIDAD')
        st.plotly_chart(px.bar(h,x='HORNO',y='CALIDAD',text=h['CALIDAD'].map(lambda v:f'{v:.2f}%'),title='Calidad por Horno %'),use_container_width=True)

    with tabs[2]:
      m=dff.groupby('MODELO').apply(lambda x:pd.Series({'CALIDAD_%':(x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100,'M2':x.M2.sum()})).reset_index()
      m=m[m['M2']>0]
      st.subheader('Top 10 Mejores Modelos por Calidad')
      st.dataframe(m.sort_values('CALIDAD_%',ascending=False).head(10),use_container_width=True)
      st.subheader('Top 10 Peores Modelos por Calidad')
      st.dataframe(m.sort_values('CALIDAD_%').head(10),use_container_width=True)

    with tabs[3]:
      fmt=dff.groupby('FORMATO').apply(lambda x:(x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100).reset_index(name='CALIDAD')
      fmt=fmt.dropna().sort_values('CALIDAD',ascending=False)
      st.plotly_chart(px.bar(fmt,x='FORMATO',y='CALIDAD',text=fmt['CALIDAD'].map(lambda x:f'{x:.2f}%')),use_container_width=True)

    with tabs[4]:
      md=dff.groupby('MODELO').apply(lambda x:pd.Series({'DEFECTIVO_%':100-((x[x.CALIDAD=='PRIMERA'].M2.sum()/x.M2.sum())*100),'M2':x.M2.sum()})).reset_index()
      md=md[md['M2']>0].sort_values('DEFECTIVO_%',ascending=False)
      st.plotly_chart(px.bar(md.head(15),x='DEFECTIVO_%',y='MODELO',orientation='h',text=md.head(15)['DEFECTIVO_%'].map(lambda x:f'{x:.2f}%'),title='Mayores Generadores de Defectivo %'),use_container_width=True)

    with tabs[5]:
      datos=[]
      for m in disp:
        x=df[df['MES']==m]
        t=x.M2.sum();p=x[x.CALIDAD=='PRIMERA'].M2.sum();s=x[x.CALIDAD=='SEGUNDA'].M2.sum()
        datos.append([m,q(x),p,s,t])
      td=pd.DataFrame(datos,columns=['MES','CALIDAD_%','PRIMERA_M2','SEGUNDA_M2','TOTAL_M2'])
      st.line_chart(td.set_index('MES')[['CALIDAD_%']])
      st.line_chart(td.set_index('MES')[['PRIMERA_M2','SEGUNDA_M2','TOTAL_M2']])
      st.dataframe(td,use_container_width=True)
