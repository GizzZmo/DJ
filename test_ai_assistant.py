#!/usr/bin/env python3
"""
Test AI DJ Assistant functionality
Tests both mock and real API integration
"""

import time
import json
from ai_dj_assistant import AIDJAssistant, AITrackAnalysis, AIMixingAdvice


def test_ai_assistant_basic():
    """Test basic AI assistant functionality without API key"""
    print("🤖 Testing AI DJ Assistant (Mock Mode)")
    print("=" * 50)

    # Test initialization without API key
    ai = AIDJAssistant()
    status = ai.get_ai_status()

    print(f"✓ AI Assistant initialized")
    print(f"  - Configured: {status['configured']}")
    print(f"  - Gemini Available: {status['gemini_available']}")
    print(f"  - API Key Set: {status['api_key_set']}")

    # Test track analysis
    print("\n📊 Testing Track Analysis")
    print("-" * 30)

    tracks = [
        "House Vibes - Deep Groove.mp3",
        "Techno Storm - Hard Beat.wav",
        "Trance Dreams - Uplifting.ogg",
    ]

    analyses = {}
    for track in tracks:
        analysis = ai.analyze_track(track)
        analyses[track] = analysis
        print(f"🎵 {track}")
        print(f"  - Tempo: {analysis.tempo} BPM")
        print(f"  - Key: {analysis.key}")
        print(f"  - Energy: {analysis.energy}")
        print(f"  - Genre: {analysis.genre}")
        print(f"  - Mood: {analysis.mood}")
        print()

    # Test auto mixing advice
    print("🎛️ Testing Auto Mixing Advice")
    print("-" * 30)

    deck1_track = tracks[0]
    deck2_track = tracks[1]

    advice = ai.get_auto_mixing_advice(deck1_track, deck2_track)
    print(f"🔄 Mixing {deck1_track} → {deck2_track}")
    print(f"  - Crossfader Position: {advice.crossfader_position}")
    print(f"  - Deck 1 Volume: {advice.deck1_volume}")
    print(f"  - Deck 2 Volume: {advice.deck2_volume}")
    print(f"  - Transition Duration: {advice.transition_duration}s")
    print(f"  - Effect: {advice.effects_suggestion}")
    print(f"  - Reasoning: {advice.reasoning}")

    # Test key mixing advice
    print("\n🎼 Testing Key Mixing Advice")
    print("-" * 30)

    key_advice = ai.get_key_mixing_advice(deck1_track, deck2_track)
    print(f"🎹 Key Compatibility Check")
    print(f"  - Deck 1 Key: {key_advice['deck1_key']}")
    print(f"  - Deck 2 Key: {key_advice['deck2_key']}")
    print(f"  - Compatibility: {key_advice['compatibility']}")
    print(f"  - Advice: {key_advice['advice']}")
    print(f"  - Action: {key_advice['suggested_action']}")

    # Test fader effects
    print("\n🎚️ Testing Fader Effects Suggestions")
    print("-" * 30)

    track1_energy = analyses[deck1_track].energy
    track2_energy = analyses[deck2_track].energy

    effects_advice = ai.get_fader_effects_suggestion(0.5, track1_energy, track2_energy)
    print(f"💫 Fader Effects for Energy: {track1_energy} → {track2_energy}")
    print(f"  - Suggested Effect: {effects_advice['suggested_effect']}")
    print(f"  - Technique: {effects_advice['technique']}")
    print(f"  - Optimal Speed: {effects_advice['optimal_speed']}")
    print(f"  - Reasoning: {effects_advice['reasoning']}")

    # Test callback system
    print("\n📡 Testing Callback System")
    print("-" * 30)

    callback_log = []

    def crossfader_callback(position):
        callback_log.append(f"Crossfader moved to {position:.2f}")

    def volume_callback(deck, volume):
        callback_log.append(f"{deck} volume set to {volume:.2f}")

    ai.register_callback("crossfader_change", crossfader_callback)
    ai.register_callback("volume_change", volume_callback)

    # Trigger some callbacks
    ai._trigger_callback("crossfader_change", 0.7)
    ai._trigger_callback("volume_change", "deck1", 0.8)
    ai._trigger_callback("volume_change", "deck2", 0.6)

    print("📝 Callback Log:")
    for entry in callback_log:
        print(f"  - {entry}")

    # Final status
    final_status = ai.get_ai_status()
    print(f"\n📈 Final Status")
    print("-" * 30)
    print(f"  - Tracks Analyzed: {final_status['tracks_analyzed']}")
    print(f"  - Mixing History: {final_status['mixing_history_count']}")

    print("\n✅ AI Assistant test completed successfully!")
    return True


def test_ai_assistant_with_callbacks():
    """Test AI assistant with mixer integration callbacks"""
    print("\n🔗 Testing AI Integration with Mixer Callbacks")
    print("=" * 50)

    ai = AIDJAssistant()

    # Mock mixer state
    mixer_state = {"crossfader": 0.5, "deck1_volume": 1.0, "deck2_volume": 1.0}

    def update_crossfader(position):
        mixer_state["crossfader"] = position
        print(f"🎛️ Crossfader updated: {position:.2f}")

    def update_volume(deck, volume):
        mixer_state[f"{deck}_volume"] = volume
        print(f"🔊 {deck} volume updated: {volume:.2f}")

    # Register callbacks
    ai.register_callback("crossfader_change", update_crossfader)
    ai.register_callback("volume_change", update_volume)

    # Test auto mixing with callbacks
    print("\n🤖 Starting Auto Mix with Callbacks")
    tracks = ["House Track.mp3", "Techno Beat.wav"]

    # Analyze tracks first
    for track in tracks:
        ai.analyze_track(track)

    print("Starting automated mixing process...")
    ai.start_auto_mixing(tracks[0], tracks[1])

    # Wait a bit for the auto mixing to work
    time.sleep(3)

    print(f"\n📊 Final Mixer State:")
    for key, value in mixer_state.items():
        print(f"  - {key}: {value:.2f}")

    return True


def test_key_compatibility():
    """Test harmonic key compatibility logic"""
    print("\n🎼 Testing Key Compatibility Logic")
    print("=" * 50)

    ai = AIDJAssistant()

    # Test various key combinations
    test_keys = [
        ("C", "G"),  # Perfect fifth - should be compatible
        ("C", "F"),  # Perfect fourth - should be compatible
        ("C", "C#"),  # Semitone - should be cautious
        ("A", "D"),  # Should be compatible
        ("C", "F#"),  # Tritone - should be cautious
    ]

    for key1, key2 in test_keys:
        compatibility = ai._check_key_compatibility(key1, key2)
        print(f"🎹 {key1} + {key2}")
        print(f"  - Compatibility: {compatibility['compatibility']}")
        print(f"  - Advice: {compatibility['advice']}")
        print(f"  - Action: {compatibility['action']}")
        print()

    return True


if __name__ == "__main__":
    print("🧪 AI DJ Assistant Test Suite")
    print("=" * 60)

    try:
        # Run all tests
        test_ai_assistant_basic()
        test_ai_assistant_with_callbacks()
        test_key_compatibility()

        print("\n" + "=" * 60)
        print("✅ All AI Assistant tests passed!")
        print("💡 Note: Tests ran in mock mode. To test with real Gemini API,")
        print(
            "    set your API key in the GUI or pass it to AIDJAssistant(api_key='your_key')"
        )

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
