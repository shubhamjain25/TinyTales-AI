# app.py
import uuid
import streamlit as st

from driver import get_state, start_fresh_session, resume_session
from voices import VOICE_CATALOGUE

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title   = "StoryVoice",
    page_icon    = "🎙️",
    layout       = "centered",
    initial_sidebar_state = "collapsed",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Fira+Mono:wght@400;500&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main > div { background-color: #0c0c10 !important; }

[data-testid="stAppViewContainer"] { color: #e8e3dc; font-family: 'Outfit', sans-serif; }

/* hide chrome */
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── LANDING ─────────────────────────────────────────────────── */
.hero {
    padding: 5rem 1rem 2.5rem;
    text-align: center;
    animation: rise 1s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.hero-glyph {
    font-size: 3rem;
    display: block;
    margin-bottom: 1.4rem;
    animation: levitate 4s ease-in-out infinite;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 4.2rem;
    font-weight: 700;
    color: #e8e3dc;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.hero-tagline {
    font-family: 'Fira Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c9913a;
    margin-bottom: 2rem;
}
.hero-desc {
    font-size: 1rem;
    color: #7a7680;
    max-width: 440px;
    margin: 0 auto 2.5rem;
    line-height: 1.8;
    font-weight: 300;
}
.pill-row {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 3rem;
}
.pill {
    background: #15151e;
    border: 1px solid #272732;
    border-radius: 100px;
    padding: 0.3rem 0.9rem;
    font-size: 0.7rem;
    color: #8a8695;
    letter-spacing: 0.04em;
}

/* steps strip */
.steps-strip {
    display: flex;
    gap: 1px;
    background: #1c1c26;
    border-radius: 10px;
    overflow: hidden;
    max-width: 480px;
    margin: 0 auto 3.5rem;
}
.step-cell {
    flex: 1;
    background: #0c0c10;
    padding: 0.9rem 0.5rem;
    text-align: center;
}
.step-num {
    font-family: 'Fira Mono', monospace;
    font-size: 0.6rem;
    color: #c9913a;
    letter-spacing: 0.12em;
    display: block;
    margin-bottom: 0.3rem;
}
.step-txt { font-size: 0.72rem; color: #7a7680; }

/* ── APP HEADER ──────────────────────────────────────────────── */
.app-bar {
    padding: 1.2rem 0 1rem;
    border-bottom: 1px solid #1c1c26;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 0.55rem;
}
.app-logo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: #e8e3dc;
}
.app-logo em { color: #c9913a; font-style: normal; }

/* ── FORM LABELS ─────────────────────────────────────────────── */
.field-label {
    font-family: 'Fira Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5e5b68;
    margin-bottom: 0.35rem;
    display: block;
}

/* voice description hint */
.voice-hint {
    font-family: 'Fira Mono', monospace;
    font-size: 0.7rem;
    color: #5e5b68;
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin: 0.4rem 0 1.4rem;
}
.hint-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #c9913a;
    flex-shrink: 0;
    animation: blink 1.8s ease-in-out infinite;
}

/* ── STORY CARD ──────────────────────────────────────────────── */
.story-card {
    background: #111118;
    border: 1px solid #222230;
    border-radius: 14px;
    padding: 2rem;
    margin: 1.2rem 0 1.5rem;
    animation: rise 0.55s ease both;
    position: relative;
    overflow: hidden;
}
.story-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #c9913a 0%, transparent 100%);
}
.card-eyebrow {
    font-family: 'Fira Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #c9913a;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 1.2rem;
}
.card-eyebrow-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #c9913a;
    animation: blink 1.6s ease-in-out infinite;
}
.card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: #e8e3dc;
    margin-bottom: 1.2rem;
    line-height: 1.2;
}
.card-body {
    font-family: 'Fira Mono', monospace;
    font-size: 0.8rem;
    color: #a0998e;
    line-height: 1.9;
    padding-left: 1rem;
    border-left: 2px solid #282836;
}
.card-footer {
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid #1c1c28;
    display: flex;
    gap: 0.6rem;
}
.badge {
    font-family: 'Fira Mono', monospace;
    font-size: 0.62rem;
    background: #1c180a;
    border: 1px solid #3a2e0e;
    color: #c9913a;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
    letter-spacing: 0.06em;
}

/* ── AUDIO CARD ──────────────────────────────────────────────── */
.audio-card {
    background: linear-gradient(140deg, #0e1a10 0%, #111810 100%);
    border: 1px solid #263026;
    border-radius: 14px;
    padding: 1.8rem 2rem 1.5rem;
    margin: 1rem 0 1.2rem;
    animation: rise 0.5s ease both;
    position: relative;
    overflow: hidden;
}
.audio-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4a9b5a 0%, transparent 100%);
}
.audio-eyebrow {
    font-family: 'Fira Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #4a9b5a;
    margin-bottom: 0.5rem;
}
.audio-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    color: #e8e3dc;
    margin-bottom: 1.2rem;
}
.filepath-hint {
    font-family: 'Fira Mono', monospace;
    font-size: 0.65rem;
    color: #4e4b58;
    margin-top: 0.8rem;
}

/* ── DIVIDER ─────────────────────────────────────────────────── */
.soft-divider { border: none; border-top: 1px solid #1c1c26; margin: 1.8rem 0; }

/* ── BUTTON OVERRIDES ────────────────────────────────────────── */
[data-testid="stButton"] > button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    border-radius: 9px !important;
    border: 1px solid #2a2a38 !important;
    background: #16161e !important;
    color: #c8c4be !important;
    transition: all 0.18s ease !important;
    padding: 0.55rem 1.2rem !important;
}
[data-testid="stButton"] > button:hover {
    border-color: #c9913a !important;
    color: #e8e3dc !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 18px rgba(201, 145, 58, 0.15) !important;
}
/* primary CTA — any button whose label starts with an arrow or check */
[data-testid="stButton"] > button[kind="primary"],
.cta-btn [data-testid="stButton"] > button {
    background: #c9913a !important;
    color: #0c0c10 !important;
    border-color: #c9913a !important;
}

/* input overrides */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: #14141c !important;
    border-color: #242432 !important;
    color: #e8e3dc !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.92rem !important;
    border-radius: 9px !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #c9913a !important;
    box-shadow: 0 0 0 2px rgba(201, 145, 58, 0.15) !important;
}
/* selectbox */
[data-baseweb="select"] > div {
    background: #14141c !important;
    border-color: #242432 !important;
    color: #e8e3dc !important;
    border-radius: 9px !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-baseweb="popover"] { background: #14141c !important; }

/* status widget */
[data-testid="stStatusContainer"] {
    background: #14141c !important;
    border-color: #242432 !important;
    border-radius: 10px !important;
    font-family: 'Fira Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* ── KEYFRAMES ───────────────────────────────────────────────── */
@keyframes rise {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0);    }
}
@keyframes levitate {
    0%, 100% { transform: translateY(0);   }
    50%       { transform: translateY(-9px); }
}
@keyframes blink {
    0%, 100% { opacity: 1;    }
    50%       { opacity: 0.2; }
}
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ───────────────────────────────────────────────────────────
def _init_session():
    defaults = {
        "page":          "landing",
        "thread_id":     str(uuid.uuid4()),
        "graph_state":   None,
        "voice_name":    list(VOICE_CATALOGUE.keys())[0],
        "show_feedback": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# ═══════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ═══════════════════════════════════════════════════════════════════════════
def _render_landing():
    st.markdown("""
    <div class="hero">
        <span class="hero-glyph">🎙️</span>
        <h1 class="hero-title">StoryVoice</h1>
        <p class="hero-tagline">AI Audio Story Generator &nbsp;·&nbsp; MVP</p>
        <p class="hero-desc">
            Drop a topic. Our AI writes a polished 60-second story,
            you review and approve it, then Cartesia delivers it as
            a lifelike audio file — in your chosen voice.
        </p>
        <div class="pill-row">
            <span class="pill">✦ LLM-Powered</span>
            <span class="pill">✦ Human-in-the-Loop</span>
            <span class="pill">✦ Cartesia TTS</span>
            <span class="pill">✦ 60-second stories</span>
        </div>
    </div>

    <div class="steps-strip">
        <div class="step-cell">
            <span class="step-num">01</span>
            <span class="step-txt">Pick a voice</span>
        </div>
        <div class="step-cell">
            <span class="step-num">02</span>
            <span class="step-txt">Write a topic</span>
        </div>
        <div class="step-cell">
            <span class="step-num">03</span>
            <span class="step-txt">Review story</span>
        </div>
        <div class="step-cell">
            <span class="step-num">04</span>
            <span class="step-txt">Listen</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1.3, 1, 1.3])
    with mid:
        if st.button("Start Creating →", use_container_width=True):
            st.session_state.page = "app"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  APP PAGE — SECTIONS
# ═══════════════════════════════════════════════════════════════════════════
def _app_header():
    st.markdown("""
    <div class="app-bar">
        <span style="font-size:1.1rem">🎙️</span>
        <span class="app-logo">Story<em>Voice</em></span>
    </div>
    """, unsafe_allow_html=True)


# ── Section 1: voice + topic form ──────────────────────────────────────────
def _render_form():
    st.markdown('<span class="field-label">Choose a voice</span>', unsafe_allow_html=True)
    voice_name = st.selectbox(
        "voice",
        options = list(VOICE_CATALOGUE.keys()),
        index   = list(VOICE_CATALOGUE.keys()).index(st.session_state.voice_name),
        label_visibility = "collapsed",
        key     = "voice_select",
    )
    st.session_state.voice_name = voice_name
    voice = VOICE_CATALOGUE[voice_name]

    st.markdown(
        f'<div class="voice-hint">'
        f'<span class="hint-dot"></span>'
        f'{voice["description"]} &nbsp;·&nbsp; {voice["accent"]}, {voice["gender"]}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<span class="field-label">Your story idea</span>', unsafe_allow_html=True)
    topic = st.text_area(
        "topic",
        label_visibility = "collapsed",
        placeholder      = "e.g. A lighthouse keeper who discovers a bottle with a map inside...",
        height           = 120,
        key              = "topic_input",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Generate Story →", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a story topic first.")
            return

        tid      = st.session_state.thread_id
        voice_id = voice["id"]

        with st.status("Crafting your story...", expanded=True) as s:
            st.write("🖊️  Writing a 60-second narrative...")
            state = start_fresh_session(tid, topic.strip(), voice_id)
            st.session_state.graph_state = state
            s.update(label="Story ready for your review", state="complete", expanded=False)

        st.rerun()


# ── Section 2: HITL story review ───────────────────────────────────────────
def _resolve_story_fields(state: dict) -> tuple[str, str]:
    """Handle Pydantic object OR post-checkpoint dict safely."""
    story = state.get("story") or {}
    if hasattr(story, "title"):
        return story.title, story.content
    return story.get("title", "Untitled"), story.get("content", "")


def _render_review(state: dict):
    title, content  = _resolve_story_fields(state)
    revision        = state.get("revision_count", 0)

    st.markdown(f"""
    <div class="story-card">
        <div class="card-eyebrow">
            <span class="card-eyebrow-dot"></span>
            Ready for Review
        </div>
        <div class="card-title">{title}</div>
        <div class="card-body">{content}</div>
        <div class="card-footer">
            <span class="badge">Revision {revision}</span>
            <span class="badge">~60 seconds</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("✅  Approve & Generate Audio", use_container_width=True):
            tid = st.session_state.thread_id
            with st.status("Bringing your story to life...", expanded=True) as s:
                st.write("📝  Formatting story for audio...")
                st.write("🎙️  Converting text to speech via Cartesia...")
                state = resume_session(tid, approved=True)
                st.session_state.graph_state  = state
                st.session_state.show_feedback = False
                s.update(label="Audio generated!", state="complete", expanded=False)
            st.rerun()

    with col_b:
        if st.button("🔁  Needs Revision", use_container_width=True):
            st.session_state.show_feedback = not st.session_state.get("show_feedback", False)
            st.rerun()

    if st.session_state.get("show_feedback"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="field-label">What should be improved?</span>', unsafe_allow_html=True)
        feedback = st.text_area(
            "feedback",
            label_visibility = "collapsed",
            placeholder      = "e.g. Make the ending more surprising. Cut the dialogue. Add more tension...",
            height           = 100,
            key              = "feedback_input",
        )
        if st.button("Send Feedback & Regenerate →", use_container_width=True):
            if not feedback.strip():
                st.warning("Please write some feedback before regenerating.")
                return
            tid = st.session_state.thread_id
            with st.status("Revising your story...", expanded=True) as s:
                st.write("📖  Reading your feedback...")
                st.write("🖊️  Rewriting the narrative...")
                state = resume_session(tid, approved=False, feedback=feedback.strip())
                st.session_state.graph_state  = state
                st.session_state.show_feedback = False
                s.update(label="New draft ready", state="complete", expanded=False)
            st.rerun()


# ── Section 3: audio player ────────────────────────────────────────────────
def _render_audio(state: dict):
    title, _   = _resolve_story_fields(state)
    audio_path = state.get("audio_path", "")

    st.markdown(f"""
    <div class="audio-card">
        <div class="audio-eyebrow">✓ &nbsp; Audio Generated</div>
        <div class="audio-title">{title}</div>
    </div>
    """, unsafe_allow_html=True)

    if audio_path:
        try:
            with open(audio_path, "rb") as f:
                st.audio(f.read(), format="audio/wav")
        except FileNotFoundError:
            st.error(f"Audio file not found at: `{audio_path}`")
    else:
        st.error("Audio path missing in state.")

    if audio_path:
        st.markdown(
            f'<p class="filepath-hint">🗂  {audio_path}</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        if st.button("+ Create Another Story", use_container_width=True):
            st.session_state.thread_id    = str(uuid.uuid4())
            st.session_state.graph_state  = None
            st.session_state.show_feedback = False
            st.rerun()


# ── Unexpected mid-flight states ────────────────────────────────────────────
def _render_processing(status: str):
    label_map = {
        "PARSED":         ("🖊️", "Writing your story..."),
        "NEEDS_REVISION": ("📖", "Applying feedback..."),
        "APPROVED":       ("📝", "Formatting for audio..."),
        "FORMATTED":      ("🎙️", "Converting to speech..."),
    }
    icon, label = label_map.get(status, ("⚙️", f"Processing ({status})..."))
    st.markdown(
        f'<div class="voice-hint" style="margin-top:2rem">'
        f'<span class="hint-dot"></span>'
        f'{icon} &nbsp; {label}'
        f'</div>',
        unsafe_allow_html=True,
    )
    # Auto-refresh to pick up next state
    import time; time.sleep(1)
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  APP PAGE — ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════
def _render_app():
    _app_header()

    # Always sync from checkpointer so browser refresh restores state
    live_state = get_state(st.session_state.thread_id)
    if live_state:
        st.session_state.graph_state = live_state

    state  = st.session_state.graph_state
    status = state.get("status") if state else None

    if status is None:
        _render_form()

    elif status == "GENERATED":
        _render_review(state)

    elif status in ("AUDIO_GENERATED", "PLAYED"):
        _render_audio(state)

    else:
        # Mid-flight nodes (PARSED, APPROVED, etc.) — transient, auto-advance
        _render_processing(status)


# ═══════════════════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    _render_landing()
else:
    _render_app()
