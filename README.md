# TinyTales AI 🎙️

An AI-powered MVP that generates engaging short stories and converts them to audio using advanced text-to-speech technology.

## Features

- **AI Story Generation**: Create unique short stories (~300 words) using Groq's Llama 3.3 LLM
- **Iterative Refinement**: Provide feedback to refine stories (up to 3 revisions)
- **Text-to-Speech**: Convert stories to natural-sounding audio using Cartesia's Sonic 3.5 model
- **Voice Selection**: Choose from multiple voice options to narrate your stories
- **Session Management**: Resume previous sessions or start fresh storytelling sessions
- **LangGraph Orchestration**: Robust workflow management with state persistence

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.3 70B)
- **Text-to-Speech**: Cartesia (Sonic 3.5)
- **Workflow**: LangGraph
- **Language**: Python 3.10+

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── driver.py           # Core session and workflow functions
├── graph_builder.py    # LangGraph workflow definition
├── agents.py           # AI agents for story generation and refinement
├── models.py           # LLM model configurations
├── router.py           # Conditional routing logic
├── schema.py           # Data models and constants
├── config.py           # Configuration and constants
├── voices.py           # Voice catalogue management
├── requirements.txt    # Python dependencies
├── jnb/               # Jupyter notebooks (development/testing)
├── output/
│   └── audio/         # Generated audio files
└── .env               # Environment variables (not in repo)
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "TinyTales AI"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   CARTESIA_API_KEY=your_cartesia_api_key_here
   ```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will:
1. Open in your default browser at `http://localhost:8501`
2. Allow you to enter a story topic
3. Select a voice for narration
4. Generate a story and produce an audio file
5. Provide feedback to refine the story if needed

## Configuration

Edit `config.py` to customize:
- **Story Length**: `TARGET_WORDS` (currently 300 words ≈ 60 seconds)
- **Voice**: `CARTESIA_VOICE` (select from voice catalogue)
- **Audio Format**: `CARTESIA_OUTPUT_FORMAT` (sample rate, encoding, etc.)
- **LLM Model**: `GROQ_MODEL` (change Groq model)
- **Max Revisions**: `MAX_REVISIONS` (feedback iterations)

## Dependencies

- `groq` - Groq API client
- `langchain` - LLM framework
- `langchain-groq` - Groq integration
- `langgraph` - Workflow orchestration
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management
- `streamlit` - Web UI framework

## Workflow

The application uses LangGraph to orchestrate the following workflow:

1. **Input Agent**: Validates user input
2. **Generator Agent**: Creates story using LLM
3. **Formatter Agent**: Formats story for audio
4. **TTS Agent**: Generates audio using Cartesia
5. **Router**: Determines if revision is needed based on user feedback

### Human-In-The-Loop (HITL)

The workflow incorporates HITL capabilities through LangGraph's `interrupt()` function, allowing users to:
- Review generated stories before audio conversion
- Provide detailed feedback for story refinement
- Approve stories or request revisions (up to 3 iterations)
- Resume sessions with persistent state management

## API Keys Required

- **Groq API Key**: Get from [console.groq.com](https://console.groq.com)
- **Cartesia API Key**: Get from [cartesia.ai](https://www.cartesia.ai)

## Output

Generated audio files are saved to `output/audio/` with timestamps for easy organization.

## Author

Shubham Jain