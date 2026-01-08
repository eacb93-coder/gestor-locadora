import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

# ==============================================================================
# 1. CONFIGURAÇÃO (ONLINE) ☁️
# ==============================================================================
st.set_page_config(page_title="Gestor de Locadora BR", page_icon="🇧🇷", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2Fjc9qA470SDT12L-_nNlryhKLXHZWXSYPzg-ycg-DGkt_O7suDDtUF3rQEE-pg/pub?gid=858361345&single=true&output=csv"

LOCAIS = {
    "Loja Centro": 0.0,
    "Aeroporto (Taxa Entrega)": 80.00,
    "Hotel / Delivery": 50.00
}

# ==============================================================================
# 2. MOTOR DE DADOS
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

def get_car_specs(nome_carro):
    nome = nome_carro.lower()
    if "kwid" in nome or "mobi" in nome:
        return {"lugares": 5, "malas": 1, "portas": 4, "icon": "🚗"}
    elif "hb20" in nome or "onix" in nome or "polo" in nome:
        return {"lugares": 5, "malas": 2, "portas": 4, "icon": "🚙"}
    elif "renegade" in nome or "t-cross" in nome or "suv" in nome:
        return {"lugares": 5, "malas": 3, "portas": 4, "icon": "🚙💨"}
    else:
        return {"lugares": 5, "malas": 2, "portas": 4, "icon": "🚘"}

def get_car_details(row):
    specs = get_car_specs(row['Carro'])
    return {
        "nome": row['Carro'],
        "grupo": row.get('Grupo', 'N/A'),
        "motor": row.get('Motor', '1.0'),
        "cambio": row.get('Câmbio', 'Manual'),
        "p_baixa": limpar_preco(row.get('Preço Baixa', 0)),
        "p_alta": limpar_preco(row.get('Preço Alta', 0)),
        "status": str(row.get('Disponibilidade', '')),
        "lugares": specs['lugares'],
        "malas": specs['malas'],
        "icon": specs['icon']
    }

# ==============================================================================
# 3. CÁLCULO FINANCEIRO
# ==============================================================================
def calcular_orcamento(d_inicio, h_inicio, d_fim, h_fim, preco_dia, taxa_local):
    dt_retirada = datetime.combine(d_inicio, h_inicio)
    dt_devolucao = datetime.combine(d_fim, h_fim)
    delta = dt_devolucao - dt_retirada
    dias_cobrados = max(1, delta.days)
    
    # Lógica de Horas Extras
    segundos_extras = delta.seconds
    horas_extras = segundos_extras / 3600
    
    aviso_extra = ""
    # Tolerância de 2 horas
    if dias_cobrados > 0 and segundos_extras > (2 * 3600):
        dias_cobrados += 1
        aviso_extra = f"⚠️ Tolerância excedida (+{horas_extras:.1f}h). Cobrando diária extra."
    elif delta.days == 0 and segundos_extras > 0: 
        dias_cobrados = 1
    
    total_diarias = dias_cobrados * preco_dia
    total_geral = total_diarias + taxa_local
    
    return {
        "dias": dias_cobrados,
        "preco_base": preco_dia,
        "total_diarias": total_diarias,
        "total_geral": total_geral,
        "aviso": aviso_extra
    }

# ==============================================================================
# 4. SCRIPTS DE VENDA
# ==============================================================================
def get_script_venda(data_inicio, nome_cliente):
    nome = nome_cliente if nome_cliente else "Cliente"
    m, d = data_inicio.month, data_inicio.day
    if (m == 12 and d >= 20) or (m == 1 and d <= 5):
        return {"periodo": "🔥 FIM DE ANO", "texto": f"Olá {nome}! Devido ao Reveillon, o básico esgotou. Segurei estas opções:"}
    elif m in [1, 2, 7]:
        return {"periodo": "⛱️ FÉRIAS", "texto": f"Olá {nome}! O carro popular saiu agora. Tenho este upgrade ideal para férias:"}
    else:
        return {"periodo": "📉 PADRÃO", "texto": f"Olá {nome}! O promocional não está disponível, mas consegui uma condição especial:"}

# ==============================================================================
# 5. INTERFACE DO SISTEMA
# ==============================================================================
st.title("🚗 Gestor de Locadora BR (Pro)")

if not df.empty:
    col_menu, col_detalhes = st.columns([1, 1.5])
    
    with col_menu:
        st.subheader("1. Seleção Visual")
        carro_sel = st.selectbox("Escolha o Veículo", df['Carro'].tolist())
        linha = df[df['Carro'] == carro_sel].iloc[0]
        carro = get_car_details(linha)
        
        e_isca = False
        if carro['p_baixa'] <= 100 or "Isca" in carro['status']:
            e_isca = True
            st.error(f"🎣 ISCA DETECTADA")
        
        # HERO CARD
        with st.container(border=True):
            st.markdown(f"## {carro['icon']} {carro['nome']}")
            k1, k2, k3 = st.columns(3)
            k1.metric("Lugares", f"{carro['lugares']} 👤")
            k2.metric("Malas", f"{carro['malas']} 🧳")
            k3.metric("Câmbio", f"{carro['cambio'][0:4]}. ⚙️")
            st.divider()
            c_p1, c_p2 = st.columns([2, 1])
            c_p1.metric("Diária Base", f"R$ {carro['p_baixa']:.2f}")
            if "ESGOTADO" in carro['status']: c_p2.warning("Indisp.")
            else: c_p2.success("Livre")

    with col_detalhes:
        st.subheader("2. Configuração & Cliente")
        nome_cliente = st.text_input("Nome do Cliente", placeholder="Ex: Sr. Carlos")
        
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
            cliente = nome_cliente if nome_cliente else "Cliente"
            datas_str = f"{d_ini.strftime('%d/%m')} a {d_fim.strftime('%d/%m')}"

            # --- 💰 PAINEL FINANCEIRO (BEYOND STYLE) ---
            st.markdown("### 💰 Resultado Financeiro")
            with st.container(border=True):
                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                
                # Coluna 1: Cálculo de Dias
                col_res1.metric("Aluguel (Dias)", f"{math['dias']}x Diárias")
                
                # Coluna 2: Taxa Base do Carro
                col_res2.metric("Taxa Base Carro", f"R$ {preco_aplicado:.2f}")
                
                # Coluna 3: Taxas Extras
                col_res3.metric(f"Taxas ({local[0:8]}..)", f"R$ {taxa:.2f}")
                
                # Coluna 4: Total Final
                col_res4.metric("TOTAL FINAL", f"R$ {math['total_geral']:.2f}")
                
                # Aviso de Hora Extra (se houver)
                if math['aviso']:
                    st.warning(math['aviso'])
            # -------------------------------------------

            # BENEFÍCIOS FIXOS
            beneficios = """✅ INCLUSO NA DIÁRIA:
   ✔️ Quilometragem Livre
   ✔️ Seguro Proteção Parcial (CDW)
   ✔️ Taxas de Serviço e Lavagem"""

            if e_isca:
                # MODO UPSELL
                script = get_script_venda(d_ini, cliente)
                st.toast(f"Estratégia: {script['periodo']}")
                email = f"""Assunto: ⚠️ Disponibilidade: {carro['nome']} ({datas_str}) - {cliente}

{script['texto']}

------------------------------------------------
🚫 STATUS: O {carro['nome']} está indisponível.

✅ SUGESTÃO DE UPGRADE:
🚗 Hyundai HB20 1.0 (Grupo B)
   • 5 Passageiros 👤 | 2 Malas 🧳
   • Mais conforto e motor para estrada

{beneficios}

Aguardo seu OK, {cliente}!"""

            else:
                # MODO NORMAL
                email = f"""Assunto: ✅ Reserva Confirmada: {carro['nome']} ({datas_str}) - {cliente}

Olá {cliente}, orçamento oficial gerado:

🚘 **VEÍCULO**
Modelo: {carro['nome']}
Capacidade: {carro['lugares']} Pessoas 👤 | {carro['malas']} Malas 🧳

📅 **AGENDA**
Retirada:  {d_ini.strftime('%d/%m')} às {h_ini.strftime('%H:%M')}
Devolução: {d_fim.strftime('%d/%m')} às {h_fim.strftime('%H:%M')}
Local: {local}

💰 **FINANCEIRO**
Diárias: {math['dias']}x R$ {preco_aplicado:.2f} = R$ {math['total_diarias']:.2f}
Taxas ({local}): R$ {taxa:.2f}
{math['aviso']}

---------------------------------------
✅ TOTAL FINAL: R$ {math['total_geral']:.2f}
---------------------------------------

{beneficios}

Responda "DE ACORDO" para confirmar.
Att, Equipe de Reservas."""

            st.text_area("Copiar E-mail:", email, height=500)

else: st.info("Conectando...")
