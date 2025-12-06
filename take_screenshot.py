#!/usr/bin/env python3
"""
Screenshot utility for the DJ GUI
"""

import tkinter as tk
import subprocess
import time
from dj_gui import DJMixerGUI


def take_screenshot():
    """Take a screenshot of the GUI"""
    try:
        # Create and run the GUI briefly
        app = DJMixerGUI()
        app.root.update()

        # Position and configure window
        app.root.geometry("900x700+50+50")
        app.root.update()

        # Take screenshot using import command
        time.sleep(1)
        subprocess.run(
            ["import", "-window", "root", "/home/runner/work/DJ/DJ/gui_screenshot.png"],
            env={"DISPLAY": ":99"},
            check=True,
        )

        print("Screenshot saved as gui_screenshot.png")

        # Close the GUI
        app.root.destroy()

    except Exception as e:
        print(f"Screenshot failed: {e}")


if __name__ == "__main__":
    take_screenshot()
