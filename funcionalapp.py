import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='Dashboard Calidad P1 y P3',layout='wide')

DATA_DIR=Path('data')
DATA_DIR.mkdir(exist_ok=True)
DB_FILE=DATA_DIR/'dashboard.xlsx'

ADMIN_USER='admin'
ADMIN_PASSWORD='Calidad2026'

if 'admin' not in st.session_state:
    st.session_state.admin=False

with st.sidebar:
    st.title('🔐 Acceso')
    user=st.text_input('Usuario')
    password=st.text_input('Contraseña',type='password')
    if st.button('Ingresar'):
        st.session_state.admin=(user==ADMIN_USER and password==ADMIN_PASSWORD)

    if st.session_state.admin:
        st.success('Administrador')
        up=st.file_uploader('Cargar Excel',type=['xlsx'])
        if up:
            DB_FILE.write_bytes(up.read())
            st.success('Archivo actualizado')

if not DB_FILE.exists():
    st.warning('Ingrese como administrador y cargue un Excel.')
    st.stop()

raw=pd.read_excel(DB_FILE,sheet_name='DASHBOARD',header=1)
raw.columns=[str(c).strip() for c in raw.columns]

# CALIDAD
cal=raw[['FECHA CALIDAD Y MTS2','PRIMERA','MTS2 DEL DIA','CALIDAD META']].copy()
cal['FECHA CALIDAD Y MTS2']=pd.to_datetime(cal['FECHA CALIDAD Y MTS2'],errors='coerce')
cal=cal.dropna(subset=['FECHA CALIDAD Y MTS2'])

ult=cal.iloc[-1]

# GARANTIAS
if 'MES GARANTIAS' in raw.columns:
    gar=raw[['MES GARANTIAS','GARANTIAS']].dropna(subset=['MES GARANTIAS'])
    gar_plot=gar[gar['MES GARANTIAS'].astype(str).str.upper()!='TOTAL']
    total_garantias=pd.to_numeric(gar['GARANTIAS'],errors='coerce').max()
else:
    gar_plot=pd.DataFrame()
    total_garantias=0

# DEFECTOS
req=['DEFECTO','MTS2 DEFECTO','RESPONSABLE DE DEFECTO','PORCENTAJE DE DEFECTO DEL AREA']
if all(c in raw.columns for c in req):
    defects=raw[req].dropna(subset=['DEFECTO'])
else:
    defects=pd.DataFrame()

st.title('📊 Dashboard Calidad P1 y P3')

c1,c2,c3,c4,c5,c6=st.columns(6)
c1.metric('Calidad Día',f"{ult['PRIMERA']*100:.2f}%")
c2.metric('Calidad Promedio',f"{cal['PRIMERA'].mean()*100:.2f}%")
c3.metric('M² Día',f"{ult['MTS2 DEL DIA']:,.0f}")
c4.metric('M² Acumulado',f"{cal['MTS2 DEL DIA'].sum():,.0f}")
c5.metric('Garantías',f"{total_garantias:,.0f}")
c6.metric('Meta',f"{ult['CALIDAD META']*100:.2f}%")

fig=go.Figure()
fig.add_trace(go.Scatter(x=cal['FECHA CALIDAD Y MTS2'],y=cal['PRIMERA']*100,name='Calidad'))
fig.add_trace(go.Scatter(x=cal['FECHA CALIDAD Y MTS2'],y=cal['CALIDAD META']*100,name='Meta',line=dict(dash='dash')))
st.plotly_chart(fig,use_container_width=True)

if not gar_plot.empty:
    st.plotly_chart(px.bar(gar_plot,x='MES GARANTIAS',y='GARANTIAS',title='Garantías por mes'),use_container_width=True)

if not defects.empty:
    col1,col2=st.columns(2)
    topm=defects.groupby('DEFECTO')['MTS2 DEFECTO'].sum().sort_values(ascending=False).head(10)
    topp=defects.groupby('DEFECTO')['PORCENTAJE DE DEFECTO DEL AREA'].sum().sort_values(ascending=False).head(10)
    col1.plotly_chart(px.bar(topm,title='Top defectos M²'),use_container_width=True)
    col2.plotly_chart(px.bar(topp,title='Top defectos %'),use_container_width=True)

    resp=defects.groupby('RESPONSABLE DE DEFECTO')['MTS2 DEFECTO'].sum()
    st.plotly_chart(px.pie(values=resp.values,names=resp.index,title='Defectos por responsable'),use_container_width=True)
