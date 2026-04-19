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
    /* This triggers the spin ONLY when the app is 'running' (processing) */
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
        transition: transform 0.3s ease;
    }
    /* Style for the mode selector bar */
    div.stRadio > div {
        flex-direction: row;
        justify-content: center;
        gap: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo Display Logic
logo_path = "mistral.JPG"

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/jpeg;base64,{encoded}" class="spinning-logo">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("Logo 'mistral.JPG' not found. Please upload it to your GitHub root folder.")

st.title("Mistral AI")

# 4. API Key Check (Streamlit Cloud Secrets)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 5. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Bottom UI (Mode Selector + Chat Input)
st.write("---") # Visual separator
mode = st.radio(
    "Intelligence Mode",
    ["Fast", "Thinking", "Pro"],
    horizontal=True,
    label_visibility="collapsed"
)

# Model Mapping for April 2026
model_map = {
    "Fast": "gemini-2.5-flash",
    "Thinking": "gemini-2.5-pro",
    "Pro": "gemini-2.5-pro"
}

# 8. Chat Logic
if prompt := st.chat_input("Message Mistral..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # The spinner triggers the "running" state for the spinning logo
        with st.spinner(f"Mistral {mode} is active..."):
            try:
                model = genai.GenerativeModel(
                    model_name=model_map[mode],
                    system_instruction="You are Mistral, a helpful and concise AI assistant. Always identify as Mistral."
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
                full_response = "I encountered an error. Please check your API key or logs."

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
