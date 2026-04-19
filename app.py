import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="Mistral AI", page_icon="🤖")
st.title("Mistral AI")

# 2. API Key Check
# This looks for the key in your Streamlit Cloud "Secrets" dashboard
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 4. Initialize Model with Persona
# Changed to gemini-1.5-flash-latest to fix the 404 error
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction="You are Mistral, a helpful and concise AI assistant. Always identify as Mistral."
)

# 5. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Chat Input & Response Logic
if prompt := st.chat_input("Ask Mistral something..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare history for the API (convert 'assistant' role to 'model')
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]
        
        chat_session = model.start_chat(history=history)
        
        try:
            # Send message with streaming enabled
            response = chat_session.send_message(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "I encountered an error. Please check the logs."

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
