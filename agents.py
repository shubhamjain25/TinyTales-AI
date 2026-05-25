from config import *
from schema import AppState, Story, TARGET_WORDS, MAX_REVISIONS, PREVIEW_SENTENCE_LIMIT
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt, Command
import re
from models import *
import uuid

def input_agent(p_state: AppState):
    """
    Validates that user_query exists and initialises mutable counters.
    Keeping this node makes it easy to add pre-processing later
    (language detection, topic moderation, length checks, etc.).
    """
    query = p_state.get("user_query", "").strip()
    if not query:
        raise ValueError("user_query must not be empty.")

    return {
        "status": "PARSED",
        "revision_count": 0,  #not increasing since not required here
    }


def generator_agent(p_state: AppState):
    """
    Generates (or regenerates) the story. On retries, the full feedback
    history is injected so the LLM compounds all previous notes.
    """
    llm = get_creative_llm()
    structured_llm = llm.with_structured_output(Story)

    system_prompt = f"""You are a professional short-story writer specialising in
        audio content. Write engaging stories that are EXACTLY ~{TARGET_WORDS} words long (approximately 60 seconds when read aloud at a natural pace).

        Hard rules:
        - ~{TARGET_WORDS} words — no shorter, no longer
        - Clear arc: setup → conflict/tension → resolution
        - Natural spoken language; sentences vary in length for rhythm
        - Zero markdown, zero bullet points, zero special characters
        - No dialogue tags like "(laughs)" or "[pause]"
        """

    feedback_history = p_state.get("feedback") or []
    if feedback_history:
        numbered = "\n".join(f"{i+1}. {fb}" for i, fb in enumerate(feedback_history))
        user_msg = (
            f"Topic: {p_state['user_query']}\n\n"
            f"This is revision #{p_state['revision_count']}. "
            f"Address ALL of the following feedback points:\n{numbered}"
        )
    else:
        user_msg = f"Topic: {p_state['user_query']}"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ]

    story: Story = structured_llm.invoke(messages)

    return {
        "story":    story,
        "status":   "GENERATED",
        "messages": messages,
    }


def hitl_agent(p_state: AppState):

    story = p_state["story"]
    # ── Pause here; everything below runs AFTER the human responds ──
    human_response = interrupt({
        "title":          story.title,
        "content":        story.content,
        "revision_count": p_state["revision_count"],
        "max_revisions":  MAX_REVISIONS,
        "instructions":   (
            'Reply with {"approved": true} to accept, '
            'or {"approved": false, "feedback": "<your notes>"} to revise.'
        ),
    })

    approved      = human_response.get("approved", False)
    feedback_text = human_response.get("feedback", "").strip()

    if approved:
        return {"status": "APPROVED"}

    return {
        "status":         "NEEDS_REVISION",
        "feedback":       [feedback_text] if feedback_text else ["Please improve the story."],
        "revision_count": 1,          # operator.add increments the counter
    }


def formatter_agent(p_state: AppState):
    """
    Prepares the approved story for Cartesia TTS:
      - Strips any markdown that slipped through
      - Normalises punctuation and whitespace
      - Prepends the title as a spoken introduction
    The output lands in `formatted_story` for the TTS node (next sprint).
    """
    story   = p_state["story"]

     # Guard: Pydantic model may come back as a dict after checkpoint
    if isinstance(story, dict):
        title   = story.get("title", "")
        content = story.get("content", "")
    else:
        title   = story.title
        content = story.content

    # Clean for TTS
    content = re.sub(r"\*+",           "", content)
    content = re.sub(r"#+\s*",         "", content)
    content = re.sub(r"\[.*?\]\(.*?\)","", content)
    content = re.sub(r"`+",            "", content)
    content = content.replace("\u201c", '"').replace("\u201d", '"')
    content = content.replace("\u2018", "'").replace("\u2019", "'")
    content = re.sub(r"\s+", " ", content).strip()

    # This MUST be a plain str — not a Story, not a dict
    formatted: str = f"{title}\n{content}"

    return {
        "formatted_story": formatted,
        "status":          "FORMATTED",
    }

def _get_audio_preview(text: str, sentence_limit: int = PREVIEW_SENTENCE_LIMIT) -> str:
    """
    Returns the first N sentences for TTS. Full story is shown in the UI.
    Keeps punctuation-aware splits so Cartesia gets clean, complete sentences.
    """
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    preview   = " ".join(sentences[:sentence_limit])
    return preview

def tts_agent(p_state: AppState) -> dict:
    """
    Calls Cartesia /tts/bytes with the formatter's output.
    Saves audio to AUDIO_DIR/<uuid>.wav and returns the path in state.
    """

    text = p_state.get("formatted_story")
    voice_id = p_state.get("voice_id")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = AUDIO_DIR / f"v1_{uuid.uuid4()}.wav"

    # ── Only send a short preview to conserve API credits ─────────────────
    tts_text = _get_audio_preview(text)

    client = get_cartesia_client()

    try:
        audio_bytes: bytes = client.tts.bytes(
            model_id      = CARTESIA_MODEL,
            transcript    = tts_text,
            voice={
                "mode": "id",
                "id": voice_id,
            },
            output_format = CARTESIA_OUTPUT_FORMAT,
            language = "en",
        )
    except Exception as e:
        raise Exception(f"Cartesia API error: {e}") from e

    with open(audio_path, "wb") as f:
        for chunk in audio_bytes:
            f.write(chunk)

    return {
        "audio_path": str(audio_path),
        "audio_preview": tts_text,
        "status":     "AUDIO_GENERATED",
    }