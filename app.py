import streamlit as st
import google.generativeai as genai

# Page config
st.set_page_config(page_title="Mistral AI", page_icon="🤖")
st.title("Mistral AI")

# Retrieve API Key from Streamlit Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please add your GEMINI_API_KEY to the Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize the model with the "Mistral" persona
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are Mistral, a helpful and concise AI assistant. Always identify as Mistral."
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What is on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Start chat session with history
        chat = model.start_chat(history=[
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ])
        
        try:
            response = chat.send_message(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
