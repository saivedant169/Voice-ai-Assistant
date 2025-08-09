"""
Tests for conversation handling
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conversation.chat_handler import ChatHandler
from src.conversation.memory import ConversationMemory


class TestConversationMemory(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.memory = ConversationMemory(max_messages=4)
        
    def test_add_message(self):
        """Test adding messages to memory"""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there!")
        
        messages = self.memory.get_all_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "Hello")
        
    def test_message_limit(self):
        """Test message limit enforcement"""
        # Add more messages than the limit
        for i in range(10):
            self.memory.add_message("user", f"Message {i}")
            
        messages = self.memory.get_all_messages()
        # Should not exceed double the limit (user + assistant pairs)
        self.assertLessEqual(len(messages), 8)
        
    def test_recent_messages(self):
        """Test getting recent messages"""
        self.memory.add_message("user", "First")
        self.memory.add_message("assistant", "Response 1")
        self.memory.add_message("user", "Second")
        self.memory.add_message("assistant", "Response 2")
        
        recent = self.memory.get_recent_messages(2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["content"], "Second")
        
    def test_clear_memory(self):
        """Test clearing conversation memory"""
        self.memory.add_message("user", "Test")
        self.memory.clear()
        
        messages = self.memory.get_all_messages()
        self.assertEqual(len(messages), 0)
        
    def test_context_data(self):
        """Test context data management"""
        self.memory.add_context("user_name", "John")
        self.memory.add_context("location", "New York")
        
        self.assertEqual(self.memory.get_context("user_name"), "John")
        self.assertEqual(self.memory.get_context("location"), "New York")
        self.assertIsNone(self.memory.get_context("nonexistent"))
        
        self.memory.remove_context("user_name")
        self.assertIsNone(self.memory.get_context("user_name"))
        
    def test_search_messages(self):
        """Test message search functionality"""
        self.memory.add_message("user", "What's the weather like?")
        self.memory.add_message("assistant", "It's sunny today")
        self.memory.add_message("user", "Tell me about the weather tomorrow")
        
        # Search for weather-related messages
        results = self.memory.search_messages("weather")
        self.assertEqual(len(results), 2)
        
        # Search for user messages only
        user_results = self.memory.search_messages("weather", role="user")
        self.assertEqual(len(user_results), 2)
        
    def test_conversation_stats(self):
        """Test conversation statistics"""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi")
        self.memory.add_message("user", "How are you?")
        
        stats = self.memory.get_conversation_stats()
        self.assertEqual(stats["total_messages"], 3)
        self.assertEqual(stats["user_messages"], 2)
        self.assertEqual(stats["assistant_messages"], 1)


class TestChatHandler(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.chat = ChatHandler()
        
    def test_command_handling(self):
        """Test special command handling"""
        # Test clear command
        response, is_command = self.chat.handle_command("clear conversation")
        self.assertTrue(is_command)
        self.assertIn("cleared", response.lower())
        
        # Test help command
        response, is_command = self.chat.handle_command("help")
        self.assertTrue(is_command)
        self.assertIn("help", response.lower())
        
        # Test goodbye command
        response, is_command = self.chat.handle_command("goodbye")
        self.assertTrue(is_command)
        self.assertIn("goodbye", response.lower())
        
        # Test non-command
        response, is_command = self.chat.handle_command("What's 2+2?")
        self.assertFalse(is_command)
        
    @patch('src.conversation.chat_handler.openai.OpenAI')
    def test_get_response(self, mock_openai):
        """Test getting AI response"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help?"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test getting response
        chat = ChatHandler()
        response = chat.get_response("Hello")
        
        self.assertEqual(response, "Hello! How can I help?")
        
    def test_personality_setting(self):
        """Test setting assistant personality"""
        original_content = self.chat.system_message["content"]
        
        new_personality = "a helpful cooking assistant"
        self.chat.set_personality(new_personality)
        
        self.assertIn(new_personality, self.chat.system_message["content"])
        self.assertNotEqual(original_content, self.chat.system_message["content"])
        
    def test_conversation_export_import(self):
        """Test conversation export and import"""
        # Add some messages
        self.chat.memory.add_message("user", "Hello")
        self.chat.memory.add_message("assistant", "Hi there!")
        
        # Export conversation
        exported = self.chat.export_conversation()
        self.assertEqual(len(exported), 2)
        
        # Clear and import
        self.chat.memory.clear()
        self.chat.import_conversation(exported)
        
        # Verify import
        messages = self.chat.memory.get_all_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["content"], "Hello")


if __name__ == '__main__':
    unittest.main()
