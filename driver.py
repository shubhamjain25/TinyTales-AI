from langgraph.types import Command
import uuid
from typing import Optional
from graph_builder import build_graph
from schema import AppState

# ═══════════════════════════════════════════════════════════════════════════
#  CORE FUNCTIONS  (called by Streamlit later — no print/input here)
# ═══════════════════════════════════════════════════════════════════════════

graph = build_graph()

def get_state(thread_id: str) -> Optional[AppState]:
    """
    Returns the current graph state for a thread, or None if it doesn't exist.
    Streamlit: call this to decide what to render (fresh form vs review panel).
    """
    config   = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)
    return snapshot.values if snapshot and snapshot.values else None

def start_fresh_session(thread_id: str, topic: str, voice_id: str) -> AppState:
    """
    Kicks off a brand-new story session.
    """
    config        = {"configurable": {"thread_id": thread_id}}
    initial_state = AppState(user_query = topic, revision_count = 0, status = "PARSED", formatted_story="", voice_id = voice_id)
    graph.invoke(initial_state, config=config)
    return get_state(thread_id)

def resume_session(thread_id : str, approved : bool, feedback  : Optional[str] = None,) -> AppState:
    """
    Resumes a session that is paused at the HITL node.
    Graph state is restored automatically from the checkpointer.
    Streamlit: call from 'Approve' / 'Revise' button handlers.
    """
    config = {"configurable": {"thread_id": thread_id}}

    resume_payload = {"approved": approved}
    if not approved:
        resume_payload["feedback"] = (feedback or "").strip()

    graph.invoke(Command(resume=resume_payload), config=config)
    return get_state(thread_id)

# ═══════════════════════════════════════════════════════════════════════════
#  CLI HARNESS  (temporary — replace entirely with Streamlit widgets)
# ═══════════════════════════════════════════════════════════════════════════

def _display_story(state: AppState) -> None:
    """Pretty-print the current story. → Replace with st.markdown() in Streamlit."""
    story = state.get("story")
    if not story:
        print("  (no story yet)")
        return
    print(f"\n  Title   : {story.title}")
    print(f"  Content : {story.content}")
    print(f"  Revision: {state['revision_count']}")
    print(f"  Status  : {state['status']}")


def _get_hitl_input() -> dict:
    """
    Structured input collection from the terminal.
    → Replace with st.radio + st.text_area + st.button in Streamlit.
    Returns: {"approved": bool, "feedback": str | None}
    """
    while True:
        choice = input("\n  Approve story? [y / n]: ").strip().lower()
        if choice in ("y", "n","Yes","No","yes","no"):
            break
        print("  Please enter Yes or No.")

    if choice.lower() in ("yes","y"):
        approved = True
    else:
        approved = False

    feedback = None

    if not approved:
        while True:
            feedback = input("  Feedback for revision: ").strip()
            if feedback:
                break
            print("  Feedback cannot be empty.")

    return {"approved": approved, "feedback": feedback}


def run(thread_id: Optional[str] = None):


    thread_id = thread_id or str(uuid.uuid4())
    print(f"\n[thread_id: {thread_id}]")

    state = get_state(thread_id)

    # ── No existing state → start fresh ────────────────────────────────────
    if state is None:
        topic = input("Enter story topic: ").strip()
        print(f"\nGenerating story for: '{topic}' ...")
        state = start_fresh_session(thread_id, topic)

    # ── HITL loop ───────────────────────────────────────────────────────────
    while state and state.get("status") != "FORMATTED":
        status = state.get("status")

        if status == "GENERATED":
            print("\n──────────── Story Ready for Review ────────────")
            _display_story(state)

            hitl_input = _get_hitl_input()
            state = resume_session(
                thread_id = thread_id,
                approved  = hitl_input["approved"],
                feedback  = hitl_input.get("feedback"),
            )

        elif status in ("APPROVED", "PARSED"):
            # Graph is mid-flight between nodes; just read updated state
            state = get_state(thread_id)

        else:
            break

    # ── Done ────────────────────────────────────────────────────────────────
    if state and state.get("status") == "FORMATTED":
        print("\n──────────── Final Formatted Story ─────────────")
        print(f"  {state['formatted_story']}")
        print("\n✓ Story ready for TTS pipeline.")
    else:
        print("\n  Session ended without a formatted story.")

