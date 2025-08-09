"""
Tests for speech processing modules
"""
import unittest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.speech.speech_to_text import SpeechToText
from src.speech.text_to_speech import TextToSpeech


class TestSpeechToText(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.stt = SpeechToText()
        
    def test_wake_word_detection(self):
        """Test wake word detection functionality"""
        # Test positive cases
        self.assertTrue(self.stt.detect_wake_word("hey assistant"))
        self.assertTrue(self.stt.detect_wake_word("Hey Assistant how are you"))
        self.assertTrue(self.stt.detect_wake_word("I said hey assistant"))
        
        # Test negative cases
        self.assertFalse(self.stt.detect_wake_word("hello there"))
        self.assertFalse(self.stt.detect_wake_word("assistant hey"))
        self.assertFalse(self.stt.detect_wake_word(""))
        
    @patch('src.speech.speech_to_text.whisper')
    def test_transcribe_audio(self, mock_whisper):
        """Test audio transcription"""
        # Mock Whisper response
        mock_whisper.load_model.return_value.transcribe.return_value = {
            "text": "Hello world"
        }
        
        # Test transcription
        audio_data = np.random.random(16000)  # 1 second of audio
        result = self.stt.transcribe_audio(audio_data)
        
        self.assertEqual(result, "Hello world")
        
    def test_audio_preprocessing(self):
        """Test audio data preprocessing"""
        # Test with different audio formats
        audio_2d = np.random.random((1000, 2))  # Stereo audio
        audio_1d = np.random.random(1000)       # Mono audio
        
        # Should handle both formats without error
        try:
            self.stt.transcribe_audio(audio_2d)
            self.stt.transcribe_audio(audio_1d)
        except Exception as e:
            self.fail(f"Audio preprocessing failed: {e}")


class TestTextToSpeech(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.tts = TextToSpeech()
        
    @patch('src.speech.text_to_speech.pyttsx3')
    def test_pyttsx3_initialization(self, mock_pyttsx3):
        """Test pyttsx3 TTS engine initialization"""
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        
        # Create TTS instance
        tts = TextToSpeech(engine_type="pyttsx3")
        
        # Verify initialization
        mock_pyttsx3.init.assert_called_once()
        self.assertIsNotNone(tts.engine)
        
    def test_speak_functionality(self):
        """Test basic speak functionality"""
        # Mock the engine to avoid actual speech output during tests
        self.tts.engine = Mock()
        
        # Test speaking
        result = self.tts.speak("Hello world")
        
        # Should return True for successful speech
        self.assertTrue(result)
        
    def test_voice_properties(self):
        """Test voice property setting"""
        # Mock the engine
        self.tts.engine = Mock()
        self.tts.engine_type = "pyttsx3"
        
        # Test setting voice properties
        self.tts.set_voice_properties(rate=1.5, volume=0.8)
        
        # Verify properties were set
        self.tts.engine.setProperty.assert_called()
        
    def test_list_voices(self):
        """Test voice listing functionality"""
        # Mock the engine
        self.tts.engine = Mock()
        self.tts.engine_type = "pyttsx3"
        
        # Mock voices
        mock_voice = Mock()
        mock_voice.id = "voice1"
        mock_voice.name = "Test Voice"
        self.tts.engine.getProperty.return_value = [mock_voice]
        
        # Test listing voices
        voices = self.tts.list_voices()
        
        self.assertEqual(len(voices), 1)
        self.assertEqual(voices[0]["id"], "voice1")
        self.assertEqual(voices[0]["name"], "Test Voice")


if __name__ == '__main__':
    unittest.main()
