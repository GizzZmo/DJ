#!/usr/bin/env python3
"""
Demo of PyAudio with ASIO driver support in DJ Mixer
Demonstrates the new PyAudio integration and ASIO device selection
"""

from enhanced_mixer import EnhancedDJMixer


def demo_pyaudio_asio():
    """Demo PyAudio with ASIO support"""
    print("=" * 70)
    print("DJ Mixer - PyAudio with ASIO Driver Support Demo")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("1. Standard PyAudio Mode (Default Output)")
    print("=" * 70)

    # Create mixer with PyAudio
    mixer = EnhancedDJMixer(use_pyaudio=True, use_asio=False)

    if mixer.initialize():
        print("\n✓ Mixer initialized with PyAudio")

        # Show audio devices
        print("\n--- Available Audio Devices ---")
        devices = mixer.get_audio_devices()
        for device in devices:
            default_marker = " [DEFAULT]" if device.is_default_output else ""
            print(
                f"  {device.index}: {device.name} "
                f"({device.host_api}){default_marker}"
            )

        # Show mixer status
        print("\n--- Mixer Status ---")
        status = mixer.get_mixer_status()
        if "audio_device" in status:
            print(f"  Active Device: {status['audio_device']['name']}")
            print(f"  Host API: {status['audio_device']['host_api']}")
            print(
                f"  Sample Rate: {status['audio_device']['sample_rate']} Hz"
            )
            print(f"  Channels: {status['audio_device']['channels']}")

        # Test controls
        print("\n--- Testing Basic Controls ---")
        mixer.set_master_volume(0.8)
        print(f"  Master Volume: {mixer.get_master_volume()}")

        mixer.set_crossfader(0.5)
        print(f"  Crossfader: {mixer.get_crossfader()}")

        mixer.cleanup()
        print("\n✓ Standard PyAudio mode demo complete")

    print("\n" + "=" * 70)
    print("2. PyAudio with ASIO Mode")
    print("=" * 70)

    # Create mixer with ASIO preference
    mixer_asio = EnhancedDJMixer(use_pyaudio=True, use_asio=True)

    if mixer_asio.initialize():
        print("\n✓ Mixer initialized with ASIO preference")

        # Show ASIO devices specifically
        print("\n--- ASIO Devices ---")
        asio_devices = mixer_asio.get_asio_devices()
        if asio_devices:
            for device in asio_devices:
                print(
                    f"  {device.index}: {device.name} "
                    f"({device.max_output_channels} channels)"
                )
        else:
            print("  No ASIO devices found")

        # Show active device
        print("\n--- Active Audio Configuration ---")
        status = mixer_asio.get_mixer_status()
        if "audio_device" in status:
            print(f"  Device: {status['audio_device']['name']}")
            print(f"  Host API: {status['audio_device']['host_api']}")
            print(
                f"  Sample Rate: {status['audio_device']['sample_rate']} Hz"
            )
            print(f"  Channels: {status['audio_device']['channels']}")

            # Check if ASIO is being used
            if "ASIO" in status["audio_device"]["host_api"]:
                print("\n  ✓ Using ASIO driver for low-latency audio!")
            else:
                print("\n  ℹ ASIO device not available, using default")

        mixer_asio.cleanup()
        print("\n✓ ASIO mode demo complete")

    print("\n" + "=" * 70)
    print("3. Comparison: pygame vs PyAudio Mode")
    print("=" * 70)

    print("\n--- pygame Mode (Original) ---")
    mixer_pygame = EnhancedDJMixer(use_pyaudio=False)
    # Don't initialize pygame in demo, just show config
    print(f"  use_pyaudio: {mixer_pygame.use_pyaudio}")
    print(f"  use_asio: {mixer_pygame.use_asio}")
    print("  ✓ pygame provides simple audio playback")
    print("  ✓ Good for basic DJ functionality")
    print("  ℹ Limited device control and routing")

    print("\n--- PyAudio Mode (New) ---")
    mixer_pyaudio = EnhancedDJMixer(use_pyaudio=True)
    mixer_pyaudio.initialize()
    print(f"  use_pyaudio: {mixer_pyaudio.use_pyaudio}")
    print(f"  use_asio: {mixer_pyaudio.use_asio}")
    print("  ✓ Full control over audio devices")
    print("  ✓ ASIO support for professional interfaces")
    print("  ✓ Lower latency with ASIO drivers")
    print("  ✓ Better multi-device routing")
    mixer_pyaudio.cleanup()

    print("\n" + "=" * 70)
    print("Key Benefits of PyAudio with ASIO")
    print("=" * 70)
    print("""
  1. Professional Audio Interfaces
     - Support for ASIO drivers
     - Low-latency audio processing
     - Direct hardware access

  2. Device Control
     - Select specific output devices
     - Route different decks to different outputs
     - Support for multi-channel interfaces

  3. Flexibility
     - Works with any audio interface
     - Automatic fallback to standard drivers
     - Compatible with existing pygame mode

  4. Performance
     - Reduced audio latency with ASIO
     - Real-time audio processing
     - Professional DJ setups
""")

    print("=" * 70)
    print("Usage Examples")
    print("=" * 70)
    print("""
  # Use PyAudio with default output
  mixer = EnhancedDJMixer(use_pyaudio=True)
  mixer.initialize()

  # Use PyAudio with ASIO preference
  mixer = EnhancedDJMixer(use_pyaudio=True, use_asio=True)
  mixer.initialize()

  # Use specific device by index
  mixer = EnhancedDJMixer(use_pyaudio=True)
  mixer.initialize(device_index=2)

  # List ASIO devices
  asio_devices = mixer.get_asio_devices()
  for device in asio_devices:
      print(f"{device.name} - {device.host_api}")
""")

    print("\n" + "=" * 70)
    print("✓ PyAudio/ASIO Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    demo_pyaudio_asio()
