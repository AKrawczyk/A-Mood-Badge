# Tufty2040 boot menu/loader.

import gc
import time
from os import listdir
from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB565
from pimoroni import Button
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

def hsv_to_rgb(h: float, s: float, v: float) -> tuple[float, float, float]:  # noqa: RET503
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    v = int(v * 255)
    t = int(t * 255)
    p = int(p * 255)
    q = int(q * 255)
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


def get_applications() -> list[dict[str, str]]:
    # fetch a list of the applications that are stored in the filesystem
    applications = []
    for file in listdir():
        if file.endswith(".py") and file != "main.py" and file != "settings.py" and file != "clock.py":
            # remove any numeric prefix such as "4_" from filenames like "4_jam.py"
            base_name = file[:-3]
            while base_name and base_name[0].isdigit():
                base_name = base_name[1:]
            if base_name.startswith("_"):
                base_name = base_name[1:]

            # convert the filename from "something_or_other" to "Something Or Other"
            title = " ".join([v[:1].upper() + v[1:] for v in base_name.split("_")])

            applications.append(
                {
                    "file": file,
                    "title": title
                }
            )

    # sort the application list alphabetically by title and return the list
    return applications


def prepare_for_launch() -> None:
    for k in locals().keys():
        if k not in ("__name__",
                     "application_file_to_launch",
                     "gc"):
            del locals()[k]
    gc.collect()
    

def menu() -> str:
    applications = get_applications()

    button_up = Button(22, invert=False)
    button_down = Button(6, invert=False)
    button_a = Button(7, invert=False)
    button_b = Button(8, invert=False)
    button_c = Button(9, invert=False)

    display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB565)
    display.set_backlight(brightness)
    WIDTH, HEIGHT = display.get_bounds()

    selected_item = 2
    scroll_position = 2
    target_scroll_position = 2

    selected_pen = display.create_pen(255, 255, 255)
    unselected_pen = display.create_pen(80, 80, 100)
    background_pen = display.create_pen(50, 50, 70)
    shadow_pen = display.create_pen(0, 0, 0)

    while True:
        t = time.ticks_ms() / 1000.0

        if button_up.read():
            target_scroll_position -= 1
            target_scroll_position = target_scroll_position if target_scroll_position >= 0 else len(applications) - 1

        if button_down.read():
            target_scroll_position += 1
            target_scroll_position = target_scroll_position if target_scroll_position < len(applications) else 0

        if button_a.read():
            # Wait for the button to be released.
            while button_a.is_pressed:
                time.sleep(0.01)

            return applications[selected_item]["file"]

        if button_b.read():
            # Wait for the button to be released.
            while button_b.is_pressed:
                time.sleep(0.01)

            # Clean up this module
            #prepare_for_launch()
            
            # Return to main menu (import without .py extension)
            return "settings" 

        if button_c.read():
            # Wait for the button to be released.
            while button_c.is_pressed:
                time.sleep(0.01)
            
            # Clean up this module
            #prepare_for_launch()
            
            # Return to main menu (import without .py extension)
            return "clock" 

        display.set_pen(background_pen)
        display.clear()
        display.set_font("sans")

        scroll_position += (target_scroll_position - scroll_position) / 5

        grid_size = 40
        for y in range(240 // grid_size):
            for x in range(320 // grid_size):
                h = x + y + int(t * 5)
                h = h / 50.0
                r, g, b = hsv_to_rgb(h, 0.5, 1)

                display.set_pen(display.create_pen(r, g, b))
                display.rectangle(x * grid_size, y * grid_size, grid_size, grid_size)

        # work out which item is selected (closest to the current scroll position)
        selected_item = round(target_scroll_position)

        for list_index, application in enumerate(applications):
            distance = list_index - scroll_position

            text_size = 1 if selected_item == list_index else 1

            # center text horixontally
            title_width = display.measure_text(application["title"], text_size)
            text_x = int(160 - title_width / 2)

            row_height = text_size * 5 + 20

            # center list items vertically
            text_y = int(120 + distance * row_height - (row_height / 2))

            # draw the text, selected item brightest and with shadow
            if selected_item == list_index:
                display.set_pen(shadow_pen)
                display.text(application["title"], text_x + 1, text_y + 1, -1, text_size)

            text_pen = selected_pen if selected_item == list_index else unselected_pen
            display.set_pen(text_pen)
            display.text(application["title"], text_x, text_y, -1, text_size)
        
        display.set_pen(unselected_pen)
        display.set_font("serif")
        display.text("A: Select | B: Settings | C: Clock", 30, HEIGHT - 20, WIDTH, 0.5)
        display.update()


# The application we will be launching. This should be ouronly global, so we can
# drop everything else.
application_file_to_launch = menu()

# Run whatever we've set up to.
# If this fails, we'll exit the script and drop to the REPL, which is
# fairly reasonable.
prepare_for_launch()
__import__(application_file_to_launch)


