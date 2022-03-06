import os

# Folder location of image assets used 
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

# only use 4 characters for the label at the standard size or shrink the font size

# how much to increase or decrease the gain
volume_step = 10
# show the volume step on the keys
show_volume_step = False

# [device], [type (mic|speaker)], [label], [internal info (do not change)]
# just set the device to None to disable it
# example:
# device_1 = None

device_1 = ['hi1', 'mic', 'Hi1', 'one']
device_2 = ['b1', 'speaker', 'B1', 'two']
device_3 = ['vi1', 'speaker', 'Vi1', 'three']
device_4 = ['a1', 'speaker', 'A1', 'four']
device_5 = ['a2', 'speaker', 'A2', 'five']

# remember to put the font in the assets folder
font = "Roboto-Regular.ttf"
font_size = 14
