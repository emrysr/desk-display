from picographics import PicoGraphics, DISPLAY_INKY_PACK
import time
from pimoroni import Button

# Initialize the display using the correct Pico Inky Pack configuration
display = PicoGraphics(display=DISPLAY_INKY_PACK)

# You can change the update speed (0=slowest, 3=fastest, often 2 or 3 is good for clearing)
display.set_update_speed(2)

# Define colours (pen values) for the Pico Inky Pack
# 0 is black, 15 is white (for this specific display, these are often the default values in PicoGraphics)
BLACK = 0
WHITE = 15

# Optional: Define buttons if you have them on your Pico Inky Pack
# button_a = Button(12)
# button_b = Button(13)
# button_c = Button(14)

print("Clearing Inky Pack to white...")
display.set_pen(WHITE) # Set the pen to white
display.clear()        # Fill the entire display with the current pen colour
display.update()       # Send the updated buffer to the display
time.sleep(1)

print("Drawing some text...")
display.set_pen(BLACK) # Set the pen to black for text
display.set_font("bitmap8") # Set a font (bitmap8 is a common built-in font)
display.text("Hello Pico Inky!", 10, 10, scale=2) # Text: (text, x, y, wrap, scale)
display.text("Pimoroni MicroPython", 10, 30, scale=1)

# You can draw shapes too!
display.set_pen(BLACK)
display.rectangle(5, 50, 100, 20) # (x, y, width, height)

display.update() # Refresh the display to show the text and rectangle
time.sleep(5)

print("Clearing Inky Pack to black...")
display.set_pen(BLACK) # Set the pen to black
display.clear()        # Fill the entire display with the current pen colour
display.update()       # Send the updated buffer to the display
time.sleep(1)

print("Done!")