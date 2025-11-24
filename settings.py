# Settings menu for Tufty 2040 badge
# Two pages: Display settings and Clock settings

from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB565
from pimoroni import Button
import gc
import sys
import time
import os
import json
import machine

def prepare_for_launch() -> None:
    """Clean up before launching another module"""
    if 'settings' in sys.modules:
        del sys.modules['settings']
    gc.collect()

# --- Display setup ---
display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB565)
display.set_backlight(1.0)
WIDTH, HEIGHT = display.get_bounds()

# --- Color definitions ---
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
GREY = display.create_pen(128, 128, 128)
DARK_GREY = display.create_pen(64, 64, 64)
LIGHT_GREY = display.create_pen(200, 200, 200)
BLUE = display.create_pen(0, 100, 255)
GREEN = display.create_pen(0, 255, 0)
RED = display.create_pen(255, 0, 0)
# Additional colors for background selection
ORANGE = display.create_pen(246, 138, 30)
YELLOW = display.create_pen(255, 216, 0)
INDIGO = display.create_pen(36, 64, 142)
VIOLET = display.create_pen(115, 41, 130)
PINK = display.create_pen(255, 175, 200)
CYAN = display.create_pen(33, 177, 255)
MAGENTA = display.create_pen(255, 33, 140)
AMETHYST = display.create_pen(156, 89, 209)

# --- Settings file path ---
SETTINGS_FILE = "/settings.json"

# --- Default settings ---
DEFAULT_SETTINGS = {
    "brightness": 1.0,
    "text_overlay": True,
    "selected_image": "",
    "badge_image": True,
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

# --- Save settings to file ---
def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

# --- Get list of PNG files in badge folder ---
def list_png_files(directory: str) -> list:
    """Get list of PNG files in directory"""
    try:
        # Check if directory exists by trying to list it
        try:
            files = [f for f in os.listdir(directory) if f.lower().endswith(".png")]
            files.sort()
            return files
        except OSError:
            # Directory doesn't exist
            return []
    except Exception as e:
        print(f"Error listing PNG files: {e}")
        return []

# --- Background color options ---
BACKGROUND_COLORS = [
    "Black", "White", "Red", "Orange", "Yellow", "Green", 
    "Blue", "Indigo", "Violet", "Pink", "Cyan", "Magenta", "Amethyst", "Grey"
]

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
clock_image = settings.get("clock_image", True)
background_color = settings.get("background_color", "Black")
# Ensure background_color is valid
if background_color not in BACKGROUND_COLORS:
    background_color = "Black"
    settings["background_color"] = background_color
    save_settings(settings)

# --- Get RTC for clock settings ---
rtc = machine.RTC()
year, month, day, weekday, hour, minute, second, _ = rtc.datetime()

# --- Get list of images ---
image_files = list_png_files("/badge")
if selected_image and selected_image not in image_files:
    selected_image = image_files[0] if image_files else ""
elif not selected_image and image_files:
    selected_image = image_files[0]

# --- State management ---
current_page = 1  # 1 = Display settings, 2 = Clock settings
selected_item = 0  # Which item is selected on current page
editing = False  # Whether we're editing a value

# Page 1 items: brightness, text_overlay, image_selection, clock_image, background_color
page1_items = ["Badge Text", "Badge Image", "Clock Image", "Image", "Colour", "Display"]
page1_item_count = len(page1_items)

# Page 2 items: year, month, day, hour, minute, second
page2_items = ["Year", "Month", "Day", "Hour", "Minute", "Second"]
page2_item_count = len(page2_items)

# --- Button setup ---
button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_c = Button(9, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)

# --- Helper function to get days in month ---
def days_in_month(month, year):
    """Get number of days in a month"""
    if month == 2:
        # Check for leap year
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        return 28
    return (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month - 1]

# --- Draw page 1 (Display settings) ---
def draw_page1():
    """Draw the display settings page"""
    display.set_pen(BLACK)
    display.clear()
    
    try:
        display.set_font("sans")
    except:
        display.set_font("bitmap8")
    
    # Title
    display.set_pen(WHITE)
    title = "System Settings"
    title_width = display.measure_text(title, 1.2)
    display.text(title, (WIDTH - title_width) // 2, 15, WIDTH, 1.2)
    
    # Draw items
    y_start = 50
    line_height = 28
    
    for i, item in enumerate(page1_items):
        y_pos = y_start + i * line_height
        
        # Highlight selected item
        if i == selected_item:
            display.set_pen(DARK_GREY)
            display.rectangle(10, y_pos - 13, WIDTH - 20, line_height - 4)
        
        # Item name
        display.set_pen(WHITE if i == selected_item else LIGHT_GREY)
        display.text(item, 20, y_pos, WIDTH, 0.8)
        
        # Item value
        value_x = 150
        
        if item == "Badge Text":
            value = "ON" if text_overlay else "OFF"
        elif item == "Badge Image":
            value = "ON" if badge_image else "OFF"
        elif item == "Clock Image":
            value = "ON" if clock_image else "OFF"
        elif item == "Image":
            value = selected_image if selected_image else "none"
        if len(value) > 15:
            value = value[:12] + "..."
        elif item == "Colour":
            value = background_color
            if len(value) > 15:
                value = value[:12] + "..."
        elif item == "Display":
            value = f"{int(brightness * 100)}%"
        
        display.set_pen(GREEN if i == selected_item and editing and i != 4 else WHITE if i == selected_item else GREY)
        display.text(value, value_x + 40, y_pos, WIDTH - value_x - 10, 0.7)
        if selected_item == 4 and editing and item == "Colour":
            bg_colour = COLOR_PENS.get(background_color, BLACK)
            display.set_pen(bg_colour)
            display.text(value, value_x + 40, y_pos, WIDTH - value_x - 10, 0.7)
        
     
    # Instructions
    display.set_pen(GREY)
    try:
        display.set_font("serif")
    except:
        display.set_font("bitmap8")
    display.text("A: Menu | B: Page | C: Select", 20, HEIGHT - 20, WIDTH, 0.6)
    
    display.update()

# --- Draw page 2 (Clock settings) ---
def draw_page2():
    """Draw the clock settings page"""
    display.set_pen(BLACK)
    display.clear()
    
    try:
        display.set_font("sans")
    except:
        display.set_font("bitmap8")
    
    # Title
    display.set_pen(WHITE)
    title = "Set Date & Time"
    title_width = display.measure_text(title, 1.2)
    display.text(title, (WIDTH - title_width) // 2, 15, WIDTH, 1.2)
    
    # Draw items
    y_start = 50
    line_height = 28
    
    for i, item in enumerate(page2_items):
        y_pos = y_start + i * line_height
        
        # Highlight selected item
        if i == selected_item:
            display.set_pen(DARK_GREY)
            display.rectangle(10, y_pos - 13, WIDTH - 20, line_height - 4)
        
        # Item name
        display.set_pen(WHITE if i == selected_item else LIGHT_GREY)
        display.text(item, 20, y_pos, WIDTH, 0.8)
        
        # Item value
        value_x = 150
        if item == "Year":
            value = str(year)
        elif item == "Month":
            value = f"{month:02}"
        elif item == "Day":
            value = f"{day:02}"
        elif item == "Hour":
            value = f"{hour:02}"
        elif item == "Minute":
            value = f"{minute:02}"
        elif item == "Second":
            value = f"{second:02}"
        
        display.set_pen(GREEN if i == selected_item and editing else WHITE if i == selected_item else GREY)
        display.text(value, value_x + 40, y_pos, WIDTH - value_x - 10, 0.7)
    
    # Instructions
    display.set_pen(GREY)
    try:
        display.set_font("serif")
    except:
        display.set_font("bitmap8")
    display.text("A: Menu | B: Page | C: Select", 20, HEIGHT - 20, WIDTH, 0.6)
    
    display.update()

# --- Handle button presses for page 1 ---
def handle_page1_buttons():
    """Handle button presses on page 1"""
    global brightness, text_overlay, selected_image, badge_image, clock_image, background_color, selected_item, editing, settings
    
    if button_c.read():
        while button_c.is_pressed:
            time.sleep(0.01)
        
        
        if selected_item == 0:  # Text Overlay
            text_overlay = not text_overlay
            settings["text_overlay"] = text_overlay
            save_settings(settings)
        elif selected_item == 1:  # Badge Image
            badge_image = not badge_image
            settings["badge_image"] = badge_image
            save_settings(settings)
        elif selected_item == 2:  # Clock Image
            clock_image = not clock_image
            settings["clock_image"] = clock_image
            save_settings(settings)
        elif selected_item == 3:  # Image
            editing = not editing
        elif selected_item == 4:  # Background Color
            editing = not editing
        elif selected_item == 5:  # Brightness
            editing = not editing
    
    if editing:
        if selected_item == 5:  # Brightness
            if button_up.read():
                while button_up.is_pressed:
                    time.sleep(0.01)
                brightness = round(min(1.0, brightness + 0.1), 1)
                display.set_backlight(brightness)
                settings["brightness"] = brightness
                save_settings(settings)
            if button_down.read():
                while button_down.is_pressed:
                    time.sleep(0.01)
                brightness = round(max(0.4, brightness - 0.1), 1)
                display.set_backlight(brightness)
                settings["brightness"] = brightness
                save_settings(settings)
        
        elif selected_item == 3:  # Image selection
            if button_up.read():
                while button_up.is_pressed:
                    time.sleep(0.01)
                if image_files:
                    current_idx = image_files.index(selected_image) if selected_image in image_files else 0
                    current_idx = (current_idx - 1) % len(image_files)
                    selected_image = image_files[current_idx]
                    settings["selected_image"] = selected_image
                    save_settings(settings)
            if button_down.read():
                while button_down.is_pressed:
                    time.sleep(0.01)
                if image_files:
                    current_idx = image_files.index(selected_image) if selected_image in image_files else 0
                    current_idx = (current_idx + 1) % len(image_files)
                    selected_image = image_files[current_idx]
                    settings["selected_image"] = selected_image
                    save_settings(settings)
        
        elif selected_item == 4:  # Background Color selection
            if button_up.read():
                while button_up.is_pressed:
                    time.sleep(0.01)
                current_idx = BACKGROUND_COLORS.index(background_color) if background_color in BACKGROUND_COLORS else 0
                current_idx = (current_idx - 1) % len(BACKGROUND_COLORS)
                background_color = BACKGROUND_COLORS[current_idx]
                settings["background_color"] = background_color
                save_settings(settings)
            if button_down.read():
                while button_down.is_pressed:
                    time.sleep(0.01)
                current_idx = BACKGROUND_COLORS.index(background_color) if background_color in BACKGROUND_COLORS else 0
                current_idx = (current_idx + 1) % len(BACKGROUND_COLORS)
                background_color = BACKGROUND_COLORS[current_idx]
                settings["background_color"] = background_color
                save_settings(settings)
    else:
        if button_up.read():
            while button_up.is_pressed:
                time.sleep(0.01)
            selected_item = (selected_item - 1) % page1_item_count
        
        if button_down.read():
            while button_down.is_pressed:
                time.sleep(0.01)
            selected_item = (selected_item + 1) % page1_item_count

# --- Handle button presses for page 2 ---
def handle_page2_buttons():
    """Handle button presses on page 2"""
    global year, month, day, hour, minute, second, selected_item, editing
    
    if button_c.read():
        while button_c.is_pressed:
            time.sleep(0.01)
        editing = not editing
    
    if editing:
        if button_up.read():
            while button_up.is_pressed:
                time.sleep(0.01)
            
            if selected_item == 0:  # Year
                year += 1
                if year > 2099:
                    year = 2024
                # Adjust day if needed (e.g., Feb 29 -> Feb 28)
                max_day = days_in_month(month, year)
                if day > max_day:
                    day = max_day
            elif selected_item == 1:  # Month
                month = (month % 12) + 1
                # Adjust day if needed
                max_day = days_in_month(month, year)
                if day > max_day:
                    day = max_day
            elif selected_item == 2:  # Day
                max_day = days_in_month(month, year)
                day = (day % max_day) + 1
            elif selected_item == 3:  # Hour
                hour = (hour + 1) % 24
            elif selected_item == 4:  # Minute
                minute = (minute + 1) % 60
            elif selected_item == 5:  # Second
                second = (second + 1) % 60
        
        if button_down.read():
            while button_down.is_pressed:
                time.sleep(0.01)
            
            if selected_item == 0:  # Year
                year -= 1
                if year < 2024:
                    year = 2099
                # Adjust day if needed
                max_day = days_in_month(month, year)
                if day > max_day:
                    day = max_day
            elif selected_item == 1:  # Month
                month = ((month - 2) % 12) + 1
                # Adjust day if needed
                max_day = days_in_month(month, year)
                if day > max_day:
                    day = max_day
            elif selected_item == 2:  # Day
                max_day = days_in_month(month, year)
                day = ((day - 2) % max_day) + 1
            elif selected_item == 3:  # Hour
                hour = (hour - 1) % 24
            elif selected_item == 4:  # Minute
                minute = (minute - 1) % 60
            elif selected_item == 5:  # Second
                second = (second - 1) % 60
    else:
        if button_up.read():
            while button_up.is_pressed:
                time.sleep(0.01)
            selected_item = (selected_item - 1) % page2_item_count
        
        if button_down.read():
            while button_down.is_pressed:
                time.sleep(0.01)
            selected_item = (selected_item + 1) % page2_item_count

# --- Main loop ---
# Set initial brightness
display.set_backlight(brightness)

# Draw initial page
if current_page == 1:
    draw_page1()
else:
    draw_page2()

while True:
    time.sleep(0.01)
    
    # Button A: Back to menu
    if button_a.read():
        while button_a.is_pressed:
            time.sleep(0.01)
        
        # Save clock settings to RTC before exiting
        if current_page == 2:
            rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
        
        prepare_for_launch()
        break
    
    # Button B: Toggle between pages
    if button_b.read():
        while button_b.is_pressed:
            time.sleep(0.01)
        
        # Save clock settings when leaving page 2
        if current_page == 2:
            rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
        
        current_page = 2 if current_page == 1 else 1
        selected_item = 0
        editing = False
        
        if current_page == 1:
            draw_page1()
        else:
            # Refresh RTC values when entering page 2
            year, month, day, weekday, hour, minute, second, _ = rtc.datetime()
            draw_page2()
    
    # Handle page-specific buttons
    if current_page == 1:
        handle_page1_buttons()
        draw_page1()
    else:
        handle_page2_buttons()
        draw_page2()

# Return to main menu
import machine
machine.reset()
