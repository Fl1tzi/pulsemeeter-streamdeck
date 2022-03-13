import os

# Folder location of image assets used 
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
check_running = True

# ----------------------------------------------------------------
# CONFIGURATION

# how much to increase or decrease the gain
volume_step = 10
# round volume (only works with 10 or 5 as volume_step)
round_volume = True
# the brightness of the streamdeck
brightness = 30

# ---
# KEY STYLING

# remember to put the font in the assets folder
# font used in examples:
font = "JetBrains_Mono_Medium_Nerd_Font_Complete.ttf"
# font = "Roboto-Regular.ttf"
text_color = "white"
inactive_text_color = "grey"
font_size = 12

# show the volume step on the keys
show_volume_step = False
# use the inactive_text_color if mute is active
show_mute_state_color = True

# shows the mute state on the key or will show a settings icon (standard icons only work with nerd fonts) (first: unmuted, second: muted)
show_mute_state_text_icon = True
mute_mic = ['', '']
mute_speaker = ['蓼', '遼']

# the seperator used between the volume and your label (can also be \n)
label_seperator = "\n "
# change the margins of the icon (you probably only want to change the first value for the size)
margins = [30, 0, 10, 0]
# margin of the title (where the volume is)
title_margin = [45, 0, 10, 0]

# ---
# DEVICE SETTINGS

# show the device name on the device page
show_device = True

# device: device type (hi|vi|a|b)
# device_id: device id (probably 1-3)
# label: what should be showed on the key (also supports \n for labels)
# type: what icon to use (mic or speaker)

# (device) (device_id) (label) (type)
device_1 = ['hi', 1, 'Hi1', 'mic']
device_2 = ['vi', 1, 'Vi1', 'speaker']
device_3 = ['vi', 2, 'Vi2', 'speaker']
device_4 = ['a', 1, 'out', 'speaker']
device_5 = ['b', 1, 'mic', 'mic']


# faq
# how can I change the icon:
# currently you look into the assets folder and put a file in there and replace it with a current one
