import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Carga de Datos", layout="centered")

st.title("Cargar Datos de Cultivo")
st.markdown("Selecciona el tipo de operación para comenzar:")

# Selector de tipo de operación
tipo_operacion = st.radio(
    "¿Qué tipo de datos quieres cargar?",
    ["Siembra", "Cosecha"],
    horizontal=True
)

st.success(f"Has seleccionado: **{tipo_operacion}**")
