import streamlit as st
from groq import Groq
import tempfile, os
from datetime import datetime

st.set_page_config(page_title="DoneForYou", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
    /* HIDE ALL STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    a[href*="github"] {display: none !important;}
    .stDeployButton {display: none !important;}
</style>
""", unsafe_allow_html=True)

if "notes" not in st.session_state:
    st.session_state.notes = []
if "current_note" not in st.session_state:
    st.session_state.current_note = None

groq_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=groq_key) if groq_key else None

# SIDEBAR - stays light
with st.sidebar:
    st.markdown("## 🎙️ DoneForYou")
    st.markdown("")
    if st.button("＋ New Meeting Note", use_container_width=True, type="primary"):
        st.session_state.current_note = None
        st.rerun()
    st.markdown("---")
    st.markdown("PAST MEETINGS")
    if not st.session_state.notes:
        st.markdown("🗃️")
        st.caption("No notes yet")
    else:
        for n in reversed(st.session_state.notes):
            if st.button(n['title'], key=n['date'], use_container_width=True):
                st.session_state.current_note = n
                st.rerun()

# MAIN
if st.session_state.current_note:
    st.title(st.session_state.current_note['title'])
    st.caption(st.session_state.current_note['date'])
    st.divider()
    st.markdown(st.session_state.current_note['content'])
    if st.button("← Back to upload"):
        st.session_state.current_note = None
        st.rerun()
    st.stop()

# UPLOAD SCREEN
st.markdown("<br><br>", unsafe_allow_html=True)
st.title("Your meetings, summarized.")
st.write("Upload your audio. We'll transcribe the conversation, extract action items, and draft a follow-up email instantly.")
st.markdown("<br>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Drop your audio file here", type=["mp3","m4a","wav","mp4"], help="MP3, WAV, M4A up to 200MB")

st.caption("Click to upload or drag and drop • Supports MP3, WAV, M4A")

if uploaded_file and client:
    with st.spinner("Transcribing..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(file=(tmp_path, f.read()), model="whisper-large-v3", response_format="text")
        os.unlink(tmp_path)
        text = transcription if isinstance(transcription, str) else str(transcription)

        st.info("Transcription done. Summarizing...")
        chat = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content": f"Summarize: ## Summary (3 bullets), ## Action Items, ## Follow-up Email. Transcript: {text[:12000]}"}])
        result = chat.choices[0].message.content

    st.success("Done!")
    st.markdown(result)

    title = f"Meeting {datetime.now().strftime('%b %d %I:%M %p')}"
    st.session_state.notes.append({"title": title, "date": datetime.now().strftime('%Y-%m-%d %H:%M'), "content": result})
    st.download_button("Download Notes", result, file_name="notes.txt")
