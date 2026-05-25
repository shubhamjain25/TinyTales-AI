from typing import Literal, Annotated, Optional, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
import operator

###########################################
#HARD CONSTANTS

MAX_REVISIONS = 3
GROQ_MODEL = "llama-3.3-70b-versatile"
TARGET_WORDS = 300  # ~120s at avg reading/speaking pace
PREVIEW_SENTENCE_LIMIT = 3   # ~15-20s of audio, conserves API credits

###########################################

class Story(BaseModel):
    title: str = Field(
        description="The title of the story",
    )
    content: str = Field(
        description=(
            f"Complete story content. Must be ~{TARGET_WORDS} words "
            "(≈60 seconds spoken aloud). No markdown, no special formatting."
        )
    )


class AppState(TypedDict):
    user_query: str
    revision_count: Annotated[int, operator.add]
    status: Literal["PARSED", "GENERATED", "APPROVED", "NEEDS_REVISION", "FORMATTED", "AUDIO_GENERATED","PLAYED"]
    messages: Annotated[list, add_messages]
    feedback: Annotated[list[str], operator.add]
    story: Optional[Story]
    formatted_story: str
    audio_path: Optional[str]
    audio_preview: str
    voice_id: str