#!/usr/bin/env python3
"""
Command-line interface for the Voice Assistant
"""
import sys
import os
import argparse
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.assistant import VoiceAssistant
from config.settings import Config


class CLI:
    def __init__(self):
        self.assistant = None
        
    def run_interactive(self, wake_word_mode=True, continuous=False):
        """Run the assistant in interactive mode"""
        try:
            print("🤖 Voice Assistant CLI")
            print("=" * 50)
            
            # Initialize assistant
            self.assistant = VoiceAssistant()
            
            # Test critical components
            if not self._check_requirements():
                return
                
            # Set up callbacks
            self._setup_callbacks()
            
            if continuous:
                print("🎙️ Continuous listening mode")
                print("The assistant will listen continuously without wake words")
                print("Press Ctrl+C to stop")
                self.assistant.start(wake_word_mode=False)
            else:
                print(f"🎯 Wake word mode: '{Config.WAKE_WORD}'")
                print("Say the wake word to start a conversation")
                print("Press Ctrl+C to stop")
                self.assistant.start(wake_word_mode=True)
                
        except KeyboardInterrupt:
            print("\\n\\n👋 Assistant stopped by user")
        except Exception as e:
            print(f"\\n❌ Error: {e}")
        finally:
            if self.assistant:
                self.assistant.stop()
                
    def run_text_mode(self):
        """Run the assistant in text-only mode"""
        try:
            print("📝 Text-Only Mode")
            print("=" * 30)
            
            self.assistant = VoiceAssistant()
            
            print(f"💬 Chat with {Config.ASSISTANT_NAME}")
            print("Commands: 'help', 'status', 'export', 'clear', 'quit'\\n")
            
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        continue
                        
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    elif user_input.lower() == 'status':
                        self._show_status()
                        continue
                    elif user_input.lower() == 'export':
                        self._export_conversation()
                        continue
                    elif user_input.lower() == 'clear':
                        self.assistant.chat.memory.clear()
                        print("🗑️ Conversation cleared\\n")
                        continue
                        
                    # Process normal input
                    response = self.assistant.process_text_input(user_input)
                    print(f"🤖 {response}\\n")
                    
                except KeyboardInterrupt:
                    break
                    
            print("👋 Goodbye!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
    def test_components(self):
        """Test all assistant components"""
        print("🧪 Component Testing")
        print("=" * 30)
        
        try:
            self.assistant = VoiceAssistant()
            results = self.assistant.test_components()
            
            print("\\n📊 Summary:")
            passed = sum(results.values())
            total = len(results)
            print(f"✅ {passed}/{total} components working")
            
            if passed == total:
                print("🎉 All systems operational!")
            else:
                print("⚠️ Some components need attention")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            
    def _check_requirements(self):
        """Check if basic requirements are met"""
        try:
            # Test conversation capability (most critical)
            response = self.assistant.chat.get_response("test")
            if not response:
                print("❌ OpenAI API not working. Check your API key.")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Requirements check failed: {e}")
            print("\\nPlease ensure:")
            print("1. OpenAI API key is set in .env file")
            print("2. All dependencies are installed")
            return False
            
    def _setup_callbacks(self):
        """Set up event callbacks for better user experience"""
        def on_wake_word():
            print("\\n🎯 Wake word detected! Listening...")
            
        def on_speech(text):
            print(f"\\n👤 You said: {text}")
            
        def on_response(text):
            print(f"🤖 {Config.ASSISTANT_NAME}: {text}\\n")
            print("Waiting for wake word...")
            
        def on_error(error):
            print(f"\\n❌ Error: {error}")
            
        self.assistant.set_callbacks(
            on_wake_word_detected=on_wake_word,
            on_speech_recognized=on_speech,
            on_response_generated=on_response,
            on_error=on_error
        )
        
    def _show_status(self):
        """Show assistant status"""
        status = self.assistant.get_status()
        stats = status['conversation_stats']
        
        print("\\n📊 Assistant Status:")
        print(f"  Active: {status['is_active']}")
        print(f"  Assistant: {status['assistant_name']}")
        print(f"  Wake word: '{status['wake_word']}'")
        print(f"  Conversation messages: {stats['total_messages']}")
        print(f"  Session duration: {stats['duration_minutes']:.1f} minutes\\n")
        
    def _export_conversation(self):
        """Export conversation to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        try:
            self.assistant.export_conversation(filename)
            print(f"💾 Conversation exported to {filename}\\n")
        except Exception as e:
            print(f"❌ Export failed: {e}\\n")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Voice-Activated AI Assistant CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_assistant.py                    # Normal wake word mode
  python cli_assistant.py --continuous       # Continuous listening
  python cli_assistant.py --text             # Text-only mode
  python cli_assistant.py --test             # Test components
        """
    )
    
    parser.add_argument('--text', action='store_true',
                       help='Run in text-only mode (no voice)')
    parser.add_argument('--continuous', action='store_true',
                       help='Continuous listening (no wake word)')
    parser.add_argument('--test', action='store_true',
                       help='Test all components')
    
    args = parser.parse_args()
    
    cli = CLI()
    
    if args.test:
        cli.test_components()
    elif args.text:
        cli.run_text_mode()
    else:
        cli.run_interactive(continuous=args.continuous)


if __name__ == "__main__":
    main()
