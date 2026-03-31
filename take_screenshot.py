#!/usr/bin/env python3
"""
Screenshot utility for the DJ GUI
"""

import tkinter as tk
import subprocess
import time
from pathlib import Path

from dj_gui import DJMixerGUI


def take_screenshot():
    """Take a screenshot of the GUI using scrot (works with xvfb-run)."""
    try:
        # Create and run the GUI briefly
        app = DJMixerGUI()
        app.root.update()

        # Position and configure window
        app.root.geometry("900x700+50+50")
        app.root.update()

        # Take screenshot using scrot (works under xvfb-run)
        time.sleep(1)
        output_path = Path(__file__).parent / "gui_screenshot.png"
        subprocess.run(
            ["scrot", str(output_path), "-q", "90"],
            check=True,
        )

        print(f"Screenshot saved as {output_path.name}")

        # Close the GUI
        app.root.destroy()

    except Exception as e:
        print(f"Screenshot failed: {e}")


if __name__ == "__main__":
    take_screenshot()
