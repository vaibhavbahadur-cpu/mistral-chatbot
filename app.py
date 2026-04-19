import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for the Spinning Logo & Short Integrated Chat Bar
st.markdown("""
    <style>
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .stApp[data-test-script-state="running"] img.spinning-logo { animation: spin 2s linear infinite; }
    
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .spinning-logo { width: 80px; border-radius: 50%; }

    /* FIXED BOTTOM BAR - Shortened for Mobile */
    div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
        position: fixed;
        bottom: 20px;
        left: 50%;
transform: translateX(-50%);
width: 700px; /* This is a standard width for computer chat bars */
        background-color: #1e1e1e;
        padding: 5px 10px;
        border-radius: 30px;
        border: 1px solid #444;
        z-index: 1000;
    }
    
    /* Make the input blend into the bar */
    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
    }

    /* Push chat messages up so they aren't covered */
    .main-chat-container { margin-bottom: 110px; }
    
    /* Shrink the selectbox/dropdown height */
    .stSelectbox div[data-baseweb="select"] {
        height: 40px;
        min-height: 40px;
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

# 7. THE SHORT INTEGRATED CHAT BAR
with st.container():
    # Ratios [Dropdown, Text, Send Button] - tuned to keep everything on-screen
    c1, c2, c3 = st.columns([1, 4, 0.5])
    
    with c1:
        # The Fast/Thinking/Pro dropdown
        mode = st.selectbox("Mode", ["Fast", "Thinking", "Pro"], label_visibility="collapsed", key="active_mode")
    with c2:
        # The text input
        user_input = st.text_input("Msg", label_visibility="collapsed", key="user_query", placeholder="Message Mistral...")
    with c3:
        # The Send button
        send_clicked = st.button("🚀", use_container_width=True)

# 8. Execution Logic (Using Gemini 2.5)
# This handles both the 'Enter' key and the button click
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
                # 2.5 Model Mapping (Updated for April 2026)
                m_map = {
                    "Fast": "gemini-2.5-flash", 
                    "Thinking": "gemini-2.5-pro", 
                    "Pro": "gemini-2.5-pro"
                }
                model = genai.GenerativeModel(
                    model_name=m_map[mode],
                    system_instruction="You are Mistral, a helpful and concise AI assistant."
                )
                
                history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1]
                ]
                
                chat = model.start_chat(history=history)
                response = chat.send_message(user_input, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")
                full_response = "I encountered a connection error. Check your API key or model availability."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
