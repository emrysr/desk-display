# display_manager.py (Updated to be an orchestrator, minimal boot flashes)
import utime
from picographics import PicoGraphics, DISPLAY_INKY_PACK 
import time

class DisplayManager:
    def __init__(self):
        self.display = None
        self.log_messages = []
        self.MAX_LOG_MESSAGES = 8

        self.BLACK = 0
        self.WHITE = 15

        self.WIDTH = 296
        self.HEIGHT = 128
        
        self.init_display()

    def init_display(self):
        self.add_log_message("DisplayManager: Initializing PicoGraphics...")
        try:
            self.display = PicoGraphics(display=DISPLAY_INKY_PACK)
            self.add_log_message("DisplayManager: PicoGraphics initialized successfully.") 

            self.display.set_pen(self.WHITE)
            #self.display.clear()

        except Exception as e:
            self.add_log_message(f"DisplayManager: Error initializing display: {e}")
            self.add_log_message("DisplayManager: Please ensure PicoGraphics libraries are correctly installed and connected for Inky Pack.")
            self.display = None 

    def add_log_message(self, message):
        """Adds a message to the internal log list and prints to console."""
        timestamp = utime.localtime()
        ts_str = "{:02d}:{:02d}:{:02d}".format(timestamp[3], timestamp[4], timestamp[5])
        log_entry = f"[{ts_str}] {message}"
        self.log_messages.append(log_entry)
        if len(self.log_messages) > self.MAX_LOG_MESSAGES:
            self.log_messages.pop(0) 
        print(log_entry) # Always print to console

    def clear_display_buffer(self):
        """Clears the display buffer (sets all pixels to white) without updating."""
        if self.display:
            self.display.set_pen(self.WHITE)
            self.display.clear()

    def show_connection_error(self):
        """Displays a generic Wi-Fi connection error message."""
        if self.display:
            self.clear_display_buffer()
            self.display.set_pen(self.BLACK) 
            self.display.text("WiFi Error!", 5, 5, scale=2)
            self.display.text("Check config.toml and network", 5, 30, scale=1)
            self.display.update()
            time.sleep(1) # Small pause for visibility

    def show_ntp_error(self):
        """Displays an NTP synchronization error message."""
        if self.display:
            self.clear_display_buffer()
            self.display.set_pen(self.BLACK)
            self.display.text("NTP Error!", 5, 5, scale=2)
            self.display.text("Could not sync time.", 5, 30, scale=1)
            self.display.text("Check WiFi connection & NTP server.", 5, 45, scale=1)
            self.display.update()
            time.sleep(1) # Small pause for visibility

    # Screen-specific rendering methods are in 'screens' directory.