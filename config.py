from pathlib import Path

# ── Config — swap these from Streamlit dropdowns later ─────────────────────
CARTESIA_MODEL  = "sonic-3.5"
CARTESIA_VOICE  = "7e8cb11d-37af-476b-ab8f-25da99b18644"  # Anuj (Indian)
CARTESIA_OUTPUT_FORMAT = {
    "container":   "wav",
    "encoding":    "pcm_f32le",
    "sample_rate": 44100,
}
AUDIO_DIR = Path("output/audio")