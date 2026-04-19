import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. Advanced CSS for Mobile-Responsive Integrated Bar
st.markdown("""
    <style>
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .stApp[data-test-script-state="running"] img.spinning-logo { animation: spin 2s linear infinite; }
    
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .spinning-logo { width: 80px; border-radius: 50%; }

    /* THE PILL BAR */
    div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
        position: fixed;
        bottom: 25px;
        left: 5%;
        right: 5%;
        background-color: #1e1e1e;
        padding: 10px 15px;
        border-radius: 35px;
        border: 1px solid #333;
        z-index: 1000;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    }
    
    /* Input Styling */
    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
    }

    /* Prevent chat from being hidden behind the bar */
    .main-chat-container { margin-bottom: 120px; }
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
    st.error("Missing API Key! Please add it to Secrets.")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 5. Initialize Chat History & Input State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 7. THE INTEGRATED CHAT BAR
with st.container():
    # Ratios optimized for phone screens
    c1, c2, c3 = st.columns([1.5, 4, 1])
    
    with c1:
        mode = st.selectbox("M", ["Fast", "Thinking", "Pro"], label_visibility="collapsed", key="mode")
    with c2:
        # We use a key that we can clear manually
        user_input = st.text_input("Message", label_visibility="collapsed", key="user_query", placeholder="Ask Mistral...")
    with c3:
        send_clicked = st.button("🚀", use_container_width=True)

# 8. Execution Logic
if (send_clicked or (user_input and st.session_state.get('prev_input') != user_input)) and user_input:
    # Update state to prevent double-firing
    st.session_state.prev_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
            
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(""):
            try:
                # Using stable identifiers to ensure 100% uptime
                m_map = {"Fast": "gemini-1.5-flash", "Thinking": "gemini-1.5-pro", "Pro": "gemini-1.5-pro"}
                model = genai.GenerativeModel(
                    model_name=m_map[mode],
                    system_instruction="You are Mistral, a concise and helpful AI."
                )
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                           for m in st.session_state.messages[:-1]]
                
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
    # Resetting the text_input effectively
    st.rerun()
