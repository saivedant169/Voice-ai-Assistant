"""
Configuration settings for the Voice AI Assistant
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    
    # Assistant Settings
    ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Assistant")
    WAKE_WORD = os.getenv("WAKE_WORD", "hey assistant")
    VOICE_SPEED = float(os.getenv("VOICE_SPEED", "1.0"))
    VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", "0.8"))
    
    # Audio Settings
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))
    CHANNELS = int(os.getenv("CHANNELS", "1"))
    
    # Conversation Settings
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
    RESPONSE_TIMEOUT = int(os.getenv("RESPONSE_TIMEOUT", "30"))
    LISTENING_TIMEOUT = int(os.getenv("LISTENING_TIMEOUT", "5"))
    
    # Model Settings
    WHISPER_MODEL = "base"  # base, small, medium, large
    GPT_MODEL = "gpt-3.5-turbo"
    
    # TTS Settings
    TTS_ENGINE = "pyttsx3"  # pyttsx3, azure, elevenlabs
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        return True
