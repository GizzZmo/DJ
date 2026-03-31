#!/usr/bin/env python3
"""
Screenshot utility for the DJ GUI (requires `scrot`; install on Debian/Ubuntu with
`sudo apt-get install -y scrot`).
"""

from pathlib import Path
import subprocess
import time
import tkinter as tk

from dj_gui import DJMixerGUI


def take_screenshot():
    """Take a screenshot of the GUI using scrot (works with xvfb-run)."""
    app = None
    try:
        # Create and run the GUI briefly
        app = DJMixerGUI()
        app.root.update()

        # Position and configure window
        app.root.geometry("900x700+50+50")
        app.root.lift()
        app.root.focus_force()
        app.root.attributes("-topmost", True)
        app.root.update()

        # Take screenshot using scrot (works under xvfb-run)
        time.sleep(1)
        output_path = Path(__file__).parent / "gui_screenshot.png"
        subprocess.run(
            ["scrot", "--focused", str(output_path)],
            check=True,
        )

        print(f"Screenshot saved as {output_path.name}")

    except FileNotFoundError:
        print(
            "Screenshot failed: scrot not found. Install with "
            "`sudo apt-get install -y scrot`."
        )
    except Exception as e:
        print(f"Screenshot failed: {e}")
    finally:
        if app:
            try:
                app.root.destroy()
            except Exception:
                pass


if __name__ == "__main__":
    take_screenshot()
