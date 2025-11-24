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
    "badge_image": True,
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

# --- Settings file path ---
BADGE_TEXT_FILE = "/badge_text.json"

# --- Default settings ---
DEFAULT_BADGE_TEXT = {
    "line_1": "Name",
    "line_2": "Descriptor"
}

# --- Load settings from file ---
def load_badge_text():
    """Load settings from JSON file, return defaults if file doesn't exist"""
    try:
        # Check if file exists by trying to stat it
        try:
            os.stat(BADGE_TEXT_FILE)
            # File exists, try to read it
            with open(BADGE_TEXT_FILE, 'r') as f:
                badge_text = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key in DEFAULT_BADGE_TEXT:
                    print(key)
                    if key not in badge_text:
                        print("no key")
                        badge_text[key] = DEFAULT_BADGE_TEXT[key]
                return badge_text
        except OSError:
            # File doesn't exist, return defaults
            pass
    except Exception as e:
        print(f"Error loading settings: {e}")
    return DEFAULT_BADGE_TEXT.copy()

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
text_overlay = settings.get("text_overlay", True)
selected_image = settings.get("selected_image", "")
badge_image = settings.get("badge_image", True)
background_color_name = settings.get("background_color", "Black")
bg_colour = COLOR_PENS.get(background_color_name, BLACK)

# --- Load current badge_text ---
badge_text = load_badge_text()
LINE1 = badge_text.get("line_1", "Name")
LINE2 = badge_text.get("line_2", "Discriptor")

display.set_backlight(brightness)

# --- Clear background ---
display.set_pen(display.create_pen(0, 0, 0))  # Black
display.clear()

# --- Text overlay setup ---
try:
    display.set_font("sans")
except Exception:
    display.set_font("bitmap8")

# Change the colour of the text (swapping these works better on a light background)
TEXT_COLOUR = WHITE
DROP_SHADOW_COLOUR = GREY
DROP_SHADOW_COLOUR_2 = BLACK


def draw_text_overlay() -> None:
    if not LINE1 and not LINE2:
        return

    # Set a starting scale for text size.
    # This is intentionally bigger than will fit on the screen, we'll shrink it to fit.
    name_size = 20
    pronouns_size = 20

    # These loops adjust the scale of the text until it fits on the screen
    while True:
        # Load the PCF font
        try:
            display.set_font("sans")
        except Exception as e:
            print(f"Error loading font: {e}")
            print("Using default font instead")
            display.set_font("bitmap8")  # Fallback to built-in font
    #    display.set_font("bitmap8")
        name_length = display.measure_text(LINE1, name_size)
        if name_length >= WIDTH - 20:
            name_size -= 1
        else:
            # comment out this section if you hate drop shadow
            DROP_SHADOW_OFFSET = 1
            display.set_pen(DROP_SHADOW_COLOUR)
            display.text(LINE1, int((WIDTH - name_length) / 2) - DROP_SHADOW_OFFSET, 78 + DROP_SHADOW_OFFSET, WIDTH, name_size)
            
            # comment out this section if you hate drop shadow
            DROP_SHADOW_OFFSET = 1
            display.set_pen(DROP_SHADOW_COLOUR_2)
            display.text(LINE1, int((WIDTH - name_length) / 2) - DROP_SHADOW_OFFSET, 82 + DROP_SHADOW_OFFSET, WIDTH, name_size)

            # draw name and stop looping
            display.set_pen(TEXT_COLOUR)
            display.text(LINE1, int((WIDTH - name_length) / 2), 80, WIDTH, name_size)
            
            break

    while True:
        # Load the PCF font
        try:
            display.set_font("serif")
        except Exception as e:
            print(f"Error loading font: {e}")
            print("Using default font instead")
            display.set_font("bitmap8")  # Fallback to built-in font
    #    display.set_font("bitmap8")
        pronouns_length = display.measure_text(LINE2, pronouns_size)
        if pronouns_length >= WIDTH - 60:
            pronouns_size -= 1
        else:
            # comment out this section if you hate drop shadow
            DROP_SHADOW_OFFSET = 1
            display.set_pen(DROP_SHADOW_COLOUR)
            display.text(LINE2, int((WIDTH - pronouns_length) / 2) - DROP_SHADOW_OFFSET, 173 + DROP_SHADOW_OFFSET, WIDTH, pronouns_size)
            
            # comment out this section if you hate drop shadow
            DROP_SHADOW_OFFSET = 1
            display.set_pen(DROP_SHADOW_COLOUR_2)
            display.text(LINE2, int((WIDTH - pronouns_length) / 2) - DROP_SHADOW_OFFSET, 177 + DROP_SHADOW_OFFSET, WIDTH, pronouns_size)
            
            # draw pronouns and stop looping
            display.set_pen(TEXT_COLOUR)
            display.text(LINE2, int((WIDTH - pronouns_length) / 2), 175, WIDTH, pronouns_size)
            break


# --- Image helpers ---
def list_png_files(directory: str) -> list[str]:
    try:
        files = [f for f in os.listdir(directory) if f.lower().endswith(".png")]
        files.sort()
        return files
    except Exception as e:
        print(f"Error listing PNG files in '{directory}': {e}")
        return []


def show_image(path: str, draw_overlay: bool) -> None:
    # --- Clear background ---
    display.set_pen(display.create_pen(0, 0, 0))  # Black
    display.clear()

    try:
        png.open_file(path)
        png.decode(0, 0)
        print(f"Displayed '{path}'")
    except Exception as e:
        print(f"Error loading image '{path}': {e}")
        display.set_pen(GREEN)
        display.rectangle(0, 0, WIDTH, HEIGHT)

    if draw_overlay:
        draw_text_overlay()

    display.update()

if badge_image:
    png = pngdec.PNG(display)
    image_files = list_png_files("/badge")
    current_index = image_files.index(selected_image) if selected_image in image_files else -1
    #current_index = 0 if image_files else -1
    show_overlay = text_overlay

    if current_index >= 0:
        show_image(f"/badge/{image_files[current_index]}", show_overlay)
    else:
        display.set_pen(display.create_pen(200, 0, 0))
        display.text("No PNG files in /badge", 10, HEIGHT // 2, scale=2)
        display.update()
else:
    display.set_pen(bg_colour)
    display.rectangle(0, 0, WIDTH, HEIGHT)
    if text_overlay:
        draw_text_overlay()

    display.update()

button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)

while True:
    time.sleep(0.01)  # Small delay to prevent busy-waiting
    
    if button_a.read():
        # Wait for the button to be released
        while button_a.is_pressed:
            time.sleep(0.01)
        break  # Exit the loop after importing
    
    if badge_image:
        if button_up.read() and current_index >= 0 and image_files:
            while button_up.is_pressed:
                time.sleep(0.01)
            current_index = (current_index - 1) % len(image_files)
            show_image(f"/badge/{image_files[current_index]}", show_overlay)
                
        if button_down.read() and current_index >= 0 and image_files:
            while button_down.is_pressed:
                time.sleep(0.01)
            current_index = (current_index + 1) % len(image_files)
            show_image(f"/badge/{image_files[current_index]}", show_overlay)

        if button_b.read():
            while button_b.is_pressed:
                time.sleep(0.01)
            show_overlay = not show_overlay
            if current_index >= 0:
                show_image(f"/badge/{image_files[current_index]}", show_overlay)
    else:                                                                                                                                                                                                                                                                            
        if button_b.read():
            while button_b.is_pressed:
                time.sleep(0.01)
            text_overlay = not text_overlay
            if text_overlay:
                draw_text_overlay()
            else:
                display.set_pen(bg_colour)                                 
                display.clear() 
            display.update()

# Alternative: If you want to completely restart, use machine.reset()
# Uncomment these lines instead of __import__("main"):
import machine
machine.reset()



