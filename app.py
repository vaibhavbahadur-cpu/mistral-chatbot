import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. Ultra-Compact CSS for Mobile
st.markdown("""
    <style>
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .stApp[data-test-script-state="running"] img.spinning-logo { animation: spin 2s linear infinite; }
    
    .logo-container { display: flex; justify-content: center; padding: 5px; }
    .spinning-logo { width: 70px; border-radius: 50%; }

    /* SHORT BAR CSS */
    div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
        position: fixed;
        bottom: 15px;
        left: 2%;
        right: 2%;
        background-color: #1e1e1e;
        padding: 5px 10px;
        border-radius: 30px;
        border: 1px solid #444;
        z-index: 1000;
    }

    /* Make the input box background transparent to blend in */
    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
    }

    .main-chat-container { margin-bottom: 100px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo
logo_path = "mistral.JPG"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{encoded}" class="spinning-logo"></div>', unsafe_allow_html=True)

# 4. API & History
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Add API Key to Secrets!")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Chat Display
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 6. THE SHORT BAR (3-Column Layout)
# [1, 3, 1] ratio ensures the middle box is small enough to fit the buttons on the sides
with st.container():
    c1, c2, c3 = st.columns([1, 2.5, 0.8])
    
    with c1:
        mode = st.selectbox("M", ["Fast", "Think", "Pro"], label_visibility="collapsed", key="m")
        
    with c2:
        user_input = st.text_input("Msg", label_visibility="collapsed", key="q", placeholder="Ask...")
        
    with c3:
        # Using a very small icon to save space
        send = st.button("🚀", use_container_width=True)

# 7. Logic
if (send or (user_input and st.session_state.get('last') != user_input)) and user_input:
    st.session_state.last = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
            
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(""):
            try:
                # 2026 Model Names
                m_map = {"Fast": "gemini-3.1-flash", "Think": "gemini-3.1-pro", "Pro": "gemini-3.1-ultra"}
                model = genai.GenerativeModel(model_name=m_map[mode])
                
                chat = model.start_chat(history=[
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1]
                ])
                
                response = chat.send_message(user_input, stream=True)
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
