import streamlit as st
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Localização constante (Exemplo: Avenida Paulista, São Paulo, Brasil)
LATITUDE = -23.5613
LONGITUDE = -46.6565

# Parâmetros do sistema fotovoltaico (hipotético)
SYSTEM_CAPACITY_KW = 5
MODULE_TYPE = 0
ARRAY_TYPE = 1
TILT = 23
AZIMUTH = 0
# --- FIM DA CONFIGURAÇÃO ---

# Configuração modelo
load_dotenv()
NREL_API_KEY = os.getenv("NREL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Erro: A variável de ambiente GROQ_API_KEY não está configurada.")
    st.stop()

SELECTED_MODEL = "openai/gpt-oss-20b"

# Configuração da página
st.set_page_config(
    page_title="Assistant",
    page_icon="images/logo.svg",
    layout="wide"
)

# CSS para interface limpa
st.markdown("""
<style>
    /* Estilos das mensagens (mantidos como você pediu) */
    .chat-container {
        /* A altura agora é gerenciada pelo layout do Streamlit, podemos remover a altura fixa */
        /* height: 500px; */
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
        flex-grow: 1; /* Permite que o container cresça */
    }

    .user-message {
        background-color: #484b4f;
        color: white;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
        word-wrap: break-word;
    }

    .assistant-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.8rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 20%;
        word-wrap: break-word;
    }

    .timestamp {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 0.3rem;
    }

    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: white;
        color: black;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* --- MUDANÇA 1: CSS Adicional para um visual mais limpo --- */
    /* Remove o padding do bloco principal para que o chat input fique no fundo */
    .main .block-container {
        padding-bottom: 1rem;
    }

    /* Estilo para o botão de limpar */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #ff4b4b;
        color: #ff4b4b;
    }
    .stButton>button:hover {
        border: 1px solid #ff4b4b;
        color: white;
        background-color: #ff4b4b;
    }

    /* Esconder elementos do Streamlit */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    section[data-testid="stSidebar"] {display: none !important;}
    .stMultiPageNav {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []


def send_to_groq(messages, temperature=0.7, max_tokens=1000):
    """Envia mensagem para Groq API"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": SELECTED_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "❌ Erro: API Key inválida."
        elif response.status_code == 429:
            return "⏰ Limite excedido. Tente novamente em alguns minutos."
        else:
            return f"❌ Erro: {response.status_code}"
    except requests.exceptions.Timeout:
        return "⏰ Timeout na resposta."
    except Exception as e:
        return f"❌ Erro: {str(e)}"

# Header
col1, col2, col3 = st.columns([6, 1, 6])
with col2:
    st.image("images/a.png", width=200)

# Área principal do chat
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Container do chat com altura definida para criar um scroll
    with st.container(height=500, border=False):
        # Mostrar histórico do chat
        if st.session_state.messages:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'''
                    <div class="user-message">
                        {message["content"]}
                        <div class="timestamp">{message.get("timestamp", "")}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                elif message["role"] == "assistant":
                    st.markdown(f'''
                    <div class="assistant-message">
                        {message["content"]}
                        <div class="timestamp">{message.get("timestamp", "")}</div>
                    </div>
                    ''', unsafe_allow_html=True)

# Função de envio agora é chamada diretamente pelo chat_input
def send_message(user_input):
    if not user_input.strip():
        return

    # Adicionar mensagem do usuário
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Preparar mensagens para a API (últimas 10 mensagens)
    messages_for_api = []
    for msg in st.session_state.messages[-10:]:
        if msg["role"] in ["user", "assistant"] and msg.get("content", "").strip():
            messages_for_api.append({
                "role": msg["role"],
                "content": msg["content"].strip()
            })
    
    if not messages_for_api:
        return

    # Enviar para Groq
    with st.spinner("Pensando..."):
        response = send_to_groq(messages_for_api)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

# --- MUDANÇA 3: Substituição do st.form pelo st.chat_input ---
# O st.chat_input fica fixo na parte de baixo da tela.
# Ele retorna o valor digitado quando o usuário pressiona "Enter".
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    cleaned_input = prompt.strip().lower()
    if cleaned_input == "reporte":
        st.switch_page("pages/Reporte.py")
    else:
        # Chama a função de envio e depois recarrega a página para mostrar a nova mensagem
        send_message(prompt)
        st.rerun()