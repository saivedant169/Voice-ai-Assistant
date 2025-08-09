# Voice-Activated AI Assistant

A sophisticated voice-activated AI assistant that combines speech-to-text, conversational AI, and text-to-speech technologies to provide a natural voice interaction experience.

## Features

- 🎤 **Real-time Speech Recognition** using OpenAI Whisper
- 🧠 **Intelligent Conversations** with context awareness
- 🔊 **Natural Text-to-Speech** output
- 💬 **Multi-turn Conversations** with memory
- ⚡ **Real-time Processing** for responsive interactions
- 🎛️ **Configurable Voice Settings** and wake words

## Tech Stack

- **Speech-to-Text**: OpenAI Whisper
- **Conversational AI**: OpenAI GPT-4 or compatible LLM
- **Text-to-Speech**: pyttsx3 / Azure Speech Services / ElevenLabs
- **Audio Processing**: PyAudio, sounddevice
- **Framework**: Python 3.8+
- **UI**: Streamlit (optional web interface)

## Project Structure

```
voice-ai-assistant/
├── src/
│   ├── __init__.py
│   ├── speech/
│   │   ├── __init__.py
│   │   ├── speech_to_text.py      # Whisper integration
│   │   └── text_to_speech.py      # TTS implementation
│   ├── conversation/
│   │   ├── __init__.py
│   │   ├── chat_handler.py        # Conversation management
│   │   └── memory.py              # Context and memory
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── recorder.py            # Audio recording
│   │   └── player.py              # Audio playback
│   └── assistant.py               # Main assistant class
├── config/
│   └── settings.py                # Configuration settings
├── tests/
│   ├── __init__.py
│   ├── test_speech.py
│   ├── test_conversation.py
│   └── test_assistant.py
├── examples/
│   ├── basic_usage.py
│   ├── web_interface.py           # Streamlit web UI
│   └── cli_assistant.py           # Command line interface
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
└── README.md
```

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your API keys
5. Run the assistant:
   ```bash
   python examples/cli_assistant.py
   ```

## Configuration

Set up your environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_api_key
AZURE_SPEECH_KEY=your_azure_speech_key (optional)
AZURE_SPEECH_REGION=your_region (optional)
ELEVENLABS_API_KEY=your_elevenlabs_key (optional)
```

## Usage

### Basic Usage
```python
from src.assistant import VoiceAssistant

assistant = VoiceAssistant()
assistant.start_listening()
```

### Web Interface
```bash
streamlit run examples/web_interface.py
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New TTS Engines
Extend the `text_to_speech.py` module to support additional TTS services.

### Customizing Wake Words
Modify the `speech_to_text.py` to add custom wake word detection.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper and GPT models
- Contributors to open-source speech processing libraries
