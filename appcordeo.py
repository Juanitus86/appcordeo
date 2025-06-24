import streamlit as st
from datetime import date

# Configuración inicial de la app
st.set_page_config(page_title="Carga de Datos de Cultivo", layout="centered")

# Aplicar estilo claro personalizado
st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
        }
        .stButton>button {
            width: 100%;
            padding: 1em;
            font-size: 1.1em;
            background-color: #e6e6e6;
            color: #000;
            border: none;
            border-radius: 10px;
        }
        .stRadio>div>label {
            font-size: 1.1em;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌱 Cargar Datos de Cultivo")
st.markdown("### Selecciona el tipo de operación para comenzar:")

operacion = st.radio("¿Qué tipo de datos quieres cargar?", ("Siembra", "Cosecha"))

st.success(f"Has seleccionado: **{operacion}**")

# Campos comunes para ambas operaciones
fecha = st.date_input("Fecha", value=date.today())
producto = st.text_input("Producto")
huella = st.selectbox("Huella", options=[1, 2, 3, 4, 5, 6])
piso = st.selectbox("Piso", options=[1, 2, 3, 4, 5, 6, 7, 8])
lado = st.radio("Lado", ("A", "B"), horizontal=True)

if operacion == "Siembra":
    acordeones = st.number_input("Cantidad de acordeones", min_value=1, step=1)
    plantas = st.number_input("Cantidad de plántulas", min_value=1, step=1)
    observaciones = st.text_area("Observaciones")
    if st.button("📥 Cargar Siembra"):
        st.success("Datos de siembra cargados correctamente (simulado).")

elif operacion == "Cosecha":
    acordeones = st.number_input("Cantidad de acordeones", min_value=1, step=1)
    peso = st.number_input("Peso cosechado (en gramos)", min_value=1, step=1)
    observaciones = st.text_area("Observaciones")
    if st.button("📥 Cargar Cosecha"):
        st.success("Datos de cosecha cargados correctamente (simulado).")
