import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

# ==============================================================================
# 1. CONFIGURAÇÃO & CONEXÃO (ONLINE) ☁️
# ==============================================================================
st.set_page_config(page_title="Gestor de Locadora BR", page_icon="🇧🇷", layout="wide")

# SEU LINK DO GOOGLE SHEETS
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2Fjc9qA470SDT12L-_nNlryhKLXHZWXSYPzg-ycg-DGkt_O7suDDtUF3rQEE-pg/pub?gid=858361345&single=true&output=csv"

LOCAIS = {
    "Loja Centro": 0.0,
    "Aeroporto (Taxa Entrega)": 80.00,
    "Hotel / Delivery": 50.00
}

# ==============================================================================
# 2. MOTOR DE DADOS & LIMPEZA 🧼
# ==============================================================================
@st.cache_data(ttl=0)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"❌ Erro de Conexão: {e}")
        return pd.DataFrame()

df = load_data()

def limpar_preco(valor):
    try:
        if isinstance(valor, (int, float)): return float(valor)
        valor_limpo = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        return float(valor_limpo)
    except: return 0.0

def get_car_details(row):
    return {
        "nome": row['Carro'],
        "grupo": row.get('Grupo', 'N/A'),
        "motor": row.get('Motor', '1.0'),
        "cambio": row.get('Câmbio', 'Manual'),
        "p_baixa": limpar_preco(row.get('Preço Baixa', 0)),
        "p_alta": limpar_preco(row.get('Preço Alta', 0)),
        "status": str(row.get('Disponibilidade', ''))
    }

# ==============================================================================
# 3. INTELIGÊNCIA DE CÁLCULO 🧠
# ==============================================================================
def calcular_orcamento(d_inicio, h_inicio, d_fim, h_fim, preco_dia, taxa_local):
    dt_retirada = datetime.combine(d_inicio, h_inicio)
    dt_devolucao = datetime.combine(d_fim, h_fim)
    
    delta = dt_devolucao - dt_retirada
    dias_cobrados = max(1, delta.days)
    
    # Tolerância de 2h
    segundos_extras = delta.seconds
    if dias_cobrados > 0 and segundos_extras > (2 * 3600):
        dias_cobrados += 1
        aviso_extra = "(Inclui diária extra por horário estendido)"
    elif delta.days == 0 and segundos_extras > 0: 
        dias_cobrados = 1
        aviso_extra = ""
    else:
        aviso_extra = ""

    total_diarias = dias_cobrados * preco_dia
    total
