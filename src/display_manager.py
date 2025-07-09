# display_manager.py

import utime
from picographics import PicoGraphics, DISPLAY_INKY_PACK 
import time

class DisplayManager:
    def __init__(self):
        self.display = None
        
        # Setting WIDTH and HEIGHT for 2.9-inch Pico Inky Pack (296x128px)
        self.WIDTH = 296
        self.HEIGHT = 128
        
        self.BLACK = 0
        self.WHITE = 15

        # This line MUST be here and executed before the try/except block
        # to ensure self.log_messages exists for subsequent calls.
        self.log_messages = [] 
        self.MAX_LOG_MESSAGES = 5 

        try:
            self.display = PicoGraphics(display=DISPLAY_INKY_PACK)
            
            # --- FIX: Removed the problematic line trying to access self.display.width/height ---
            self._log("PicoGraphics initialized successfully.") 
            # --- END FIX ---

            self.display.set_pen(self.WHITE)
            self.display.clear()

        except Exception as e:
            self._log(f"Error initializing display: {e}")
            self._log("Please ensure PicoGraphics libraries are correctly installed and connected for Inky Pack.")
            self.display = None 

    def _log(self, message):
        """Internal logging to console."""
        print(message)

    def add_log_message(self, message):
        """Adds a message to the internal log list and prints to console."""
        timestamp = utime.localtime()
        ts_str = "{:02d}:{:02d}:{:02d}".format(timestamp[3], timestamp[4], timestamp[5])
        log_entry = f"[{ts_str}] {message}"
        self.log_messages.append(log_entry)
        if len(self.log_messages) > self.MAX_LOG_MESSAGES:
            self.log_messages.pop(0) 
        self._log(log_entry)

    def clear_display_full_refresh(self):
        """Clears the display buffer with a full refresh (sets all pixels to white)."""
        if self.display:
            self.display.set_pen(self.WHITE)
            self.display.clear()

    def render_log_screen(self):
        """Renders the current log messages to the display buffer."""
        if self.display:
            self.clear_display_full_refresh()
            y_offset = 5
            for msg in self.log_messages:
                self.display.set_pen(self.BLACK)
                self.display.text(msg, 5, y_offset, scale=1)
                y_offset += 15 

    def show_connection_error(self):
        """Displays a generic Wi-Fi connection error message."""
        if self.display:
            self.clear_display_full_refresh()
            self.display.set_pen(self.BLACK) 
            self.display.text("WiFi Error!", 5, 5, scale=2)
            self.display.set_pen(self.BLACK)
            self.display.text("Check config.toml and network", 5, 30, scale=1)

    def show_ntp_error(self):
        """Displays an NTP synchronization error message."""
        if self.display:
            self.clear_display_full_refresh()
            self.display.set_pen(self.BLACK)
            self.display.text("NTP Error!", 5, 5, scale=2)
            self.display.set_pen(self.BLACK)
            self.display.text("Could not sync time.", 5, 30, scale=1)
            self.display.text("Check WiFi connection & NTP server.", 5, 45, scale=1)