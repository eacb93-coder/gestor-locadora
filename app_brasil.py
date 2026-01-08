import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

# ==============================================================================
# 1. CONFIGURAÇÃO (MODO ONLINE - GOOGLE SHEETS) ☁️
# ==============================================================================
st.set_page_config(page_title="Gestor de Locadora BR", page_icon="🇧🇷", layout="wide")

# SEU LINK (Já verificado)
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

# --- NOVA FUNÇÃO DE LIMPEZA DE PREÇO ---
def limpar_preco(valor):
    """Transforma 'R$ 120,00' (texto) em 120.00 (número)"""
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        
        # Remove R$, espaços e troca vírgula por ponto
        valor_limpo = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        return float(valor_limpo)
    except:
        return 0.0

def get_car_details(row):
    # Aplica a limpeza nos preços AGORA
    p_baixa = limpar_preco(row.get('Preço Baixa', 0))
    p_alta = limpar_preco(row.get('Preço Alta', 0))
    
    return {
        "nome": row['Carro'],
        "grupo": row.get('Grupo', 'N/A'),
        "motor": row.get('Motor', '1.0'),
        "cambio": row.get('Câmbio', 'Manual'),
        "p_baixa": p_baixa,
        "p_alta": p_alta,
        "status": str(row.get('Disponibilidade', ''))
    }

# ==============================================================================
# 3. INTELIGÊNCIA DE VENDAS (Script Sazonal) 🧠
# ==============================================================================
def get_script_venda(data_inicio):
    m, d = data_inicio.month, data_inicio.day
    
    # 🎆 REVEILLON
    if (m == 12 and d >= 20) or (m == 1 and d <= 5):
        return {
            "periodo": "🔥 ALTA TEMPORADA (Fim de Ano)",
            "texto": """Olá! Agradecemos o contato.
Infelizmente, o modelo econômico básico já está **ESGOTADO** para o Reveillon.
Mas consegui segurar estas opções superiores:
🚗 **Chevrolet Onix Turbo (Automático)** - Conforto no trânsito.
🚙 **Jeep Renegade Turbo (SUV)** - Status e Espaço.
⚠️ A frota deve zerar em 24h. Recomendo garantir agora."""
        }

    # 🎉 FÉRIAS
    elif m in [2, 3, 7]:
        return {
            "periodo": "⛱️ ALTA TEMPORADA (Férias)",
            "texto": """Olá! O carro popular promocional acabou de sair.
Mas tenho um upgrade com ótimo custo-benefício:
🚗 **Hyundai HB20** - Mais espaço para malas.
🚗 **Chevrolet Onix Turbo** - Wi-Fi e Automático.
Vale muito a pena o conforto extra na viagem!"""
        }

    # 💼 BAIXA (Padrão)
    else:
        return {
            "periodo": "📉 BAIXA TEMPORADA",
            "texto": """Olá! O promocional de entrada não está disponível.
Mas trago boas notícias: estamos com condições especiais em categorias acima:
🚗 **Hyundai HB20** - Por uma pequena diferença, muito mais carro.
🚗 **Onix Turbo** - Economia e Potência.
Posso reservar o HB20? É o nosso campeão de vendas."""
        }

# ==============================================================================
# 4. INTERFACE VISUAL
# ==============================================================================
st.title("🚗 Gestor de Locadora Brasil")
st.caption(f"Status do Sistema: 🟢 Conectado ao Google Sheets (Online)")

if not df.empty:
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("1. Seleção do Veículo")
        carro_selecionado = st.selectbox("Escolha o Carro Solicitado", df['Carro'].tolist())
        
        linha = df[df['Carro'] == carro_selecionado].iloc[0]
        carro = get_car_details(linha)
        
        # --- DETECTOR DE ISCA ---
        e_isca = False
        if carro['p_baixa'] <= 100 or "Isca" in carro['status']:
            e_isca = True
            st.error(f"🎣 CARRO ISCA DETECTADO: {carro['nome']}")
            st.info("Upsell Automático Ativado.")
        
        with st.container(border=True):
            c1, c2 = st.columns(2)
            c1.metric("Grupo", carro['grupo'])
            c2.metric("Motor", carro['motor'])
            # Agora formatamos o preço garantindo que é número
            st.metric("Diária Base", f"R$ {carro['p_baixa']:.2f}")
            
            if "ESGOTADO" in carro['status']:
                st.warning(f"Status: {carro['status']}")
            else:
                st.success(f"Status: {carro['status']}")

    with col2:
        st.subheader("2. Dados da Reserva")
        c_a, c_b = st.columns(2)
        with c_a: d_inicio = st.date_input("Retirada", datetime.today())
        with c_b: d_fim = st.date_input("Devolução", datetime.today() + timedelta(days=3))
        local_ret = st.selectbox("Local", list(LOCAIS.keys()))
        
        if st.button("Gerar Orçamento 🚀", type="primary"):
            dt_inicio = datetime.combine(d_inicio, time(10))
            taxa_entrega = LOCAIS[local_ret]
            dias = max((d_fim - d_inicio).days, 1)
            
            # --- CÁLCULO FINANCEIRO REAL ---
            is_alta = d_inicio.month in [1, 2, 7, 12]
            p_dia = carro['p_alta'] if is_alta else carro['p_baixa']
            total = (dias * p_dia) + taxa_entrega

            if e_isca:
                dados_script = get_script_venda(dt_inicio)
                st.success(f"✅ Estratégia: {dados_script['periodo']}")
                
                # No Script de Venda, não mostramos o total do carro indisponível,
                # mas mostramos o texto de persuasão.
                email_final = f"""Assunto: Retorno sobre {carro['nome']}

{dados_script['texto']}

---------------------------------------------------
✅ INCLUSO: Km Livre, Seguro CDW e Taxas."""
            
            else:
                # Carro Normal: MOSTRA O CÁLCULO DETALHADO
                email_final = f"""Assunto: Confirmação de Reserva: {carro['nome']}

Olá! Segue o orçamento detalhado:

📋 RESUMO FINANCEIRO:
• Veículo: {carro['nome']}
• Período: {dias} diárias x R$ {p_dia:.2f}
• Taxa de Entrega: R$ {taxa_entrega:.2f}

💰 VALOR TOTAL: R$ {total:.2f}

Para confirmar, responda "DE ACORDO"."""

            st.text_area("Copiar E-mail:", email_final, height=450)

else:
    st.warning("⚠️ Carregando dados...")
