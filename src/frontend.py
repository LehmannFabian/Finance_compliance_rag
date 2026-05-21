import os
import streamlit as st
import requests

# FastAPI backend endpoint configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

try:
    health_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    if health_response.status_code != 200:
        st.info("Backend is starting. Please wait a moment and retry.")
except requests.RequestException:
    st.info("Backend is starting. Please wait a moment and retry.")


st.set_page_config(
    page_title="Swiss Regulatory Advisor",
    page_icon="🇨🇭",
    layout="centered"
)

st.title("🇨🇭 Swiss Regulatory & Compliance Advisor")
st.write("Upload official FINMA or legal PDFs and query them securely via Gemini RAG.")

# --- SIDEBAR: Document Ingestion ---
with st.sidebar:
    st.header("Document Ingestion")
    uploaded_file = st.file_uploader("Upload a Swiss Regulatory PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process & Index Document", use_container_width=True):
            with st.spinner("Extracting text and generating vectors..."):
                # Wrap file data into a standard multipart payload format
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success(response.json().get("message", "Success!"))
                    else:
                        st.error(f"Backend Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Could not connect to FastAPI server: {str(e)}")

# --- MAIN AREA: Conversational Interface ---
st.subheader("Ask a Compliance Question")

# Initialize chat history inside Streamlit's session state memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept new text questions from the user
if user_question := st.chat_input("e.g., What are the FINMA requirements for managing cyber risks?"):
    # Append user question to visible history instantly
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Route question to backend and await Gemini's generation
    with st.chat_message("assistant"):
        with st.spinner("Searching regulatory documents..."):
            try:
                payload = {"question": user_question}
                response = requests.post(f"{BACKEND_URL}/query", json=payload)

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer")
                    sources = data.get("sources", [])

                    # If sources exist, append a scannable footer block
                    if sources:
                        answer += f"\n\n**Sources scrutinized:** {', '.join(sources)}"

                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}"
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Failed to fetch response from backend server: {str(e)}")
