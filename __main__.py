# thanks to remixicon.com for creating the beautiful icons!
# parts of this file are forked from the offical abcminiuser/python-elgato-streamdeck repository

import os
import threading
import sys
from time import sleep
import re
import math

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

import settings
from pulsemeeter import socket

volume_step = settings.volume_step
label_seperator = settings.label_seperator
margins = settings.margins

def init_settings():
    try:
        global device_1
        global device_2
        global device_3
        global device_4
        global device_5
        device_1 = settings.device_1
        device_2 = settings.device_2
        device_3 = settings.device_3
        device_4 = settings.device_4
        device_5 = settings.device_5
    except:
        print(f'Could not find all devices in settings (5 devices needed).')
        print('---')
        client.close_connection()
        sys.exit(1)

    a = range(1,6)
    for num in a:
        try:
            device = eval(f'device_{num}')
            if type(device) != list:
                print(f'device_{num} is invalid. It is not a list.')
            if len(device) != 4:
                print(f'device_{num} is invalid. It needs 4 values')
                raise
            if device[0] not in ['hi', 'vi', 'a', 'b']:
                print(f'device_{num} (first value) is invalid. It has to be one of these: hi/vi/a/b')
                raise
            if type(device[2]) != str:
                print(f'device_{num} (third value) is invalid. It needs to be a string.')
                raise
            if type(device[3]) != str or device[3].lower() not in ['mic', 'speaker']:
                print(f'device_{num} (fourth value) is invalid. It needs to be a string which has to be one of these: mic/speaker')
                raise
        except:
            print(f'error in device_{num}')
            print('---')
            client.close_connection()
            sys.exit(1)
    


    device_1.append('one')
    device_2.append('two')
    device_3.append('three')
    device_4.append('four')
    device_5.append('five')

    for i in [device_1, device_2, device_3, device_4, device_5]:
        if type(i[1]) == int:
            i[1] = str(i[1])


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

# -------------------------------
# CONFIG

def get_volume(device):
    # print('getting volume')
    val = client.config[device[0]][device[1]]['vol']
    return int(val)

def get_mute(device):
    # print('getting mute')
    val = client.config[device[0]][device[1]]['mute']
    return val

def get_eq(device):
    # print('getting eq')
    val = client.config[device[0]][device[1]]['use_eq']
    return val

def get_rnnoise(device):
    # print('getting rnnoise')
    val = client.config[device[0]][device[1]]['use_rnnoise']
    return val

def get_primary(device):
    # print('getting primary')
    val = client.config[device[0]][device[1]]['primary']
    return val

def get_connect(device, device2):
    val = client.config[device[0]][device[1]][device2]
    return val

# ------------------------------
# ICON GENERATORS

# get the picture for the speaker
def get_speaker_pic(device):
    state = get_mute(device)
    device_type = device[3].lower()
    if state == True:
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
    if value == True:
        return "toggle-fill.png"
    else:
        return "toggle-line.png"

def get_checkbox_pic(value):
    if value == True:
        return "checkbox-blank-fill.png"
    else:
        return "checkbox-blank-line.png"


# get a device by the label (eg. one/two/three/...)
def get_device_from_label(label):
    for dev in get_devices():
        if dev[4] == label:
            return dev

# -------------------------------
# LAYOUT

# Returns styling information for a key based on its position and state.
def get_current_key_style(deck, key):
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
                device_name = device[4]
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
                    label = f"{get_volume(device)}{label_seperator}{device_label}"
            except:
                name = ""
                icon = "Empty.png"
                label = ""

    # it could probably be short but I think this is more user friendly
    elif menu == "sub-menu":
        dev = get_device_from_label(curr_device)
        # print(dev[0:2])

        if key == one_base:
            name = device_1[4]
            icon = "close-line.png"
            label = "close"
        # RNNOISE
        elif key == one_down:
            if re.match('^(hi)+', dev[0]):
                name = device_1[4]+"-"
                icon = get_button_pic(get_rnnoise(dev))
                label = "rnnoise"
            else:
                name = ""
                icon = "Empty.png"
                label = ""
        # MUTE
        elif key == one_up:
            name = device_1[4]+"+"
            icon = get_speaker_pic(dev)
            label = "mute"
        if key == two_base:
            name = device_2[4]
            icon = "Empty.png"
            label = ""
        elif key == two_down:
            name = device_2[4]+"-"
            icon = "Empty.png"
            label = ""
        # EQ
        elif key == two_up:
            if re.match('^(a|b)+', dev[0]):
                name = device_2[4]+"+"
                icon = get_button_pic(get_eq(dev))
                label = "EQ"
            else:
                name = ""
                icon = "Empty.png"
                label = ""
        elif key == three_base:
            name = device_3[4]
            icon = "Empty.png"
            label = ""
            if settings.show_device:
                device = ' '.join(str(dev[1:2]))
                label = f"Device:\n{dev[0].upper()} {dev[1]}"
            else:
                label = ""
        elif key == three_down:
            name = device_3[4]+"-"
            icon = "Empty.png"
            label = ""
        # PRIMARY
        elif key == three_up:
            if re.match('^(b|vi)+', dev[0]):
                name = device_3[4]+"+"
                icon = get_button_pic(get_primary(dev))
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
                    name = device_4[4]
                    icon = get_checkbox_pic(get_connect(dev, 'a1'))
                    label = "A1"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == four_down:
                if connection_allowed:
                    name = device_4[4]+"-"
                    icon = get_checkbox_pic(get_connect(dev, 'a2'))
                    label = "A2"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == four_up:
                if connection_allowed:
                    name = device_4[4]+"+"
                    icon = get_checkbox_pic(get_connect(dev, 'a3'))
                    label = "A3"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == five_base:
                if connection_allowed:
                    name = device_5[4]
                    icon = get_checkbox_pic(get_connect(dev, 'b1'))
                    label = "B1"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == five_down:
                if connection_allowed:
                    name = device_5[4]+"-"
                    icon = get_checkbox_pic(get_connect(dev, 'b2'))
                    label = "B2"
                else:
                    name = ""
                    icon = "Empty.png"
                    label = ""
            elif key == five_up:
                if connection_allowed:
                    name = device_5[4]+"+"
                    icon = get_checkbox_pic(get_connect(dev, 'b3'))
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

# ----------------------------------------------------------------
# LISTENER (updates the data when a change happens)

def match_device(device_type, device_id):
    for device in get_devices():
        if device[0] == device_type and device[1] == device_id:
            return device[4]

def update_volume_keys(device_type, device_id, val):
    update_key_image(deck, eval(f'{match_device(device_type, device_id)}_base'))

def update_mute_button(device_type, device_id, state):
    update_key_image(deck, one_up)

def update_connection_buttons(input_type, input_id, output_type, output_id, state, latency):
    # just update the specific row because I think it won't make a much difference
    if output_type == 'a':
        for key in [four_base, four_down, four_up]:
            update_key_image(deck, key)
    elif output_type == 'b':
        for key in [five_base, five_down, five_up]:
            update_key_image(deck, key)

def update_primary_button(device_type, device_id):
    update_key_image(deck, three_up)

def listen_socket():
    if curr_site == 'main':
        client.set_callback_function('volume', update_volume_keys)
    elif curr_site == 'sub-menu':
        client.set_callback_function('mute', update_mute_button)
        client.set_callback_function('connect', update_connection_buttons)
        client.set_callback_function('primary', update_primary_button)
    print('switched listener functions')

# PAGE CHANGER
def change_page(deck, page, device=None):
    global curr_site
    curr_site = page
    global curr_device
    curr_device = device
    for i in a:
        update_key_image(deck, i)
    listen_socket()
    print(f'changed page to {curr_site} ({curr_device})')

# UPDATE SPECIFIC KEY
def update_key_image(deck, key):
    # Determine what icon and label to use on the generated key.
    key_style = get_current_key_style(deck, key)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)
        # print(f'updating key {key}')

def round_volume(device, vol, rem, val_type='+'):
    print('rounding')
    if val_type == '-':
        return vol-rem
    else:
        return vol+(10-rem)

def check_volume_keys(deck, key_style, device):
    if key_style["name"] == f"{device[4]}+":
        print(f'{device[0:2]} +')
        if settings.round_volume:
            vol = get_volume(device)
            rem = vol % 10
            if rem == 0:
                set_vol = f'+{volume_step}'
            else:
                set_vol = round_volume(device, vol, rem, '+')
        else:
            set_vol = f'+{volume_step}'
        client.volume(device[0], device[1], set_vol)
        update_key_image(deck, eval(f'{device[4]}_base'))
    elif key_style["name"] == f"{device[4]}-":
        print(f'{device[0:2]} -')
        if settings.round_volume:
            vol = get_volume(device)
            rem = vol % 10
            print(rem)
            if rem == 0:
                set_vol = f'-{volume_step}'
            else:
                set_vol = round_volume(device, vol, rem, '-')
        else:
            set_vol = f'-{volume_step}'
        client.volume(device[0], device[1], set_vol)
        update_key_image(deck, eval(f"{device[4]}_base"))
    elif key_style["name"] == f"{device[4]}":
        change_page(deck, "sub-menu", device[4])


# KEY CALLBACK (when a key is presed)
def key_change_callback(deck, key, state):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    update_key_image(deck, key)

    if state:
        global curr_device
        key_style = get_current_key_style(deck, key)

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
                client.mute(device[0], device[1])
                print(f'{key_style["device"][0:2]} mute toggled')
            elif key_style["name"] == "two+":
                device = key_style["device"]
                client.eq(device[0], device[1])
                print(f'toggle eq ({device[0:2]})')
            elif key_style["name"] == "one-":
                device = key_style["device"]
                print(f'toggle rnnoise {device[0:2]}')
                client.rnnoise(device[0], device[1])
            elif key_style["name"] == "three+":
                device = key_style["device"]
                print(f'made device primary ({device[0:2]})')
                client.primary(device[0], device[1])
            elif key_style["name"] in ['four', 'four-', 'four+', 'five', 'five-', 'five+']:
                device = key_style["device"]
                out_device = key_style["label"].lower()
                print(f'toggling connection {device[0:2]} to {out_device}')
                client.connect(device[0], device[1], out_device[0], out_device[1])
        else:
            for device in get_devices():
                check_volume_keys(deck, key_style, device)

def get_used_keys():
    variables = []
    for name in ['one', 'two', 'three']:
        for value in ['up', 'down', 'base']:
            variables.append(eval(f'{name}_{value}'))
    return variables

def get_devices():
    devices = []
    a = range(1, 6)
    for num in a:
        devices.append(eval(f'device_{num}'))
    return devices

def update_key(key):
    update_key_image(deck, key)
    print(f'setting key {key} ({curr_site})')

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))
    print('trying to connect to client')
    try:
        global client
        client = socket.Client(listen=True)
    except:
        print('connection failed')
        sys.exit(1)
    print('connected')
 
    print('---')
    print('checking settings\n')
    init_settings()
    print('settings ready')
    print('---')

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


        listen_socket()

        # Set initial key images.
        a = range(deck.key_count())
        for key in a:
            print(f'creating key image {key}')
            update_key_image(deck, key)
        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        print('finished setup')
        print('---')
        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass


