import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for the Unbreakable Atomic Pill
st.markdown("""
    <style>
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .stApp[data-test-script-state="running"] img.spinning-logo { animation: spin 2s linear infinite; }
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .spinning-logo { width: 80px; border-radius: 50%; }

    /* THE PILL CONTAINER - Global fix */
    div.pill-footer {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 800px;
        background-color: #1e1e1e;
        padding: 5px 15px;
        border-radius: 50px;
        border: 1px solid #444;
        z-index: 10000;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 10px;
    }

    /* Target the text input within our custom container */
    .pill-footer div[data-testid="stTextInput"] {
        flex-grow: 1 !important;
        width: 100% !important;
    }

    /* Target the dropdown within our custom container */
    .pill-footer div[data-testid="stSelectbox"] {
        width: 110px !important;
        flex-shrink: 0 !important;
    }

    /* Hide standard Streamlit chat UI elements */
    div[data-testid="stChatInput"], .stChatInputContainer {
        display: none !important;
    }

    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        height: 45px !important;
    }

    .main-chat-container { margin-bottom: 120px; }
    
    .stSelectbox div[data-baseweb="select"] {
        height: 35px;
        min-height: 35px;
        background-color: #333;
        border-radius: 20px;
    }

    button[kind="secondary"] {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        background-color: #2b2b2b !important;
        border: none !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo Display
logo_path = "mistral.JPG"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{encoded}" class="spinning-logo"></div>', unsafe_allow_html=True)

st.title("Mistral AI")

# 4. API Configuration
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add it to Streamlit Secrets.")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 5. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 7. THE ONE-BAR CHAT INTERFACE (Bypassing st.columns)
# This raw HTML wrapper forces the items into one line regardless of screen size
st.markdown('<div class="pill-footer">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 4, 0.5])
with col1:
    mode = st.selectbox("Mode", ["Fast", "Thinking", "Pro"], label_visibility="collapsed", key="active_mode")
with col2:
    user_input = st.text_input("Msg", label_visibility="collapsed", key="user_query", placeholder="Message Mistral...")
with col3:
    send_clicked = st.button("🚀")
st.markdown('</div>', unsafe_allow_html=True)

# 8. Execution Logic
if (send_clicked or (user_input and st.session_state.get('last_query') != user_input)) and user_input:
    st.session_state.last_query = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
            
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(""):
            try:
                m_map = {"Fast": "gemini-2.5-flash", "Thinking": "gemini-2.5-pro", "Pro": "gemini-2.5-pro"}
                model = genai.GenerativeModel(
                    model_name=m_map[mode],
                    system_instruction="You are Mistral, a helpful and concise AI assistant."
                )
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                response = chat.send_message(user_input, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
