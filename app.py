import streamlit as st
import google.generativeai as genai
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for the Spinning Logo and UI Styling
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
        width: 120px;
        border-radius: 50%;
    }
    /* This makes the mode selector look like a clean pill/dropdown */
    div[data-testid="stHorizontalBlock"] {
        align-items: end;
        gap: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo Display Logic
logo_path = "mistral.JPG"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{encoded}" class="spinning-logo"></div>', unsafe_allow_html=True)
else:
    st.info("Logo 'mistral.JPG' not found.")

st.title("Mistral AI")

# 4. API Configuration
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key!")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 5. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. CHAT BAR AREA (Selectbox + Input side-by-side)
# We create two columns: one narrow for the mode, one wide for the text
col1, col2 = st.columns([1, 4])

with col1:
    mode = st.selectbox(
        "Mode",
        ["Fast", "Thinking", "Pro"],
        label_visibility="collapsed",
        index=0
    )

with col2:
    prompt = st.chat_input("Message Mistral...")

# Model Mapping
model_map = {
    "Fast": "gemini-2.5-flash",
    "Thinking": "gemini-2.5-pro",
    "Pro": "gemini-2.5-pro"
}

# 8. Execution Logic
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Since chat_input is in a column, we use st.rerun to ensure the message appears immediately
    st.rerun()

# Processing the last message if it's from the user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(f"Mistral {mode}..."):
            try:
                model = genai.GenerativeModel(
                    model_name=model_map[mode],
                    system_instruction="You are Mistral, a helpful and concise AI assistant."
                )
                
                history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
                
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(last_prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")
                full_response = "Error connecting to AI."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
