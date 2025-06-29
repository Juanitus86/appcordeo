import streamlit as st
from datetime import date
from google.oauth2.service_account import Credentials
import gspread

# --- Conexión a Google Sheets ---
gcp_creds = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(
    gcp_creds,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1nlKCJcshLWilc6rVbQezExz6Dvx6OKl-vFpCVlgf0og"
spreadsheet = client.open_by_key(SPREADSHEET_ID)

sheet_siembras = spreadsheet.worksheet("SIEMBRA - INGRESOS")
sheet_cosechas = spreadsheet.worksheet("COSECHA - EGRESOS")

# --- UI ---

st.set_page_config(page_title="Carga de Datos de Cultivo", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
        }
        .stButton>button {
            width: 100%;
            padding: 1em;
            font-size: 1.1em;
            background-color: #d8f3dc;
            color: #1b4332;
            border: none;
            border-radius: 30px;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #b7e4c7;
        }
        .stRadio>div>label {
            font-size: 1.1em;
        }
        input[type=text] {
            font-size: 1.1em;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #ccc;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌱 Cargar Datos de Cultivo")
st.markdown("### Selecciona el tipo de operación para comenzar:")

operacion = st.radio("¿Qué tipo de datos quieres cargar?", ("Siembra", "Cosecha"))

st.success(f"Has seleccionado: **{operacion}**")

fecha = st.date_input("Fecha", value=date.today())

productos = [
    "Albahaca verde", "Albahaca Morada", "Pak choi", "Pakchoi Morado", "Arugula",
    "Acelga arcoiris", "Acelga Natural", "Betabel red", "Betabel golden", "Sorrel",
    "Shizo", "Kale red", "Kale verde", "Viola Flor",
]
producto = st.selectbox("Producto", options=sorted(productos))

id_manual = st.text_input("ID (ingresalo manualmente)")

st.markdown("#### Huella (H)")
huella = st.radio("", options=[6, 3], horizontal=True, label_visibility="collapsed")

# Pisos válidos según huella
pisos_por_huella = {
    6: [1, 3, 5, 7],
    3: [2, 4, 6, 8]
}
pisos_validos = pisos_por_huella[huella]

st.markdown("#### Piso (P)")
piso = st.radio("", options=pisos_validos, horizontal=True, label_visibility="collapsed")

st.markdown("#### Lado (L)")
lado = st.radio("", ("A", "B"), horizontal=True, label_visibility="collapsed")

if operacion == "Siembra":
    acordeones = st.number_input("Cantidad de acordeones (#ACOR)", min_value=1, step=1)
    plantas = st.number_input("Cantidad de plántulas (#PLANT)", min_value=1, step=1)
    merma = st.number_input("Cantidad de merma (#MERMA)", min_value=0, step=1)
    observaciones = st.text_area("Observaciones", height=150)
    if st.button("📥 Cargar Siembra"):
        fila = [
            str(fecha),     # FECHA
            producto,       # PRODUCTO
            id_manual,      # ID manual
            huella,         # H
            piso,           # P
            lado,           # L
            acordeones,     # #ACOR
            plantas,        # #PLANT
            merma,          # #MERMA
            observaciones   # Observaciones
        ]
        sheet_siembras.append_row(fila)
        st.success("Datos de siembra cargados correctamente.")

elif operacion == "Cosecha":
    acordeones = st.number_input("Cantidad de acordeones (#ACOR)", min_value=1, step=1)
    peso = st.number_input("Peso cosechado (PESO GR)", min_value=1, step=1)
    observaciones = st.text_area("Observaciones", height=150)
    if st.button("📥 Cargar Cosecha"):
        fila = [
            str(fecha),     # FECHA
            producto,       # PRODUCTO
            id_manual,      # ID manual
            huella,         # H
            piso,           # P
            lado,           # L
            acordeones,     # #ACOR
            peso,           # PESO GR
            observaciones   # Observaciones
        ]
        sheet_cosechas.append_row(fila)
        st.success("Datos de cosecha cargados correctamente.")