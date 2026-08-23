import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='CALIDAD P1 Y P3', layout='wide')

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
EXCEL_FILE = DATA_DIR/'dashboard.xlsx'

ADMIN_USER='admin'
ADMIN_PASSWORD='Calidad2026'

st.markdown('''
<style>
.block-container{padding-top:1rem;}
[data-testid="stMetric"]{background:#f5f5f5;padding:12px;border-radius:12px;border-left:5px solid #232323;}
</style>
''',unsafe_allow_html=True)

if 'admin' not in st.session_state:
    st.session_state.admin=False

with st.sidebar:
    st.header('Acceso')
    u=st.text_input('Usuario')
    p=st.text_input('Contraseña',type='password')
    if st.button('Ingresar'):
        st.session_state.admin=(u==ADMIN_USER and p==ADMIN_PASSWORD)

    if st.session_state.admin:
        up=st.file_uploader('Actualizar Excel',type=['xlsx'])
        if up:
            EXCEL_FILE.write_bytes(up.read())
            st.success('Archivo actualizado')

if not EXCEL_FILE.exists():
    st.warning('Cargue un Excel como administrador.')
    st.stop()

raw=pd.read_excel(EXCEL_FILE,sheet_name='DASHBOARD',header=1)
raw.columns=[str(c).strip() for c in raw.columns]

cal=raw[['FECHA CALIDAD Y MTS2','PRIMERA','MTS2 DEL DIA','CALIDAD META']].copy()
cal['FECHA CALIDAD Y MTS2']=pd.to_datetime(cal['FECHA CALIDAD Y MTS2'],errors='coerce')
cal=cal.dropna(subset=['FECHA CALIDAD Y MTS2'])
ultima_fecha=cal['FECHA CALIDAD Y MTS2'].max()
ult=cal.iloc[-1]

logo='/mnt/data/Cesantoni_Positivo.jpg'
cl,ct,cf=st.columns([1,3,1])
with cl:
    try: st.image(logo,width=220)
    except: pass
with ct:
    st.markdown('## CALIDAD P1 Y P3')
    st.markdown('### TODOS SOMOS CALIDAD')
with cf:
    st.metric('Última actualización',ultima_fecha.strftime('%d/%m/%Y'))

# KPI
c1,c2,c3,c4,c5,c6=st.columns(6)
c1.metric('Calidad Día',f"{ult['PRIMERA']*100:.2f}%")
c2.metric('Calidad del Mes',f"{cal['PRIMERA'].mean()*100:.2f}%")
c3.metric('M² Día',f"{ult['MTS2 DEL DIA']:,.2f}")
c4.metric('M² Acumulado',f"{cal['MTS2 DEL DIA'].sum():,.2f}")
c5.metric('Meta Calidad',f"{ult['CALIDAD META']*100:.2f}%")

# Garantias
try:
    gar=raw[['MES GARANTIAS','GARANTIAS']].dropna(subset=['MES GARANTIAS'])
    total=pd.to_numeric(gar['GARANTIAS'],errors='coerce').max()
except:
    total=0
c6.metric('Garantías',f'{total:,.2f}')

# Tonos
try:
    tono=raw[['%CUMPLIMIENTO A TONO P1','%CUMPLIMIENTO A TONO P3','%CUMPLIMIENTO A TONO ACUMULADO']].dropna(how='all')
    t=tono.iloc[-1]
    cols=st.columns(3)
    for i,(lab,val) in enumerate({
        'Tono P1':t.iloc[0],
        'Tono P3':t.iloc[1],
        'Tono Acumulado':t.iloc[2]}.items()):
        fig=go.Figure(go.Indicator(mode='gauge+number',value=float(val)*100,title={'text':lab},number={'suffix':'%'},gauge={'axis':{'range':[0,100]}}))
        cols[i].plotly_chart(fig,use_container_width=True)
except: pass

fig=go.Figure()
fig.add_trace(go.Scatter(x=cal['FECHA CALIDAD Y MTS2'],y=cal['PRIMERA']*100,text=(cal['PRIMERA']*100).round(2),textposition='top center',mode='lines+markers+text',name='Calidad'))
fig.add_trace(go.Scatter(x=cal['FECHA CALIDAD Y MTS2'],y=cal['CALIDAD META']*100,mode='lines',name='Meta'))
fig.update_xaxes(dtick='D1')
fig.update_layout(title='Calidad P1 y P3 vs Meta')
st.plotly_chart(fig,use_container_width=True)
