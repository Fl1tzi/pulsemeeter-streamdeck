# thanks to remixicon.com for creating the beautiful icons!

# THANKS FOR USING MY CODE (:
# GitHub: https://github.com/Fl1tzi

import yaml
import os
import threading
import sys
import re

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from packaging import version
from textwrap import wrap

from pulsemeeter import socket

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
BACKUP_FONT = "Assets/Roboto-Regular.ttf"
CONFIG_FILE = 'settings.yaml'


# this basically checks every value if they are correct
def init_settings(deck):
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

    # this makes the config global and reads it 
    global config
    config = read_config()
    
    # with open(SYNC_CONFIG, 'r') as file:
    #    try:
    #        sync_config = yaml.safe_load(file)
    #    except yaml.YAMLError as ex:
    #        printS(ex)
    #        raise
    
    # this appends items which are not synced with the standard config (adds them to the end)
    #update_value = []
    #for name, value in sync_config.items():
    #    try:
    #        config[name]
    #    except:
    #        update_value.append(f"\n{name}: {value}")
    
    # checks if there are any values to update
    #if len(update_value) != 0:
    #    printS('syncing config')
    #    printS('appending to file')
        # print(update_values)
        #config["config_version"] = f'"{VERSION}"'
    #    try:
    #        with open(CONFIG_FILE, 'a') as file:
    #            file.write(f'\n# ---\n# version: {VERSION} update')
    #            file.writelines(update_value)
    #
    #    except Exception as ex:
    #        printS('could not update config')
    #        printS(ex)

        # this to update the config
    #    config = read_config()
    

    # values to check with type
    validate_values= {
        '["check_running"]': bool, 
        '["device_1"]["id"]': int,
        '["show_device"]': bool, 
        '["show_volume_step"]': bool, 
        '["round_volume"]': bool, 
        '["show_mute_state_color"]': bool, 
        '["show_mute_state_text_icon"]': bool,
        '["brightness"]': int,
        '["volume_step"]': int,
        '["font_size"]': int,
        '["font"]': str,
        '["text_color"]': str,
        '["inactive_text_color"]': str,
        '["mute_mic_icons"][0]': str,
        '["mute_mic_icons"][1]': str,
        '["mute_speaker_icons"][0]': str,
        '["mute_speaker_icons"][1]': str
        }
    
    # add devices to check
    for num in range(1, 6):
        validate_values[f'["device_{num}"]["group"]'] = str
        validate_values[f'["device_{num}"]["id"]'] = int
        validate_values[f'["device_{num}"]["label"]'] = str
        validate_values[f'["device_{num}"]["type"]'] = str
    
    for value in ['regular', 'title']:
        for num in range(0, 4):
            validate_values[f'["margins"]["{value}"][{num}]'] = int
    
    # validate everything and if there is an error print it in console and on the stream deck
    # it sure is a little big ugly but works fine for every error
    for value, val_type in validate_values.items(): 
        try:
            if type(eval(f'config{value}')) != val_type:
                # this happens if the value has the wrong type
                error_type = 1
            else:
                continue
        except:
            # this happens when the value could not be located
            error_type = 2

        if val_type.__name__ == 'bool':
            val_help = 'yes | no\ntrue | false\n'
        elif val_type.__name__ == 'int':
            val_help = 'number'
        elif val_type.__name__ == 'str':
            val_help = 'text'
        else:
            val_help = ''

        output = value.replace('][', '-> ').replace('"', '').replace(']', ')').replace('[', '(')

        out_print = f'config value {output} has to be a {val_type.__name__} ({val_help})'

        # this renders the output when an error happens
        printS(f"\033[91m{out_print}\033[0m")
        for key in range(deck.key_count()):
            text_color = "white"
            if key == key1_up:
                text = "CONFIG\nERROR"
            elif key == key2_up:
                # doesn't this look beautiful
                text = "\n".join(wrap(output.replace("->", "\n->").replace("(", "").replace(")", ""), 10))
                text_color = "yellow"
            elif key == key1_down:
                text = "value needs\nto be:"
            elif key == key2_down:
                text = val_type.__name__
                text_color = "yellow"
            elif key == key3_down:
                text = val_help
                text_color = "yellow"
            elif key == key5_base:
                text = "more help?\nAsk on\nPulsemeeter\nDiscord"
            elif key == key4_base:
                text = "if you updated\nyou may need\nto add\nthis value"
            elif key == key3_up:
                if error_type == 2:
                    text = "could not get\noption"
                elif error_type == 1:
                    text = "wrong\nvalue type"
                text_color = "yellow"
            else:
                text = ""
            image = render_error(deck, text, text_color)
            with deck:
                deck.set_key_image(key, image)
        printS('closing deck')
        deck.close()
        client.close_connection()
        sys.exit(1)
    
    # try to add all devices (should error if device does not exist)
    try:
        global device_1
        global device_2
        global device_3
        global device_4
        global device_5
        device_1 = config['device_1']
        device_2 = config['device_2']
        device_3 = config['device_3']
        device_4 = config['device_4']
        device_5 = config['device_5']
    except:
        printS(f'Could not find all devices in settings (5 devices needed).')
        deck.close()
        client.close_connection()
        sys.exit(1)
    
    # this checks if the font selected in config is available
    try:
        config['font'] = ImageFont.truetype(config['font'], config['font_size'])
    except:
        print('STREAMDECK: the font you selected could not be found')
        print('STREAMDECK: reverting to backup font')
        try:
            config['font'] = ImageFont.truetype(BACKUP_FONT)
        except Exception as ex:
            printS('STREAMDECK: could not load backup font')
            printS(ex) 
            sys.exit(1)
    
    
    device_1['int_id'] = 1
    device_2['int_id'] = 2
    device_3['int_id'] = 3
    device_4['int_id'] = 4
    device_5['int_id'] = 5

    global can_round_volume
    if config["volume_step"] in [5, 10]: can_round_volume = True
    else: can_round_volume = False

    for i in [device_1, device_2, device_3, device_4, device_5]:
        if type(i['id']) == int:
            i['id'] = str(i['id'])

def read_config():
    with open(CONFIG_FILE, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as ex:
            printS('YAML ERROR:')
            printS(ex)

def render_error(deck, label_text, text_color):
    # icon = Image.open(os.path.join(ASSETS_PATH, "Empty.png"))
    # image = PILHelper.create_scaled_image(deck, icon, (0, 0, 0, 0))
    image = Image.new("RGB", (100, 100), "black")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(BACKUP_FONT, 15)
    draw.text((image.width / 2, image.height - 70), text=label_text, font=font, anchor="ms", fill=text_color)
    return PILHelper.to_native_format(deck, image)

def render_key_image(deck, icon_filename, label_text, name, text_color):
    if name in ['1', '2', '3', '4', '5'] and curr_site == 'main':
        margins = config['margins']['title']
    else:
        margins = config['margins']['regular']
    
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=margins)
    font = config['font']

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
            
    if text_color != None:
        fill = text_color
    else:
        fill = config['text_color']
    draw.text((image.width / 2, image.height - 55), text=label_text, font=font, anchor="ms", fill=fill)

    return PILHelper.to_native_format(deck, image)

# -------------------------------
# CONFIG

def get_volume(device):
    # print('getting volume')
    val = client.config[device['group']][device['id']]['vol']
    return int(val)

def get_mute(device):
    # print('getting mute')
    val = client.config[device['group']][device['id']]['mute']
    return str2bool(val)

def get_eq(device):
    # print('getting eq')
    val = client.config[device['group']][device['id']]['use_eq']
    return str2bool(val)

def get_rnnoise(device):
    # print('getting rnnoise')
    val = client.config[device['group']][device['id']]['use_rnnoise']
    return str2bool(val)

def get_primary(device):
    # print('getting primary')
    val = client.config[device['group']][device['id']]['primary']
    return str2bool(val)

def get_connect(device, device2):
    val = client.config[device['group']][device['id']][device2]
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
    device_type = device['type'].lower()
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
        if dev['int_id'] == label:
            return dev

def get_text_mute_icon(device, state):
    if device['type'].lower() == 'mic':
        if state == True: return config['mute_mic_icons'][1]
        else: return config['mute_mic_icons'][0]
    elif device['type'].lower() == 'speaker':
        if state == True: return config['mute_speaker_icons'][1]
        else: return config['mute_speaker_icons'][0]
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

    dev = None
    text_color = None

    if menu == "main":
        for device in get_devices():
            if key == eval(f'key{device["int_id"]}_up'):
                name = f"{device['int_id']}+"
                icon = "volume-up-line.png"

                if config['show_volume_step'] == True:
                    label = "+ "+str(config['volume_step'])
                else:
                    label = "+"

            elif key == eval(f'key{device["int_id"]}_down'):
                name = f"{device['int_id']}-"
                icon = "volume-down-line.png"

                if config['show_volume_step'] == True:
                    label = "- "+str(config["volume_step"])
                else:
                    label = "-"

            elif key == eval(f'key{device["int_id"]}_base'):
                name = f'{device["int_id"]}'
                ismuted = get_mute(device)
                icon = "sound-module-fill.png"
                if config['show_mute_state_text_icon'] == True:
                    mute_icon = get_text_mute_icon(device, ismuted)+' '
                else:
                    mute_icon = ''
                if ismuted == True and config['show_mute_state_color'] == True:
                    text_color = config['inactive_text_color']
                if value is None:
                    label = f"{mute_icon}{get_volume(device)}{config['label_seperator']}{device['label']}"
                else:
                    label = f"{mute_icon}{value}{config['label_seperator']}{device['label']}"

    # it could probably be short but I think this is more user friendly
    elif menu == "sub-menu":
        dev = get_device_from_label(curr_device)
        # print(dev[0:2])

        if key == key1_base:
            name = str(device_1['int_id'])
            icon = "close-line.png"
            label = "close"
        # RNNOISE
        elif key == key1_down:
            if re.match('^(hi)+', dev['group']):
                name = str(device_1['int_id'])+"-"
                icon = get_button_pic(get_rnnoise(dev))
                label = "rnnoise"
            else:
                name = ""
                icon = "Empty.png"
                label = ""
        # MUTE
        elif key == key1_up:
            name = str(device_1['int_id'])+"+"
            if value != None:
                icon = get_speaker_pic(dev, value)
            else:
                icon = get_speaker_pic(dev, get_mute(dev))
            label = "mute"
        elif key == key2_base:
            name = str(device_2['int_id'])
            icon = "Empty.png"
            label = ""
        elif key == key2_down:
            name = str(device_2['int_id'])+"-"
            icon = "Empty.png"
            label = ""
        # EQ
        elif key == key2_up:
            if re.match('^(a|b)+', dev['group']):
                name = str(device_2['int_id'])+"+"
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
            name = device_3['int_id']
            icon = "Empty.png"
            label = ""
            if config['show_device']:
                # device = ' '.join(str(dev[1:2]))
                device = f'{dev["group"]} {dev["id"]}'
                label = f"Device:\n{dev['group'].upper()} {dev['id']}"
            else:
                label = ""
        elif key == key3_down:
            name = str(device_3['int_id'])+"-"
            icon = "Empty.png"
            label = ""
        # PRIMARY
        elif key == key3_up:
            if re.match('^(b|vi)+', dev['group']):
                name = str(device_3['int_id'])+"+"
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
            if re.match('^(hi|vi)+', dev['group']):
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
                        name = f'{str(eval(f"device_{variables[0]}")["int_id"])}{val}'
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
        "icon": os.path.join(ASSETS_PATH, icon),
        "label": label,
        "menu": menu,
        "device": dev, 
        "text_color": text_color
    }

# ----------------------------------------------------------------
# LISTENER (updates the data when a change happens)

def match_device(device_type, device_id):
    for device in get_devices():
        if device['group'] == device_type and device['id'] == device_id:
            return device['int_id']

def update_volume_keys(device_type, device_id, val):
    # printS('callback volume')
    update_key_image(deck, eval(f'key{match_device(device_type, device_id)}_base'), val)

def update_mute_button(device_type, device_id, state):
    # printS('callback mute')
    update_key_image(deck, key1_up, str2bool(state))

def update_connection_buttons(input_type, input_id, output_type, output_id, state, latency):
    printS('callback connection')
    state = str2bool(state)
    output_id = int(output_id)
    if output_type == 'a':
        if output_id == 1: update_key_image(deck, key4_base)
        elif output_id == 2: update_key_image(deck, key4_down)
        elif output_id == 3: update_key_image(deck, key4_up)
    elif output_type == 'b':
        if output_id == 1: update_key_image(deck, key5_base)
        elif output_id == 2: update_key_image(deck, key5_down)
        elif output_id == 3: update_key_image(deck, key5_up)

def update_primary_button(device_type, device_id):
    printS('callback primary')
    update_key_image(deck, key3_up)

def listen_socket():
    if curr_site == 'main':
        client.set_callback_function('volume', update_volume_keys)
    elif curr_site == 'sub-menu':
        client.set_callback_function('mute', update_mute_button)
        client.set_callback_function('connect', update_connection_buttons)
        client.set_callback_function('primary', update_primary_button)
    if log == True:
        printS('switched listener functions')

# PAGE CHANGER
def change_page(deck, page, device=None):
    global curr_site
    curr_site = page
    global curr_device
    curr_device = device
    update_keys = range(deck.key_count())
    for key in update_keys:
        update_key_image(deck, key)
    listen_socket()
    printS(f'changed page to {curr_site} ({curr_device})')

# UPDATE SPECIFIC KEY
def update_key_image(deck, key, value=None):
    # Determine what icon and label to use on the generated key.
    if value == None:
        key_style = get_current_key_style(deck, key)
    else:
        key_style = get_current_key_style(deck, key, value)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["label"], key_style["name"], key_style["text_color"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)
        # print(f'updating key {key}')

def round_volume(device, vol, val_type='+'):
    vol = get_volume(device)
    if config['volume_step'] == 10: allowed = [0]
    elif config['volume_step'] == 5: allowed = [0, 5]

    rem = vol % config['volume_step']
    if rem in allowed:
        return f'{val_type}{config["volume_step"]}'
    else:
        if val_type == '-':
            return vol-rem
        else:
            return vol+(config["volume_step"]-rem)

def check_volume_keys(deck, key_style, device):
    if key_style["name"] == f"{device['int_id']}+":
        # print(f'{device["group"] + device["id"]} +')
        if config['round_volume'] == True and can_round_volume:
            vol = get_volume(device)
            set_vol = round_volume(device, vol, '+')
        else:
            set_vol = f'+{config["volume_step"]}'
        server_return = client.volume(device['group'], device['id'], set_vol).split(' ')
        update_key_image(deck, eval(f'key{device["int_id"]}_base'), server_return[-1])
    elif key_style["name"] == f"{device['int_id']}-":
        # print(f'{device["group"] + device["id"]} -')
        if config['round_volume'] == True and can_round_volume:
            vol = get_volume(device)
            set_vol = round_volume(device, vol, '-')
        else:
            set_vol = f'-{config["volume_step"]}'
        server_return = client.volume(device['group'], device['id'], set_vol).split(' ')
        update_key_image(deck, eval(f"key{device['int_id']}_base"), server_return[-1])
    elif key_style["name"] == f"{device['int_id']}":
        change_page(deck, "sub-menu", device['int_id'])


# KEY CALLBACK (when a key is presed)
def key_change_callback(deck, key, state):
    # Print new key state

    if log == True:
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
            if key_style["name"] == "1":
                change_page(deck, "main")

            elif key_style["name"] == "1+":
                device = key_style["device"]
                server_return = client.mute(device['group'], device['id'])
                if log == True:
                    printS(f'{device["group"]}{device["id"]} mute')

            elif key_style["name"] == "2+":
                device = key_style["device"]
                client.eq(device['group'], device['id'])
                if log == True:
                    printS(f'{device["group"]}{device["id"]} eq')

            elif key_style["name"] == "1-":
                device = key_style["device"]
                client.rnnoise(device['group'], device['id'])
                if log == True:
                    printS(f'{device["group"]}{device["id"]} rnnoise')

            elif key_style["name"] == "3+":
                device = key_style["device"]
                client.primary(device['group'], device['id'])
                if log == True:
                    printS(f'STREAMDECK: {device["group"]}{device["id"]} primary')

            elif key_style["name"] in ['4', '4-', '4+', '5', '5-', '5+']:
                device = key_style["device"]
                out_device = key_style["label"].lower()
                client.connect(device['group'], device['id'], out_device[0], out_device[1])
                if log == True:
                    printS(f'connect {device["group"]}{device["id"]} to {out_device[0]}{out_device[1]}')
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

def printS(string):
    print(f'STREAMDECK: {string}')

def start_streamdeck(cl, loglevel):
    stremdecks = DeviceManager().enumerate()

    global client
    client = cl

    global log
    if loglevel > 1 : log = True
    else: log = False

    global deck


    for index, deck in enumerate(streamdecks):
        try:
            deck.open()
        except Exception as ex:
            printS(ex)
            printS('please try to reconnect your stream deck')
            client.close_connection()
            sys.exit(1)
        deck.reset()

        init_settings(deck)

        deck.set_brightness(config["brightness"])

        global curr_site
        curr_site = 'main'

        global curr_device
        curr_device = None

        listen_socket()

        printS('creating key images')
        for key in range(deck.key_count()):
            update_key_image(deck, key)
        deck.set_key_callback(key_change_callback)

        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    printS("Found {} Stream Deck(s).\n".format(len(streamdecks)))
    printS('trying to connect to client')
    try:
        cl = socket.Client(listen=True)
    except:
        printS('connection failed')
        sys.exit(1)
    printS('connected')

    loglevel = 2
 
    start_streamdeck(cl, loglevel)
