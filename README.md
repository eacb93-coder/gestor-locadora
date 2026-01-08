# 🚗 Gestor de Locadora BR (Intelligent Fleet Manager)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Focus](https://img.shields.io/badge/Focus-Revenue%20Optimization-orange)

> **Sistema de Inteligência Comercial para Locadoras de Veículos. Integração em Nuvem (Google Sheets), precificação dinâmica e algoritmos de Upsell Automático.**

---

## 🎯 Contexto de Negócio
No setor de locação de veículos, a agilidade na resposta e a precisão no cálculo de taxas complexas são vitais para a conversão. Este projeto resolve três dores operacionais comuns:
1.  **Perda de Receita:** Falha humana no cálculo de taxas de retorno (devolução em outra loja) e adicionais.
2.  **Estoque Ocioso:** Dificuldade em converter reservas de carros "Isca" (esgotados) para categorias superiores.
3.  **Descentralização:** Dados de frota desconectados da ferramenta de orçamentos.

## 💡 A Solução Técnica
Desenvolvi uma aplicação **Full-Stack em Python (Streamlit)** que atua como um motor de decisão para o time de vendas:

* **Cloud Data Integration:** Consumo de dados em tempo real via API pública do Google Sheets (CSV), garantindo que preços e disponibilidade estejam sempre atualizados.
* **Logistics Engine (One-Way Fee):** Algoritmo que detecta automaticamente divergência entre Local de Retirada e Devolução, aplicando a taxa de retorno (Logística Reversa) sem intervenção manual.
* **Upsell Algorithm:** Detecta solicitações de carros indisponíveis ("Isca") e gera scripts de persuasão baseados em gatilhos mentais (Escassez/Sazonalidade), calculando automaticamente o upgrade.

---

## 📸 Interface do Sistema (Hero Shot)

![Dashboard Preview](https://via.placeholder.com/800x400?text=Inserir+Print+do+Sistema+Aqui)

*O sistema calculando automaticamente: Diárias Sazonais + Taxa de Retorno + Condutor Adicional.*

---

## 🛠️ Funcionalidades Críticas (Business Logic)

### 1. Precificação Dinâmica & Sazonalidade
O código identifica datas de "Alta Temporada" (Férias, Feriados, Fim de Ano) e ajusta o valor da diária automaticamente, maximizando a margem de lucro.

### 2. Motor de Logística (One-Way Fee)
```python
# Exemplo da Lógica aplicada no Backend
if local_retirada != local_devolucao:
    taxa_retorno = 150.00
    aviso = "Inclui Taxa de Logística Reversa"
