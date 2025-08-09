"""
Main Voice-Activated AI Assistant
"""
import time
import threading
from typing import Optional, Dict, Callable
from datetime import datetime

from config.settings import Config
from src.speech.speech_to_text import SpeechToText
from src.speech.text_to_speech import TextToSpeech
from src.conversation.chat_handler import ChatHandler
from src.audio.recorder import AudioRecorder
from src.audio.player import AudioPlayer


class VoiceAssistant:
    def __init__(self):
        """Initialize the Voice Assistant"""
        print("Initializing Voice Assistant...")
        
        # Validate configuration
        Config.validate()
        
        # Initialize components
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.chat = ChatHandler()
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        
        # Assistant state
        self.is_active = False
        self.is_listening = False
        self.wake_word_mode = True
        self.conversation_active = False
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_speech_recognized = None
        self.on_response_generated = None
        self.on_error = None
        
        print(f"✓ {Config.ASSISTANT_NAME} initialized successfully!")
        
    def start(self, wake_word_mode: bool = True):
        """
        Start the voice assistant
        
        Args:
            wake_word_mode: If True, listen for wake word. If False, always listen.
        """
        if self.is_active:
            print("Assistant is already running")
            return
            
        self.is_active = True
        self.wake_word_mode = wake_word_mode
        
        print(f"🎤 {Config.ASSISTANT_NAME} is now active!")
        
        if wake_word_mode:
            print(f"Say '{Config.WAKE_WORD}' to start a conversation")
            self._listen_for_wake_word()
        else:
            print("Listening for speech...")
            self._start_continuous_listening()
            
    def stop(self):
        """Stop the voice assistant"""
        self.is_active = False
        self.is_listening = False
        self.stt.stop_listening()
        self.player.stop_playback()
        
        print(f"👋 {Config.ASSISTANT_NAME} stopped")
        
    def _listen_for_wake_word(self):
        """Listen for wake word in a loop"""
        while self.is_active:
            try:
                if not self.conversation_active:
                    print("Listening for wake word...")
                    
                    # Record audio with voice activity detection
                    audio_data = self.recorder.record_with_vad(max_duration=10.0)
                    
                    if len(audio_data) > 0:
                        # Transcribe the audio
                        text = self.stt.transcribe_audio(audio_data)
                        
                        if text and self.stt.detect_wake_word(text):
                            print(f"✓ Wake word detected: {text}")
                            self._handle_wake_word_detected()
                        elif text:
                            print(f"Heard: {text} (not wake word)")
                            
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\\nStopping assistant...")
                self.stop()
                break
            except Exception as e:
                print(f"Error in wake word detection: {e}")
                if self.on_error:
                    self.on_error(e)
                time.sleep(1)
                
    def _handle_wake_word_detected(self):
        """Handle wake word detection"""
        self.conversation_active = True
        
        # Play acknowledgment sound
        self.player.play_notification_sound()
        
        # Acknowledge wake word
        self.tts.speak("Yes, how can I help you?")
        
        if self.on_wake_word_detected:
            self.on_wake_word_detected()
            
        # Start conversation
        self._start_conversation()
        
    def _start_conversation(self):
        """Start a conversation session"""
        print("\\n🗣️ Conversation started. Speak your request...")
        
        try:
            # Record user's request
            audio_data = self.recorder.record_with_vad(max_duration=30.0)
            
            if len(audio_data) > 0:
                # Transcribe
                user_input = self.stt.transcribe_audio(audio_data)
                
                if user_input:
                    print(f"You said: {user_input}")
                    self._process_user_input(user_input)
                else:
                    self.tts.speak("I didn't catch that. Please try again.")
            else:
                self.tts.speak("I didn't hear anything. Let me know if you need help.")
                
        except Exception as e:
            print(f"Error in conversation: {e}")
            self.tts.speak("I'm sorry, I encountered an error. Please try again.")
            if self.on_error:
                self.on_error(e)
                
        finally:
            self.conversation_active = False
            
    def _start_continuous_listening(self):
        """Start continuous listening mode (no wake word)"""
        while self.is_active:
            try:
                print("🎙️ Listening...")
                
                # Record audio with voice activity detection
                audio_data = self.recorder.record_with_vad(max_duration=30.0)
                
                if len(audio_data) > 0:
                    # Transcribe
                    user_input = self.stt.transcribe_audio(audio_data)
                    
                    if user_input:
                        self._process_user_input(user_input)
                        
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\\nStopping assistant...")
                self.stop()
                break
            except Exception as e:
                print(f"Error in continuous listening: {e}")
                if self.on_error:
                    self.on_error(e)
                time.sleep(1)
                
    def _process_user_input(self, user_input: str):
        """
        Process user input and generate response
        
        Args:
            user_input: Transcribed user speech
        """
        if self.on_speech_recognized:
            self.on_speech_recognized(user_input)
            
        # Check for special commands first
        command_response, is_command = self.chat.handle_command(user_input)
        
        if is_command:
            response = command_response
            
            # Handle special exit commands
            if any(phrase in user_input.lower() for phrase in ["goodbye", "exit", "quit", "stop listening"]):
                self.tts.speak(response)
                self.stop()
                return
        else:
            # Get AI response
            context = self._get_context()
            response = self.chat.get_response(user_input, context)
            
        print(f"Assistant: {response}")
        
        if self.on_response_generated:
            self.on_response_generated(response)
            
        # Speak the response
        self.tts.speak(response)
        
    def _get_context(self) -> Dict:
        """Get current context information"""
        return {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "assistant_name": Config.ASSISTANT_NAME,
            "conversation_active": self.conversation_active
        }
        
    def process_text_input(self, text: str) -> str:
        """
        Process text input directly (for testing or text-only mode)
        
        Args:
            text: Text input to process
            
        Returns:
            Assistant's response
        """
        context = self._get_context()
        
        # Check for commands
        command_response, is_command = self.chat.handle_command(text)
        
        if is_command:
            return command_response
        else:
            return self.chat.get_response(text, context)
            
    def speak_text(self, text: str):
        """
        Make the assistant speak text directly
        
        Args:
            text: Text to speak
        """
        self.tts.speak(text)
        
    def test_components(self) -> Dict[str, bool]:
        """
        Test all assistant components
        
        Returns:
            Dictionary with test results
        """
        results = {}
        
        print("🧪 Testing assistant components...")
        
        # Test audio input
        print("Testing audio input...")
        results['audio_input'] = self.recorder.test_audio_input(duration=2.0)
        
        # Test audio output
        print("Testing audio output...")
        results['audio_output'] = self.player.test_playback()
        
        # Test speech-to-text
        print("Testing speech-to-text...")
        try:
            test_audio = self.recorder.record_fixed_duration(3.0)
            if len(test_audio) > 0:
                test_result = self.stt.transcribe_audio(test_audio)
                results['speech_to_text'] = len(test_result) > 0
                print(f"STT result: {test_result}")
            else:
                results['speech_to_text'] = False
        except Exception as e:
            print(f"STT test failed: {e}")
            results['speech_to_text'] = False
            
        # Test text-to-speech
        print("Testing text-to-speech...")
        try:
            self.tts.speak("This is a test of the text to speech system.")
            results['text_to_speech'] = True
        except Exception as e:
            print(f"TTS test failed: {e}")
            results['text_to_speech'] = False
            
        # Test chat
        print("Testing conversation handler...")
        try:
            response = self.chat.get_response("Hello, this is a test")
            results['conversation'] = len(response) > 0
            print(f"Chat response: {response}")
        except Exception as e:
            print(f"Chat test failed: {e}")
            results['conversation'] = False
            
        # Print results
        print("\\n📊 Test Results:")
        for component, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {component}: {status}")
            
        return results
        
    def get_status(self) -> Dict:
        """Get current assistant status"""
        return {
            "is_active": self.is_active,
            "is_listening": self.is_listening,
            "wake_word_mode": self.wake_word_mode,
            "conversation_active": self.conversation_active,
            "assistant_name": Config.ASSISTANT_NAME,
            "wake_word": Config.WAKE_WORD,
            "conversation_stats": self.chat.memory.get_conversation_stats()
        }
        
    def set_callbacks(self, 
                     on_wake_word_detected: Optional[Callable] = None,
                     on_speech_recognized: Optional[Callable] = None,
                     on_response_generated: Optional[Callable] = None,
                     on_error: Optional[Callable] = None):
        """
        Set callback functions for events
        
        Args:
            on_wake_word_detected: Called when wake word is detected
            on_speech_recognized: Called when speech is recognized
            on_response_generated: Called when response is generated
            on_error: Called when an error occurs
        """
        self.on_wake_word_detected = on_wake_word_detected
        self.on_speech_recognized = on_speech_recognized
        self.on_response_generated = on_response_generated
        self.on_error = on_error
        
    def export_conversation(self, filename: str):
        """Export conversation history to file"""
        self.chat.memory.export_to_file(filename)
        
    def import_conversation(self, filename: str):
        """Import conversation history from file"""
        self.chat.memory.import_from_file(filename)
