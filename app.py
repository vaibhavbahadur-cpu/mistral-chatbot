import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for the Integrated Chat Bar & Spinning Logo
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
        width: 100px;
        border-radius: 50%;
    }
    
    /* CUSTOM CHAT BAR STYLING */
    /* This wraps the selectbox and text input to look like one unit */
    .stTextArea textarea {
        background-color: #212121;
        border-radius: 20px;
        border: 1px solid #424242;
        padding-right: 50px;
    }
    
    /* Centers the bottom bar and reduces spacing */
    div[data-testid="stHorizontalBlock"] {
        background-color: #1e1e1e;
        padding: 8px 15px;
        border-radius: 30px;
        border: 1px solid #333;
        align-items: center;
        position: fixed;
        bottom: 30px;
        z-index: 100;
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

# 6. Display Chat History (with a spacer for the fixed bottom bar)
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# 7. THE INTEGRATED CHAT BAR
# We use a form so the 'Enter' key works to send
with st.container():
    col_tools, col_input, col_btn = st.columns([0.2, 0.6, 0.2])
    
    with col_tools:
        # The dropdown like the 'Fast' button in your photo
        mode = st.selectbox(
            "Mode",
            ["Fast", "Thinking", "Pro"],
            label_visibility="collapsed",
            index=0
        )
        
    with col_input:
        # A text area that looks like a chat box
        user_input = st.text_input("Message Mistral...", label_visibility="collapsed", key="user_query")
        
    with col_btn:
        send_clicked = st.button("▶️", use_container_width=True)

# 8. Execution Logic
if send_clicked and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Process immediately
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner(f"Mistral {mode}..."):
                try:
                    # Model Mapping
                    model_map = {"Fast": "gemini-3.1-flash", "Thinking": "gemini-3.1-pro", "Pro": "gemini-3.1-pro"}
                    model = genai.GenerativeModel(model_name=model_map[mode])
                    
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
                    full_response = "Error connecting to AI."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    # Reset input after sending
    st.rerun()
