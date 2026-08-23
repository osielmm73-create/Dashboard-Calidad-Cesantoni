# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Dashboard Calidad P1 y P3", page_icon="📊", layout="wide")
DATA_DIR=Path("data")
DATA_DIR.mkdir(exist_ok=True)
EXCEL_FILE=DATA_DIR/'dashboard.xlsx'
ADMIN_USER='admin'
ADMIN_PASSWORD='Calidad2026'
if 'logged' not in st.session_state: st.session_state.logged=False
if 'role' not in st.session_state: st.session_state.role='viewer'
with st.sidebar:
    st.title('🔐 Acceso')
    user=st.text_input('Usuario')
    password=st.text_input('Contraseña',type='password')
    if st.button('Ingresar'):
        if user==ADMIN_USER and password==ADMIN_PASSWORD:
            st.session_state.logged=True
            st.session_state.role='admin'
        else:
            st.session_state.logged=True
            st.session_state.role='viewer'
    if st.session_state.role=='admin':
        uploaded=st.file_uploader('Cargar Excel',type=['xlsx'])
        if uploaded:
            with open(EXCEL_FILE,'wb') as f: f.write(uploaded.read())
            st.success('Archivo actualizado')
if not EXCEL_FILE.exists():
    st.warning('Carga un Excel primero.')
    st.stop()
# Version inicial. Requiere ajuste fino a la estructura exacta del DASHBOARD.
st.title('Dashboard Calidad P1 y P3')
st.info('Base cargada correctamente. Aplicación base generada.')
