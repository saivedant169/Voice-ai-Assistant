"""
Audio recording functionality
"""
import sounddevice as sd
import numpy as np
import wave
import threading
import queue
import time
from typing import Optional, Callable
from config.settings import Config


class AudioRecorder:
    def __init__(self):
        """Initialize the audio recorder"""
        self.sample_rate = Config.SAMPLE_RATE
        self.channels = Config.CHANNELS
        self.chunk_size = Config.CHUNK_SIZE
        
        self.is_recording = False
        self.audio_data = []
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        
        # Callbacks
        self.on_audio_data = None
        self.on_silence_detected = None
        self.on_speech_detected = None
        
        # Voice activity detection parameters
        self.silence_threshold = 0.01
        self.silence_duration = 2.0  # seconds of silence to stop recording
        self.min_recording_duration = 1.0  # minimum recording duration
        
    def start_recording(self, callback: Optional[Callable] = None):
        """
        Start recording audio
        
        Args:
            callback: Optional callback function for audio data
        """
        if self.is_recording:
            return False
            
        self.is_recording = True
        self.audio_data = []
        self.on_audio_data = callback
        
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        return True
        
    def stop_recording(self) -> np.ndarray:
        """
        Stop recording and return audio data
        
        Returns:
            Recorded audio as numpy array
        """
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)
            
        if self.audio_data:
            return np.concatenate(self.audio_data, axis=0)
        return np.array([])
        
    def _recording_loop(self):
        """Main recording loop"""
        try:
            with sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            ):
                while self.is_recording:
                    time.sleep(0.01)
                    
        except Exception as e:
            print(f"Recording error: {e}")
            self.is_recording = False
            
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream"""
        if status:
            print(f"Audio callback status: {status}")
            
        if self.is_recording:
            # Store audio data
            audio_chunk = indata.copy()
            self.audio_data.append(audio_chunk)
            
            # Call user callback if provided
            if self.on_audio_data:
                self.on_audio_data(audio_chunk)
                
            # Add to queue for voice activity detection
            self.audio_queue.put(audio_chunk)
            
    def record_with_vad(self, max_duration: float = 30.0) -> np.ndarray:
        """
        Record audio with voice activity detection
        
        Args:
            max_duration: Maximum recording duration in seconds
            
        Returns:
            Recorded audio data
        """
        print("Starting recording with voice activity detection...")
        
        self.start_recording()
        
        start_time = time.time()
        last_speech_time = start_time
        speech_detected = False
        
        try:
            while self.is_recording and (time.time() - start_time) < max_duration:
                # Check for voice activity
                if not self.audio_queue.empty():
                    chunk = self.audio_queue.get()
                    
                    # Simple energy-based voice activity detection
                    energy = np.mean(chunk.flatten() ** 2)
                    
                    if energy > self.silence_threshold:
                        # Speech detected
                        last_speech_time = time.time()
                        if not speech_detected:
                            speech_detected = True
                            print("Speech detected, recording...")
                            if self.on_speech_detected:
                                self.on_speech_detected()
                    else:
                        # Silence detected
                        if speech_detected and (time.time() - last_speech_time) > self.silence_duration:
                            # Enough silence after speech, stop recording
                            if (time.time() - start_time) > self.min_recording_duration:
                                print("Silence detected, stopping recording...")
                                if self.on_silence_detected:
                                    self.on_silence_detected()
                                break
                                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("Recording interrupted by user")
            
        return self.stop_recording()
        
    def record_fixed_duration(self, duration: float) -> np.ndarray:
        """
        Record audio for a fixed duration
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Recorded audio data
        """
        print(f"Recording for {duration} seconds...")
        
        # Use sounddevice's simple recording function
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        
        return audio_data.flatten()
        
    def save_audio(self, audio_data: np.ndarray, filename: str):
        """
        Save audio data to a WAV file
        
        Args:
            audio_data: Audio data to save
            filename: Output filename
        """
        try:
            # Ensure audio data is in the right format
            if audio_data.dtype != np.int16:
                # Convert float32 to int16
                audio_data = (audio_data * 32767).astype(np.int16)
                
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data.tobytes())
                
            print(f"Audio saved to {filename}")
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            
    def get_audio_info(self) -> dict:
        """Get information about audio settings"""
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            
            return {
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "chunk_size": self.chunk_size,
                "default_input_device": default_input['name'] if default_input else "Unknown",
                "available_devices": len(devices)
            }
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return {}
            
    def test_audio_input(self, duration: float = 3.0) -> bool:
        """
        Test audio input by recording for a short duration
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if audio input is working
        """
        try:
            print(f"Testing audio input for {duration} seconds...")
            audio_data = self.record_fixed_duration(duration)
            
            # Check if we got audio data
            if len(audio_data) > 0:
                energy = np.mean(audio_data ** 2)
                print(f"Audio test completed. Energy level: {energy:.6f}")
                
                if energy > 0.0001:  # Very low threshold
                    print("✓ Audio input is working")
                    return True
                else:
                    print("⚠ Audio input detected but very quiet")
                    return True
            else:
                print("✗ No audio data received")
                return False
                
        except Exception as e:
            print(f"✗ Audio test failed: {e}")
            return False
            
    def set_vad_parameters(self, silence_threshold: float = None, 
                          silence_duration: float = None,
                          min_recording_duration: float = None):
        """
        Update voice activity detection parameters
        
        Args:
            silence_threshold: Energy threshold for silence detection
            silence_duration: Duration of silence to stop recording
            min_recording_duration: Minimum recording duration
        """
        if silence_threshold is not None:
            self.silence_threshold = silence_threshold
        if silence_duration is not None:
            self.silence_duration = silence_duration
        if min_recording_duration is not None:
            self.min_recording_duration = min_recording_duration
