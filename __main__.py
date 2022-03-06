# thanks to remixicon.com for creating the beautiful icons!
# parts of this file are forked from the offical abcminiuser/python-elgato-streamdeck repository

import os
import threading
import sys
from subprocess import Popen, PIPE, run
import math
from time import sleep
import re
import multiprocessing.dummy as mp

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

import settings

device_1 = settings.device_1
device_2 = settings.device_2
device_3 = settings.device_3
device_4 = settings.device_4
device_5 = settings.device_5

volume_step = settings.volume_step
label_seperator = settings.label_seperator
margins = settings.margins

# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename, font_filename, label_text):
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=margins)

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(font_filename, settings.font_size)
    except:
        print('the font you selected is not available in the Assets folder')
        sys.exit(1)
    draw.text((image.width / 2, image.height - 55), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_format(deck, image)

def get_volume(device):
    # print('getting volume')
    if device != None:
        process = Popen(['pulsemeeter', 'get', 'volume', device], stdout=PIPE)
        return int(process.communicate()[0])

def get_mute(device):
    # print('getting mute')
    process = Popen(['pulsemeeter', 'get', 'mute', device], stdout=PIPE)
    return process.communicate()[0].decode().strip()

def get_eq(device):
    # print('getting eq')
    process = Popen(['pulsemeeter', 'get', 'eq', device], stdout=PIPE)
    return process.communicate()[0].decode().strip()

def get_rnnoise(device):
    # print('getting rnnoise')
    process = Popen(['pulsemeeter', 'get', 'rnnoise', device], stdout=PIPE)
    return process.communicate()[0].decode().strip()

def get_primary(device):
    # print('getting primary')
    process = Popen(['pulsemeeter', 'get', 'primary', device], stdout=PIPE)
    return process.communicate()[0].decode().strip()

def get_connect(device, device2):
    process = Popen(['pulsemeeter', 'get', 'connect', device, device2], stdout=PIPE)
    return process.communicate()[0].decode().strip()

# get the picture for the speaker
def get_speaker_pic(device, device_type):
    state = get_mute(device)
    if state == 'True':
        if device_type == 'mic':
            return "mic-off-line.png"
        else:
            return "volume-mute-line.png"
    else:
        if device_type == 'mic':
            return "mic-line.png"
        else:
            return "speaker-line.png"

def get_button_pic(value):
    if value == 'True':
        return "toggle-fill.png"
    else:
        return "toggle-line.png"

def get_checkbox_pic(value):
    if value == 'True':
        return "checkbox-blank-fill.png"
    else:
        return "checkbox-blank-line.png"


# get a device by the label (eg. one/two/three/...)
def get_device_from_label(label):
    for dev in get_devices():
        if dev[3] == label:
            return dev


# Returns styling information for a key based on its position and state.
def get_current_key_style(deck, key, load_data=False):
    menu = curr_site

    if key not in get_used_keys():
        name = "None"
        icon = "Empty.png"
        label = ''
        #label = "Pressed!" if state else "Key {}".format(key)

    # here are the designed menus. Change them how you like it.
    # these are the fields:
    '''
    | one_up    | two_up    | three_up    | four_up    | five_up   |
    | one_down  | two_down  | three_down  | four_down  | five_down |
    | one_base  | two_base  | three_base  | four_base  | five_base |
    '''
    dev = None

    if menu == "main":
        devices = get_devices()
        for device in devices:
            try:
                device_name = device[3]
                device_label = device[2]

                if key == eval(f'{device_name}_up'):
                    name = f"{device_name}+"
                    icon = "volume-up-line.png"
                    if settings.show_volume_step:
                        label = "+ "+str(volume_step)
                    else:
                        label = "+"

                elif key == eval(f'{device_name}_down'):
                    name = f"{device_name}-"
                    icon = "volume-down-line.png"
                    if settings.show_volume_step:
                        label = "- "+str(volume_step)
                    else:
                        label = "-"

                elif key == eval(f'{device_name}_base'):
                    name = f'{device_name}'
                    icon = "sound-module-fill.png"
                    #device_type = device[1]
                    #icon = get_speaker_pic(device[0], device_type)
                    if load_data:
                        label = f"{get_volume(device[0])}{label_seperator}{device_label}"
                    else:
                        label = f"0{label_seperator}{device_label}"
            except:
                name = ""
                icon = "Empty.png"
                label = ""

    # it could probably be short but I think this is more user friendly
    elif menu == "sub-menu":
        dev = get_device_from_label(curr_device)

        if key == one_base:
            name = device_1[3]
            icon = "close-line.png"
            label = "close"
        # RNNOISE
        elif key == one_down:
            if re.match('^(hi)+', dev[0]):
                name = device_1[3]+"-"
                if load_data:
                    icon = get_button_pic(get_rnnoise(dev[0]))
                else:
                    icon = "refresh-line.png"
                label = "rnnoise"
            else:
                name = ""
                icon = "Empty.png"
                label = ""
        # MUTE
        elif key == one_up:
            name = device_1[3]+"+"
            if load_data:
                icon = get_speaker_pic(dev[0], dev[1])
            else:
                icon = 'refresh-line.png'
            label = "mute"
        if key == two_base:
            name = device_2[3]
            icon = "Empty.png"
            label = ""
        elif key == two_down:
            name = device_2[3]+"-"
            icon = "Empty.png"
            label = ""
        # EQ
        elif key == two_up:
            if re.match('^(a|b)+', dev[0]):
                name = device_2[3]+"+"
                if load_data:
                    icon = get_button_pic(get_eq(dev[0]))
                else:
                    icon = "refresh-line.png"
                label = "EQ"
            else:
                name = ""
                icon = "Empty.png"
                label = ""
        elif key == three_base:
            name = device_3[3]
            icon = "Empty.png"
            label = ""
            if settings.show_device:
                label = f"Device:\n{dev[0].upper()}"
            else:
                label = ""
        elif key == three_down:
            name = device_3[3]+"-"
            icon = "Empty.png"
            label = ""
        # PRIMARY
        elif key == three_up:
            if re.match('^(b|vi)+', dev[0]):
                name = device_3[3]+"+"
                if load_data:
                    icon = get_button_pic(get_primary(dev[0]))
                else:
                    icon = "refresh-line.png"
                label = "primary"
            else:
                icon = "Empty.png"
                label = ""
                name = ""
        else:
            # CONNECTIONS
            if re.match('^(hi|vi)+', dev[0]):
                connection_allowed = True
            else:
                connection_allowed = False

            if key == four_base:
                if connection_allowed:
                    name = device_4[3]
                    if load_data:
                        icon = get_checkbox_pic(get_connect(dev[0], 'a1'))
                    else:
                        icon = "checkbox-blank-line.png"
                    label = "A1"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == four_down:
                if connection_allowed:
                    name = device_4[3]+"-"
                    if load_data:
                        icon = get_checkbox_pic(get_connect(dev[0], 'a2'))
                    else:
                        icon = "checkbox-blank-line.png"
                    label = "A2"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == four_up:
                if connection_allowed:
                    name = device_4[3]+"+"
                    if load_data:
                        icon = get_checkbox_pic(get_connect(dev[0], 'a3'))
                    else:
                        icon = "checkbox-blank-line.png"
                    label = "A3"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == five_base:
                if connection_allowed:
                    name = device_5[3]
                    if load_data:
                        icon = get_checkbox_pic(get_connect(dev[0], 'b1'))
                    else:
                        icon = "checkbox-blank-line.png"
                    label = "B1"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == five_down:
                if connection_allowed:
                    name = device_5[3]+"-"
                    if load_data:
                        icon = get_checkbox_pic(get_connect(dev[0], 'b2'))
                    else:
                        icon = "checkbox-blank-line.png"
                    label = "B2"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == five_up:
                if connection_allowed:
                    name = device_5[3]+"+"
                    if load_data:
                        icon = get_checkbox_pic(get_connect(dev[0], 'b3'))
                    else:
                        icon = "checkbox-blank-line.png"
                    label = "B3"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
    return {
        "name": name,
        "icon": os.path.join(settings.ASSETS_PATH, icon),
        "font": os.path.join(settings.ASSETS_PATH, settings.font),
        "label": label,
        "menu": menu,
        "device": dev, 
    }

def change_page(deck, page, device=None):
    global curr_site
    curr_site = page
    global curr_device
    curr_device = device
    a = range(deck.key_count())
    for i in a:
        update_key_image(deck, i, False)
    print(f'changed page to {curr_site} ({curr_device})')
    reload_data()

# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, load_data=False):
    # Determine what icon and label to use on the generated key.
    key_style = get_current_key_style(deck, key, load_data)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)

def check_volume_keys(deck, key_style, key, device):
    if key_style["name"] == f"{key}+":
        print(f'{device[0]} +')
        run(['pulsemeeter', 'volume', device[0], f'+{volume_step}'])
        update_key_image(deck, eval(f'{key}_base'), True)
    elif key_style["name"] == f"{key}-":
        print(f'{device[0]} -')
        run(['pulsemeeter', 'volume', device[0], f'-{volume_step}'])
        update_key_image(deck, eval(f"{key}_base"), True)
    elif key_style["name"] == f"{key}":
        change_page(deck, "sub-menu", key)


# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    # Update the key image based on the new key state.
    update_key_image(deck, key, True)

    # Check if the key is changing to the pressed state.
    if state:
        global curr_device
        key_style = get_current_key_style(deck, key, False)

        # When an exit button is pressed, close the application.
        if key_style["name"] == "exit":
            # Use a scoped-with on the deck to ensure we're the only thread
            # using it right now.
            with deck:
                # Reset deck, clearing all button images.
                deck.reset()

                # Close deck handle, terminating internal worker threads.
                deck.close()
        elif key_style["menu"] == "sub-menu":
            if key_style["name"] == "one":
                change_page(deck, "main")
            elif key_style["name"] == "one+":
                device = key_style["device"]
                run(['pulsemeeter', 'mute', device[0]])
                print(f'{key_style["device"][0]} mute toggled')
            elif key_style["name"] == "two+":
                device = key_style["device"]
                print(f'toggle eq ({device[0]})')
                run(['pulsemeeter', 'eq', device[0]])
            elif key_style["name"] == "one-":
                device = key_style["device"]
                print(f'toggle rnnoise {device[0]}')
                run(['pulsemeeter', 'rnnoise', device[0]])
            elif key_style["name"] == "three+":
                device = key_style["device"]
                print(f'made device primary ({device[0]})')
                run(['pulsemeeter', 'primary', device[0]])
            elif key_style["name"] in ['four', 'four-', 'four+', 'five', 'five-', 'five+']:
                device = key_style["device"]
                out_device = key_style["label"].lower()
                print(f'toggling connection {device[0]} to {out_device}')
                run(['pulsemeeter', 'connect', device[0], out_device])
        else:
            check_volume_keys(deck, key_style, "one", device_1)
            check_volume_keys(deck, key_style, "two", device_2)
            check_volume_keys(deck, key_style, "three", device_3)
            check_volume_keys(deck, key_style, "four", device_4)
            check_volume_keys(deck, key_style, "five", device_5)

def get_used_keys():
    variables = []
    for name in ['one', 'two', 'three']:
        for value in ['up', 'down', 'base']:
            variables.append(eval(f'{name}_{value}'))
    return variables

def get_devices():
    devices = []
    devices.append(device_1)
    devices.append(device_2)
    devices.append(device_3)
    devices.append(device_4)
    devices.append(device_5)
    return devices

def update_data_key(key):
    update_key_image(deck, key, True)
    print(f'settings data key {key} ({curr_site})')

def update_key(key):
    update_key_image(deck, key, False)
    print(f'setting key {key} ({curr_site})')

# I do not really want to make the pool higher because that increases the cpu usage
def reload_data():
    use_multiprocessing = settings.use_multiprocessing
    if curr_site == 'main':
        updating_keys = [one_base, two_base, three_base, four_base, five_base]
        if use_multiprocessing:
            p = mp.Pool(5)
        else:
            for key in updating_keys:
                update_data_key(key)
    elif curr_site == 'sub-menu':
        updating_keys = [one_up, one_down, two_up, three_up, four_base, four_up, four_down, five_base, five_down, five_up]
        if use_multiprocessing:
            p = mp.Pool(5)
        else:
            for key in updating_keys:
                update_data_key(key)
    if use_multiprocessing:
        p.map(update_data_key, updating_keys)
        p.close()
        p.join()



if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))
    if settings.check_running:
        print('checking if pulsemeeter is running.')
        try:
            process = Popen(['pgrep', 'pulsemeeter'], stdout=PIPE)
        except:
            print('Could not check if pulsemeeter is runnning')
        else:
            if process.communicate()[0].decode().strip() == "":
                sys.exit("pulsemeeter is not running (if this message is wrong, turn off check_running in settings)")

    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}')".format(deck.deck_type(), deck.get_serial_number()))

        # Set initial screen brightness to 30%.
        deck.set_brightness(settings.brightness)

        print('setting key variables')
        # I could probably replace this with a loop but I don't really find it necessary
        global one_up
        one_up = deck.key_count() - 15
        global one_down
        one_down = deck.key_count() - 10
        global one_base
        one_base = deck.key_count() - 5
        global two_up
        two_up = deck.key_count() - 14
        global two_down
        two_down = deck.key_count() - 9
        global two_base
        two_base = deck.key_count() - 4
        global three_up
        three_up = deck.key_count() - 13
        global three_down
        three_down = deck.key_count() - 8
        global three_base
        three_base = deck.key_count() - 3
        global four_up 
        four_up = deck.key_count() - 12
        global four_down
        four_down = deck.key_count() - 7
        global four_base
        four_base = deck.key_count() - 2
        global five_up 
        five_up = deck.key_count() - 11
        global five_down
        five_down = deck.key_count() - 6
        global five_base
        five_base = deck.key_count() - 1

        global curr_site
        curr_site = 'main'

        global curr_device
        curr_device = None

        # Set initial key images.
        a = range(deck.key_count())
        if settings.use_multiprocessing:
            print('multiprocessing is turned on')
            p = mp.Pool(4)
            p.map(update_key, a)
            p.close()
            p.join()
        else:
            print('multiprocessing is turned off.')
            for key in a:
                print(f'creating key image {key}')
                update_key_image(deck, key, False)
        reload_data()
        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        print('finished setup')
        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass


