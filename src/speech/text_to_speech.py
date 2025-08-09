"""
Text-to-Speech implementation with multiple engine support
"""
import pyttsx3
import os
from typing import Optional
from config.settings import Config


class TextToSpeech:
    def __init__(self, engine_type: str = Config.TTS_ENGINE):
        """
        Initialize the text-to-speech engine
        
        Args:
            engine_type: Type of TTS engine ('pyttsx3', 'azure', 'elevenlabs')
        """
        self.engine_type = engine_type
        self.engine = None
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize the appropriate TTS engine"""
        if self.engine_type == "pyttsx3":
            self._init_pyttsx3()
        elif self.engine_type == "azure":
            self._init_azure()
        elif self.engine_type == "elevenlabs":
            self._init_elevenlabs()
        else:
            raise ValueError(f"Unsupported TTS engine: {self.engine_type}")
            
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use the first available voice
                    self.engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.engine.setProperty('rate', int(200 * Config.VOICE_SPEED))
            self.engine.setProperty('volume', Config.VOICE_VOLUME)
            
        except Exception as e:
            print(f"Error initializing pyttsx3: {e}")
            self.engine = None
            
    def _init_azure(self):
        """Initialize Azure Speech Services"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            if not Config.AZURE_SPEECH_KEY or not Config.AZURE_SPEECH_REGION:
                raise ValueError("Azure Speech key and region are required")
                
            speech_config = speechsdk.SpeechConfig(
                subscription=Config.AZURE_SPEECH_KEY,
                region=Config.AZURE_SPEECH_REGION
            )
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            
            self.engine = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            
        except ImportError:
            print("Azure Speech SDK not installed. Install with: pip install azure-cognitiveservices-speech")
            self.engine = None
        except Exception as e:
            print(f"Error initializing Azure TTS: {e}")
            self.engine = None
            
    def _init_elevenlabs(self):
        """Initialize ElevenLabs TTS"""
        try:
            from elevenlabs import generate, set_api_key
            
            if not Config.ELEVENLABS_API_KEY:
                raise ValueError("ElevenLabs API key is required")
                
            set_api_key(Config.ELEVENLABS_API_KEY)
            self.engine = generate
            
        except ImportError:
            print("ElevenLabs not installed. Install with: pip install elevenlabs")
            self.engine = None
        except Exception as e:
            print(f"Error initializing ElevenLabs TTS: {e}")
            self.engine = None
            
    def speak(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            save_to_file: Optional file path to save audio
            
        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            print("TTS engine not available")
            return False
            
        try:
            if self.engine_type == "pyttsx3":
                return self._speak_pyttsx3(text, save_to_file)
            elif self.engine_type == "azure":
                return self._speak_azure(text, save_to_file)
            elif self.engine_type == "elevenlabs":
                return self._speak_elevenlabs(text, save_to_file)
                
        except Exception as e:
            print(f"Error in TTS: {e}")
            return False
            
        return False
        
    def _speak_pyttsx3(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """Speak using pyttsx3"""
        try:
            if save_to_file:
                self.engine.save_to_file(text, save_to_file)
                self.engine.runAndWait()
            else:
                self.engine.say(text)
                self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 error: {e}")
            return False
            
    def _speak_azure(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """Speak using Azure Speech Services"""
        try:
            result = self.engine.speak_text_async(text).get()
            
            if save_to_file and result.audio_data:
                with open(save_to_file, "wb") as audio_file:
                    audio_file.write(result.audio_data)
                    
            return True
        except Exception as e:
            print(f"Azure TTS error: {e}")
            return False
            
    def _speak_elevenlabs(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """Speak using ElevenLabs"""
        try:
            audio = self.engine(
                text=text,
                voice="Bella",  # You can customize this
                model="eleven_monolingual_v1"
            )
            
            if save_to_file:
                with open(save_to_file, "wb") as f:
                    f.write(audio)
            else:
                # Play audio directly (requires additional audio playback library)
                import sounddevice as sd
                import numpy as np
                from io import BytesIO
                
                # This is a simplified playback - you might need proper audio decoding
                print("Audio generated successfully")
                
            return True
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            return False
            
    def set_voice_properties(self, rate: Optional[float] = None, volume: Optional[float] = None):
        """
        Update voice properties
        
        Args:
            rate: Speech rate multiplier
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine_type == "pyttsx3" and self.engine:
            if rate is not None:
                self.engine.setProperty('rate', int(200 * rate))
            if volume is not None:
                self.engine.setProperty('volume', volume)
                
    def list_voices(self) -> list:
        """Get list of available voices"""
        if self.engine_type == "pyttsx3" and self.engine:
            voices = self.engine.getProperty('voices')
            return [{"id": voice.id, "name": voice.name} for voice in voices] if voices else []
        return []
        
    def stop(self):
        """Stop current speech"""
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.stop()
