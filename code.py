# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import sys
import time
from adafruit_magtag.magtag import MagTag
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_magtag.magtag import Graphics, Network
from adafruit_display_shapes.rect import Rect

magtag = MagTag()

# DisplayIO setup
font_small = bitmap_font.load_font("/fonts/Arial-12.pcf")
font_large = bitmap_font.load_font("/fonts/Arial-14.pcf")

graphics = Graphics(auto_refresh=False)
display = graphics.display


RED = 0x880000
GREEN = 0x008800
BLUE = 0x000088
YELLOW = 0x884400
CYAN = 0x0088BB
MAGENTA = 0x9900BB
WHITE = 0x888888


recipes = [{"label": 'Easy Vegan Peanut Butter-Maple Ice Cream Recipe - NYT Cooking',
            "url": "https://cooking.nytimes.com/recipes/1023276-easy-vegan-peanut-butter-maple-ice-cream"},
           {"label": 'Weasel Stew for me and you',
            "url": "https://www.nytimes.com/2016/06/14/science/weasels-are-built-for-the-hunt.html"}]


global_selection_index = 0


def render_list(recipes, selection_index=0):
    clear_screen()
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
        graphics.splash.append(label_overview_text)
        top_offset += 10 + 15
    display.refresh()


def clear_screen():
    for x in range(0, len(graphics.splash)):
        graphics.splash.pop()
    background = Rect(0, 0, 296, 128, fill=0xFFFFFF)
    graphics.splash.append(background)


def render_qr(recipes, selection_index=0):
    clear_screen()
    time.sleep(5)
    graphics.qrcode(
        recipes[selection_index]["url"], qr_size=2, x=140, y=40)
    graphics.display.show(graphics.splash)
    display.refresh()


def blink(color, duration):
    magtag.peripherals.neopixel_disable = False
    magtag.peripherals.neopixels.fill(color)
    time.sleep(duration)
    magtag.peripherals.neopixel_disable = True


blink(WHITE, 0.4)

clear_screen()
render_list(recipes)

# graphics.qrcode(
#     "https://cooking.nytimes.com/recipes/1023276-easy-vegan-peanut-butter-maple-ice-cream", qr_size=2, x=140, y=40)
# graphics.display.show(graphics.splash)
# display.refresh()

while True:
    # cursor go up
    if magtag.peripherals.button_b_pressed:
        # re-render whole list
        blink(YELLOW, 0.4)
        global_selection_index = max(global_selection_index - 1, 0)
        render_list(recipes, global_selection_index)
        time.sleep(5)
    # cursor go down
    if magtag.peripherals.button_c_pressed:
        blink(CYAN, 0.4)
        global_selection_index = min(
            global_selection_index + 1, len(recipes) - 1)
        render_list(recipes, global_selection_index)
        time.sleep(5)
    if magtag.peripherals.button_d_pressed:
        blink(GREEN, 0.4)
        render_qr(recipes, global_selection_index)
        time.sleep(5)
    if magtag.peripherals.button_a_pressed:
        blink(MAGENTA, 0.4)
        render_list(recipes, global_selection_index)
        time.sleep(5)

    time.sleep(0.01)
