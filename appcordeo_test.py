import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

# Cargar credenciales desde secrets
gcp_creds = st.secrets["gcp_service_account"]

# Crear credenciales con alcance para Google Sheets
creds = Credentials.from_service_account_info(gcp_creds, scopes=["https://www.googleapis.com/auth/spreadsheets"])

# Autorizar cliente gspread
client = gspread.authorize(creds)

# ID de la planilla Google Sheets
SPREADSHEET_ID = "1nlKCJcshLWilc6rVbQezExz6Dvx6OKl-vFpCVlgf0og"

# Abrir la primera hoja de la planilla
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Obtener todos los registros
data = sheet.get_all_records()

st.write("Datos cargados desde Google Sheets:")
st.dataframe(data)