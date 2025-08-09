"""
Conversation memory management
"""
from typing import List, Dict, Optional
from datetime import datetime
from config.settings import Config


class ConversationMemory:
    def __init__(self, max_messages: int = Config.MAX_CONVERSATION_HISTORY):
        """
        Initialize conversation memory
        
        Args:
            max_messages: Maximum number of messages to keep in memory
        """
        self.max_messages = max_messages
        self.messages: List[Dict] = []
        self.start_time = datetime.now()
        self.context_data = {}
        
    def add_message(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Add a message to the conversation memory
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat()
        }
        
        self.messages.append(message)
        
        # Trim messages if we exceed the limit
        if len(self.messages) > self.max_messages * 2:  # Keep user + assistant pairs
            # Remove oldest messages but keep them in pairs
            messages_to_remove = len(self.messages) - self.max_messages * 2
            self.messages = self.messages[messages_to_remove:]
            
    def get_recent_messages(self, count: Optional[int] = None) -> List[Dict]:
        """
        Get recent messages for API calls
        
        Args:
            count: Number of recent messages to get
            
        Returns:
            List of recent messages formatted for OpenAI API
        """
        if count is None:
            count = self.max_messages * 2
            
        recent_messages = self.messages[-count:] if count < len(self.messages) else self.messages
        
        # Format for OpenAI API (remove timestamp)
        return [{"role": msg["role"], "content": msg["content"]} for msg in recent_messages]
        
    def get_all_messages(self) -> List[Dict]:
        """Get all messages with timestamps"""
        return self.messages.copy()
        
    def clear(self):
        """Clear all conversation memory"""
        self.messages.clear()
        self.start_time = datetime.now()
        self.context_data.clear()
        
    def get_start_time(self) -> str:
        """Get conversation start time"""
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        
    def add_context(self, key: str, value: any):
        """
        Add context data that persists across messages
        
        Args:
            key: Context key
            value: Context value
        """
        self.context_data[key] = value
        
    def get_context(self, key: str, default=None):
        """
        Get context data
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        return self.context_data.get(key, default)
        
    def remove_context(self, key: str):
        """Remove context data"""
        self.context_data.pop(key, None)
        
    def get_conversation_stats(self) -> Dict:
        """Get conversation statistics"""
        user_messages = sum(1 for msg in self.messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.messages if msg["role"] == "assistant")
        
        return {
            "total_messages": len(self.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "start_time": self.get_start_time(),
            "duration_minutes": (datetime.now() - self.start_time).total_seconds() / 60
        }
        
    def search_messages(self, query: str, role: Optional[str] = None) -> List[Dict]:
        """
        Search for messages containing specific text
        
        Args:
            query: Text to search for
            role: Optional role filter ('user' or 'assistant')
            
        Returns:
            List of matching messages
        """
        query_lower = query.lower()
        matches = []
        
        for msg in self.messages:
            if role and msg["role"] != role:
                continue
                
            if query_lower in msg["content"].lower():
                matches.append(msg)
                
        return matches
        
    def get_last_user_message(self) -> Optional[str]:
        """Get the last message from the user"""
        for msg in reversed(self.messages):
            if msg["role"] == "user":
                return msg["content"]
        return None
        
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the last message from the assistant"""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
        
    def export_to_file(self, filename: str):
        """
        Export conversation to a file
        
        Args:
            filename: File path to save conversation
        """
        import json
        
        export_data = {
            "start_time": self.get_start_time(),
            "stats": self.get_conversation_stats(),
            "context": self.context_data,
            "messages": self.messages
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
            
    def import_from_file(self, filename: str):
        """
        Import conversation from a file
        
        Args:
            filename: File path to load conversation from
        """
        import json
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            self.clear()
            
            if "messages" in data:
                self.messages = data["messages"]
                
            if "context" in data:
                self.context_data = data["context"]
                
            if "start_time" in data:
                self.start_time = datetime.fromisoformat(data["start_time"])
                
        except Exception as e:
            print(f"Error importing conversation: {e}")
            
    def summarize_conversation(self) -> str:
        """Generate a summary of the conversation"""
        if not self.messages:
            return "No conversation to summarize."
            
        stats = self.get_conversation_stats()
        
        # Simple summary - in a real implementation, you might use AI to generate this
        recent_topics = []
        for msg in self.messages[-10:]:  # Look at last 10 messages
            if msg["role"] == "user" and len(msg["content"]) > 20:
                recent_topics.append(msg["content"][:50] + "...")
                
        summary = f"""Conversation Summary:
        - Duration: {stats['duration_minutes']:.1f} minutes
        - Messages: {stats['total_messages']} total ({stats['user_messages']} user, {stats['assistant_messages']} assistant)
        - Started: {stats['start_time']}
        """
        
        if recent_topics:
            summary += f"\nRecent topics: {', '.join(recent_topics[:3])}"
            
        return summary
