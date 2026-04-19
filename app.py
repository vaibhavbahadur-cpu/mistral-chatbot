import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for Mobile-Responsive Integrated Chat Bar & Spinning Logo
st.markdown("""
    <style>
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .stApp[data-test-script-state="running"] img.spinning-logo {
        animation: spin 2s linear infinite;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 10px;
    }
    .spinning-logo {
        width: 80px;
        border-radius: 50%;
    }
    
    /* MOBILE OPTIMIZED CHAT BAR */
    /* This creates a floating bar that stays visible above mobile keyboards */
    div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
        position: fixed;
        bottom: 20px;
        left: 5%;
        right: 5%;
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 25px;
        border: 1px solid #333;
        z-index: 1000;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }

    /* Fix for button and selectbox alignment on mobile */
    .stButton button {
        border-radius: 20px;
        height: 3rem;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 20px;
    }

    /* Ensures the chat history doesn't get hidden behind the bar */
    .main-chat-container {
        margin-bottom: 120px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo Display
logo_path = "mistral.JPG"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{encoded}" class="spinning-logo"></div>', unsafe_allow_html=True)

st.title("Mistral AI")

# 4. API Configuration
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key!")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 5. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History inside a div with margin for the bottom bar
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 7. THE MOBILE-FRIENDLY INTEGRATED BAR
# We use a container to wrap the columns for the fixed positioning
with st.container():
    # On mobile, these columns will stack or shrink. 
    # [1.5, 5, 1.2] provides a better balance for narrow screens
    col_tools, col_input, col_btn = st.columns([1.5, 5, 1.2])
    
    with col_tools:
        mode = st.selectbox(
            "Mode",
            ["Fast", "Thinking", "Pro"],
            label_visibility="collapsed",
            index=0,
            key="mode_select"
        )
        
    with col_input:
        user_input = st.text_input(
            "Message...", 
            label_visibility="collapsed", 
            key="user_query",
            placeholder="Type here..."
        )
        
    with col_btn:
        # Use a simple arrow icon for the button
        send_clicked = st.button("🚀", use_container_width=True)

# 8. Execution Logic
if (send_clicked or (user_input and st.session_state.get('last_input') != user_input)) and user_input:
    st.session_state.last_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
            
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(f"Mistral {mode}..."):
            try:
                # Using Gemini 3.1 stable names for 2026
                model_map = {
                    "Fast": "gemini-3.1-flash", 
                    "Thinking": "gemini-3.1-pro", 
                    "Pro": "gemini-3.1-ultra"
                }
                model = genai.GenerativeModel(
                    model_name=model_map[st.session_state.mode_select],
                    system_instruction="You are Mistral, a concise AI assistant."
                )
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                           for m in st.session_state.messages[:-1]]
                
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(user_input, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")
                full_response = "Connection error."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
