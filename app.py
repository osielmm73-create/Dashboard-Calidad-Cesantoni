import streamlit as st

st.set_page_config(
    page_title="Dashboard Calidad Cesantoni",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Ejecutivo de Calidad")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Resumen",
        "🔥 Hornos",
        "🚨 Defectivos",
        "📞 Reclamaciones y Tonos"
    ]
)

with tab1:
    st.header("Resumen Ejecutivo")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Calidad General", "--")
    c2.metric("Meta", "94.5%")
    c3.metric("M² Totales", "--")
    c4.metric("Reclamaciones", "--")

with tab2:

    st.header("Hornos")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Horno 1", "--")
    c2.metric("Horno 4", "--")
    c3.metric("Horno 5", "--")
    c4.metric("Horno 6", "--")

with tab3:

    st.header("Defectivos")

    st.info(
        "Aquí aparecerá el Pareto de defectos"
    )

with tab4:

    st.header("Reclamaciones y Tonos")

    st.info(
        "Aquí aparecerán reclamaciones y visor de tonos"
    )
