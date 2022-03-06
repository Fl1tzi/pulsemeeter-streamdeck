import os

# Folder location of image assets used 
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
# higher cpu usage but faster data loading
use_multiprocessing = True
check_running = True

# ----------------------------------------------------------------
# CONFIGURATION

# how much to increase or decrease the gain
volume_step = 10
# the brightness of the streamdeck
brightness = 30

# show the volume step on the keys
show_volume_step = False
# show the device name on the device page
show_device = False

# [device], [(mic|speaker)], [label], [internal info (do not change)]
# just set the device to None to disable it
# example:
# device_1 = None
# it also supports \n for labels

device_1 = ['hi1', 'mic', 'LABEL', 'one']
device_2 = ['vi2', 'speaker', 'LABEL2', 'two']
device_3 = ['vi1', 'speaker', 'LABEL3', 'three']
device_4 = ['a1', 'speaker', 'LABEL4', 'four']
device_5 = ['b1', 'mic', 'LABEL5', 'five']

# the seperator used between the volume and your label (can also be \n)
label_seperator = "-"
# change the margins of the icon (you probably only want to change the first value for the size)
margins = [25, 0, 10, 0]

# remember to put the font in the assets folder
# font used in examples:
# font = "JetBrains_Mono_Medium_Nerd_Font_Complete.ttf"
font = "Roboto-Regular.ttf"

font_size = 12
