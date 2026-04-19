import streamlit as st
import google.generativeai as genai
import os

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="centered")

# 2. CSS for Spinning Logo & Bottom UI
st.markdown("""
    <style>
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spinning-logo {
        animation: spin 3s linear infinite;
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100px;
    }
    /* Style for the mode selector bar at the bottom */
    div[data-testid="stVerticalBlock"] > div:has(div.stRadio) {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 15px;
        margin-bottom: -20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo Display (Top Center)
if os.path.exists("mistral.JPG"):
    # If the app is "running", show the spinning version
    if st.exists("messages") and len(st.session_state.messages) > 0:
         st.markdown('<img src="app/static/mistral.JPG" class="spinning-logo">', unsafe_allow_html=True)
    else:
         st.image("mistral.JPG", width=100)
else:
    st.info("Logo 'mistral.JPG' not found in repo. Upload it to fix this.")

st.title("Mistral AI")

# 4. API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 5. Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Bottom UI (Mode Selector + Chat Input)
# We place the radio button right before the input
mode = st.radio(
    "Select Intelligence Mode:",
    ["Fast", "Thinking", "Pro"],
    horizontal=True,
    label_visibility="collapsed"
)

# Map modes to models
model_map = {
    "Fast": "gemini-2.5-flash",
    "Thinking": "gemini-2.5-pro",
    "Pro": "gemini-2.5-pro" 
}

if prompt := st.chat_input("Message Mistral..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Trigger the spinner (and the CSS animation)
        with st.spinner(f"Mistral {mode} is typing..."):
            model = genai.GenerativeModel(
                model_name=model_map[mode],
                system_instruction="You are Mistral, a concise AI assistant. Always identify as Mistral."
            )
            
            history = [
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                for m in st.session_state.messages[:-1]
            ]
            
            try:
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
