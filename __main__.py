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
    
    device_1.append(1)
    device_2.append(2)
    device_3.append(3)
    device_4.append(4)
    device_5.append(5)

    global can_round_volume
    if volume_step in [5, 10]: can_round_volume = True
    else: can_round_volume = False

    for i in [device_1, device_2, device_3, device_4, device_5]:
        if type(i[1]) == int:
            i[1] = str(i[1])

# \033[91m
# \033[0m
# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename, font_filename, label_text, name, text_color):
    icon = Image.open(icon_filename)
    if name in ['1', '2', '3', '4', '5'] and curr_site == 'main':
        margins = settings.title_margin
    else:
        margins = settings.margins
    image = PILHelper.create_scaled_image(deck, icon, margins=margins)

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(font_filename, settings.font_size)
    except:
        print('the font you selected is not available in the Assets folder')
        sys.exit(1)
    
    if text_color != None:
        fill = text_color
    else:
        fill = settings.text_color
    draw.text((image.width / 2, image.height - 55), text=label_text, font=font, anchor="ms", fill=fill)

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
    return str2bool(val)

def get_eq(device):
    # print('getting eq')
    val = client.config[device[0]][device[1]]['use_eq']
    return str2bool(val)

def get_rnnoise(device):
    # print('getting rnnoise')
    val = client.config[device[0]][device[1]]['use_rnnoise']
    return str2bool(val)

def get_primary(device):
    # print('getting primary')
    val = client.config[device[0]][device[1]]['primary']
    return str2bool(val)

def get_connect(device, device2):
    val = client.config[device[0]][device[1]][device2]
    return str2bool(val)

# ------------------------------
# ICON GENERATORS

def str2bool(value):
    if type(value) == bool:
        return value
    else:
        if value in ['True', 'true']: return True
        elif value in ['False', 'false']: return False

# get the picture for the speaker
def get_speaker_pic(device, state):
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

def get_text_mute_icon(device, state):
    if device[3].lower() == 'mic':
        if state == True: return settings.mute_mic[1]
        else: return settings.mute_mic[0]
    elif device[3].lower() == 'speaker':
        if state == True: return settings.mute_speaker[1]
        else: return settings.mute_speaker[0]
    else:
        return ''

        

# -------------------------------
# LAYOUT

# Returns styling information for a key based on its position and state.
def get_current_key_style(deck, key, value=None):
    menu = curr_site

    if key in get_unused_keys():
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
    text_color = None

    if menu == "main":
        devices = get_devices()
        for device in devices:
            try:
                device_group = device[4]
                device_label = device[2]

                if key == eval(f'key{device_group}_up'):
                    name = f"{device_group}+"
                    icon = "volume-up-line.png"
                    if settings.show_volume_step:
                        label = "+ "+str(volume_step)
                    else:
                        label = "+"

                elif key == eval(f'key{device_group}_down'):
                    name = f"{device_group}-"
                    icon = "volume-down-line.png"
                    if settings.show_volume_step:
                        label = "- "+str(volume_step)
                    else:
                        label = "-"

                elif key == eval(f'key{device_group}_base'):
                    name = f'{device_group}'
                    ismuted = get_mute(device)
                    icon = "sound-module-fill.png"
                    if settings.show_mute_state_text_icon:
                        mute_icon = get_text_mute_icon(device, ismuted)+' '
                    else:
                        mute_icon = ''
                    if ismuted == True and settings.show_mute_state_color == True:
                        text_color = settings.inactive_text_color
                    if value is None:
                        label = f"{mute_icon}{get_volume(device)}{settings.label_seperator}{device_label}"
                    else:
                        label = f"{mute_icon}{value}{settings.label_seperator}{device_label}"
            except:
                name = ""
                icon = "Empty.png"
                label = ""

    # it could probably be short but I think this is more user friendly
    elif menu == "sub-menu":
        dev = get_device_from_label(curr_device)
        # print(dev[0:2])

        if key == key1_base:
            name = str(device_1[4])
            icon = "close-line.png"
            label = "close"
        # RNNOISE
        elif key == key1_down:
            if re.match('^(hi)+', dev[0]):
                name = str(device_1[4])+"-"
                icon = get_button_pic(get_rnnoise(dev))
                label = "rnnoise"
            else:
                name = ""
                icon = "Empty.png"
                label = ""
        # MUTE
        elif key == key1_up:
            name = str(device_1[4])+"+"
            if value != None:
                icon = get_speaker_pic(dev, value)
            else:
                icon = get_speaker_pic(dev, get_mute(dev))
            label = "mute"
        elif key == key2_base:
            name = str(device_2[4])
            icon = "Empty.png"
            label = ""
        elif key == key2_down:
            name = str(device_2[4])+"-"
            icon = "Empty.png"
            label = ""
        # EQ
        elif key == key2_up:
            if re.match('^(a|b)+', dev[0]):
                name = str(device_2[4])+"+"
                if value != None:
                    icon = get_button_pic(value)
                else:
                    icon = get_button_pic(get_eq(dev))
                label = "EQ"
            else:
                name = ""
                icon = "Empty.png"
                label = ""
        elif key == key3_base:
            name = device_3[4]
            icon = "Empty.png"
            label = ""
            if settings.show_device:
                device = ' '.join(str(dev[1:2]))
                label = f"Device:\n{dev[0].upper()} {dev[1]}"
            else:
                label = ""
        elif key == key3_down:
            name = str(device_3[4])+"-"
            icon = "Empty.png"
            label = ""
        # PRIMARY
        elif key == key3_up:
            if re.match('^(b|vi)+', dev[0]):
                name = str(device_3[4])+"+"
                if value != None:
                    print('using value')
                    icon = get_button_pic(value)
                else:
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
            
            buttons = {'key4_base': ['4', 'a1'], 'key4_down': ['4', 'a2'], 'key4_up': ['4', 'a3'],
                    'key5_base': ['5', 'b1'], 'key5_down': ['5', 'b2'], 'key5_up': ['5', 'b3']}
            
            if connection_allowed:
                for dict_name, variables in buttons.items():
                    if key == eval(dict_name):
                        val = dict_name.split('_')
                        if val[-1]== 'base': val = ''
                        elif val[-1] == 'up': val = '+'
                        elif val[-1] == 'down': val = '-'
                        name = f'{str(eval(f"device_{variables[0]}")[4])}{val}'
                        if value != None:
                            icon = get_checkbox_pic(value)
                        else:
                            icon = get_checkbox_pic(get_connect(dev, variables[1]))
                        label = variables[1].upper()
                        break
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
        "text_color": text_color
    }

# ----------------------------------------------------------------
# LISTENER (updates the data when a change happens)

def match_device(device_type, device_id):
    for device in get_devices():
        if device[0] == device_type and device[1] == device_id:
            return device[4]

def update_volume_keys(device_type, device_id, val):
    print('callback volume')
    update_key_image(deck, eval(f'key{match_device(device_type, device_id)}_base'), val)

def update_mute_button(device_type, device_id, state):
    print('callback volume')
    update_key_image(deck, key1_up, str2bool(state))

def update_connection_buttons(input_type, input_id, output_type, output_id, state, latency):
    print('callback connection')
    state = str2bool(state)
    if output_type == 'a':
        if output_id == 1: update_key_image(deck, key4_base, state)
        elif output_id == 2: update_key_image(deck, key4_down, state)
        elif output_id == 3: update_key_image(deck, key4_up, state)
    elif output_type == 'b':
        if output_id == 1: update_key_image(deck, key5_base, state)
        elif output_id == 2: update_key_image(deck, key5_down, state)
        elif output_id == 3: update_key_image(deck, key5_up, state)

def update_primary_button(device_type, device_id):
    print('callback primary')
    update_key_image(deck, key3_up)

def listen_socket():
    if curr_site == 'main':
        print('main')
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
    update_keys = range(deck.key_count())
    for key in update_keys:
        update_key_image(deck, key)
    print('---')
    listen_socket()
    print(f'changed page to {curr_site} ({curr_device})')

# UPDATE SPECIFIC KEY
def update_key_image(deck, key, value=None):
    # Determine what icon and label to use on the generated key.
    if value == None:
        key_style = get_current_key_style(deck, key)
    else:
        key_style = get_current_key_style(deck, key, value)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"], key_style["name"], key_style["text_color"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)
        # print(f'updating key {key}')

def round_volume(device, vol, val_type='+'):
    vol = get_volume(device)
    if volume_step == 10: allowed = [0]
    elif volume_step == 5: allowed = [0, 5]

    rem = vol % volume_step
    if rem in allowed:
        return f'{val_type}{volume_step}'
    else:
        if val_type == '-':
            return vol-rem
        else:
            return vol+(volume_step-rem)

def check_volume_keys(deck, key_style, device):
    if key_style["name"] == f"{device[4]}+":
        print(f'{device[0] + device[1]} +')
        if settings.round_volume and can_round_volume:
            vol = get_volume(device)
            set_vol = round_volume(device, vol, '+')
        else:
            set_vol = f'+{volume_step}'
        server_return = client.volume(device[0], device[1], set_vol)
        server_return = server_return.split(' ')
        update_key_image(deck, eval(f'key{device[4]}_base'), server_return[-1])
    elif key_style["name"] == f"{device[4]}-":
        print(f'{device[0] + device[1]} -')
        if settings.round_volume and can_round_volume:
            vol = get_volume(device)
            set_vol = round_volume(device, vol, '-')
        else:
            set_vol = f'-{volume_step}'
        server_return = client.volume(device[0], device[1], set_vol)
        server_return = server_return.split(' ')
        update_key_image(deck, eval(f"key{device[4]}_base"), server_return[-1])
    elif key_style["name"] == f"{device[4]}":
        change_page(deck, "sub-menu", device[4])


# KEY CALLBACK (when a key is presed)
def key_change_callback(deck, key, state):
    # Print new key state
    # print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

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
            if key_style["name"] == "1":
                change_page(deck, "main")

            elif key_style["name"] == "1+":
                device = key_style["device"]
                server_return = client.mute(device[0], device[1])
                print(f'{device[0]}{device[1]} mute')

            elif key_style["name"] == "2+":
                device = key_style["device"]
                client.eq(device[0], device[1])
                print(f'{device[0]}{device[1]} eq')

            elif key_style["name"] == "1-":
                device = key_style["device"]
                client.rnnoise(device[0], device[1])
                print(f'{device[0]}{device[1]} rnnoise')

            elif key_style["name"] == "3+":
                device = key_style["device"]
                client.primary(device[0], device[1])
                print(f'{device[0]}{device[1]} primary')

            elif key_style["name"] in ['4', '4-', '4+', '5', '5-', '5+']:
                device = key_style["device"]
                out_device = key_style["label"].lower()
                client.connect(device[0], device[1], out_device[0], out_device[1])
                print(f'connect {device[0]}{device[1]} to {out_device[0]}{out_device[1]}')
        else:
            for device in get_devices():
                check_volume_keys(deck, key_style, device)

def get_unused_keys():
    variables = []
    if curr_site == 'sub-menu':
        for key in [key2_base, key2_down, key3_down]:
            variables.append(key)
    return variables

def get_devices():
    devices = []
    a = range(1, 6)
    for num in a:
        devices.append(eval(f'device_{num}'))
    return devices

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
        global key1_up
        key1_up = deck.key_count() - 15
        global key1_down
        key1_down = deck.key_count() - 10
        global key1_base
        key1_base = deck.key_count() - 5
        global key2_up
        key2_up = deck.key_count() - 14
        global key2_down
        key2_down = deck.key_count() - 9
        global key2_base
        key2_base = deck.key_count() - 4
        global key3_up
        key3_up = deck.key_count() - 13
        global key3_down
        key3_down = deck.key_count() - 8
        global key3_base
        key3_base = deck.key_count() - 3
        global key4_up 
        key4_up = deck.key_count() - 12
        global key4_down
        key4_down = deck.key_count() - 7
        global key4_base
        key4_base = deck.key_count() - 2
        global key5_up 
        key5_up = deck.key_count() - 11
        global key5_down
        key5_down = deck.key_count() - 6
        global key5_base
        key5_base = deck.key_count() - 1

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
        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass
