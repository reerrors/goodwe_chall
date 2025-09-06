import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random

# Configuração da página
st.set_page_config(
    page_title="análises",
    page_icon="images/goodwe_favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.header("Análises")
# CSS customizado em tons de cinza e preto
st.markdown("""
<style>
    /* Reset e fundo branco */
    .stApp {
        background-color: white !important;
    }

    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    /* Título compacto */
    .main-title {
        color: #222222 !important; /* ALTERADO: Tom de preto */
        font-size: 2rem !important;
        font-weight: bold !important;
        text-align: center !important;
        margin: 0 0 5px 0 !important;
    }

    .subtitle {
        color: #666666 !important; /* ALTERADO: Cinza médio */
        font-size: 0.9rem !important;
        text-align: center !important;
        margin: 0 0 15px 0 !important;
    }

    /* KPI Cards compactos */
    .kpi-container {
        display: flex !important;
        gap: 15px !important;
        margin-bottom: 15px !important;
        justify-content: space-between !important;
    }

    .kpi-card {
        background: white !important;
        border: 2px solid #f0f0f0 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        flex: 1 !important;
        min-height: 120px !important;
    }

    .kpi-value {
        color: #111111 !important; /* ALTERADO: Preto forte */
        font-size: 1.8rem !important;
        font-weight: bold !important;
        margin: 5px 0 !important;
    }

    .kpi-label {
        color: #333333 !important; /* ALTERADO: Cinza escuro */
        font-size: 0.85rem !important;
        margin-bottom: 8px !important;
    }

    .status-badge {
        background: #555555 !important;
        color: white !important;
        padding: 4px 10px !important;
        border-radius: 15px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
    }

    .status-negative {
        background: black !important;
    }

    .status-neutral {
        background: #888888 !important;
    }

    /* Seções compactas */
    .section-title {
        color: #333333 !important; /* ALTERADO: Cinza escuro */
        font-size: 1.1rem !important;
        font-weight: bold !important;
        margin: 15px 0 10px 0 !important;
        border-bottom: 2px solid black !important; /* ALTERADO: Borda preta */
        padding-bottom: 5px !important;
    }

    /* Metric cards (coluna da direita) */
    .metric-card {
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-left: 4px solid black !important; /* ALTERADO: Borda preta */
        border-radius: 8px !important;
        padding: 12px !important;
        text-align: center !important;
        flex: 1 !important;
    }

    .metric-value {
        color: black !important; /* ALTERADO: Preto */
        font-size: 1.4rem !important;
        font-weight: bold !important;
        margin: 0 !important;
    }

    .metric-label {
        color: #666666 !important;
        font-size: 0.8rem !important;
        margin-top: 4px !important;
    }

    /* Tabs compactas */
    .stTabs > div > div > div > div {
        gap: 0.5rem !important;
    }

    /* Gráficos menores */
    .plot-container {
        height: 300px !important;
    }
</style>
""", unsafe_allow_html=True)

# Função para gerar dados mockados compactos
@st.cache_data
def generate_compact_data():
    current_time = datetime.now()
    hour = current_time.hour

    # KPIs atuais
    if 6 <= hour <= 18:
        production = np.sin((hour - 6) * np.pi / 12) * 6 + random.uniform(-0.5, 0.5)
    else:
        production = random.uniform(0, 0.3)

    consumption = random.uniform(2.5, 4.5)
    battery = random.uniform(78, 92)

    # Dados da curva diária (12 horas apenas)
    hours = pd.date_range(start=current_time - timedelta(hours=11), end=current_time, freq='H')
    daily_data = []
    
    for h in hours:
        h_val = h.hour
        if 6 <= h_val <= 18:
            prod = np.sin((h_val - 6) * np.pi / 12) * 6 + random.uniform(-0.3, 0.3)
        else:
            prod = random.uniform(0, 0.2)
        
        cons = random.uniform(2, 4.5)
        daily_data.append({
            'time': h.strftime('%H:%M'),
            'production': max(0, prod),
            'consumption': cons,
            'grid': cons - max(0, prod)
        })
    
    return {
        'current': {
            'production': max(0, production),
            'consumption': consumption,
            'battery': battery,
            'balance': max(0, production) - consumption
        },
        'daily': pd.DataFrame(daily_data)
    }


# Carregar dados
data = generate_compact_data()
current = data['current']
daily_df = data['daily']

# KPIs em linha única
balance = current['balance']
if balance > 0:
    balance_status = "status-badge"
    balance_text = f"Exportando {balance:.1f}kW"
elif balance < 0:
    balance_status = "status-badge status-negative"  
    balance_text = f"Importando {abs(balance):.1f}kW"
else:
    balance_status = "status-badge status-neutral"
    balance_text = "Equilibrado"

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-label">Produção Atual</div>
        <div class="kpi-value">{current['production']:.1f} kW</div>
        <div class="status-badge">Ativo</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Consumo Casa</div>
        <div class="kpi-value">{current['consumption']:.1f} kW</div>
        <div class="status-badge status-neutral">Normal</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Balanço</div>
        <div class="kpi-value">{abs(balance):.1f} kW</div>
        <div class="{balance_status}">{balance_text}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Bateria</div>
        <div class="kpi-value">{current['battery']:.0f}%</div>
        <div class="status-badge">Carregada</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout em 2 colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-title">Curva de Energia (Últimas 12h)</div>', unsafe_allow_html=True)
    
    # Gráfico compacto
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_df['time'], 
        y=daily_df['production'],
        name='Produção',
        line=dict(color="black", width=3), # ALTERADO: Cor da linha para preto
        fill='tozeroy',
        fillcolor='rgba(50, 50, 50, 0.2)' # ALTERADO: Cor do preenchimento para cinza
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_df['time'], 
        y=daily_df['consumption'],
        name='Consumo',
        line=dict(color="#666666", width=3), # ALTERADO: Cor da linha para cinza
        fill='tonexty', # Mantido para preencher entre produção e consumo
        fillcolor='rgba(150, 150, 150, 0.2)' # ALTERADO: Cor do preenchimento para cinza mais claro
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_df['time'], 
        y=daily_df['grid'],
        name='Grid',
        line=dict(color='#aaaaaa', width=2, dash='dash') # ALTERADO: Cor da linha para cinza claro
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=40, r=40, t=30, b=40),
        showlegend=True,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis_title="Hora",
        yaxis_title="kW"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">Resumo Hoje</div>', unsafe_allow_html=True)
    
    # Cálculos
    energy_today = daily_df['production'].sum() * 0.5  # kWh aproximado
    savings_today = energy_today * 0.65
    self_consumption = min(100, (min(energy_today, daily_df['consumption'].sum()*0.5) / energy_today * 100)) if energy_today > 0 else 0
    
    st.markdown(f"""
    <div class="metric-card" style="margin-bottom: 10px;">
        <div class="metric-value">{energy_today:.1f} kWh</div>
        <div class="metric-label">Energia Gerada</div>
    </div>
    <div class="metric-card" style="margin-bottom: 10px;">
        <div class="metric-value">R$ {savings_today:.2f}</div>
        <div class="metric-label">Economia</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{self_consumption:.1f}%</div>
        <div class="metric-label">Autoconsumo</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ALTERADO: A seção de impacto ambiental foi REMOVIDA daqui.

# Seção de histórico compacta
st.markdown('<div class="section-title">Performance Histórica</div>', unsafe_allow_html=True)

# ALTERADO: Adicionada a terceira aba "Impacto Ambiental"
tab1, tab2, tab3 = st.tabs(["Mensal", "Financeiro", "Impacto Ambiental"])

with tab1:
    # Gráfico mensal compacto
    months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set']
    production = [850, 920, 1050, 980, 890, 760, 820, 950, 1100]
    consumption = [650, 680, 720, 700, 650, 600, 580, 620, 680]
    
    fig_monthly = go.Figure()
    # ALTERADO: Cores das barras para preto e cinza claro
    fig_monthly.add_trace(go.Bar(x=months, y=production, name='Produção', marker_color='black'))
    fig_monthly.add_trace(go.Bar(x=months, y=consumption, name='Consumo', marker_color='#cccccc'))
    
    fig_monthly.update_layout(
        height=250,
        margin=dict(l=40, r=40, t=20, b=40),
        showlegend=True,
        template='plotly_white',
        barmode='group',
        yaxis_title="kWh"
    )
    
    st.plotly_chart(fig_monthly, use_container_width=True)

with tab2:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">R$ 6.240</div>
            <div class="metric-label">Economia Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">36 meses</div>
            <div class="metric-label">⏱ROI Estimado</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">8.320 kWh</div>
            <div class="metric-label">Total Gerado</div>
        </div>
        """, unsafe_allow_html=True)

# ALTERADO: Nova aba para o Impacto Ambiental com dados históricos
with tab3:
    # Usando o valor "Total Gerado" da aba financeira para consistência
    total_generated_kwh = 8320
    
    # Cálculos do impacto total
    total_co2_avoided_kg = total_generated_kwh * 0.0817
    # Considerando que 1 árvore absorve aprox. 22kg de CO₂ por ano
    equivalent_trees = total_co2_avoided_kg / 22

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_co2_avoided_kg / 1000:.2f} ton</div>
            <div class="metric-label">🌍 Total de CO₂ Evitado</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{equivalent_trees:.0f}</div>
            <div class="metric-label">🌳 Árvores Equivalentes</div>
        </div>
        """, unsafe_allow_html=True)


# Footer compacto
st.markdown(f"""
<div style="text-align: center; color: #666666; margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 8px; font-size: 0.8rem;">
    <strong style="color: #333333;">Solar Assistant Dashboard</strong> | 
    <span style="color: black;">Última atualização: {datetime.now().strftime("%d/%m/%Y %H:%M")}</span>
</div>
""", unsafe_allow_html=True)