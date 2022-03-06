# pulsemeeter-streamdeck
pulsemeeter cli example on streamdeck

**This application uses a beta version of pulsemeeter so it is not available with the current version**

# installation
first install the dependencies using:

- `pip3 install streamdeck`
- `pip3 install pulsemeeter`

Then download all the files and go into their directory.

Finally just execute it using `python3 __main__.py`

**If it gives you an error that it couldn't open the device, you should add the udev rules.**

`sudo cp 10-streamdeck.rules /etc/udev/rules.d`

Reload the rules:

`sudo udevadm trigger`

# usage
To change your settings go into the `settings.py` file and change the values.

## examples
![pic1](https://raw.githubusercontent.com/Fl1tzi/pictures/main/pic4-streamdeck.jpeg)
![pic2](https://raw.githubusercontent.com/Fl1tzi/pictures/main/pic2-streamdeck.jpeg)
![pic3](https://raw.githubusercontent.com/Fl1tzi/pictures/main/pic3-streamdeck.jpeg)
![pic4](https://raw.githubusercontent.com/Fl1tzi/pictures/main/pic1-streamdeck.jpeg)

# thanks to:
- [abcminiuser/python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck)
- [Remix-Design/RemixIcon](https://github.com/Remix-Design/remixicon)
