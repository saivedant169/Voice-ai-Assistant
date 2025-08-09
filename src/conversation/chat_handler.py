"""
Chat handler for managing conversations with AI
"""
import openai
from typing import List, Dict, Optional
from config.settings import Config
from .memory import ConversationMemory


class ChatHandler:
    def __init__(self, model: str = Config.GPT_MODEL):
        """
        Initialize the chat handler
        
        Args:
            model: OpenAI model to use for conversations
        """
        self.model = model
        self.memory = ConversationMemory()
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # System message to define assistant personality
        self.system_message = {
            "role": "system",
            "content": f"""You are {Config.ASSISTANT_NAME}, a helpful voice-activated AI assistant. 
            You should respond naturally and conversationally, as if speaking to the user.
            Keep responses concise but informative. You can help with questions, tasks, 
            reminders, general knowledge, and casual conversation. Always be polite and helpful."""
        }
        
    def get_response(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        Get AI response to user input
        
        Args:
            user_input: User's spoken input
            context: Optional context information
            
        Returns:
            AI response text
        """
        try:
            # Add user message to memory
            self.memory.add_message("user", user_input)
            
            # Prepare messages for API call
            messages = [self.system_message]
            
            # Add conversation history
            messages.extend(self.memory.get_recent_messages())
            
            # Add context if provided
            if context:
                context_msg = self._format_context(context)
                if context_msg:
                    messages.append(context_msg)
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,  # Keep responses concise for voice
                temperature=0.7,
                timeout=Config.RESPONSE_TIMEOUT
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Add assistant response to memory
            self.memory.add_message("assistant", assistant_response)
            
            return assistant_response
            
        except openai.RateLimitError:
            return "I'm sorry, I'm currently experiencing high demand. Please try again in a moment."
        except openai.APITimeoutError:
            return "I'm taking too long to respond. Let me try that again."
        except openai.APIError as e:
            print(f"OpenAI API error: {e}")
            return "I'm experiencing some technical difficulties right now."
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "I'm sorry, I couldn't process that request."
            
    def _format_context(self, context: Dict) -> Optional[Dict]:
        """
        Format context information into a message
        
        Args:
            context: Context dictionary
            
        Returns:
            Formatted context message or None
        """
        if not context:
            return None
            
        context_parts = []
        
        if "time" in context:
            context_parts.append(f"Current time: {context['time']}")
        if "location" in context:
            context_parts.append(f"User location: {context['location']}")
        if "weather" in context:
            context_parts.append(f"Current weather: {context['weather']}")
        if "user_info" in context:
            context_parts.append(f"User info: {context['user_info']}")
            
        if context_parts:
            return {
                "role": "system",
                "content": "Context: " + " | ".join(context_parts)
            }
            
        return None
        
    def handle_command(self, user_input: str) -> tuple[str, bool]:
        """
        Handle special commands
        
        Args:
            user_input: User input to check for commands
            
        Returns:
            Tuple of (response, is_command)
        """
        user_input_lower = user_input.lower().strip()
        
        # Clear conversation command
        if any(phrase in user_input_lower for phrase in ["clear conversation", "forget everything", "start over"]):
            self.memory.clear()
            return "I've cleared our conversation history. How can I help you?", True
            
        # Stop/exit commands
        if any(phrase in user_input_lower for phrase in ["stop listening", "goodbye", "exit", "quit"]):
            return "Goodbye! Have a great day!", True
            
        # Status commands
        if any(phrase in user_input_lower for phrase in ["how are you", "how's it going"]):
            return "I'm doing well, thank you for asking! How can I assist you today?", True
            
        # Help command
        if "help" in user_input_lower or "what can you do" in user_input_lower:
            help_text = """I can help you with:
            - Answering questions and providing information
            - Having conversations and casual chat
            - Helping with tasks and reminders
            - General knowledge and explanations
            
            Just speak naturally and I'll do my best to help!"""
            return help_text, True
            
        return "", False
        
    def set_personality(self, personality: str):
        """
        Update the assistant's personality
        
        Args:
            personality: New personality description
        """
        self.system_message["content"] = f"""You are {Config.ASSISTANT_NAME}, {personality}
        You should respond naturally and conversationally, as if speaking to the user.
        Keep responses concise but informative."""
        
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation"""
        messages = self.memory.get_all_messages()
        if not messages:
            return "No conversation history yet."
            
        return f"Conversation contains {len(messages)} messages. Started: {self.memory.get_start_time()}"
        
    def export_conversation(self) -> List[Dict]:
        """Export the current conversation"""
        return self.memory.get_all_messages()
        
    def import_conversation(self, messages: List[Dict]):
        """Import a conversation history"""
        self.memory.clear()
        for msg in messages:
            if "role" in msg and "content" in msg:
                self.memory.add_message(msg["role"], msg["content"])
