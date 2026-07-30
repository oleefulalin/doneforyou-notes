import streamlit as st
from groq import Groq
import tempfile
import os

st.set_page_config(page_title="DoneForYou Notes", page_icon="📝", layout="centered")

st.title("📝 DoneForYou Notes")
st.caption("Upload any meeting audio → Get Summary + Action Items + Email in 30 seconds")

# Get key from Streamlit secrets
groq_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else None

if not groq_key:
    groq_key = st.text_input("Paste your Groq API Key (gsk_...) to start - it's free", type="password")
    st.info("Get one free at console.groq.com -> API Keys")
    if not groq_key:
        st.stop()

client = Groq(api_key=groq_key)

uploaded = st.file_uploader("Upload meeting audio (mp3, m4a, wav, mp4)", type=["mp3","m4a","wav","mp4","m4","mpga"])

if uploaded:
    with st.spinner("Transcribing..."):
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        # Transcribe with Whisper
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, f.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        os.unlink(tmp_path)

    st.success("Transcribed! Now summarizing...")
    transcript_text = transcription if isinstance(transcription, str) else transcription.text

    with st.spinner("Writing your summary..."):
        prompt = f"""
        You are an executive assistant. Take this transcript and create:

        1. **SUMMARY** - 3 bullet points max
        2. **ACTION ITEMS** - List with Owner: Task format
        3. **FOLLOW-UP EMAIL** - Professional, ready to send

        Transcript:
        {transcript_text[:15000]}
        """

        summary = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content": prompt}]
        )
        result = summary.choices[0].message.content

    st.divider()
    st.markdown(result)

    st.divider()
    with st.expander("See Full Transcript"):
        st.write(transcript_text)

    st.download_button("Download Notes as.txt", result, file_name="meeting_notes.txt")
