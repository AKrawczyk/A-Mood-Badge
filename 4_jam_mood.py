# Jam mood displays image or text for Tufty 2040 badge

from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB565
import pngdec
import time
from pimoroni import Button
import gc
import sys
import os
import json

def prepare_for_launch() -> None:
    """Clean up before launching another module"""
    # Remove this module from sys.modules so it can be reloaded fresh next time
    if '5_jam_badge' in sys.modules:
        del sys.modules['5_jam_badge']
    
    # Collect garbage to free memory
    gc.collect()
    
# --- Settings file path ---
SETTINGS_FILE = "/settings.json"

# --- Default settings ---
DEFAULT_SETTINGS = {
    "brightness": 1.0,
    "text_overlay": True,
    "selected_image": ""
}
    
# --- Load settings from file ---
def load_settings():
    """Load settings from JSON file, return defaults if file doesn't exist"""
    try:
        # Check if file exists by trying to stat it
        try:
            os.stat(SETTINGS_FILE)
            # File exists, try to read it
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key in DEFAULT_SETTINGS:
                    if key not in settings:
                        settings[key] = DEFAULT_SETTINGS[key]
                return settings
        except OSError:
            # File doesn't exist, return defaults
            pass
    except Exception as e:
        print(f"Error loading settings: {e}")
    return DEFAULT_SETTINGS.copy()

# --- Load current settings ---
settings = load_settings()
brightness = round(settings.get("brightness", 1.0), 1)

# --- Display setup ---
display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB565) #332)
display.set_backlight(brightness)
WIDTH, HEIGHT = display.get_bounds()

# Create pens
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
GREY = display.create_pen(64, 64, 64)

# --- Clear background ---
display.set_pen(WHITE)
display.clear()

# --- Try to display the image ---
try:
    png = pngdec.PNG(display)
    png.open_file("jam.png")
    png.decode(0, 0)
    
except Exception as e:
    print(f"Error loading image: {e}")
    print("Make sure 'jam.png' (320x240 baseline PNG) is on the device.")
    display.set_pen(WHITE)
    display.rectangle(0, 0, WIDTH, HEIGHT)

    # --- Draw centered "bold" text overlay ---
    try:
        display.set_font("sans")
    except Exception:
        display.set_font("bitmap8")

    text = "JAM"
    text2 = "Just A Minute"
    scale = 1.3
    
    # Measure text width to center it
    text_width = display.measure_text(text, scale)
    text_x = (WIDTH - text_width) // 2
    text_y = HEIGHT - 160  # 40px from bottom

    # Optional: drop shadow for readability
    display.set_pen(BLACK)
    display.text(text, text_x + 1, text_y + 1, scale=scale)

    # Draw text multiple times for a bold effect
    display.set_pen(GREY)
    for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]:
        display.text(text, text_x + dx, text_y + dy, scale=scale)

    # Measure text width to center it
    text_width = display.measure_text(text2, scale)
    text_x = (WIDTH - text_width) // 2
    text_y = HEIGHT - 80  # 40px from bottom

    # Optional: drop shadow for readability
    display.set_pen(BLACK)
    display.text(text2, text_x + 1, text_y + 1, scale=scale)

    # Draw text multiple times for a bold effect
    display.set_pen(GREY)
    for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]:
        display.text(text2, text_x + dx, text_y + dy, scale=scale)

# --- Update display ---
display.update()
print("Display updated successfully!")
button_a = Button(7, invert=False)

while True:
    time.sleep(0.01)  # Small delay to prevent busy-waiting
    
    if button_a.read():
        # Wait for the button to be released
        while button_a.is_pressed:
            time.sleep(0.01)
        
        # Clean up this module
        prepare_for_launch()
        
        # Return to main menu (import without .py extension)
#         __import__("main")
        break  # Exit the loop after importing

# Alternative: If you want to completely restart, use machine.reset()
# Uncomment these lines instead of __import__("main"):
import machine
machine.reset()
