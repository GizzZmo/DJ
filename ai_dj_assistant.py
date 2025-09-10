#!/usr/bin/env python3
"""
AI DJ Assistant using Gemini API
Provides intelligent auto mixing, key-mixing, and fader effects
"""

import json
import time
import random
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from pathlib import Path

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. AI features will use mock implementation.")


@dataclass
class AITrackAnalysis:
    """Analysis of a track for AI mixing decisions"""
    tempo: float = 120.0  # BPM
    key: str = "C"  # Musical key
    energy: float = 0.5  # Energy level 0-1
    genre: str = "Electronic"  # Music genre
    mood: str = "Neutral"  # Track mood
    duration: float = 180.0  # Duration in seconds
    

@dataclass 
class AIMixingAdvice:
    """AI-generated mixing advice"""
    crossfader_position: float = 0.5
    deck1_volume: float = 1.0
    deck2_volume: float = 1.0
    transition_duration: float = 10.0  # seconds
    effects_suggestion: str = "None"
    reasoning: str = "Balanced mix"


class AIDJAssistant:
    """AI-powered DJ assistant using Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = None
        self.is_configured = False
        self.track_analyses: Dict[str, AITrackAnalysis] = {}
        self.mixing_history: List[Dict] = []
        self.callbacks: Dict[str, Callable] = {}
        
        if api_key and GEMINI_AVAILABLE:
            self.configure_gemini(api_key)
    
    def configure_gemini(self, api_key: str) -> bool:
        """Configure Gemini API with the provided key"""
        try:
            if not GEMINI_AVAILABLE:
                return False
                
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.api_key = api_key
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Failed to configure Gemini API: {e}")
            return False
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for AI events (volume changes, crossfader moves, etc.)"""
        self.callbacks[event] = callback
    
    def _trigger_callback(self, event: str, *args, **kwargs) -> None:
        """Trigger registered callback if it exists"""
        if event in self.callbacks:
            try:
                self.callbacks[event](*args, **kwargs)
            except Exception as e:
                print(f"Callback error for {event}: {e}")
    
    def analyze_track(self, track_name: str, file_path: str = None) -> AITrackAnalysis:
        """Analyze a track for AI mixing decisions"""
        if self.is_configured and GEMINI_AVAILABLE:
            return self._analyze_track_with_ai(track_name, file_path)
        else:
            return self._analyze_track_mock(track_name, file_path)
    
    def _analyze_track_with_ai(self, track_name: str, file_path: str = None) -> AITrackAnalysis:
        """Use Gemini AI to analyze track characteristics"""
        try:
            # Extract track info from filename/path for AI analysis
            prompt = f"""
            Analyze this music track for DJ mixing: "{track_name}"
            
            Based on the track name, provide estimates for:
            1. Tempo (BPM) - typical range 60-200
            2. Musical key (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
            3. Energy level (0.0 to 1.0, where 0 is calm and 1 is high energy)
            4. Genre (Electronic, House, Techno, Trance, Hip-Hop, Rock, Pop, etc.)
            5. Mood (Energetic, Calm, Dark, Uplifting, Melancholic, etc.)
            6. Estimated duration in seconds (typical 180-300 for most tracks)
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "tempo": 120.0,
                "key": "C",
                "energy": 0.5,
                "genre": "Electronic",
                "mood": "Neutral",
                "duration": 180.0
            }}
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            
            analysis = AITrackAnalysis(
                tempo=float(result.get('tempo', 120.0)),
                key=str(result.get('key', 'C')),
                energy=float(result.get('energy', 0.5)),
                genre=str(result.get('genre', 'Electronic')),
                mood=str(result.get('mood', 'Neutral')),
                duration=float(result.get('duration', 180.0))
            )
            
            self.track_analyses[track_name] = analysis
            return analysis
            
        except Exception as e:
            print(f"AI track analysis failed, using mock: {e}")
            return self._analyze_track_mock(track_name, file_path)
    
    def _analyze_track_mock(self, track_name: str, file_path: str = None) -> AITrackAnalysis:
        """Mock track analysis for testing"""
        # Generate pseudo-realistic analysis based on track name
        name_lower = track_name.lower()
        
        # Guess tempo based on keywords
        if any(word in name_lower for word in ['house', 'deep', 'tech']):
            tempo = random.uniform(120, 130)
        elif any(word in name_lower for word in ['techno', 'hardstyle']):
            tempo = random.uniform(130, 150)
        elif any(word in name_lower for word in ['trance', 'uplifting']):
            tempo = random.uniform(130, 140)
        elif any(word in name_lower for word in ['hip-hop', 'rap', 'trap']):
            tempo = random.uniform(70, 100)
        else:
            tempo = random.uniform(110, 140)
        
        # Guess key
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = random.choice(keys)
        
        # Guess energy based on keywords
        if any(word in name_lower for word in ['energy', 'power', 'hard', 'intense']):
            energy = random.uniform(0.7, 1.0)
        elif any(word in name_lower for word in ['chill', 'calm', 'ambient', 'deep']):
            energy = random.uniform(0.1, 0.4)
        else:
            energy = random.uniform(0.4, 0.8)
        
        # Guess genre
        if any(word in name_lower for word in ['house', 'deep']):
            genre = "House"
        elif any(word in name_lower for word in ['techno']):
            genre = "Techno"
        elif any(word in name_lower for word in ['trance']):
            genre = "Trance"
        elif any(word in name_lower for word in ['hip-hop', 'rap']):
            genre = "Hip-Hop"
        else:
            genre = "Electronic"
        
        analysis = AITrackAnalysis(
            tempo=round(tempo, 1),
            key=key,
            energy=round(energy, 2),
            genre=genre,
            mood="Energetic" if energy > 0.6 else "Calm" if energy < 0.3 else "Balanced",
            duration=random.uniform(180, 300)
        )
        
        self.track_analyses[track_name] = analysis
        return analysis
    
    def get_auto_mixing_advice(self, deck1_track: str, deck2_track: str, 
                              current_position: float = 0.5) -> AIMixingAdvice:
        """Get AI advice for auto mixing between two tracks"""
        if self.is_configured and GEMINI_AVAILABLE:
            return self._get_auto_mixing_advice_with_ai(deck1_track, deck2_track, current_position)
        else:
            return self._get_auto_mixing_advice_mock(deck1_track, deck2_track, current_position)
    
    def _get_auto_mixing_advice_with_ai(self, deck1_track: str, deck2_track: str, 
                                       current_position: float) -> AIMixingAdvice:
        """Use Gemini AI to generate mixing advice"""
        try:
            track1_analysis = self.track_analyses.get(deck1_track)
            track2_analysis = self.track_analyses.get(deck2_track)
            
            if not track1_analysis:
                track1_analysis = self.analyze_track(deck1_track)
            if not track2_analysis:
                track2_analysis = self.analyze_track(deck2_track)
            
            prompt = f"""
            You are a professional DJ AI assistant. Provide mixing advice for transitioning between these two tracks:
            
            DECK 1 (Left): {deck1_track}
            - Tempo: {track1_analysis.tempo} BPM
            - Key: {track1_analysis.key}
            - Energy: {track1_analysis.energy}
            - Genre: {track1_analysis.genre}
            - Mood: {track1_analysis.mood}
            
            DECK 2 (Right): {deck2_track}
            - Tempo: {track2_analysis.tempo} BPM
            - Key: {track2_analysis.key}
            - Energy: {track2_analysis.energy}
            - Genre: {track2_analysis.genre}
            - Mood: {track2_analysis.mood}
            
            Current crossfader position: {current_position} (0.0 = full left, 1.0 = full right)
            
            Provide optimal mixing settings and explain your reasoning. Consider:
            - Key compatibility for harmonic mixing
            - Tempo matching and transition timing
            - Energy flow between tracks
            - Genre compatibility
            
            Respond with ONLY a JSON object:
            {{
                "crossfader_position": 0.5,
                "deck1_volume": 1.0,
                "deck2_volume": 1.0,
                "transition_duration": 10.0,
                "effects_suggestion": "Slow fade",
                "reasoning": "Explanation of mixing decision"
            }}
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            
            return AIMixingAdvice(
                crossfader_position=float(result.get('crossfader_position', 0.5)),
                deck1_volume=float(result.get('deck1_volume', 1.0)),
                deck2_volume=float(result.get('deck2_volume', 1.0)),
                transition_duration=float(result.get('transition_duration', 10.0)),
                effects_suggestion=str(result.get('effects_suggestion', 'None')),
                reasoning=str(result.get('reasoning', 'AI mixing advice'))
            )
            
        except Exception as e:
            print(f"AI mixing advice failed, using mock: {e}")
            return self._get_auto_mixing_advice_mock(deck1_track, deck2_track, current_position)
    
    def _get_auto_mixing_advice_mock(self, deck1_track: str, deck2_track: str, 
                                    current_position: float) -> AIMixingAdvice:
        """Mock auto mixing advice"""
        track1_analysis = self.track_analyses.get(deck1_track)
        track2_analysis = self.track_analyses.get(deck2_track)
        
        if not track1_analysis:
            track1_analysis = self.analyze_track(deck1_track)
        if not track2_analysis:
            track2_analysis = self.analyze_track(deck2_track)
        
        # Simple mock logic for mixing advice
        tempo_diff = abs(track1_analysis.tempo - track2_analysis.tempo)
        energy_diff = abs(track1_analysis.energy - track2_analysis.energy)
        
        # Suggest transition duration based on tempo difference
        if tempo_diff < 5:
            transition_duration = 8.0  # Quick transition for similar tempos
        elif tempo_diff < 15:
            transition_duration = 15.0  # Medium transition
        else:
            transition_duration = 25.0  # Slow transition for very different tempos
        
        # Suggest crossfader position based on energy levels
        if track2_analysis.energy > track1_analysis.energy:
            suggested_position = 0.7  # Favor higher energy track
        elif track1_analysis.energy > track2_analysis.energy:
            suggested_position = 0.3  # Favor higher energy track
        else:
            suggested_position = 0.5  # Balanced
        
        effects = "Slow fade" if tempo_diff > 10 else "Quick cut"
        reasoning = f"Tempo difference: {tempo_diff:.1f} BPM, Energy difference: {energy_diff:.2f}"
        
        return AIMixingAdvice(
            crossfader_position=suggested_position,
            deck1_volume=1.0,
            deck2_volume=1.0,
            transition_duration=transition_duration,
            effects_suggestion=effects,
            reasoning=reasoning
        )
    
    def start_auto_mixing(self, deck1_track: str, deck2_track: str) -> None:
        """Start automated mixing between two tracks"""
        def auto_mix_worker():
            advice = self.get_auto_mixing_advice(deck1_track, deck2_track)
            
            # Record mixing decision
            self.mixing_history.append({
                'timestamp': time.time(),
                'deck1': deck1_track,
                'deck2': deck2_track,
                'advice': advice,
                'type': 'auto_mix'
            })
            
            print(f"[AI AUTO MIX] {advice.reasoning}")
            print(f"[AI AUTO MIX] Transitioning over {advice.transition_duration:.1f} seconds")
            print(f"[AI AUTO MIX] Effect: {advice.effects_suggestion}")
            
            # Animate transition
            start_pos = 0.5
            target_pos = advice.crossfader_position
            steps = int(advice.transition_duration * 2)  # 2 updates per second
            
            for i in range(steps + 1):
                progress = i / steps
                current_pos = start_pos + (target_pos - start_pos) * progress
                
                # Trigger callbacks to update mixer
                self._trigger_callback('crossfader_change', current_pos)
                self._trigger_callback('volume_change', 'deck1', advice.deck1_volume)
                self._trigger_callback('volume_change', 'deck2', advice.deck2_volume)
                
                time.sleep(advice.transition_duration / steps)
            
            print(f"[AI AUTO MIX] Transition complete at position {target_pos:.2f}")
        
        # Run in background thread
        thread = threading.Thread(target=auto_mix_worker, daemon=True)
        thread.start()
    
    def get_key_mixing_advice(self, deck1_track: str, deck2_track: str) -> Dict[str, Any]:
        """Get harmonic mixing advice based on musical keys"""
        track1_analysis = self.track_analyses.get(deck1_track)
        track2_analysis = self.track_analyses.get(deck2_track)
        
        if not track1_analysis:
            track1_analysis = self.analyze_track(deck1_track)
        if not track2_analysis:
            track2_analysis = self.analyze_track(deck2_track)
        
        # Harmonic mixing rules (simplified Camelot wheel concept)
        key_compatibility = self._check_key_compatibility(track1_analysis.key, track2_analysis.key)
        
        return {
            'deck1_key': track1_analysis.key,
            'deck2_key': track2_analysis.key,
            'compatibility': key_compatibility['compatibility'],
            'advice': key_compatibility['advice'],
            'suggested_action': key_compatibility['action']
        }
    
    def _check_key_compatibility(self, key1: str, key2: str) -> Dict[str, str]:
        """Check harmonic compatibility between two keys"""
        # Simplified harmonic mixing rules
        compatible_keys = {
            'C': ['C', 'F', 'G', 'Am', 'Dm', 'Em'],
            'C#': ['C#', 'F#', 'G#', 'A#m', 'D#m', 'Fm'],
            'D': ['D', 'G', 'A', 'Bm', 'Em', 'F#m'],
            'D#': ['D#', 'G#', 'A#', 'Cm', 'Fm', 'Gm'],
            'E': ['E', 'A', 'B', 'C#m', 'F#m', 'G#m'],
            'F': ['F', 'A#', 'C', 'Dm', 'Gm', 'Am'],
            'F#': ['F#', 'B', 'C#', 'D#m', 'G#m', 'A#m'],
            'G': ['G', 'C', 'D', 'Em', 'Am', 'Bm'],
            'G#': ['G#', 'C#', 'D#', 'Fm', 'A#m', 'Cm'],
            'A': ['A', 'D', 'E', 'F#m', 'Bm', 'C#m'],
            'A#': ['A#', 'D#', 'F', 'Gm', 'Cm', 'Dm'],
            'B': ['B', 'E', 'F#', 'G#m', 'C#m', 'D#m']
        }
        
        if key2 in compatible_keys.get(key1, []):
            return {
                'compatibility': 'Excellent',
                'advice': f'{key1} and {key2} are harmonically compatible',
                'action': 'Mix freely - keys work well together'
            }
        else:
            return {
                'compatibility': 'Caution',
                'advice': f'{key1} and {key2} may clash harmonically',
                'action': 'Consider using effects or quick transition'
            }
    
    def get_fader_effects_suggestion(self, current_position: float, track1_energy: float, 
                                   track2_energy: float) -> Dict[str, Any]:
        """Get AI suggestions for fader effects"""
        energy_diff = abs(track1_energy - track2_energy)
        
        if energy_diff > 0.3:
            # High energy difference - suggest dramatic effects
            if track1_energy > track2_energy:
                effect = "Quick cut to maintain energy"
                technique = "Fast crossfader movement"
            else:
                effect = "Build-up fade for energy increase"
                technique = "Gradual transition with filter sweep"
        else:
            # Similar energy - suggest smooth transition
            effect = "Smooth blend"
            technique = "Linear crossfader movement"
        
        return {
            'suggested_effect': effect,
            'technique': technique,
            'optimal_speed': 'Fast' if energy_diff > 0.3 else 'Medium',
            'reasoning': f'Energy difference of {energy_diff:.2f} suggests {effect.lower()}'
        }
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get current AI assistant status"""
        return {
            'configured': self.is_configured,
            'gemini_available': GEMINI_AVAILABLE,
            'tracks_analyzed': len(self.track_analyses),
            'mixing_history_count': len(self.mixing_history),
            'api_key_set': bool(self.api_key)
        }