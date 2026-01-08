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
    total_geral = total_diarias + taxa_local
    
    return {
        "dias": dias_cobrados,
        "total_diarias": total_diarias,
        "total_geral": total_geral,
        "aviso": aviso_extra
    }

# ==============================================================================
# 4. SCRIPTS DE VENDA
# ==============================================================================
def get_script_venda(data_inicio, nome_cliente):
    # Fallback se não tiver nome
    nome = nome_cliente if nome_cliente else "Cliente"
    
    m, d = data_inicio.month, data_inicio.day
    if (m == 12 and d >= 20) or (m == 1 and d <= 5):
        return {"periodo": "🔥 FIM DE ANO", "texto": f"Olá {nome}! Infelizmente o modelo básico esgotou devido ao Reveillon. Segurei estas opções superiores:"}
    elif m in [1, 2, 7]:
        return {"periodo": "⛱️ FÉRIAS", "texto": f"Olá {nome}! O carro popular saiu agora. Tenho este upgrade ideal para suas férias:"}
    else:
        return {"periodo": "📉 PADRÃO", "texto": f"Olá {nome}! O modelo promocional não está disponível, mas consegui uma condição especial no carro acima:"}

# ==============================================================================
# 5. INTERFACE DO SISTEMA
# ==============================================================================
st.title("🚗 Gestor de Locadora BR (Pro)")

if not df.empty:
    col_menu, col_detalhes = st.columns([1, 1.5])
    
    with col_menu:
        st.subheader("1. Veículo")
        carro_sel = st.selectbox("Selecione o Carro", df['Carro'].tolist())
        
        linha = df[df['Carro'] == carro_sel].iloc[0]
        carro = get_car_details(linha)
        
        e_isca = False
        if carro['p_baixa'] <= 100 or "Isca" in carro['status']:
            e_isca = True
            st.error(f"🎣 ISCA DETECTADA: {carro['nome']}")
        
        with st.container(border=True):
            st.markdown(f"**Grupo:** {carro['grupo']}")
            st.markdown(f"**Motor:** {carro['motor']} | **Câmbio:** {carro['cambio']}")
            st.markdown(f"### R$ {carro['p_baixa']:.2f} <small>/dia</small>", unsafe_allow_html=True)
            if "ESGOTADO" in carro['status']: st.warning(carro['status'])
            else: st.success(carro['status'])

    with col_detalhes:
        st.subheader("2. Dados da Reserva")
        
        # --- NOVO CAMPO: NOME DO CLIENTE ---
        nome_cliente = st.text_input("Nome do Cliente", placeholder="Ex: João da Silva")
        
        # DATAS E HORAS
        c1, c2, c3, c4 = st.columns(4)
        with c1: d_ini = st.date_input("Retirada", datetime.today())
        with c2: h_ini = st.time_input("Hora Ret.", time(10, 0))
        with c3: d_fim = st.date_input("Devolução", datetime.today() + timedelta(days=3))
        with c4: h_fim = st.time_input("Hora Dev.", time(10, 0))

        local = st.selectbox("Local", list(LOCAIS.keys()))
        
        if st.button("Gerar Orçamento Oficial 📄", type="primary"):
            taxa = LOCAIS[local]
            is_alta = d_ini.month in [1, 2, 7, 12]
            preco_aplicado = carro['p_alta'] if is_alta else carro['p_baixa']
            
            math = calcular_orcamento(d_ini, h_ini, d_fim, h_fim, preco_aplicado, taxa)
            
            # Formata nome para o e-mail
            cliente_tratamento = nome_cliente if nome_cliente else "Cliente"

            if e_isca:
                # Upsell
                script = get_script_venda(d_ini, cliente_tratamento)
                st.toast(f"Upsell Ativo: {script['periodo']}")
                
                email = f"""Assunto: Disponibilidade: {carro['nome']} - {cliente_tratamento}

{script['texto']}

------------------------------------------------
⚠️ RESUMO DA INDISPONIBILIDADE:
O {carro['nome']} a R$ {preco_aplicado:.2f} está indisponível.

SUGESTÃO DE UPGRADE DISPONÍVEL IMEDIATO:
(Insira o carro superior aqui)

Fico no aguardo, {cliente_tratamento}!"""

            else:
                # Carro Normal - Orçamento Detalhado
                email = f"""Assunto: Confirmação de Reserva - {cliente_tratamento}

Olá {cliente_tratamento}, tudo certo com a disponibilidade!

🚘 **VEÍCULO CONFIRMADO**
Modelo: {carro['nome']} ({carro['motor']} - {carro['cambio']})

📅 **AGENDA**
Retirada:  {d_ini.strftime('%d/%m')} às {h_ini.strftime('%H:%M')}
Devolução: {d_fim.strftime('%d/%m')} às {h_fim.strftime('%H:%M')}
Local: {local}

💰 **DETALHAMENTO**
Diárias: {math['dias']}x R$ {preco_aplicado:.2f} = R$ {math['total_diarias']:.2f}
Taxas ({local}): R$ {taxa:.2f}
{math['aviso']}

---------------------------------------
✅ TOTAL A PAGAR: R$ {math['total_geral']:.2f}
---------------------------------------

Para confirmar, responda "DE ACORDO".
Att, Equipe de Reservas."""

            st.success("Orçamento Gerado!")
            st.text_area("Copiar E-mail:", email, height=500)
            
            if not e_isca:
                st.metric("VALOR TOTAL", f"R$ {math['total_geral']:.2f}")

else:
    st.info("Conectando ao banco de dados...")
