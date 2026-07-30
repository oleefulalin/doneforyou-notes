import streamlit as st
from groq import Groq
import tempfile, os
from datetime import datetime

st.set_page_config(page_title="DoneForYou", page_icon="🎙️", layout="wide")

# --- CSS TO MATCH YOUR SCREENSHOT ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #f8f7f5; border-right: 1px solid #eee; }
   .stApp { background-color: #fdfcfb; }
    h1 { font-family: 'Georgia', serif; font-weight: 800!important; color: #111827!important; }
   .upload-card {
        border: 2px dashed #e5e7eb; background: white;
        border-radius: 16px; padding: 80px 20px; text-align: center;
    }
   .past-item {
        background: white; border: 1px solid #eee; padding: 12px;
        border-radius: 10px; margin-bottom: 8px; font-size: 14px;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #e5e7eb!important; border-radius: 16px!important;
        background: white!important; padding: 60px 20px!important;
    }
</style>
""", unsafe_allow_html=True)

if "notes" not in st.session_state:
    st.session_state.notes = []

groq_key = st.secrets.get("GROQ_API_KEY")
if not groq_key:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()
client = Groq(api_key=groq_key)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎙️ DoneForYou")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋ New Meeting Note", use_container_width=True, type="primary"):
        st.session_state.current_note = None
        st.rerun()

    st.markdown("<br><br>")
    st.markdown('<p style="font-size:11px; letter-spacing:1px; color:#9ca3af; font-weight:600;">PAST MEETINGS</p>', unsafe_allow_html=True)

    if not st.session_state.notes:
        st.markdown('<div style="text-align:center; margin-top:60px; color:#9ca3af;"><div style="font-size:30px;">🗃️</div><br>No notes yet</div>', unsafe_allow_html=True)
    else:
        for i, note in enumerate(reversed(st.session_state.notes)):
            if st.button(f"{note['title'][:22]}...", key=f"note_{i}", use_container_width=True):
                st.session_state.current_note = note

# --- MAIN ---
# If viewing a past note
if st.session_state.get("current_note"):
    note = st.session_state.current_note
    st.markdown(f"# {note['title']}")
    st.caption(f"Created {note['date']}")
    st.divider()
    st.markdown(note['content'])
    if st.button("← Back to upload"):
        st.session_state.current_note = None
        st.rerun()
    st.stop()

# Default Upload View
st.markdown("<div style='max-width:700px; margin: 40px auto 0 auto;'>", unsafe_allow_html=True)
st.markdown("# Your meetings, summarized.")
st.markdown('<p style="color:#6b7280; font-size:18px; margin-top:10px;">Upload your audio. We\'ll transcribe the conversation,<br>extract action items, and draft a follow-up email instantly.</p>', unsafe_allow_html=True)
st.markdown("</div><br><br>", unsafe_allow_html=True)

st.markdown("<div style='max-width:700px; margin: 0 auto;'>", unsafe_allow_html=True)
uploaded = st.file_uploader("", type=["mp3","m4a","wav","mp4","mpga"], label_visibility="collapsed")

if not uploaded:
    st.markdown("""
    <div style="text-align:center; margin-top:-140px; pointer-events:none;">
        <div style="background:white; width:70px; height:70px; margin:0 auto; border-radius:16px; display:flex; align-items:center; justify-content:center; border:1px solid #eee; font-size:32px;">🎧</div>
        <p style="font-weight:600; margin-top:20px; color:#111;">Click to upload or drag and drop</p>
        <p style="color:#9ca3af; font-size:14px;">Supports MP3, WAV, or M4A</p>
        <br>
        <span style="background:#f3f1ee; padding:10px 18px; border-radius:20px; font-size:14px; font-weight:500;">Select Audio File</span>
    </div>
    """, unsafe_allow_html=True)

if uploaded:
    with st.status("Transcribing and summarizing...", expanded=True) as status:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(file=(tmp_path, f.read()), model="whisper-large-v3", response_format="text")
        os.unlink(tmp_path)
        transcript_text = transcription if isinstance(transcription, str) else str(transcription)

        st.write("Summarizing...")
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content": f"Format cleanly with: ## Summary, ## Action Items (Person: Task), ## Follow-up Email. Transcript:\n{transcript_text[:12000]}"}]
        )
        result = chat.choices[0].message.content
        status.update(label="Ready!", state="complete", expanded=False)

    st.markdown(result)

    # Save to history
    title = f"Meeting {datetime.now().strftime('%b %d, %I:%M %p')}"
    st.session_state.notes.append({"title": title, "date": datetime.now().strftime('%Y-%m-%d %H:%M'), "content": result})

    st.download_button("Download Notes", result, file_name="notes.txt", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
