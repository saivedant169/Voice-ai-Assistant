#!/usr/bin/env python3
"""
Streamlit web interface for the Voice Assistant
"""
import sys
import os
import streamlit as st
import time
import threading
import queue

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.assistant import VoiceAssistant
from config.settings import Config


class WebInterface:
    def __init__(self):
        self.assistant = None
        self.message_queue = queue.Queue()
        self.is_listening = False
        
    def initialize_assistant(self):
        """Initialize the assistant if not already done"""
        if self.assistant is None:
            try:
                self.assistant = VoiceAssistant()
                self._setup_callbacks()
                return True
            except Exception as e:
                st.error(f"Failed to initialize assistant: {e}")
                return False
        return True
        
    def _setup_callbacks(self):
        """Set up assistant callbacks"""
        def on_wake_word():
            self.message_queue.put(("wake_word", "Wake word detected!"))
            
        def on_speech(text):
            self.message_queue.put(("user", text))
            
        def on_response(text):
            self.message_queue.put(("assistant", text))
            
        def on_error(error):
            self.message_queue.put(("error", str(error)))
            
        self.assistant.set_callbacks(
            on_wake_word_detected=on_wake_word,
            on_speech_recognized=on_speech,
            on_response_generated=on_response,
            on_error=on_error
        )


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Voice AI Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize session state
    if 'web_interface' not in st.session_state:
        st.session_state.web_interface = WebInterface()
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'assistant_active' not in st.session_state:
        st.session_state.assistant_active = False
        
    web_interface = st.session_state.web_interface
    
    # Header
    st.title("🤖 Voice-Activated AI Assistant")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Initialize button
        if st.button("🔧 Initialize Assistant"):
            with st.spinner("Initializing assistant..."):
                if web_interface.initialize_assistant():
                    st.success("✅ Assistant initialized!")
                else:
                    st.error("❌ Initialization failed")
                    
        # Status
        if web_interface.assistant:
            status = web_interface.assistant.get_status()
            st.subheader("📊 Status")
            st.write(f"**Assistant:** {status['assistant_name']}")
            st.write(f"**Active:** {'✅' if status['is_active'] else '❌'}")
            st.write(f"**Wake Word:** {status['wake_word']}")
            
            # Conversation stats
            stats = status['conversation_stats']
            st.write(f"**Messages:** {stats['total_messages']}")
            st.write(f"**Duration:** {stats['duration_minutes']:.1f}m")
            
        st.markdown("---")
        
        # Settings
        st.subheader("🎛️ Settings")
        
        # Wake word mode toggle
        wake_word_mode = st.checkbox("Wake Word Mode", value=True)
        
        # Voice settings
        if web_interface.assistant:
            st.slider("Voice Speed", 0.5, 2.0, Config.VOICE_SPEED, 0.1)
            st.slider("Voice Volume", 0.0, 1.0, Config.VOICE_VOLUME, 0.1)
            
        # Test components button
        if st.button("🧪 Test Components"):
            if web_interface.assistant:
                with st.spinner("Testing components..."):
                    results = web_interface.assistant.test_components()
                    
                st.subheader("Test Results")
                for component, passed in results.items():
                    icon = "✅" if passed else "❌"
                    st.write(f"{icon} {component.replace('_', ' ').title()}")
                    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Conversation")
        
        # Chat container
        chat_container = st.container()
        
        # Display conversation history
        with chat_container:
            for msg in st.session_state.conversation_history:
                if msg['role'] == 'user':
                    st.chat_message("user").write(msg['content'])
                elif msg['role'] == 'assistant':
                    st.chat_message("assistant").write(msg['content'])
                elif msg['role'] == 'system':
                    st.info(msg['content'])
                elif msg['role'] == 'error':
                    st.error(msg['content'])
                    
        # Text input for testing
        st.subheader("📝 Text Mode")
        text_input = st.text_input("Type your message:", key="text_input")
        
        col_send, col_clear = st.columns([1, 1])
        
        with col_send:
            if st.button("📤 Send", key="send_button"):
                if text_input and web_interface.assistant:
                    # Add user message
                    st.session_state.conversation_history.append({
                        'role': 'user',
                        'content': text_input
                    })
                    
                    # Get response
                    try:
                        response = web_interface.assistant.process_text_input(text_input)
                        st.session_state.conversation_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
        with col_clear:
            if st.button("🗑️ Clear Chat", key="clear_button"):
                st.session_state.conversation_history = []
                if web_interface.assistant:
                    web_interface.assistant.chat.memory.clear()
                st.rerun()
                
    with col2:
        st.header("🎤 Voice Control")
        
        if not web_interface.assistant:
            st.warning("Please initialize the assistant first")
        else:
            # Voice control buttons
            start_col, stop_col = st.columns(2)
            
            with start_col:
                if st.button("🎙️ Start Listening", key="start_voice"):
                    if not st.session_state.assistant_active:
                        try:
                            st.session_state.assistant_active = True
                            
                            # Start assistant in a separate thread
                            def start_assistant():
                                web_interface.assistant.start(wake_word_mode=wake_word_mode)
                                
                            thread = threading.Thread(target=start_assistant)
                            thread.daemon = True
                            thread.start()
                            
                            st.success("🎤 Assistant started!")
                            
                        except Exception as e:
                            st.error(f"Failed to start: {e}")
                            st.session_state.assistant_active = False
                            
            with stop_col:
                if st.button("⏹️ Stop Listening", key="stop_voice"):
                    if st.session_state.assistant_active:
                        web_interface.assistant.stop()
                        st.session_state.assistant_active = False
                        st.info("🛑 Assistant stopped")
                        
            # Voice status
            if st.session_state.assistant_active:
                st.success("🟢 Listening...")
                if wake_word_mode:
                    st.info(f"Say '{Config.WAKE_WORD}' to start")
                else:
                    st.info("Continuous listening mode")
            else:
                st.info("🔴 Not listening")
                
            # Instructions
            st.markdown("---")
            st.subheader("📋 Instructions")
            st.markdown("""
            **Voice Commands:**
            - Say wake word to activate
            - "Help" - Show capabilities
            - "Clear conversation" - Reset chat
            - "Goodbye" - Stop assistant
            
            **Text Mode:**
            - Type messages for testing
            - No microphone required
            - Same AI responses
            """)
            
        # Export conversation
        st.markdown("---")
        if st.button("💾 Export Conversation"):
            if web_interface.assistant:
                try:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"conversation_{timestamp}.json"
                    web_interface.assistant.export_conversation(filename)
                    st.success(f"Exported to {filename}")
                except Exception as e:
                    st.error(f"Export failed: {e}")
                    
    # Process any queued messages from assistant callbacks
    try:
        while not web_interface.message_queue.empty():
            msg_type, content = web_interface.message_queue.get_nowait()
            
            if msg_type == "user":
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': content
                })
            elif msg_type == "assistant":
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': content
                })
            elif msg_type == "wake_word":
                st.session_state.conversation_history.append({
                    'role': 'system',
                    'content': content
                })
            elif msg_type == "error":
                st.session_state.conversation_history.append({
                    'role': 'error',
                    'content': content
                })
                
        # Auto-refresh if there are new messages
        if len(st.session_state.conversation_history) > 0:
            time.sleep(0.1)
            st.rerun()
            
    except queue.Empty:
        pass


if __name__ == "__main__":
    main()
