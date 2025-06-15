import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread

from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from gspread_dataframe import get_as_dataframe

# Configurar la página
st.set_page_config(layout='wide', page_title="Vista de Cultivo")

# Conectar a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credenciales.json", scopes=scope)
client = gspread.authorize(creds)
sh = client.open("Cultivo en Acordeones")

# Leer hojas
df_siembra = get_as_dataframe(sh.worksheet('SIEMBRA - INGRESOS'), evaluate_formulas=True).dropna(how='all')
df_cosecha = get_as_dataframe(sh.worksheet('COSECHA - EGRESOS'), evaluate_formulas=True).dropna(how='all')

# Limpieza
df_siembra.columns = df_siembra.columns.str.strip()
df_cosecha.columns = df_cosecha.columns.str.strip()

df_siembra['FECHA'] = pd.to_datetime(df_siembra['FECHA'], dayfirst=True, errors='coerce')
df_cosecha['FECHA'] = pd.to_datetime(df_cosecha['FECHA'], dayfirst=True, errors='coerce')
df_siembra['#ACOR'] = pd.to_numeric(df_siembra['#ACOR'], errors='coerce')
df_siembra['#PLANT'] = pd.to_numeric(df_siembra['#PLANT'], errors='coerce')
df_cosecha['#ACOR'] = pd.to_numeric(df_cosecha['#ACOR'], errors='coerce')
df_cosecha['PESO GR'] = pd.to_numeric(df_cosecha['PESO GR'], errors='coerce')
df_siembra['L'] = df_siembra['L'].astype(str).str.strip().str.upper()
df_cosecha['L'] = df_cosecha['L'].astype(str).str.strip().str.upper()

# --- Aquí empieza la modificación para PRODUCTO ---
# Normalizar producto: quitar espacios y pasar a minúsculas
df_siembra['PRODUCTO'] = df_siembra['PRODUCTO'].astype(str).str.strip().str.lower()
df_cosecha['PRODUCTO'] = df_cosecha['PRODUCTO'].astype(str).str.strip().str.lower()

# Diccionario de corrección de nombres comunes mal escritos
correcciones = {
    'albahca': 'albahaca',
    'albahaka': 'albahaca',
    'albhaca': 'albahaca',
    'cilantro ': 'cilantro',
    'cilantro': 'cilantro',
    'cilntro': 'cilantro',
    'albahca': 'albahaca',
    # Añade más correcciones que detectes
}

# Aplicar correcciones
df_siembra['PRODUCTO'] = df_siembra['PRODUCTO'].replace(correcciones)
df_cosecha['PRODUCTO'] = df_cosecha['PRODUCTO'].replace(correcciones)

# Filtros de la app
st.sidebar.title("Filtros")

fecha_hoy = pd.Timestamp.today()
fecha_inicio = st.sidebar.date_input("Fecha desde", value=fecha_hoy - timedelta(days=7))
fecha_fin = st.sidebar.date_input("Fecha hasta", value=fecha_hoy)

producto_filtro = st.sidebar.multiselect(
    "Filtrar por producto",
    options=sorted(df_siembra['PRODUCTO'].dropna().unique()),
    default=None
)

# Lotes activos
lotes_activos = df_siembra[~df_siembra['ID'].isin(df_cosecha['ID'])]

# Filtro de fecha y producto
lotes_filtrados = lotes_activos[
    (lotes_activos['FECHA'] >= pd.to_datetime(fecha_inicio)) &
    (lotes_activos['FECHA'] <= pd.to_datetime(fecha_fin))
]

if producto_filtro:
    lotes_filtrados = lotes_filtrados[lotes_filtrados['PRODUCTO'].isin(producto_filtro)]

# Combinaciones válidas (sin huella 4)
combinaciones = [(6,1), (6,3), (6,5), (6,7), (3,2), (3,4), (3,6), (3,8)]

# Escala de color
def fecha_a_color_por_dias(fecha):
    if fecha in ['NN', 'Sin Fecha']:
        return 'white'
    try:
        dias = (pd.Timestamp.today().normalize() - pd.to_datetime(fecha)).days
        dias = max(0, min(dias, 45))
        return plt.cm.YlGn(dias / 45)
    except:
        return 'white'

# Resumen por lado
def resumen_lado(df_siem, df_cos, h, p, lado):
    siem = df_siem[(df_siem['H']==h)&(df_siem['P']==p)&(df_siem['L'].str.upper()==lado)&
                   (df_siem['FECHA'] >= pd.to_datetime(fecha_inicio)) & (df_siem['FECHA'] <= pd.to_datetime(fecha_fin))]
    cos = df_cos[(df_cos['H']==h)&(df_cos['P']==p)&(df_cos['L'].str.upper()==lado)&
                 (df_cos['FECHA'] >= pd.to_datetime(fecha_inicio)) & (df_cos['FECHA'] <= pd.to_datetime(fecha_fin))]
    pl = siem.groupby('PRODUCTO')['#PLANT'].sum()
    gr = cos.groupby('PRODUCTO')['PESO GR'].sum()
    resumen = f"{fecha_inicio.strftime('%d/%m/%Y')} a {fecha_fin.strftime('%d/%m/%Y')}\n"
    for prod in sorted(set(pl.index).union(gr.index)):
        resumen += f"{prod}: {int(pl.get(prod, 0))} Plant / {int(gr.get(prod, 0))} g\n"
    return resumen.strip()

# Dibujar cada piso
def dibujar_piso(df, h, p):
    A = df[(df['H']==h)&(df['P']==p)&(df['L'].str.upper()=='A')]
    B = df[(df['H']==h)&(df['P']==p)&(df['L'].str.upper()=='B')]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(-1, 13)
    ax.set_ylim(-2.5, 3.2)
    ax.set_aspect('equal')
    ax.set_title(f'Huella {h} — Piso {p}', fontsize=16)

    def P(t): return (12*t, 0.6 + (1.9 - 0.6)*t)
    xs, ys = zip(*[P(t) for t in (0,1)])
    ax.plot([0,12],[2.5,2.5], 'k-'); ax.plot(xs,ys, 'k-')
    ax.plot([0,12],[0,0], 'k-'); ax.plot(xs,ys, 'k-')

    def fill_bandas(lotes, arriba):
        lotes = lotes.sort_values('FECHA', ascending=False).reset_index(drop=True)
        registros = []; total = 0
        for _, row in lotes.iterrows():
            acor = int(row['#ACOR'])
            if total + acor > 55: continue
            registros.append({
                'ID': row['ID'], 'PRODUCTO': row['PRODUCTO'],
                'CANTIDAD_ACORDEONES': acor,
                'FECHA': row['FECHA'].strftime('%d-%m-%Y') if pd.notnull(row['FECHA']) else 'Sin Fecha',
                'color': fecha_a_color_por_dias(row['FECHA']), 'es_nn': False
            })
            total += acor
        for _ in range((55 - total) // 2):
            registros.append({'ID':'NN','PRODUCTO':'NN','CANTIDAD_ACORDEONES':2,
                              'FECHA':'NN','color':'white','es_nn':True})
        n = len(registros)
        for i, reg in enumerate(registros):
            frac = i/n; width = 1/n
            t0 = 1-frac if arriba else frac
            t1 = 1-(frac+width) if arriba else frac+width
            x0,y0 = P(t0); x1,y1 = P(t1)
            pts = [(x0,y0),(x1,y1),(x1,2.5 if arriba else 0),(x0,2.5 if arriba else 0)]
            ax.add_patch(plt.Polygon(pts, facecolor=reg['color'], edgecolor='black', alpha=0.9, linewidth=0.6))
            xm = (x0+x1)/2
            ym = ((y0+(2.5 if arriba else 0))/2 + (y1+(2.5 if arriba else 0))/2)/2
            ax.text(xm, ym, f"{reg['ID']}\n{reg['PRODUCTO']}\n{reg['CANTIDAD_ACORDEONES']} acor",
                    ha='center', va='center', fontsize=5, color='black')

    fill_bandas(A, True)
    fill_bandas(B, False)

    resumen = f"LADO A\n{resumen_lado(df_siembra, df_cosecha, h, p, 'A')}\n\nLADO B\n{resumen_lado(df_siembra, df_cosecha, h, p, 'B')}"
    ax.text(6, -1.5, resumen, fontsize=9, ha='center', va='top',
            bbox=dict(facecolor='#fefce8', edgecolor='gray', linewidth=0.5, alpha=0.9))
    ax.axis('off')
    st.pyplot(fig)

# Mostrar todos los gráficos
for h, p in combinaciones:
    dibujar_piso(lotes_filtrados, h, p)
    st.markdown("---")
