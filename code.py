import sys
import time
from adafruit_magtag.magtag import MagTag
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_magtag.magtag import Graphics, Network
from adafruit_display_shapes.rect import Rect
import adafruit_requests
import displayio
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.sequence import AnimationSequence, AnimateOnce
from adafruit_led_animation.group import AnimationGroup

TSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_c5arGMBsm6tPDyCbTXZt9qgc2HEhv3P86uEoRvWi4INJYrJl5z6bN8LYX2mM4VZdIpdsskvWns1v/pub?gid=0&single=true&output=tsv'

magtag = MagTag()
pixels = magtag.peripherals.neopixels
pixels.brightness = 0.5
magtag.peripherals.neopixel_disable = False

# DisplayIO setup
font_small = bitmap_font.load_font("/fonts/Arial-12.pcf")
font_large = bitmap_font.load_font("/fonts/Arial-14.pcf")

graphics = Graphics(auto_refresh=False)
display = graphics.display
main_group = displayio.Group()

RED = 0x880000
GREEN = 0x008800
BLUE = 0x000088
YELLOW = 0x884400
CYAN = 0x0088BB
MAGENTA = 0x9900BB
WHITE = 0x888888


global_selection_index = 0


def try_refresh():
    """Attempt to refresh the display. Catch 'refresh too soon' error
    and retry after waiting 10 seconds.
    """
    try:
        display.refresh()
    except RuntimeError as too_soon_error:
        # catch refresh too soon
        print(too_soon_error)
        print("waiting before retry refresh()")
        time.sleep(10)
        display.refresh()


def render_list(recipes, selection_index=0):
    bg_bitmap = displayio.Bitmap(display.width // 8, display.height // 8, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0xFFFFFF
    bg_sprite = displayio.TileGrid(
        bg_bitmap, x=0, y=0, pixel_shader=bg_palette)
    bg_group = displayio.Group(scale=8)
    bg_group.append(bg_sprite)
    main_group.append(bg_group)

    top_offset = 10
    for i, recipe in enumerate(recipes):
        label_overview_text = Label(
            font_large,
            x=0,
            y=top_offset,
            line_spacing=0.75,
            color=(0x000000 if i != selection_index else 0xFFFFFF),
            background_color=(0xFFFFFF if i != selection_index else 0x000000),
            text=recipe["label"],
        )
        main_group.append(label_overview_text)
        top_offset += 10 + 15

    display.show(main_group)
    try_refresh()


def render_qr(recipes, selection_index=0):
    graphics.qrcode(
        recipes[selection_index]["url"], qr_size=2, x=140, y=40)
    graphics.display.show(graphics.splash)
    try_refresh()


def blink(color, duration):
    magtag.peripherals.neopixel_disable = False
    magtag.peripherals.neopixels.fill(color)
    time.sleep(duration)
    magtag.peripherals.neopixel_disable = True


def play_start_lightshow():
    blink(WHITE, 0.4)
    blink(RED, 0.4)
    blink(WHITE, 0.4)


def fetch_recipes(url):
    try:
        # My pet theory is this throw away http request is required
        # to circumvent the RuntimeError: Sending request failed error
        test = magtag.network.fetch("https://www.google.com", timeout=30)
        tsv_response = magtag.network.fetch(url, timeout=30)
    except (RuntimeError, OSError) as e:
        print(e)
        time.sleep(3)
        tsv_response = magtag.network.fetch(url, timeout=30)

    # Get spreadsheet data as TSV and parse it
    print(tsv_response.status_code)
    tsv_data = tsv_response.text
    print(tsv_data)

    lines = tsv_data.split('\r\n')

    # MOCK DATA
    # recipes = [{"label": 'Easy Vegan Peanut Butter-Maple Ice Cream Recipe - NYT Cooking',
    #             "url": "https://cooking.nytimes.com/recipes/1023276-easy-vegan-peanut-butter-maple-ice-cream"},
    #            {"label": 'Weasel Stew for me and you',
    #             "url": "https://google.com?q=weasel+stew"}]

    recipes = []
    for line in lines[1:]:  # Skip first line
        cells = line.split("\t")  # Tab-separated!
        recipes.append({"label": cells[2],
                        "url":  cells[3]})
    return recipes


play_start_lightshow()
time.sleep(2)
recipes = fetch_recipes(TSV_URL)
render_list(recipes)

animations = AnimationSequence(
    AnimationGroup(
        Sparkle(pixels, .1, BLUE, 15)),
    AnimationGroup(
        # Turn the LEDs off.
        Solid(pixels, 0),
    ),
    auto_clear=True,
)
btn_sleep_time = 5
while True:
    # cursor go up
    if magtag.peripherals.button_b_pressed:
        # re-render whole list
        blink(YELLOW, 0.4)
        global_selection_index = max(global_selection_index - 1, 0)
        render_list(recipes, global_selection_index)
        time.sleep(btn_sleep_time)
    # cursor go down
    if magtag.peripherals.button_c_pressed:
        blink(CYAN, 0.4)
        global_selection_index = min(
            global_selection_index + 1, len(recipes) - 1)
        render_list(recipes, global_selection_index)
        time.sleep(btn_sleep_time)
    # cursor go right
    if magtag.peripherals.button_d_pressed:
        blink(GREEN, 0.4)
        render_qr(recipes, global_selection_index)
        time.sleep(btn_sleep_time)
    # cursor go left
    if magtag.peripherals.button_a_pressed:
        blink(MAGENTA, 0.4)
        render_list(recipes, global_selection_index)
        time.sleep(btn_sleep_time)

    # animations.animate()
    # need this? time.sleep(0.01)
