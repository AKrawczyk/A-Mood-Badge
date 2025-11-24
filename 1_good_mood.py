# Good mood displays image or text for Tufty 2040 badge

from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB565
import pngdec
import time
from pimoroni import Button
import gc
import sys

def prepare_for_launch() -> None:
    """Clean up before launching another module"""
    # Remove this module from sys.modules so it can be reloaded fresh next time
    if '1_Good_Mood' in sys.modules:
        del sys.modules['1_Good_Mood']
    
    # Collect garbage to free memory
    gc.collect()

# --- Display setup ---
display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB565)
display.set_backlight(0.4)
WIDTH, HEIGHT = display.get_bounds()

# Create pens
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
GREY = display.create_pen(64, 64, 64)
GREEN = display.create_pen(0, 255, 0)

# --- Clear background ---
display.set_pen(GREEN)
display.clear()

# --- Try to display the image ---
try:
    png = pngdec.PNG(display)
    png.open_file("thumb_up2.png")
    png.decode(0, 0)
    
except Exception as e:
    print(f"Error loading image: {e}")
    print("Make sure 'thumb_up2.png' (320x240 baseline PNG) is on the device.")
    display.set_pen(GREEN)
    display.rectangle(0, 0, WIDTH, HEIGHT)

    # --- Draw centered "bold" text overlay ---
    try:
        display.set_font("sans")
    except Exception:
        display.set_font("bitmap8")

    text = "Good/Happy"
    text2 = "Mood"
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
