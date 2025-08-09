"""
Audio playback functionality
"""
import sounddevice as sd
import numpy as np
import wave
import threading
import time
from typing import Optional
from config.settings import Config


class AudioPlayer:
    def __init__(self):
        """Initialize the audio player"""
        self.sample_rate = Config.SAMPLE_RATE
        self.is_playing = False
        self.current_thread = None
        
    def play_audio_data(self, audio_data: np.ndarray, sample_rate: Optional[int] = None):
        """
        Play audio data directly
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate (defaults to config value)
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        try:
            # Ensure audio data is in the right format
            if len(audio_data.shape) == 1:
                # Mono audio
                audio_data = audio_data.reshape(-1, 1)
                
            # Normalize if needed
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32767.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483647.0
                
            self.is_playing = True
            sd.play(audio_data, samplerate=sample_rate)
            sd.wait()  # Wait for playback to complete
            self.is_playing = False
            
        except Exception as e:
            print(f"Error playing audio data: {e}")
            self.is_playing = False
            
    def play_audio_file(self, filename: str):
        """
        Play audio from a WAV file
        
        Args:
            filename: Path to audio file
        """
        try:
            with wave.open(filename, 'rb') as wav_file:
                # Get audio parameters
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                frames = wav_file.getnframes()
                
                # Read audio data
                audio_data = wav_file.readframes(frames)
                
                # Convert to numpy array
                if wav_file.getsampwidth() == 1:
                    # 8-bit audio
                    audio_array = np.frombuffer(audio_data, dtype=np.uint8)
                    audio_array = (audio_array - 128) / 128.0
                elif wav_file.getsampwidth() == 2:
                    # 16-bit audio
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    audio_array = audio_array.astype(np.float32) / 32767.0
                elif wav_file.getsampwidth() == 4:
                    # 32-bit audio
                    audio_array = np.frombuffer(audio_data, dtype=np.int32)
                    audio_array = audio_array.astype(np.float32) / 2147483647.0
                else:
                    raise ValueError(f"Unsupported sample width: {wav_file.getsampwidth()}")
                
                # Reshape for multi-channel audio
                if channels > 1:
                    audio_array = audio_array.reshape(-1, channels)
                    
                self.play_audio_data(audio_array, sample_rate)
                
        except Exception as e:
            print(f"Error playing audio file {filename}: {e}")
            
    def play_audio_async(self, audio_data: np.ndarray, sample_rate: Optional[int] = None):
        """
        Play audio data asynchronously (non-blocking)
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate (defaults to config value)
        """
        if self.is_playing:
            self.stop_playback()
            
        self.current_thread = threading.Thread(
            target=self.play_audio_data,
            args=(audio_data, sample_rate)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
        
    def play_file_async(self, filename: str):
        """
        Play audio file asynchronously (non-blocking)
        
        Args:
            filename: Path to audio file
        """
        if self.is_playing:
            self.stop_playback()
            
        self.current_thread = threading.Thread(
            target=self.play_audio_file,
            args=(filename,)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
        
    def stop_playback(self):
        """Stop current audio playback"""
        try:
            sd.stop()
            self.is_playing = False
            
            if self.current_thread and self.current_thread.is_alive():
                self.current_thread.join(timeout=1.0)
                
        except Exception as e:
            print(f"Error stopping playback: {e}")
            
    def wait_for_playback(self, timeout: Optional[float] = None):
        """
        Wait for current playback to complete
        
        Args:
            timeout: Maximum wait time in seconds
        """
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=timeout)
            
    def get_playback_devices(self) -> list:
        """Get list of available audio output devices"""
        try:
            devices = sd.query_devices()
            output_devices = []
            
            for i, device in enumerate(devices):
                if device['max_output_channels'] > 0:
                    output_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_output_channels'],
                        'sample_rate': device['default_samplerate']
                    })
                    
            return output_devices
            
        except Exception as e:
            print(f"Error getting playback devices: {e}")
            return []
            
    def set_output_device(self, device_id: int):
        """
        Set the audio output device
        
        Args:
            device_id: Device ID to use for output
        """
        try:
            sd.default.device[1] = device_id  # Set output device
            print(f"Audio output device set to ID: {device_id}")
            
        except Exception as e:
            print(f"Error setting output device: {e}")
            
    def test_playback(self, duration: float = 1.0, frequency: float = 440.0):
        """
        Test audio playback with a sine wave
        
        Args:
            duration: Test tone duration in seconds
            frequency: Test tone frequency in Hz
        """
        try:
            print(f"Playing test tone: {frequency}Hz for {duration}s")
            
            # Generate sine wave
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            sine_wave = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            # Play the test tone
            self.play_audio_data(sine_wave.reshape(-1, 1))
            print("✓ Audio playback test completed")
            
            return True
            
        except Exception as e:
            print(f"✗ Audio playback test failed: {e}")
            return False
            
    def get_volume_level(self) -> float:
        """Get current system volume level (if available)"""
        # This is a placeholder - actual volume control depends on the platform
        # and may require additional libraries like pycaw (Windows) or osascript (macOS)
        return 1.0
        
    def set_volume_level(self, volume: float):
        """
        Set system volume level (if available)
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        # This is a placeholder - actual volume control depends on the platform
        print(f"Volume set to {volume:.1%} (placeholder - platform-specific implementation needed)")
        
    def play_notification_sound(self):
        """Play a simple notification sound"""
        try:
            # Generate a simple notification beep
            duration = 0.2
            frequencies = [800, 1000]  # Two-tone beep
            
            for freq in frequencies:
                t = np.linspace(0, duration, int(self.sample_rate * duration))
                beep = 0.3 * np.sin(2 * np.pi * freq * t)
                
                # Apply fade in/out to avoid clicks
                fade_samples = int(0.01 * self.sample_rate)  # 10ms fade
                beep[:fade_samples] *= np.linspace(0, 1, fade_samples)
                beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)
                
                self.play_audio_data(beep.reshape(-1, 1))
                time.sleep(0.1)  # Brief pause between tones
                
        except Exception as e:
            print(f"Error playing notification sound: {e}")
