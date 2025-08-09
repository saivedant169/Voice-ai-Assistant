#!/usr/bin/env python3
"""
Basic command-line usage example for the Voice Assistant
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.assistant import VoiceAssistant
from config.settings import Config


def main():
    """Main function to run the voice assistant"""
    print("🤖 Voice-Activated AI Assistant")
    print("=" * 40)
    
    try:
        # Create assistant instance
        assistant = VoiceAssistant()
        
        # Test components
        print("\\nTesting components...")
        test_results = assistant.test_components()
        
        # Check if critical components are working
        if not test_results.get('conversation', False):
            print("❌ Critical error: Conversation handler not working")
            print("Please check your OpenAI API key in .env file")
            return
            
        # Set up callbacks for better interaction
        def on_wake_word():
            print("🎯 Wake word detected!")
            
        def on_speech(text):
            print(f"👤 User: {text}")
            
        def on_response(text):
            print(f"🤖 {Config.ASSISTANT_NAME}: {text}")
            
        def on_error(error):
            print(f"❌ Error: {error}")
            
        assistant.set_callbacks(
            on_wake_word_detected=on_wake_word,
            on_speech_recognized=on_speech,
            on_response_generated=on_response,
            on_error=on_error
        )
        
        # Show usage instructions
        print(f"\\n🎤 Starting {Config.ASSISTANT_NAME}...")
        print(f"Wake word: '{Config.WAKE_WORD}'")
        print("\\nInstructions:")
        print(f"1. Say '{Config.WAKE_WORD}' to activate")
        print("2. Speak your request when prompted")
        print("3. Say 'goodbye' or press Ctrl+C to exit")
        print("\\nAlternative commands:")
        print("- 'help' - Show what I can do")
        print("- 'clear conversation' - Reset conversation history")
        print("- 'stop listening' - Exit the assistant")
        
        # Start the assistant in wake word mode
        assistant.start(wake_word_mode=True)
        
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
    except Exception as e:
        print(f"\\n❌ Error starting assistant: {e}")
        print("\\nTroubleshooting:")
        print("1. Make sure your microphone is connected and working")
        print("2. Check that your .env file has the correct API keys")
        print("3. Ensure all dependencies are installed: pip install -r requirements.txt")
    finally:
        if 'assistant' in locals():
            assistant.stop()


def text_mode():
    """Run the assistant in text-only mode for testing"""
    print("📝 Text Mode - Voice Assistant")
    print("=" * 40)
    
    try:
        assistant = VoiceAssistant()
        
        print(f"\\n💬 Chatting with {Config.ASSISTANT_NAME} (text mode)")
        print("Type 'quit' to exit\\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'goodbye']:
                break
                
            if user_input:
                response = assistant.process_text_input(user_input)
                print(f"{Config.ASSISTANT_NAME}: {response}\\n")
                
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
    except Exception as e:
        print(f"\\n❌ Error: {e}")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--text":
        text_mode()
    else:
        main()
