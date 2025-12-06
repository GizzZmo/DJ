#!/usr/bin/env python3
"""
Recording and Export Functionality for DJ Mixer
Handles recording mixer output and exporting to various formats
"""

import wave
import numpy as np
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import threading
import time


@dataclass
class RecordingSettings:
    """Settings for audio recording"""
    sample_rate: int = 44100
    channels: int = 2  # Stereo
    sample_width: int = 2  # 16-bit
    format: str = "wav"  # wav, mp3, ogg


class AudioRecorder:
    """Records audio from the mixer output"""
    
    def __init__(self, settings: Optional[RecordingSettings] = None):
        self.settings = settings or RecordingSettings()
        self.is_recording = False
        self.recorded_data: List[np.ndarray] = []
        self.start_time: Optional[float] = None
        self.duration: float = 0.0
        self.output_file: Optional[str] = None
    
    def start_recording(self, output_file: Optional[str] = None) -> bool:
        """Start recording audio"""
        if self.is_recording:
            print("Already recording")
            return False
        
        # Generate filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"dj_mix_{timestamp}.{self.settings.format}"
        
        self.output_file = output_file
        self.recorded_data = []
        self.start_time = time.time()
        self.is_recording = True
        
        print(f"Recording started: {self.output_file}")
        return True
    
    def stop_recording(self) -> bool:
        """Stop recording and save to file"""
        if not self.is_recording:
            print("Not recording")
            return False
        
        self.is_recording = False
        self.duration = time.time() - self.start_time if self.start_time else 0.0
        
        # Save recorded data
        if self.recorded_data and self.output_file:
            success = self.save_recording(self.output_file)
            if success:
                print(f"Recording saved: {self.output_file} ({self.duration:.1f}s)")
                return True
        
        return False
    
    def pause_recording(self) -> bool:
        """Pause recording (keeps data but stops capturing)"""
        if self.is_recording:
            self.is_recording = False
            return True
        return False
    
    def resume_recording(self) -> bool:
        """Resume recording after pause"""
        if not self.is_recording and self.start_time is not None:
            self.is_recording = True
            return True
        return False
    
    def capture_audio(self, audio_data: np.ndarray) -> None:
        """Capture audio data during recording"""
        if self.is_recording and len(audio_data) > 0:
            self.recorded_data.append(audio_data.copy())
    
    def save_recording(self, output_file: str) -> bool:
        """Save recorded audio to file"""
        if not self.recorded_data:
            print("No audio data to save")
            return False
        
        try:
            # Concatenate all recorded chunks
            full_audio = np.concatenate(self.recorded_data)
            
            # Determine format from extension
            file_path = Path(output_file)
            format_type = file_path.suffix.lower().lstrip('.')
            
            if format_type == 'wav':
                return self._save_wav(output_file, full_audio)
            elif format_type == 'mp3':
                return self._save_mp3(output_file, full_audio)
            elif format_type == 'ogg':
                return self._save_ogg(output_file, full_audio)
            else:
                print(f"Unsupported format: {format_type}")
                return False
                
        except Exception as e:
            print(f"Error saving recording: {e}")
            return False
    
    def _save_wav(self, output_file: str, audio_data: np.ndarray) -> bool:
        """Save audio as WAV file"""
        try:
            with wave.open(output_file, 'wb') as wav_file:
                wav_file.setnchannels(self.settings.channels)
                wav_file.setsampwidth(self.settings.sample_width)
                wav_file.setframerate(self.settings.sample_rate)
                
                # Convert to bytes
                audio_bytes = audio_data.tobytes()
                wav_file.writeframes(audio_bytes)
            
            return True
        except Exception as e:
            print(f"Error saving WAV: {e}")
            return False
    
    def _save_mp3(self, output_file: str, audio_data: np.ndarray) -> bool:
        """Save audio as MP3 file using pydub"""
        try:
            from pydub import AudioSegment
            
            # First save as WAV
            temp_wav = output_file.replace('.mp3', '_temp.wav')
            if not self._save_wav(temp_wav, audio_data):
                return False
            
            # Convert WAV to MP3
            audio = AudioSegment.from_wav(temp_wav)
            audio.export(output_file, format='mp3', bitrate='320k')
            
            # Remove temp file
            Path(temp_wav).unlink()
            
            return True
        except ImportError:
            print("MP3 export requires pydub and ffmpeg")
            print("Install with: pip install pydub")
            return False
        except Exception as e:
            print(f"Error saving MP3: {e}")
            return False
    
    def _save_ogg(self, output_file: str, audio_data: np.ndarray) -> bool:
        """Save audio as OGG file using pydub"""
        try:
            from pydub import AudioSegment
            
            # First save as WAV
            temp_wav = output_file.replace('.ogg', '_temp.wav')
            if not self._save_wav(temp_wav, audio_data):
                return False
            
            # Convert WAV to OGG
            audio = AudioSegment.from_wav(temp_wav)
            audio.export(output_file, format='ogg')
            
            # Remove temp file
            Path(temp_wav).unlink()
            
            return True
        except ImportError:
            print("OGG export requires pydub and ffmpeg")
            return False
        except Exception as e:
            print(f"Error saving OGG: {e}")
            return False
    
    def get_recording_duration(self) -> float:
        """Get current recording duration in seconds"""
        if self.is_recording and self.start_time:
            return time.time() - self.start_time
        return self.duration
    
    def get_recording_info(self) -> dict:
        """Get information about current/last recording"""
        return {
            "is_recording": self.is_recording,
            "duration": self.get_recording_duration(),
            "output_file": self.output_file,
            "sample_rate": self.settings.sample_rate,
            "channels": self.settings.channels,
            "format": self.settings.format,
            "data_size": sum(len(d) for d in self.recorded_data)
        }
    
    def clear_recording(self) -> None:
        """Clear recorded data"""
        self.recorded_data = []
        self.start_time = None
        self.duration = 0.0
        self.output_file = None


class ExportManager:
    """Manages exporting audio in various formats"""
    
    @staticmethod
    def export_audio(input_file: str, output_file: str, format: Optional[str] = None,
                    bitrate: str = '320k', sample_rate: Optional[int] = None) -> bool:
        """
        Export audio file to different format
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output audio file
            format: Output format (wav, mp3, ogg, flac) - auto-detected from extension if None
            bitrate: Bitrate for compressed formats (e.g., '320k' for MP3)
            sample_rate: Target sample rate (None to keep original)
            
        Returns:
            True if export successful
        """
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(input_file)
            
            # Resample if needed
            if sample_rate and audio.frame_rate != sample_rate:
                audio = audio.set_frame_rate(sample_rate)
            
            # Determine format
            if format is None:
                format = Path(output_file).suffix.lower().lstrip('.')
            
            # Export
            if format == 'mp3':
                audio.export(output_file, format='mp3', bitrate=bitrate)
            elif format == 'ogg':
                audio.export(output_file, format='ogg')
            elif format == 'flac':
                audio.export(output_file, format='flac')
            elif format == 'wav':
                audio.export(output_file, format='wav')
            else:
                print(f"Unsupported format: {format}")
                return False
            
            return True
            
        except ImportError:
            print("Export requires pydub and ffmpeg")
            print("Install with: pip install pydub")
            return False
        except Exception as e:
            print(f"Error exporting audio: {e}")
            return False
    
    @staticmethod
    def normalize_audio(input_file: str, output_file: str, 
                       target_dBFS: float = -3.0) -> bool:
        """
        Normalize audio file to target loudness
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output audio file
            target_dBFS: Target loudness in dBFS (default -3.0 for headroom)
            
        Returns:
            True if normalization successful
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(input_file)
            
            # Calculate change needed
            change_in_dBFS = target_dBFS - audio.dBFS
            
            # Apply normalization
            normalized_audio = audio.apply_gain(change_in_dBFS)
            
            # Export
            format = Path(output_file).suffix.lower().lstrip('.')
            normalized_audio.export(output_file, format=format)
            
            return True
            
        except ImportError:
            print("Normalization requires pydub")
            return False
        except Exception as e:
            print(f"Error normalizing audio: {e}")
            return False
    
    @staticmethod
    def split_audio(input_file: str, output_dir: str, 
                   chunk_duration_ms: int = 60000) -> List[str]:
        """
        Split audio file into chunks
        
        Args:
            input_file: Path to input audio file
            output_dir: Directory for output chunks
            chunk_duration_ms: Duration of each chunk in milliseconds
            
        Returns:
            List of output file paths
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(input_file)
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Split into chunks
            output_files = []
            chunk_num = 1
            
            for i in range(0, len(audio), chunk_duration_ms):
                chunk = audio[i:i + chunk_duration_ms]
                
                # Generate output filename
                input_name = Path(input_file).stem
                ext = Path(input_file).suffix
                output_file = output_path / f"{input_name}_part{chunk_num:03d}{ext}"
                
                # Export chunk
                chunk.export(str(output_file), format=ext.lstrip('.'))
                output_files.append(str(output_file))
                chunk_num += 1
            
            return output_files
            
        except ImportError:
            print("Splitting requires pydub")
            return []
        except Exception as e:
            print(f"Error splitting audio: {e}")
            return []
    
    @staticmethod
    def concatenate_audio(input_files: List[str], output_file: str) -> bool:
        """
        Concatenate multiple audio files into one
        
        Args:
            input_files: List of input audio file paths
            output_file: Path to output audio file
            
        Returns:
            True if concatenation successful
        """
        try:
            from pydub import AudioSegment
            
            if not input_files:
                return False
            
            # Load first file
            combined = AudioSegment.from_file(input_files[0])
            
            # Append remaining files
            for audio_file in input_files[1:]:
                audio = AudioSegment.from_file(audio_file)
                combined += audio
            
            # Export
            format = Path(output_file).suffix.lower().lstrip('.')
            combined.export(output_file, format=format)
            
            return True
            
        except ImportError:
            print("Concatenation requires pydub")
            return False
        except Exception as e:
            print(f"Error concatenating audio: {e}")
            return False
