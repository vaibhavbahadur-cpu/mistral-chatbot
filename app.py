import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for the Locked Single-Pill Bottom Bar
st.markdown("""
    <style>
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .stApp[data-test-script-state="running"] img.spinning-logo { animation: spin 2s linear infinite; }
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .spinning-logo { width: 80px; border-radius: 50%; }

    .pill-footer {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 850px;
        background-color: #1e1e1e;
        padding: 8px 15px;
        border-radius: 50px;
        border: 1px solid #444;
        z-index: 10000 !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 10px;
    }

    .pill-footer > div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        align-items: center !important;
    }

    div[data-testid="column"] { width: auto !important; flex: none !important; }
    div[data-testid="column"]:nth-of-type(2) { flex-grow: 1 !important; }

    div[data-testid="stChatInput"], .stChatInputContainer { display: none !important; }

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
        width: 110px !important;
    }

    button[kind="secondary"] {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
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

# 5. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_input" not in st.session_state:
    st.session_state.temp_input = ""

def handle_submit():
    if st.session_state.user_query.strip() != "":
        st.session_state.temp_input = st.session_state.user_query
        st.session_state.user_query = "" 

# 6. Display Chat History
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 7. THE ONE-BAR CHAT INTERFACE
st.markdown('<div class="pill-footer">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 4, 0.5])
with c1:
    mode = st.selectbox("Mode", ["Fast", "Thinking", "Pro"], label_visibility="collapsed", key="active_mode")
with c2:
    st.text_input("Msg", label_visibility="collapsed", key="user_query", 
                  placeholder="Message Mistral...", on_change=handle_submit)
with c3:
    send_clicked = st.button("🚀")
    if send_clicked:
        handle_submit()
st.markdown('</div>', unsafe_allow_html=True)

# 8. Execution Logic
if st.session_state.temp_input:
    query_to_send = st.session_state.temp_input
    st.session_state.temp_input = "" 
    
    st.session_state.messages.append({"role": "user", "content": query_to_send})
    with st.chat_message("user"):
        st.markdown(query_to_send)
            
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(""):
            try:
                # UPDATED MAPPING TO 2.5
                m_map = {
                    "Fast": "gemini-2.5-flash", 
                    "Thinking": "gemini-2.5-pro", 
                    "Pro": "gemini-2.5-pro"
                }
                
                model = genai.GenerativeModel(
                    model_name=m_map[mode],
                    system_instruction="You are Mistral, a helpful assistant."
                )
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                response = chat.send_message(query_to_send, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error using {mode} (Model 2.5): {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
