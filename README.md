# Pico Inky Desk Screen

Using the pico inky to display daily info as reference

https://shop.pimoroni.com/products/pico-inky-pack


# Install

Use Pimoroni's version of micropython to get all the required packages 'baked in'

https://github.com/pimoroni/pimoroni-pico/releases

Copy all the files from src to the pico.


# Config

Copy src/WIFI_CONFIG.example.py to src/WIFI_CONFIG.py

Edit the file to match your local Wifi AP

> TODO: add more config options for local timezones and daylight savings etc - DEFAULT = Europe/London


# Usage

Hit the reboot button.

The boot.py will connect to your wifi before main.py starts to update the display.


# Debugging

Device boot errors written to boot_log.txt

When developing you can run the main.py in the REPL.



