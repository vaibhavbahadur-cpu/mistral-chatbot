import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. Stable CSS for Spinning Logo
st.markdown("""
    <style>
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .stApp[data-test-script-state="running"] img.spinning-logo { animation: spin 2s linear infinite; }
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .spinning-logo { width: 100px; border-radius: 50%; }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo Display
logo_path = "mistral.JPG"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{encoded}" class="spinning-logo"></div>', unsafe_allow_html=True)

st.title("Mistral AI")

# 4. Settings in Sidebar (Keeps the main chat bar clean for mobile)
with st.sidebar:
    st.header("Settings")
    mode = st.selectbox("Intelligence Mode", ["Fast", "Thinking", "Pro"], index=0)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# 5. API Configuration
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 6. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 7. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. THE CHAT INPUT (Back to the stable version that works on all phones)
if prompt := st.chat_input("Message Mistral..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(""):
            try:
                # 2026 Model Mapping
                m_map = {
                    "Fast": "gemini-3.1-flash", 
                    "Thinking": "gemini-3.1-pro", 
                    "Pro": "gemini-3.1-ultra"
                }
                model = genai.GenerativeModel(
                    model_name=m_map[mode],
                    system_instruction="You are Mistral, a helpful and concise AI assistant."
                )
                
                # Format history for the Gemini API
                history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1]
                ]
                
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")
                full_response = "I hit an error. Please try again."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
