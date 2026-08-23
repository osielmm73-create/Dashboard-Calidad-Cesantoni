# VERSION V2 - Dashboard Ejecutivo Calidad P1 y P3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='CALIDAD P1 Y P3', layout='wide')

st.markdown('''
<style>
.main {background:#F4F6F8;}
div[data-testid="stMetric"]{background:white;border-radius:12px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,.12)}
h1,h2,h3{color:#263238;}
</style>
''', unsafe_allow_html=True)

st.title('CALIDAD P1 Y P3')
st.caption('TODOS SOMOS CALIDAD')
st.info('Base V2 ejecutiva. Sustituye tu app actual y conserva la lógica existente para lectura de datos.')
