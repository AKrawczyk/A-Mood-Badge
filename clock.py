from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB565
import pngdec
import time
from pimoroni import Button
import gc
import sys
import os
import json

# --- Settings file path ---
SETTINGS_FILE = "/settings.json"

# --- Default settings ---
DEFAULT_SETTINGS = {
    "brightness": 1.0,
    "text_overlay": True,
    "selected_image": "",
    "clock_image": True,
    "background_color": "Black"
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

# --- Display setup ---
display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB565)
WIDTH, HEIGHT = display.get_bounds()

# List of available pen colours, add more if necessary
RED = display.create_pen(209, 34, 41)
ORANGE = display.create_pen(246, 138, 30)
YELLOW = display.create_pen(255, 216, 0)
GREEN = display.create_pen(0, 121, 64)
INDIGO = display.create_pen(36, 64, 142)
VIOLET = display.create_pen(115, 41, 130)
WHITE = display.create_pen(255, 255, 255)
PINK = display.create_pen(255, 175, 200)
BLUE = display.create_pen(116, 215, 238)
BROWN = display.create_pen(97, 57, 21)
BLACK = display.create_pen(0, 0, 0)
MAGENTA = display.create_pen(255, 33, 140)
CYAN = display.create_pen(33, 177, 255)
AMETHYST = display.create_pen(156, 89, 209)
GREY = display.create_pen(200, 200, 200)

# Color name to pen mapping
COLOR_PENS = {
    "Black": BLACK,
    "White": WHITE,
    "Red": RED,
    "Orange": ORANGE,
    "Yellow": YELLOW,
    "Green": GREEN,
    "Blue": BLUE,
    "Indigo": INDIGO,
    "Violet": VIOLET,
    "Pink": PINK,
    "Cyan": CYAN,
    "Magenta": MAGENTA,
    "Amethyst": AMETHYST,
    "Grey": GREY
}

# --- Load current settings ---
settings = load_settings()
brightness = round(settings.get("brightness", 1.0), 1)
selected_image = settings.get("selected_image", "")
clock_image = settings.get("clock_image", True)
background_color_name = settings.get("background_color", "Black")
bg_colour = COLOR_PENS.get(background_color_name, BLACK)

# Set brightness
display.set_backlight(brightness)

# --- Clear background ---
display.set_pen(display.create_pen(0, 0, 0))  # Black
display.clear()

if clock_image:
    png = pngdec.PNG(display)

    # --- Try to display the image ---
    try:  
        png.open_file(f"/badge/{selected_image}")
        png.decode(0, 0)
        
    except Exception as e:
        print(f"Error loading image: {e}")
        print("Make sure 'jam.png' (320x240 baseline PNG) is on the device.")
        display.set_pen(bg_colour)
        display.rectangle(0, 0, WIDTH, HEIGHT)
else:
    display.set_pen(bg_colour)
    display.rectangle(0, 0, WIDTH, HEIGHT)

print(time.localtime())

last_second = None

#vector.set_transform(None)
button_a = Button(7, invert=False)

# --- Draw centered "bold" text overlay ---
try:
    display.set_font("sans")
except Exception:
    display.set_font("bitmap8")

while True:
    #t.reset()
    t_start = time.ticks_ms()
    year, month, day, hour, minute, second, _, _ = time.localtime()

    if last_second == second:
        continue

    last_second = second

    display.set_pen(0)
    display.clear()

    display.set_pen(GREY)

    text = f"{hour:02}:{minute:02}:{second:02}"
    text2 = f"{day:02}/{month:02}/{year:04}"
    scale = 2
    scale2 = 1

    # Measure text width to center it
    text_width = display.measure_text(text, scale)
    text_x = (WIDTH - 270) // 2
    text_y = HEIGHT - 160  # 40px from bottom
    
    # Measure text2 width to center it
    text2_width = display.measure_text(text2, scale2)
    text2_x = (WIDTH - 200) // 2
    text2_y = HEIGHT - 80  # 40px from bottom

    # Create pens
    WHITE = display.create_pen(255, 255, 255)
    BLACK = display.create_pen(0, 0, 0)

    # --- Try to display the image ---
    if clock_image:
        try:  
            png.open_file(f"/badge/{selected_image}")
            png.decode(0, 0)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            print("Make sure 'jam.png' (320x240 baseline PNG) is on the device.")
            display.set_pen(bg_colour)
            display.rectangle(0, 0, WIDTH, HEIGHT)
    else:
        display.set_pen(bg_colour)
        display.rectangle(0, 0, WIDTH, HEIGHT)
    
    # Optional: drop shadow for readability
    display.set_pen(BLACK)
    display.text(text2, text2_x + 1, text2_y + 1, scale=scale2)

    # Draw text2 multiple times for a bold effect
    display.set_pen(GREY)
    for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]:
        display.text(text2, text2_x + dx, text2_y + dy, scale=scale2)

    # Optional: drop shadow for readability
    display.set_pen(BLACK)
    display.text(text, text_x + 1, text_y + 1, scale=scale)

    # Draw text multiple times for a bold effect
    display.set_pen(GREY)
    for dx, dy in [(0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (-1, 0), (0, -1), (-2, 0), (0, -2)]:
        display.text(text, text_x + dx, text_y + dy, scale=scale)
    
    display.update()
    mem = gc.mem_free()
    gc.collect()
    used = gc.mem_free() - mem

    t_end = time.ticks_ms()
    #print(f"Took {t_end - t_start}ms, mem free: {gc.mem_free()} {used}")
    
    if button_a.read():
        # Wait for the button to be released
        while button_a.is_pressed:
            time.sleep(0.01)
        break  # Exit the loop after importing

# Alternative: If you want to completely restart, use machine.reset()
# Uncomment these lines instead of __import__("main"):
import machine
machine.reset()



