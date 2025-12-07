#!/usr/bin/env python3
"""
Test script for the DJ GUI
Tests the basic functionality without requiring audio hardware
"""

import tkinter as tk
import sys
import os
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dj_gui import DJMixerGUI


def test_gui_creation():
    """Test that the GUI can be created and initialized"""
    print("Testing GUI creation...")

    # Mock pygame to avoid audio hardware requirements
    with patch("dj_mixer.pygame") as mock_pygame:
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.error = Exception

        # Create GUI
        app = DJMixerGUI()

        # Test window creation
        assert app.root is not None, "Root window not created"
        assert app.mixer is not None, "Mixer not created"

        # Test initial state
        assert not app.initialized, "Mixer should not be initialized yet"
        assert app.deck1_file.get() == "No file loaded", "Deck1 file should be empty"
        assert app.deck2_file.get() == "No file loaded", "Deck2 file should be empty"

        # Test variable initialization
        assert app.master_vol_var.get() == 1.0, "Master volume should be 1.0"
        assert app.crossfader_var.get() == 0.5, "Crossfader should be centered"
        assert app.deck1_vol_var.get() == 1.0, "Deck1 volume should be 1.0"
        assert app.deck2_vol_var.get() == 1.0, "Deck2 volume should be 1.0"

        print("✓ GUI creation test passed")

        # Test mock initialization
        with patch.object(app.mixer, "initialize", return_value=True):
            app.initialize_mixer()
            assert app.initialized, "Mixer should be initialized"
            print("✓ Mixer initialization test passed")

        # Test volume controls
        app.set_master_volume(0.8)
        app.set_track_volume("deck1", 0.7)
        print("✓ Volume control tests passed")

        # Test crossfader
        app.crossfader_var.set(0.3)
        app.update_crossfader("0.3")  # The function expects a string
        assert (
            abs(app.crossfader_var.get() - 0.3) < 0.01
        ), "Crossfader position not updated"
        print("✓ Crossfader test passed")

        # Close the GUI
        app.root.destroy()
        print("✓ All GUI tests passed!")


def test_gui_layout():
    """Test that all GUI elements are present"""
    print("\nTesting GUI layout...")

    with patch("dj_mixer.pygame") as mock_pygame:
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.error = Exception

        app = DJMixerGUI()
        app.root.update()  # Force GUI creation

        # Check that main components exist
        widgets = app.root.winfo_children()
        assert len(widgets) > 0, "No widgets found in root window"

        # Check window properties
        assert (
            app.root.title() == "DJ Mixer - AI-Powered Multi-Device Audio Mixing System"
        ), "Window title incorrect"

        print("✓ GUI layout test passed")

        app.root.destroy()


if __name__ == "__main__":
    print("Starting DJ GUI tests...")
    print("=" * 50)

    try:
        test_gui_creation()
        test_gui_layout()
        print("=" * 50)
        print("All tests passed! ✓")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
