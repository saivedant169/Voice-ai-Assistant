"""
Speech-to-Text using OpenAI Whisper
"""
import whisper
import numpy as np
import sounddevice as sd
import queue
import threading
import time
from typing import Optional, Callable
from config.settings import Config


class SpeechToText:
    def __init__(self, model_name: str = Config.WHISPER_MODEL):
        """Initialize the speech-to-text processor"""
        self.model = whisper.load_model(model_name)
        self.sample_rate = Config.SAMPLE_RATE
        self.chunk_size = Config.CHUNK_SIZE
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        
    def start_listening(self, on_speech_detected: Optional[Callable] = None):
        """Start continuous listening for speech"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.on_speech_detected = on_speech_detected
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_listening(self):
        """Stop listening for speech"""
        self.is_listening = False
        if self.recording_thread:
            self.recording_thread.join()
            
    def _recording_loop(self):
        """Continuous recording loop"""
        with sd.InputStream(
            channels=Config.CHANNELS,
            samplerate=self.sample_rate,
            dtype=np.float32,
            blocksize=self.chunk_size,
            callback=self._audio_callback
        ):
            while self.is_listening:
                time.sleep(0.1)
                
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input"""
        if status:
            print(f"Audio input status: {status}")
        self.audio_queue.put(indata.copy())
        
    def listen_once(self, duration: float = 5.0) -> str:
        """
        Record audio for a specified duration and transcribe
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text
        """
        print(f"Listening for {duration} seconds...")
        
        # Record audio
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=Config.CHANNELS,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        
        # Transcribe
        return self.transcribe_audio(audio_data.flatten())
        
    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio data using Whisper
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Transcribed text
        """
        try:
            # Ensure audio is in the right format for Whisper
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
                
            # Whisper expects audio at 16kHz
            if self.sample_rate != 16000:
                # Simple resampling (for production, use proper resampling)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), int(len(audio_data) * 16000 / self.sample_rate)),
                    np.arange(len(audio_data)),
                    audio_data
                )
            
            # Transcribe with Whisper
            result = self.model.transcribe(audio_data)
            text = result["text"].strip()
            
            print(f"Transcribed: {text}")
            return text
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
            
    def detect_wake_word(self, text: str) -> bool:
        """
        Check if the wake word is present in the text
        
        Args:
            text: Transcribed text to check
            
        Returns:
            True if wake word detected
        """
        wake_word = Config.WAKE_WORD.lower()
        return wake_word in text.lower()
        
    def process_continuous_audio(self) -> Optional[str]:
        """
        Process audio from the continuous recording queue
        
        Returns:
            Transcribed text if speech detected, None otherwise
        """
        if self.audio_queue.empty():
            return None
            
        # Collect audio chunks
        audio_chunks = []
        while not self.audio_queue.empty():
            chunk = self.audio_queue.get()
            audio_chunks.append(chunk)
            
        if not audio_chunks:
            return None
            
        # Combine chunks
        audio_data = np.concatenate(audio_chunks, axis=0).flatten()
        
        # Simple voice activity detection (energy-based)
        energy = np.mean(audio_data ** 2)
        if energy < 0.001:  # Threshold for silence
            return None
            
        return self.transcribe_audio(audio_data)
