#!/usr/bin/env python3
"""
Playlist Management for DJ Mixer
Handles playlist creation, loading, saving, and navigation
"""

import json
from typing import List, Optional, Dict
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PlaylistTrack:
    """Represents a track in a playlist"""

    path: str
    title: str
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"
    duration: float = 0.0
    bpm: float = 0.0
    key: str = ""
    genre: str = ""
    added_date: str = ""

    def __post_init__(self):
        if not self.added_date:
            self.added_date = datetime.now().isoformat()


class Playlist:
    """Playlist management class"""

    def __init__(self, name: str = "New Playlist"):
        self.name = name
        self.tracks: List[PlaylistTrack] = []
        self.current_index: int = 0
        self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
        self.description = ""

    def add_track(self, track: PlaylistTrack) -> bool:
        """Add a track to the playlist"""
        self.tracks.append(track)
        self.modified_date = datetime.now().isoformat()
        return True

    def add_track_from_path(self, file_path: str, **metadata) -> bool:
        """Add a track from file path with optional metadata"""
        path = Path(file_path)
        if not path.exists():
            return False

        track = PlaylistTrack(
            path=str(path),
            title=metadata.get("title", path.stem),
            artist=metadata.get("artist", "Unknown Artist"),
            album=metadata.get("album", "Unknown Album"),
            duration=metadata.get("duration", 0.0),
            bpm=metadata.get("bpm", 0.0),
            key=metadata.get("key", ""),
            genre=metadata.get("genre", ""),
        )

        return self.add_track(track)

    def remove_track(self, index: int) -> bool:
        """Remove track at specified index"""
        if 0 <= index < len(self.tracks):
            self.tracks.pop(index)
            self.modified_date = datetime.now().isoformat()
            if self.current_index >= len(self.tracks) and len(self.tracks) > 0:
                self.current_index = len(self.tracks) - 1
            return True
        return False

    def move_track(self, from_index: int, to_index: int) -> bool:
        """Move track from one position to another"""
        if 0 <= from_index < len(self.tracks) and 0 <= to_index < len(self.tracks):
            track = self.tracks.pop(from_index)
            self.tracks.insert(to_index, track)
            self.modified_date = datetime.now().isoformat()
            return True
        return False

    def get_track(self, index: int) -> Optional[PlaylistTrack]:
        """Get track at specified index"""
        if 0 <= index < len(self.tracks):
            return self.tracks[index]
        return None

    def get_current_track(self) -> Optional[PlaylistTrack]:
        """Get currently selected track"""
        return self.get_track(self.current_index)

    def next_track(self) -> Optional[PlaylistTrack]:
        """Move to next track and return it"""
        if self.current_index < len(self.tracks) - 1:
            self.current_index += 1
        else:
            self.current_index = 0  # Loop to beginning
        return self.get_current_track()

    def previous_track(self) -> Optional[PlaylistTrack]:
        """Move to previous track and return it"""
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.tracks) - 1  # Loop to end
        return self.get_current_track()

    def set_current_index(self, index: int) -> bool:
        """Set current track index"""
        if 0 <= index < len(self.tracks):
            self.current_index = index
            return True
        return False

    def shuffle(self) -> None:
        """Shuffle the playlist"""
        import random

        current_track = self.get_current_track()
        random.shuffle(self.tracks)
        # Try to maintain current track
        if current_track and current_track in self.tracks:
            self.current_index = self.tracks.index(current_track)
        else:
            self.current_index = 0
        self.modified_date = datetime.now().isoformat()

    def sort_by_bpm(self, ascending: bool = True) -> None:
        """Sort playlist by BPM"""
        self.tracks.sort(key=lambda t: t.bpm, reverse=not ascending)
        self.current_index = 0
        self.modified_date = datetime.now().isoformat()

    def sort_by_title(self, ascending: bool = True) -> None:
        """Sort playlist by title"""
        self.tracks.sort(key=lambda t: t.title.lower(), reverse=not ascending)
        self.current_index = 0
        self.modified_date = datetime.now().isoformat()

    def sort_by_artist(self, ascending: bool = True) -> None:
        """Sort playlist by artist"""
        self.tracks.sort(key=lambda t: t.artist.lower(), reverse=not ascending)
        self.current_index = 0
        self.modified_date = datetime.now().isoformat()

    def filter_by_bpm(self, min_bpm: float, max_bpm: float) -> List[PlaylistTrack]:
        """Get tracks within BPM range"""
        return [t for t in self.tracks if min_bpm <= t.bpm <= max_bpm]

    def filter_by_key(self, key: str) -> List[PlaylistTrack]:
        """Get tracks in specific key"""
        return [t for t in self.tracks if t.key == key]

    def filter_by_genre(self, genre: str) -> List[PlaylistTrack]:
        """Get tracks of specific genre"""
        return [t for t in self.tracks if t.genre.lower() == genre.lower()]

    def get_track_count(self) -> int:
        """Get total number of tracks"""
        return len(self.tracks)

    def get_total_duration(self) -> float:
        """Get total duration of all tracks in seconds"""
        return sum(t.duration for t in self.tracks)

    def clear(self) -> None:
        """Clear all tracks from playlist"""
        self.tracks.clear()
        self.current_index = 0
        self.modified_date = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert playlist to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "current_index": self.current_index,
            "tracks": [asdict(t) for t in self.tracks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Playlist":
        """Create playlist from dictionary"""
        playlist = cls(data.get("name", "Untitled"))
        playlist.description = data.get("description", "")
        playlist.created_date = data.get("created_date", datetime.now().isoformat())
        playlist.modified_date = data.get("modified_date", datetime.now().isoformat())
        playlist.current_index = data.get("current_index", 0)

        for track_data in data.get("tracks", []):
            track = PlaylistTrack(**track_data)
            playlist.tracks.append(track)

        return playlist

    def save(self, file_path: str) -> bool:
        """Save playlist to JSON file"""
        try:
            with open(file_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving playlist: {e}")
            return False

    @classmethod
    def load(cls, file_path: str) -> Optional["Playlist"]:
        """Load playlist from JSON file"""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading playlist: {e}")
            return None


class PlaylistManager:
    """Manages multiple playlists"""

    def __init__(self):
        self.playlists: Dict[str, Playlist] = {}
        self.current_playlist_name: Optional[str] = None

    def create_playlist(self, name: str) -> Playlist:
        """Create a new playlist"""
        playlist = Playlist(name)
        self.playlists[name] = playlist
        if self.current_playlist_name is None:
            self.current_playlist_name = name
        return playlist

    def delete_playlist(self, name: str) -> bool:
        """Delete a playlist"""
        if name in self.playlists:
            del self.playlists[name]
            if self.current_playlist_name == name:
                self.current_playlist_name = next(iter(self.playlists.keys()), None)
            return True
        return False

    def get_playlist(self, name: str) -> Optional[Playlist]:
        """Get playlist by name"""
        return self.playlists.get(name)

    def get_current_playlist(self) -> Optional[Playlist]:
        """Get currently active playlist"""
        if self.current_playlist_name:
            return self.playlists.get(self.current_playlist_name)
        return None

    def set_current_playlist(self, name: str) -> bool:
        """Set active playlist"""
        if name in self.playlists:
            self.current_playlist_name = name
            return True
        return False

    def get_playlist_names(self) -> List[str]:
        """Get list of all playlist names"""
        return list(self.playlists.keys())

    def save_all(self, directory: str) -> bool:
        """Save all playlists to directory"""
        try:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)

            for name, playlist in self.playlists.items():
                file_name = f"{name.replace(' ', '_')}.json"
                file_path = dir_path / file_name
                playlist.save(str(file_path))

            return True
        except Exception as e:
            print(f"Error saving playlists: {e}")
            return False

    def load_all(self, directory: str) -> bool:
        """Load all playlists from directory"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return False

            for json_file in dir_path.glob("*.json"):
                playlist = Playlist.load(str(json_file))
                if playlist:
                    self.playlists[playlist.name] = playlist
                    if self.current_playlist_name is None:
                        self.current_playlist_name = playlist.name

            return True
        except Exception as e:
            print(f"Error loading playlists: {e}")
            return False

    def import_m3u(
        self, file_path: str, playlist_name: Optional[str] = None
    ) -> Optional[Playlist]:
        """Import M3U playlist file"""
        try:
            if playlist_name is None:
                playlist_name = Path(file_path).stem

            playlist = self.create_playlist(playlist_name)

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        playlist.add_track_from_path(line)

            return playlist
        except Exception as e:
            print(f"Error importing M3U: {e}")
            return None

    def export_m3u(self, playlist_name: str, file_path: str) -> bool:
        """Export playlist to M3U format"""
        playlist = self.get_playlist(playlist_name)
        if not playlist:
            return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for track in playlist.tracks:
                    f.write(
                        f"#EXTINF:{int(track.duration)},{track.artist} - {track.title}\n"
                    )
                    f.write(f"{track.path}\n")
            return True
        except Exception as e:
            print(f"Error exporting M3U: {e}")
            return False
