import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configuração da página
st.set_page_config(
    page_title="Assistant",
    page_icon="images/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para estilizar o chat
st.markdown("""
<style>
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.8rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .assistant-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.8rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    
    .timestamp {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 0.3rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: white;
        color: black;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_url" not in st.session_state:
    st.session_state.api_url = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = ""

# Header
st.markdown("""
<div class="main-header">
    <h1>Assistant</h1>
    <p>At your service.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Configurações da API
    api_url = st.text_input(
        "URL da API",
        value=st.session_state.api_url,
        placeholder="http://localhost:8000/v1",
        help="URL base da API compatível com OpenAI (ex: Ollama, vLLM, LocalAI)"
    )
    
    api_key = st.text_input(
        "Chave da API",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-...",
        help="Deixe em branco se não precisar de autenticação"
    )
    
    model_name = st.text_input(
        "Nome do Modelo",
        value=st.session_state.model_name,
        placeholder="llama2, mistral, codellama, etc.",
        help="Nome do modelo OSS a ser usado"
    )
    
    # Parâmetros de geração
    st.subheader("🎛️ Parâmetros")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.slider("Max Tokens", 50, 4000, 1000, 50)
    top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.1)
    
    # Botão para salvar configurações
    if st.button("💾 Salvar Configurações"):
        st.session_state.api_url = api_url
        st.session_state.api_key = api_key
        st.session_state.model_name = model_name
        st.success("Configurações salvas!")
    
    st.divider()
    
    # Status da conexão
    if api_url and model_name:
        st.subheader("📊 Status")
        if st.button("🔍 Testar Conexão"):
            try:
                headers = {
                    "Content-Type": "application/json"
                }
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                
                test_payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Olá"}],
                    "max_tokens": 10,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    f"{api_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=test_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    st.success("✅ Conexão OK!")
                else:
                    st.error(f"❌ Erro {response.status_code}")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    else:
        st.warning("⚠️ Configure URL e modelo")
    
    st.divider()
    
    # Exemplos de configuração
    st.subheader("📝 Exemplos")
    
    with st.expander("Ollama Local"):
        st.code("""
URL: http://localhost:11434/v1
Modelo: llama2, mistral, codellama
API Key: (deixar vazio)
        """)
    
    with st.expander("vLLM Server"):
        st.code("""
URL: http://localhost:8000/v1
Modelo: microsoft/DialoGPT-large
API Key: (opcional)
        """)
    
    with st.expander("LocalAI"):
        st.code("""
URL: http://localhost:8080/v1
Modelo: ggml-gpt4all-j
API Key: (deixar vazio)
        """)

# Área principal do chat
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Container do chat
    chat_container = st.container()
    
    # Função para enviar mensagem
    def send_message(user_input):
        if not api_url or not model_name:
            st.error("Por favor, configure a URL da API e o nome do modelo na sidebar.")
            return
        
        if not user_input.strip():
            return
        
        # Adicionar mensagem do usuário
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Preparar headers
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Preparar payload
        messages_for_api = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages[-10:]  # Últimas 10 mensagens
            if msg["role"] in ["user", "assistant"]
        ]
        
        payload = {
            "model": model_name,
            "messages": messages_for_api,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }
        
        try:
            # Mostrar indicador de carregamento
            with st.spinner("Pensando..."):
                response = requests.post(
                    f"{api_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                
                # Adicionar resposta do assistente
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            else:
                st.error(f"Erro na API: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("⏰ Timeout na requisição. Tente novamente.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Erro de conexão. Verifique se a API está rodando.")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {str(e)}")
    
    # Mostrar histórico do chat
    with chat_container:
        if st.session_state.messages:
            chat_html = ""
            for message in st.session_state.messages:
                if message["role"] == "user":
                    chat_html += f"""
                    <div class="user-message">
                        <strong>Você:</strong><br>
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                    """
                else:
                    chat_html += f"""
                    <div class="assistant-message">
                        <strong>🤖 Assistente:</strong><br>
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                    """
            
            st.markdown(f'<div class="chat-container">{chat_html}</div>', 
                       unsafe_allow_html=True)
    
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Mensagem:",
            placeholder="Digite sua mensagem aqui...",
            height=100,
            label_visibility="collapsed"
        )
        
        col_send, col_clear = st.columns([1, 1])
        
        with col_send:
            send_button = st.form_submit_button("Enviar", use_container_width=True)
        
        with col_clear:
            if st.form_submit_button("Limpar", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    if send_button and user_input:
        send_message(user_input)
        st.rerun()

