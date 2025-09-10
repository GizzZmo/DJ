#!/usr/bin/env python3
"""
Take a screenshot of the new AI-powered DJ GUI
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_virtual_display():
    """Setup virtual display for GUI screenshot"""
    try:
        # Start Xvfb virtual display
        subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1400x900x24'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Give it time to start
        
        # Set DISPLAY environment variable
        os.environ['DISPLAY'] = ':99'
        return True
    except Exception as e:
        print(f"Failed to setup virtual display: {e}")
        return False

def create_gui_screenshot():
    """Create and screenshot the GUI"""
    try:
        # Import GUI after setting up display
        from dj_gui import DJMixerGUI
        import tkinter as tk
        
        # Create the GUI application
        app = DJMixerGUI()
        
        # Configure the AI section with demo content
        app.gemini_api_key.set("sk-demo-key-for-screenshot-purposes")
        app.ai_status_var.set("AI: Ready for demo ✓")
        app.update_ai_info("""🤖 AI-Powered DJ Assistant Ready!

✨ Features Available:
• Auto mixing with intelligent transitions
• Harmonic key analysis and mixing advice  
• Smart fader effects based on track energy
• Real-time AI decision making

💡 Enter your Gemini API key above and click 'Configure AI' to enable full AI features. The assistant works in mock mode for testing without an API key.""")
        
        # Update window title and add demo indicator
        app.root.title("🤖 AI-Powered DJ Mixer - Demo Mode")
        
        # Schedule screenshot after GUI renders
        def take_screenshot():
            time.sleep(1)  # Let GUI fully render
            try:
                # Use scrot to take screenshot
                subprocess.run(['scrot', 'ai_gui_demo.png', '-q', '95'], 
                             check=True, cwd='/home/runner/work/DJ/DJ')
                print("✅ Screenshot saved as ai_gui_demo.png")
            except Exception as e:
                print(f"Screenshot failed: {e}")
            finally:
                app.root.quit()
        
        # Schedule screenshot and start GUI
        app.root.after(2000, take_screenshot)  # Take screenshot after 2 seconds
        app.root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"Failed to create GUI screenshot: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("📸 Taking screenshot of AI-powered DJ GUI...")
    
    # Install scrot for screenshots
    try:
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'scrot'], 
                      check=True, stdout=subprocess.DEVNULL)
    except Exception:
        print("Failed to install scrot")
    
    if setup_virtual_display():
        print("✅ Virtual display setup complete")
        if create_gui_screenshot():
            print("✅ GUI screenshot process completed")
        else:
            print("❌ Failed to create screenshot")
    else:
        print("❌ Failed to setup virtual display")

if __name__ == "__main__":
    main()