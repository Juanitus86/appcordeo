import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("Prueba conexión Google Sheets")

# Cargar credenciales desde st.secrets
try:
    service_account_info = st.secrets["gcp_service_account"]
except KeyError:
    st.error("No se encontró 'gcp_service_account' en st.secrets. Configurá las credenciales en Streamlit Cloud.")
    st.stop()

try:
    creds = Credentials.from_service_account_info(service_account_info)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"Error autenticando con Google Sheets: {e}")
    st.stop()

# URL de tu Google Sheet (modificá con la tuya)
sheet_url = st.text_input("URL de Google Sheets para probar:", "")

if sheet_url:
    try:
        spreadsheet = client.open_by_url(sheet_url)
        worksheet = spreadsheet.sheet1  # Abrir la primera hoja
        data = worksheet.get_all_records()

        st.write("Datos cargados:")
        st.dataframe(data)
    except Exception as e:
        st.error(f"Error accediendo a la hoja: {e}")
else:
    st.info("Ingresá la URL de la hoja de cálculo arriba para cargar datos.")