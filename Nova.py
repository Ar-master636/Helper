import streamlit as st
import openai
import os
import whisper
import tempfile
from moviepy.editor import AudioFileClip
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# === OPENAI KEY (add yours in Streamlit Secrets later) ===
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not openai.api_key:
    st.error("OPENAI_API_KEY not found! Add it in Streamlit → Settings → Secrets.")
    st.stop()

# === LOAD WHISPER ONCE ===
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

# === PAGE TITLE ===
st.set_page_config(page_title="Nova AI – Turbo AI Killer", layout="centered")
st.title("Nova AI – Better Than Turbo AI")
st.markdown("**English only • Instant notes, quiz, flashcards, mind map & podcast**")

# === INPUT OPTIONS ===
tab1, tab2, tab3 = st.tabs(["Paste Text", "YouTube Link", "Upload File"])

text = ""

with tab1:
    text = st.text_area("Paste lecture notes, article, transcript, etc.", height=200)

with tab2:
    yt_url = st.text_input("Paste YouTube URL (auto-transcript coming soon – paste transcript for now)")
    if yt_url:
        st.info("Copy the video transcript and paste it in the first tab for best results.")

with tab3:
    uploaded = st.file_uploader("PDF • Audio • Video", type=["pdf", "txt", "mp3", "wav", "mp4", "m4a"])
    if uploaded:
        with st.spinner("Extracting text..."):
            if uploaded.type == "application/pdf":
                reader = PyPDF2.PdfReader(uploaded)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            elif uploaded.type.startswith("audio/") or uploaded.type.startswith("video/"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded.name) as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name
                if uploaded.type.startswith("video/"):
                    audio = AudioFileClip(tmp_path)
                    audio_path = tmp_path + ".wav"
                    audio.write_audiofile(audio_path, logger=None)
                    result = model.transcribe(audio_path)
                    os.unlink(audio_path)
                else:
                    result = model.transcribe(tmp_path)
                text = result["text"]
                os.unlink(tmp_path)
            else:
                text = uploaded.read().decode("utf-8")
        st.success("File processed!")
        st.text_area("Extracted text", text, height=150)

# === GENERATE BUTTON ===
if text.strip() and st.button("Generate Everything (Nova Ultra)", type="primary"):
    with st.spinner("Working magic... (5–12 seconds)"):
        try:
            # 1. Beautiful Notes
            notes = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Create beautiful, structured English study notes with emojis, tables, La
