import streamlit as st
import requests

st.title("AI Document Summarizer")

uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    mode = st.radio("Choose output mode:", ["Structured Summary", "Live Streaming Summary", "Download as Markdown"])

    if st.button("Summarize"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

        if mode == "Structured Summary":
            try:
                response = requests.post("http://127.0.0.1:8000/summarize", files=files)
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server.")
            else:
                if response.status_code == 200:
                    result = response.json()
                    st.subheader("Executive Summary")
                    st.write(result["executive_summary"])

                    st.subheader("Key Points")
                    for point in result["bullet_points"]:
                        st.write(f"- {point}")

                    st.subheader("Key Takeaways")
                    for takeaway in result["key_takeaways"]:
                        st.write(f"- {takeaway}")

                    st.subheader("Action Items")
                    for item in result["action_items"]:
                        st.write(f"- {item}")
                else:
                    st.error(f"Error: {response.json()['detail']}")

        elif mode == "Live Streaming Summary":
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/summarize/stream",
                    files=files,
                    stream=True
                )
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server.")
            else:
                placeholder = st.empty()
                full_text = ""
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_text += chunk
                        placeholder.markdown(full_text)

        elif mode == "Download as Markdown":
            try:
                response = requests.post("http://127.0.0.1:8000/summarize/download", files=files)
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server.")
            else:
                if response.status_code == 200:
                    st.download_button(
                        label="Download Summary as Markdown",
                        data=response.content,
                        file_name="summary.md",
                        mime="text/markdown"
                    )
                else:
                    st.error(f"Error: {response.json()['detail']}")