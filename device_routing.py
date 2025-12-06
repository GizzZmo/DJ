#!/usr/bin/env python3
"""
Advanced Device Routing for DJ Mixer
Provides PyAudio integration for better device control and routing
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class AudioDevice:
    """Information about an audio device"""
    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float
    host_api: str
    is_default_input: bool = False
    is_default_output: bool = False


@dataclass
class DeviceRoute:
    """Audio routing configuration"""
    source: str  # 'deck1', 'deck2', 'master', etc.
    device_index: int
    channels: List[int]  # Output channel indices
    enabled: bool = True


class AudioDeviceManager:
    """Manages audio devices and routing using PyAudio"""
    
    def __init__(self):
        self.pyaudio_instance = None
        self.available_devices: List[AudioDevice] = []
        self.routes: Dict[str, DeviceRoute] = {}
        self.initialized = False
        self.use_mock = False
    
    def initialize(self, use_mock: bool = False) -> bool:
        """Initialize PyAudio and enumerate devices"""
        self.use_mock = use_mock
        
        if use_mock:
            return self._initialize_mock()
        
        try:
            import pyaudio
            self.pyaudio_instance = pyaudio.PyAudio()
            self._enumerate_devices()
            self.initialized = True
            return True
        except ImportError:
            print("PyAudio not available. Install with: pip install pyaudio")
            print("Falling back to mock mode...")
            return self._initialize_mock()
        except Exception as e:
            print(f"Error initializing PyAudio: {e}")
            print("Falling back to mock mode...")
            return self._initialize_mock()
    
    def _initialize_mock(self) -> bool:
        """Initialize with mock devices for testing"""
        self.use_mock = True
        self.available_devices = [
            AudioDevice(
                index=0,
                name="Built-in Output (Mock)",
                max_input_channels=0,
                max_output_channels=2,
                default_sample_rate=44100.0,
                host_api="Core Audio (Mock)",
                is_default_output=True
            ),
            AudioDevice(
                index=1,
                name="USB Audio Interface (Mock)",
                max_input_channels=2,
                max_output_channels=8,
                default_sample_rate=48000.0,
                host_api="ASIO (Mock)"
            ),
            AudioDevice(
                index=2,
                name="DJ Controller Output 1-2 (Mock)",
                max_input_channels=0,
                max_output_channels=2,
                default_sample_rate=44100.0,
                host_api="ASIO (Mock)"
            ),
            AudioDevice(
                index=3,
                name="DJ Controller Output 3-4 (Mock)",
                max_input_channels=0,
                max_output_channels=2,
                default_sample_rate=44100.0,
                host_api="ASIO (Mock)"
            ),
            AudioDevice(
                index=4,
                name="Headphones Output (Mock)",
                max_input_channels=0,
                max_output_channels=2,
                default_sample_rate=44100.0,
                host_api="Core Audio (Mock)"
            )
        ]
        self.initialized = True
        print("[MOCK] Audio devices initialized")
        return True
    
    def _enumerate_devices(self) -> None:
        """Enumerate available audio devices"""
        if not self.pyaudio_instance:
            return
        
        import pyaudio
        
        self.available_devices = []
        device_count = self.pyaudio_instance.get_device_count()
        
        default_input = self.pyaudio_instance.get_default_input_device_info()
        default_output = self.pyaudio_instance.get_default_output_device_info()
        
        for i in range(device_count):
            try:
                info = self.pyaudio_instance.get_device_info_by_index(i)
                
                # Get host API name
                host_api_info = self.pyaudio_instance.get_host_api_info_by_index(
                    info['hostApi']
                )
                
                device = AudioDevice(
                    index=i,
                    name=info['name'],
                    max_input_channels=info['maxInputChannels'],
                    max_output_channels=info['maxOutputChannels'],
                    default_sample_rate=info['defaultSampleRate'],
                    host_api=host_api_info['name'],
                    is_default_input=(i == default_input['index']),
                    is_default_output=(i == default_output['index'])
                )
                
                self.available_devices.append(device)
            except Exception as e:
                print(f"Error getting device {i}: {e}")
    
    def get_devices(self, output_only: bool = True) -> List[AudioDevice]:
        """Get list of available audio devices"""
        if output_only:
            return [d for d in self.available_devices if d.max_output_channels > 0]
        return self.available_devices
    
    def get_device_by_index(self, index: int) -> Optional[AudioDevice]:
        """Get device by index"""
        for device in self.available_devices:
            if device.index == index:
                return device
        return None
    
    def get_device_by_name(self, name: str) -> Optional[AudioDevice]:
        """Get device by name (partial match)"""
        name_lower = name.lower()
        for device in self.available_devices:
            if name_lower in device.name.lower():
                return device
        return None
    
    def get_default_output_device(self) -> Optional[AudioDevice]:
        """Get default output device"""
        for device in self.available_devices:
            if device.is_default_output:
                return device
        return None
    
    def add_route(self, source: str, device_index: int, 
                 channels: Optional[List[int]] = None) -> bool:
        """Add an audio route"""
        device = self.get_device_by_index(device_index)
        if not device:
            return False
        
        if channels is None:
            # Default to first stereo pair
            channels = [0, 1]
        
        # Validate channels
        if max(channels) >= device.max_output_channels:
            print(f"Channel {max(channels)} not available on device {device.name}")
            return False
        
        route = DeviceRoute(
            source=source,
            device_index=device_index,
            channels=channels,
            enabled=True
        )
        
        self.routes[source] = route
        
        if self.use_mock:
            print(f"[MOCK] Route added: {source} -> {device.name} (channels {channels})")
        
        return True
    
    def remove_route(self, source: str) -> bool:
        """Remove an audio route"""
        if source in self.routes:
            del self.routes[source]
            if self.use_mock:
                print(f"[MOCK] Route removed: {source}")
            return True
        return False
    
    def enable_route(self, source: str, enabled: bool = True) -> bool:
        """Enable or disable a route"""
        if source in self.routes:
            self.routes[source].enabled = enabled
            if self.use_mock:
                status = "enabled" if enabled else "disabled"
                print(f"[MOCK] Route {source}: {status}")
            return True
        return False
    
    def get_route(self, source: str) -> Optional[DeviceRoute]:
        """Get route for a source"""
        return self.routes.get(source)
    
    def get_all_routes(self) -> Dict[str, DeviceRoute]:
        """Get all configured routes"""
        return self.routes.copy()
    
    def setup_default_routing(self) -> bool:
        """Setup default routing configuration"""
        default_device = self.get_default_output_device()
        if not default_device:
            return False
        
        # Route master to default output
        self.add_route("master", default_device.index, [0, 1])
        
        if self.use_mock:
            print("[MOCK] Default routing configured")
        
        return True
    
    def setup_dj_routing(self) -> bool:
        """
        Setup typical DJ routing:
        - Master to main outputs
        - Headphone cue to separate output
        """
        devices = self.get_devices()
        
        if len(devices) < 2:
            print("Not enough output devices for DJ routing")
            return self.setup_default_routing()
        
        # Find suitable devices
        main_device = self.get_default_output_device()
        headphone_device = None
        
        # Look for headphone or secondary output
        for device in devices:
            if 'headphone' in device.name.lower() or device.index != main_device.index:
                headphone_device = device
                break
        
        if not headphone_device:
            headphone_device = devices[1] if len(devices) > 1 else main_device
        
        # Setup routes
        self.add_route("master", main_device.index, [0, 1])
        self.add_route("headphone_cue", headphone_device.index, [0, 1])
        
        if self.use_mock:
            print(f"[MOCK] DJ routing configured:")
            print(f"  Master -> {main_device.name}")
            print(f"  Headphones -> {headphone_device.name}")
        
        return True
    
    def setup_multi_zone_routing(self) -> bool:
        """
        Setup multi-zone routing:
        - Zone 1 (Main): Master output
        - Zone 2: Deck 1 only
        - Zone 3: Deck 2 only
        """
        devices = self.get_devices()
        
        if len(devices) < 3:
            print("Not enough devices for multi-zone routing")
            return self.setup_dj_routing()
        
        # Use first 3 available devices
        self.add_route("master", devices[0].index, [0, 1])
        self.add_route("zone2_deck1", devices[1].index, [0, 1])
        self.add_route("zone3_deck2", devices[2].index, [0, 1])
        
        if self.use_mock:
            print("[MOCK] Multi-zone routing configured:")
            print(f"  Zone 1 (Master) -> {devices[0].name}")
            print(f"  Zone 2 (Deck 1) -> {devices[1].name}")
            print(f"  Zone 3 (Deck 2) -> {devices[2].name}")
        
        return True
    
    def get_asio_devices(self) -> List[AudioDevice]:
        """Get ASIO-compatible devices"""
        return [d for d in self.available_devices if 'ASIO' in d.host_api.upper()]
    
    def get_routing_info(self) -> dict:
        """Get routing configuration information"""
        info = {
            "initialized": self.initialized,
            "mock_mode": self.use_mock,
            "device_count": len(self.available_devices),
            "route_count": len(self.routes),
            "devices": [],
            "routes": []
        }
        
        # Add device info
        for device in self.available_devices:
            info["devices"].append({
                "index": device.index,
                "name": device.name,
                "channels": device.max_output_channels,
                "sample_rate": device.default_sample_rate,
                "host_api": device.host_api,
                "default": device.is_default_output
            })
        
        # Add route info
        for source, route in self.routes.items():
            device = self.get_device_by_index(route.device_index)
            info["routes"].append({
                "source": source,
                "device": device.name if device else "Unknown",
                "channels": route.channels,
                "enabled": route.enabled
            })
        
        return info
    
    def cleanup(self) -> None:
        """Cleanup PyAudio resources"""
        if self.pyaudio_instance and not self.use_mock:
            try:
                self.pyaudio_instance.terminate()
            except:
                pass
        
        self.pyaudio_instance = None
        self.initialized = False
        
        if self.use_mock:
            print("[MOCK] Audio device manager cleaned up")


def demo_device_routing():
    """Demo device routing functionality"""
    print("=" * 60)
    print("Audio Device Routing Demo")
    print("=" * 60)
    
    # Initialize device manager (mock mode)
    manager = AudioDeviceManager()
    if not manager.initialize(use_mock=True):
        print("Failed to initialize device manager")
        return
    
    print("\n--- Available Devices ---")
    devices = manager.get_devices()
    for device in devices:
        default_marker = " [DEFAULT]" if device.is_default_output else ""
        print(f"{device.index}: {device.name} ({device.max_output_channels} ch){default_marker}")
        print(f"    Host API: {device.host_api}, SR: {device.default_sample_rate} Hz")
    
    # Show ASIO devices
    print("\n--- ASIO Devices ---")
    asio_devices = manager.get_asio_devices()
    for device in asio_devices:
        print(f"{device.index}: {device.name} ({device.max_output_channels} ch)")
    
    # Setup default routing
    print("\n--- Setting Up Default Routing ---")
    manager.setup_default_routing()
    
    # Setup DJ routing
    print("\n--- Setting Up DJ Routing ---")
    manager.setup_dj_routing()
    
    # Setup multi-zone routing
    print("\n--- Setting Up Multi-Zone Routing ---")
    manager.setup_multi_zone_routing()
    
    # Show routing info
    print("\n--- Routing Configuration ---")
    info = manager.get_routing_info()
    print(f"Devices: {info['device_count']}")
    print(f"Routes: {info['route_count']}")
    print(f"Mock Mode: {info['mock_mode']}")
    
    print("\nConfigured Routes:")
    for route in info['routes']:
        status = "✓" if route['enabled'] else "✗"
        print(f"  {status} {route['source']} -> {route['device']} (ch {route['channels']})")
    
    # Cleanup
    manager.cleanup()
    print("\n✓ Device routing demo complete")


if __name__ == "__main__":
    demo_device_routing()
