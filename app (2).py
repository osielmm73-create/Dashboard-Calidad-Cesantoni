import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='Dashboard Calidad',layout='wide')

DATA=Path('data'); DATA.mkdir(exist_ok=True)
FILE=DATA/'dashboard.xlsx'

ADMIN_USER='admin'
ADMIN_PASSWORD='Calidad2026'

if 'role' not in st.session_state:
    st.session_state.role='viewer'

with st.sidebar:
    st.header('Acceso')
    u=st.text_input('Usuario')
    p=st.text_input('Contraseña',type='password')
    if st.button('Ingresar'):
        if u==ADMIN_USER and p==ADMIN_PASSWORD:
            st.session_state.role='admin'

    if st.session_state.role=='admin':
        up=st.file_uploader('Cargar Excel',type='xlsx')
        if up:
            FILE.write_bytes(up.read())
            st.success('Archivo actualizado')

if not FILE.exists():
    st.warning('Cargue un archivo Excel.')
    st.stop()

raw=pd.read_excel(FILE,sheet_name='DASHBOARD',header=1)
raw.columns=[str(c).strip() for c in raw.columns]

# Calidad
cal=raw[['FECHA','PRIMERA','MTS2','CALIDAD META']].copy()
cal=cal.dropna(subset=['FECHA'])
cal['FECHA']=pd.to_datetime(cal['FECHA'])
ult=cal.iloc[-1]

# Garantias
if 'MES' in raw.columns:
    gar=raw[['MES','GARANTIAS']].dropna(subset=['MES'])
    gar_mes=gar[gar['MES'].astype(str)!='TOTAL']
    gar_total=pd.to_numeric(gar['GARANTIAS'],errors='coerce').max()
else:
    gar_mes=pd.DataFrame(); gar_total=0

# Defectos
cols=['DEFECTO','MTS2.1','RESPONSABLE','PORCENTAJE DE DEFECTO DEL AREA']
exist=[c for c in cols if c in raw.columns]
dfdef=raw[exist].copy() if exist else pd.DataFrame()
if not dfdef.empty:
    dfdef.columns=['DEFECTO','MTS2','RESPONSABLE','PCT']
    dfdef=dfdef.dropna(subset=['DEFECTO'])

st.title('📊 Dashboard Calidad P1 y P3')

c1,c2,c3,c4,c5=st.columns(5)
c1.metric('Calidad Día',f"{ult['PRIMERA']*100:.2f}%")
c2.metric('Calidad Promedio',f"{cal['PRIMERA'].mean()*100:.2f}%")
c3.metric('M² Día',f"{ult['MTS2']:,.0f}")
c4.metric('M² Acumulado',f"{cal['MTS2'].sum():,.0f}")
c5.metric('Meta',f"{ult['CALIDAD META']*100:.2f}%")

fig=go.Figure()
fig.add_scatter(x=cal['FECHA'],y=cal['PRIMERA']*100,name='Calidad')
fig.add_scatter(x=cal['FECHA'],y=cal['CALIDAD META']*100,name='Meta')
st.plotly_chart(fig,use_container_width=True)

if not gar_mes.empty:
    st.plotly_chart(px.bar(gar_mes,x='MES',y='GARANTIAS',title='Garantías'),use_container_width=True)

if not dfdef.empty:
    a,b=st.columns(2)
    topm=dfdef.groupby('DEFECTO')['MTS2'].sum().sort_values(ascending=False).head(10)
    topp=dfdef.groupby('DEFECTO')['PCT'].sum().sort_values(ascending=False).head(10)
    a.plotly_chart(px.bar(topm,title='Top defectos M²'),use_container_width=True)
    b.plotly_chart(px.bar(topp,title='Top defectos %'),use_container_width=True)
