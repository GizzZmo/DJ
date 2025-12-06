#!/usr/bin/env python3
"""
MIDI Controller Support for DJ Mixer
Handles MIDI input and mapping to mixer controls
"""

from typing import Dict, Callable, Optional, List, Any
from dataclasses import dataclass
from enum import Enum


class MIDIControlType(Enum):
    """Types of MIDI controls"""
    KNOB = "knob"           # Continuous control (0-127)
    FADER = "fader"         # Continuous control (0-127)
    BUTTON = "button"       # On/Off (0 or 127)
    PAD = "pad"            # Trigger button
    ENCODER = "encoder"     # Relative encoder


@dataclass
class MIDIMapping:
    """Mapping between MIDI control and mixer function"""
    control_number: int
    control_type: MIDIControlType
    function_name: str
    min_value: float = 0.0
    max_value: float = 1.0
    channel: int = 0


class MIDIController:
    """MIDI controller interface for DJ Mixer"""
    
    def __init__(self):
        self.mappings: Dict[int, MIDIMapping] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.midi_input = None
        self.connected = False
        self.device_name = ""
        
    def connect(self, device_name: Optional[str] = None) -> bool:
        """
        Connect to MIDI device
        
        Args:
            device_name: Name of MIDI device to connect to (None for first available)
            
        Returns:
            True if connected successfully
        """
        try:
            # Try to import mido (MIDI library)
            import mido
            
            # List available input devices
            available_devices = mido.get_input_names()
            
            if not available_devices:
                print("No MIDI input devices found")
                return False
            
            # Select device
            if device_name:
                if device_name not in available_devices:
                    print(f"MIDI device '{device_name}' not found")
                    return False
                self.device_name = device_name
            else:
                self.device_name = available_devices[0]
            
            # Open MIDI input
            self.midi_input = mido.open_input(self.device_name)
            self.connected = True
            print(f"Connected to MIDI device: {self.device_name}")
            return True
            
        except ImportError:
            print("MIDI support not available. Install 'mido' package: pip install mido python-rtmidi")
            return False
        except Exception as e:
            print(f"Error connecting to MIDI device: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MIDI device"""
        if self.midi_input:
            try:
                self.midi_input.close()
            except:
                pass
            self.midi_input = None
        self.connected = False
        print("MIDI device disconnected")
    
    def get_available_devices(self) -> List[str]:
        """Get list of available MIDI input devices"""
        try:
            import mido
            return mido.get_input_names()
        except ImportError:
            return []
        except Exception as e:
            print(f"Error getting MIDI devices: {e}")
            return []
    
    def add_mapping(self, control_number: int, control_type: MIDIControlType,
                   function_name: str, min_value: float = 0.0, 
                   max_value: float = 1.0, channel: int = 0) -> None:
        """Add a MIDI control mapping"""
        mapping = MIDIMapping(
            control_number=control_number,
            control_type=control_type,
            function_name=function_name,
            min_value=min_value,
            max_value=max_value,
            channel=channel
        )
        self.mappings[control_number] = mapping
    
    def remove_mapping(self, control_number: int) -> bool:
        """Remove a MIDI control mapping"""
        if control_number in self.mappings:
            del self.mappings[control_number]
            return True
        return False
    
    def register_callback(self, function_name: str, callback: Callable) -> None:
        """Register a callback function for a mixer function"""
        self.callbacks[function_name] = callback
    
    def unregister_callback(self, function_name: str) -> None:
        """Unregister a callback function"""
        if function_name in self.callbacks:
            del self.callbacks[function_name]
    
    def _normalize_midi_value(self, midi_value: int, mapping: MIDIMapping) -> float:
        """Normalize MIDI value (0-127) to mapped range"""
        normalized = midi_value / 127.0
        return mapping.min_value + normalized * (mapping.max_value - mapping.min_value)
    
    def process_message(self, message: Any) -> None:
        """Process incoming MIDI message"""
        try:
            # Extract message data
            if hasattr(message, 'control'):
                control_number = message.control
                value = message.value
            elif hasattr(message, 'note'):
                control_number = message.note
                value = message.velocity
            else:
                return
            
            # Check if we have a mapping for this control
            if control_number not in self.mappings:
                return
            
            mapping = self.mappings[control_number]
            
            # Get callback function
            if mapping.function_name not in self.callbacks:
                return
            
            callback = self.callbacks[mapping.function_name]
            
            # Normalize value and call callback
            if mapping.control_type in [MIDIControlType.KNOB, MIDIControlType.FADER]:
                normalized_value = self._normalize_midi_value(value, mapping)
                callback(normalized_value)
            elif mapping.control_type in [MIDIControlType.BUTTON, MIDIControlType.PAD]:
                # Button pressed (value > 0)
                if value > 0:
                    callback(True)
                else:
                    callback(False)
            
        except Exception as e:
            print(f"Error processing MIDI message: {e}")
    
    def start_listening(self) -> None:
        """Start listening for MIDI messages (blocking)"""
        if not self.connected or not self.midi_input:
            print("MIDI device not connected")
            return
        
        print(f"Listening for MIDI messages from {self.device_name}...")
        print("Press Ctrl+C to stop")
        
        try:
            for message in self.midi_input:
                self.process_message(message)
        except KeyboardInterrupt:
            print("\nStopped listening")
    
    def poll_messages(self, timeout: float = 0.0) -> None:
        """Poll for MIDI messages (non-blocking)"""
        if not self.connected or not self.midi_input:
            return
        
        try:
            for message in self.midi_input.iter_pending():
                self.process_message(message)
        except Exception as e:
            print(f"Error polling MIDI: {e}")
    
    def get_mappings(self) -> List[MIDIMapping]:
        """Get all current MIDI mappings"""
        return list(self.mappings.values())
    
    def clear_mappings(self) -> None:
        """Clear all MIDI mappings"""
        self.mappings.clear()
    
    def load_mapping_preset(self, preset_name: str) -> bool:
        """Load a predefined mapping preset"""
        presets = {
            "generic_dj": self._generic_dj_preset,
            "pioneer_ddj": self._pioneer_ddj_preset,
            "traktor_kontrol": self._traktor_kontrol_preset,
        }
        
        if preset_name not in presets:
            return False
        
        self.clear_mappings()
        presets[preset_name]()
        return True
    
    def _generic_dj_preset(self) -> None:
        """Generic DJ controller mapping"""
        # Crossfader
        self.add_mapping(0, MIDIControlType.FADER, "crossfader", 0.0, 1.0)
        
        # Deck 1 controls
        self.add_mapping(1, MIDIControlType.FADER, "deck1_volume", 0.0, 1.0)
        self.add_mapping(16, MIDIControlType.BUTTON, "deck1_play")
        self.add_mapping(17, MIDIControlType.BUTTON, "deck1_cue")
        
        # Deck 2 controls
        self.add_mapping(2, MIDIControlType.FADER, "deck2_volume", 0.0, 1.0)
        self.add_mapping(18, MIDIControlType.BUTTON, "deck2_play")
        self.add_mapping(19, MIDIControlType.BUTTON, "deck2_cue")
        
        # Master volume
        self.add_mapping(7, MIDIControlType.FADER, "master_volume", 0.0, 1.0)
        
        # EQ controls (Deck 1)
        self.add_mapping(8, MIDIControlType.KNOB, "deck1_eq_low", 0.0, 2.0)
        self.add_mapping(9, MIDIControlType.KNOB, "deck1_eq_mid", 0.0, 2.0)
        self.add_mapping(10, MIDIControlType.KNOB, "deck1_eq_high", 0.0, 2.0)
        
        # EQ controls (Deck 2)
        self.add_mapping(11, MIDIControlType.KNOB, "deck2_eq_low", 0.0, 2.0)
        self.add_mapping(12, MIDIControlType.KNOB, "deck2_eq_mid", 0.0, 2.0)
        self.add_mapping(13, MIDIControlType.KNOB, "deck2_eq_high", 0.0, 2.0)
    
    def _pioneer_ddj_preset(self) -> None:
        """Pioneer DDJ controller mapping"""
        # Similar to generic but with Pioneer-specific CC numbers
        self._generic_dj_preset()
    
    def _traktor_kontrol_preset(self) -> None:
        """Traktor Kontrol controller mapping"""
        # Similar to generic but with Traktor-specific CC numbers
        self._generic_dj_preset()
    
    def save_mappings(self, file_path: str) -> bool:
        """Save current mappings to JSON file"""
        import json
        try:
            mappings_data = {
                control_num: {
                    "control_number": m.control_number,
                    "control_type": m.control_type.value,
                    "function_name": m.function_name,
                    "min_value": m.min_value,
                    "max_value": m.max_value,
                    "channel": m.channel
                }
                for control_num, m in self.mappings.items()
            }
            
            with open(file_path, 'w') as f:
                json.dump(mappings_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving mappings: {e}")
            return False
    
    def load_mappings(self, file_path: str) -> bool:
        """Load mappings from JSON file"""
        import json
        try:
            with open(file_path, 'r') as f:
                mappings_data = json.load(f)
            
            self.clear_mappings()
            
            for control_num, data in mappings_data.items():
                control_type = MIDIControlType(data["control_type"])
                self.add_mapping(
                    control_number=data["control_number"],
                    control_type=control_type,
                    function_name=data["function_name"],
                    min_value=data["min_value"],
                    max_value=data["max_value"],
                    channel=data["channel"]
                )
            
            return True
        except Exception as e:
            print(f"Error loading mappings: {e}")
            return False


# Mock MIDI Controller for testing without hardware
class MockMIDIController(MIDIController):
    """Mock MIDI controller for testing"""
    
    def connect(self, device_name: Optional[str] = None) -> bool:
        """Mock connection"""
        self.connected = True
        self.device_name = device_name or "Mock MIDI Device"
        print(f"[MOCK] Connected to MIDI device: {self.device_name}")
        return True
    
    def disconnect(self) -> None:
        """Mock disconnection"""
        self.connected = False
        print("[MOCK] MIDI device disconnected")
    
    def get_available_devices(self) -> List[str]:
        """Mock device list"""
        return [
            "Mock DJ Controller 1",
            "Mock DJ Controller 2",
            "Virtual MIDI Device"
        ]
    
    def simulate_control_change(self, control_number: int, value: int) -> None:
        """Simulate a MIDI control change for testing"""
        print(f"[MOCK] MIDI CC {control_number}: {value}")
        
        # Create mock message object
        class MockMessage:
            def __init__(self, control, value):
                self.control = control
                self.value = value
        
        message = MockMessage(control_number, value)
        self.process_message(message)
    
    def simulate_note(self, note_number: int, velocity: int) -> None:
        """Simulate a MIDI note event for testing"""
        print(f"[MOCK] MIDI Note {note_number}: {velocity}")
        
        # Create mock message object
        class MockMessage:
            def __init__(self, note, velocity):
                self.note = note
                self.velocity = velocity
        
        message = MockMessage(note_number, velocity)
        self.process_message(message)
