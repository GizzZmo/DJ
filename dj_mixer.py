#!/usr/bin/env python3
"""
DJ Mixer for playback on multiple sound devices
Supports loading audio files and mixing them across different output devices
"""

import pygame
from typing import Dict, List, Optional
from pathlib import Path


class AudioTrack:
    """Represents a single audio track with playback controls"""
    
    def __init__(self, file_path: str, device_id: Optional[int] = None):
        self.file_path = Path(file_path)
        self.device_id = device_id
        self.sound: Optional[pygame.mixer.Sound] = None
        self.channel: Optional[pygame.mixer.Channel] = None
        self.volume = 1.0
        self.is_loaded = False
        self.is_playing = False
        
    def load(self) -> bool:
        """Load the audio file"""
        try:
            if not self.file_path.exists():
                print(f"Error: File {self.file_path} does not exist")
                return False
                
            self.sound = pygame.mixer.Sound(str(self.file_path))
            self.is_loaded = True
            print(f"Loaded: {self.file_path.name}")
            return True
        except pygame.error as e:
            print(f"Error loading {self.file_path}: {e}")
            return False
    
    def play(self, loops: int = 0, fade_ms: int = 0) -> bool:
        """Play the track"""
        if not self.is_loaded or not self.sound:
            print("Track not loaded")
            return False
            
        try:
            self.channel = self.sound.play(loops=loops, fade_ms=fade_ms)
            if self.channel:
                self.channel.set_volume(self.volume)
                self.is_playing = True
                return True
        except pygame.error as e:
            print(f"Error playing track: {e}")
        return False
    
    def stop(self, fade_ms: int = 0) -> None:
        """Stop the track"""
        if self.channel:
            if fade_ms > 0:
                self.channel.fadeout(fade_ms)
            else:
                self.channel.stop()
            self.is_playing = False
    
    def pause(self) -> None:
        """Pause the track"""
        if self.channel:
            self.channel.pause()
    
    def unpause(self) -> None:
        """Unpause the track"""
        if self.channel:
            self.channel.unpause()
    
    def set_volume(self, volume: float) -> None:
        """Set track volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.channel:
            self.channel.set_volume(self.volume)
    
    def get_volume(self) -> float:
        """Get current volume"""
        return self.volume
    
    def is_track_playing(self) -> bool:
        """Check if track is currently playing"""
        if self.channel:
            return self.channel.get_busy()
        return False


class DJMixer:
    """Main DJ Mixer class supporting multiple audio devices"""
    
    def __init__(self, frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 512):
        """Initialize the DJ mixer"""
        self.frequency = frequency
        self.size = size
        self.channels = channels
        self.buffer = buffer
        self.tracks: Dict[str, AudioTrack] = {}
        self.crossfader_position = 0.5  # 0.0 = full left, 1.0 = full right
        self.master_volume = 1.0
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize pygame mixer"""
        try:
            pygame.mixer.pre_init(
                frequency=self.frequency,
                size=self.size,
                channels=self.channels,
                buffer=self.buffer
            )
            pygame.mixer.init()
            self.is_initialized = True
            print(f"DJ Mixer initialized: {self.frequency}Hz, {self.channels} channels")
            return True
        except pygame.error as e:
            print(f"Failed to initialize mixer: {e}")
            return False
    
    def get_audio_devices(self) -> List[str]:
        """Get available audio devices (simplified - pygame doesn't expose this directly)"""
        # Note: pygame doesn't provide direct access to multiple audio devices
        # This is a placeholder for device enumeration
        return ["Default Audio Device"]
    
    def load_track(self, name: str, file_path: str, device_id: Optional[int] = None) -> bool:
        """Load an audio track"""
        if not self.is_initialized:
            print("Mixer not initialized")
            return False
            
        track = AudioTrack(file_path, device_id)
        if track.load():
            self.tracks[name] = track
            return True
        return False
    
    def play_track(self, name: str, loops: int = 0, fade_ms: int = 0) -> bool:
        """Play a loaded track"""
        if name not in self.tracks:
            print(f"Track '{name}' not found")
            return False
        return self.tracks[name].play(loops, fade_ms)
    
    def stop_track(self, name: str, fade_ms: int = 0) -> bool:
        """Stop a track"""
        if name not in self.tracks:
            return False
        self.tracks[name].stop(fade_ms)
        return True
    
    def pause_track(self, name: str) -> bool:
        """Pause a track"""
        if name not in self.tracks:
            return False
        self.tracks[name].pause()
        return True
    
    def unpause_track(self, name: str) -> bool:
        """Unpause a track"""
        if name not in self.tracks:
            return False
        self.tracks[name].unpause()
        return True
    
    def set_track_volume(self, name: str, volume: float) -> bool:
        """Set volume for a specific track"""
        if name not in self.tracks:
            return False
        if volume < 0.0 or volume > 1.0:
            return False
        self.tracks[name].set_volume(volume)
        return True
    
    def get_track_volume(self, name: str) -> float:
        """Get volume for a specific track"""
        if name in self.tracks:
            return self.tracks[name].get_volume()
        return 0.0
    
    def set_crossfader(self, position: float) -> bool:
        """Set crossfader position (0.0 = full left, 1.0 = full right)"""
        if position < 0.0 or position > 1.0:
            return False
        self.crossfader_position = max(0.0, min(1.0, position))
        return True
    
    def get_crossfader(self) -> float:
        """Get crossfader position"""
        return self.crossfader_position
    
    def apply_crossfader(self, left_track: str, right_track: str) -> bool:
        """Apply crossfader effect between two tracks"""
        if left_track not in self.tracks or right_track not in self.tracks:
            return False
        left_volume = (1.0 - self.crossfader_position) * self.master_volume
        right_volume = self.crossfader_position * self.master_volume
        
        self.tracks[left_track].set_volume(left_volume)
        self.tracks[right_track].set_volume(right_volume)
        return True
    
    def set_master_volume(self, volume: float) -> bool:
        """Set master volume"""
        if volume < 0.0 or volume > 1.0:
            return False
        self.master_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.master_volume)
        return True
    
    def get_master_volume(self) -> float:
        """Get master volume"""
        return self.master_volume
    
    def is_track_playing(self, name: str) -> bool:
        """Check if a track is playing"""
        if name in self.tracks:
            return self.tracks[name].is_track_playing()
        return False
    
    def get_loaded_tracks(self) -> List[str]:
        """Get list of loaded track names"""
        return list(self.tracks.keys())
    
    def cleanup(self) -> None:
        """Clean up resources"""
        for track in self.tracks.values():
            track.stop()
        pygame.mixer.quit()
        self.is_initialized = False
        print("DJ Mixer cleaned up")


def main():
    """Example usage of the DJ Mixer"""
    mixer = DJMixer()
    
    if not mixer.initialize():
        print("Failed to initialize mixer")
        return
    
    print("DJ Mixer initialized successfully!")
    print("Available audio devices:", mixer.get_audio_devices())
    
    # Example: Load some tracks (you would need actual audio files)
    # mixer.load_track("deck1", "track1.mp3")
    # mixer.load_track("deck2", "track2.mp3")
    
    # Example mixing operations
    mixer.set_master_volume(0.8)
    mixer.set_crossfader(0.5)  # Center position
    
    print(f"Master volume: {mixer.get_master_volume()}")
    print(f"Crossfader position: {mixer.get_crossfader()}")
    print(f"Loaded tracks: {mixer.get_loaded_tracks()}")
    
    # Cleanup
    mixer.cleanup()


if __name__ == "__main__":
    main()