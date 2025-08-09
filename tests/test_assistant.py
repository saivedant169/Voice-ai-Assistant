"""
Tests for the main Voice Assistant
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.assistant import VoiceAssistant


class TestVoiceAssistant(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Mock all the components to avoid initialization issues during testing
        with patch('src.assistant.SpeechToText'), \
             patch('src.assistant.TextToSpeech'), \
             patch('src.assistant.ChatHandler'), \
             patch('src.assistant.AudioRecorder'), \
             patch('src.assistant.AudioPlayer'), \
             patch('config.settings.Config.validate'):
            self.assistant = VoiceAssistant()
            
    def test_initialization(self):
        """Test assistant initialization"""
        self.assertIsNotNone(self.assistant.stt)
        self.assertIsNotNone(self.assistant.tts)
        self.assertIsNotNone(self.assistant.chat)
        self.assertIsNotNone(self.assistant.recorder)
        self.assertIsNotNone(self.assistant.player)
        
    def test_status_tracking(self):
        """Test assistant status tracking"""
        # Initial state
        self.assertFalse(self.assistant.is_active)
        self.assertFalse(self.assistant.is_listening)
        self.assertFalse(self.assistant.conversation_active)
        
        # Test status retrieval
        status = self.assistant.get_status()
        self.assertIn('is_active', status)
        self.assertIn('assistant_name', status)
        self.assertIn('wake_word', status)
        
    def test_text_input_processing(self):
        """Test text input processing"""
        # Mock the chat handler
        self.assistant.chat.handle_command = Mock(return_value=("Help response", True))
        
        response = self.assistant.process_text_input("help")
        self.assertEqual(response, "Help response")
        
        # Test non-command input
        self.assistant.chat.handle_command = Mock(return_value=("", False))
        self.assistant.chat.get_response = Mock(return_value="AI response")
        
        response = self.assistant.process_text_input("What's 2+2?")
        self.assertEqual(response, "AI response")
        
    def test_callback_setting(self):
        """Test setting callbacks"""
        wake_callback = Mock()
        speech_callback = Mock()
        response_callback = Mock()
        error_callback = Mock()
        
        self.assistant.set_callbacks(
            on_wake_word_detected=wake_callback,
            on_speech_recognized=speech_callback,
            on_response_generated=response_callback,
            on_error=error_callback
        )
        
        self.assertEqual(self.assistant.on_wake_word_detected, wake_callback)
        self.assertEqual(self.assistant.on_speech_recognized, speech_callback)
        self.assertEqual(self.assistant.on_response_generated, response_callback)
        self.assertEqual(self.assistant.on_error, error_callback)
        
    def test_start_stop(self):
        """Test starting and stopping the assistant"""
        # Mock the listening methods to avoid actual audio processing
        self.assistant._listen_for_wake_word = Mock()
        self.assistant._start_continuous_listening = Mock()
        
        # Test start with wake word mode
        self.assistant.start(wake_word_mode=True)
        self.assertTrue(self.assistant.is_active)
        self.assertTrue(self.assistant.wake_word_mode)
        
        # Test stop
        self.assistant.stop()
        self.assertFalse(self.assistant.is_active)
        self.assertFalse(self.assistant.is_listening)
        
    def test_context_generation(self):
        """Test context information generation"""
        context = self.assistant._get_context()
        
        self.assertIn('time', context)
        self.assertIn('assistant_name', context)
        self.assertIn('conversation_active', context)
        
    def test_conversation_export_import(self):
        """Test conversation export and import functionality"""
        # Mock the memory methods
        self.assistant.chat.memory.export_to_file = Mock()
        self.assistant.chat.memory.import_from_file = Mock()
        
        # Test export
        self.assistant.export_conversation("test.json")
        self.assistant.chat.memory.export_to_file.assert_called_with("test.json")
        
        # Test import
        self.assistant.import_conversation("test.json")
        self.assistant.chat.memory.import_from_file.assert_called_with("test.json")
        
    def test_speak_text(self):
        """Test direct text speaking"""
        self.assistant.tts.speak = Mock()
        
        self.assistant.speak_text("Hello world")
        self.assistant.tts.speak.assert_called_with("Hello world")
        
    @patch('src.assistant.VoiceAssistant._get_context')
    def test_process_user_input(self, mock_context):
        """Test processing user input with context"""
        mock_context.return_value = {"time": "2023-01-01 12:00:00"}
        
        # Mock chat components
        self.assistant.chat.handle_command = Mock(return_value=("", False))
        self.assistant.chat.get_response = Mock(return_value="Test response")
        self.assistant.tts.speak = Mock()
        
        # Test processing
        self.assistant._process_user_input("Test input")
        
        # Verify chat was called with context
        self.assistant.chat.get_response.assert_called_with("Test input", {"time": "2023-01-01 12:00:00"})
        self.assistant.tts.speak.assert_called_with("Test response")


if __name__ == '__main__':
    unittest.main()
