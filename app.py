import streamlit as st
import google.generativeai as genai
import base64

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖", layout="wide")

# 2. Custom CSS for the Spinning Logo
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# This CSS makes the image rotate when Streamlit is "busy"
st.markdown("""
    <style>
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    /* Targets the sidebar image when the app is running */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        transition: transform 0.5s;
    }
    /* Spinning effect applied during execution */
    .stAppDeployButton + div, .stApp [data-testid="stStatusWidget"] {
        visibility: visible;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Setup
with st.sidebar:
    # Display the logo (Make sure mistral.JPG is in your GitHub repo)
    try:
        st.image("mistral.JPG", width=150)
    except:
        st.warning("Logo file 'mistral.JPG' not found. Please upload it to your repo.")
    
    st.title("Settings")
    mode = st.radio("Select Mode", ["Fast", "Thinking", "Pro"])
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# 4. API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key! Add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 5. Initialize Model based on Mode
# Mapping modes to stable 2.5/3.x models
model_map = {
    "Fast": "gemini-2.5-flash",
    "Thinking": "gemini-2.5-pro",
    "Pro": "gemini-2.5-pro" # or gemini-3-ultra-preview if available
}

model = genai.GenerativeModel(
    model_name=model_map[mode],
    system_instruction="You are Mistral, a helpful and concise AI assistant. Always identify as Mistral."
)

# 6. Chat History Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Chat Input & Response
if prompt := st.chat_input("Ask Mistral..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # This context manager triggers the spinning/loading state in the UI
        with st.spinner(f"Mistral is {mode.lower()}..."):
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
