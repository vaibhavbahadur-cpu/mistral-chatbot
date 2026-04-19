import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for the Wide-Reach Unified Bar
st.markdown("""
    <style>
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .stApp[data-test-script-state="running"] img.spinning-logo { animation: spin 2s linear infinite; }
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .spinning-logo { width: 80px; border-radius: 50%; }

    /* THE PILL CONTAINER - Widened and shifted for reachability */
    div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 95%; /* Wider bar for easier typing */
        max-width: 900px; 
        background-color: #1e1e1e;
        padding: 5px 15px;
        border-radius: 50px;
        border: 1px solid #444;
        z-index: 10000 !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
    }

    /* Force the columns to stay in a single line */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        align-items: center !important;
        gap: 10px !important;
    }

    /* Column Width Management */
    div[data-testid="column"] {
        width: auto !important;
        flex: none !important;
    }

    /* Make the text input (Column 2) take up almost all the space */
    div[data-testid="column"]:nth-of-type(2) {
        flex-grow: 1 !important;
    }

    /* Remove Streamlit default chat bar */
    div[data-testid="stChatInput"], .stChatInputContainer {
        display: none !important;
    }

    /* Styling the Text Box so it is clickable */
    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        height: 45px !important;
        width: 100% !important;
    }

    .main-chat-container { margin-bottom: 120px; }
    
    /* Lowered and Styled Mode Selector */
    .stSelectbox div[data-baseweb="select"] {
        height: 35px;
        min-height: 35px;
        background-color: #333;
        border-radius: 15px;
        width: 120px !important;
        font-size: 14px !important;
    }

    /* Rocket Button */
    button[kind="secondary"] {
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        min-width: 45px !important;
        background-color: #2b2b2b !important;
        border: none !important;
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

# 7. THE WIDE CHAT BAR
with st.container():
    # Ratios set to give Column 2 (the text box) the maximum clickable area
    c1, c2, c3 = st.columns([1, 5, 0.5])
    
    with c1:
        mode = st.selectbox("Mode", ["Fast", "Thinking", "Pro"], label_visibility="collapsed", key="active_mode")
    with c2:
        user_input = st.text_input("Msg", label_visibility="collapsed", key="user_query", placeholder="Message Mistral...")
    with c3:
        send_clicked = st.button("🚀")

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
