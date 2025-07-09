# wifi_manager.py (Version 0.1.7 - Optimized for minimal display updates)

import network
import time
import machine

class WifiManager:
    """
    Manages Wi-Fi connections.
    Requires a DisplayManager instance for visual feedback.
    """
    def __init__(self, ssid, password, display_manager, led_pin=None):
        self.ssid = ssid
        self.password = password
        self.display_manager = display_manager 
        self.wlan = network.WLAN(network.STA_IF)
        self.led = None
        if led_pin:
            self.led = machine.Pin(led_pin, machine.Pin.OUT)
            self.led.value(0) 

        self.wlan.active(True) # Activate WLAN interface when manager is initialized

    def connect_to_wifi(self, timeout_seconds=20):
        """
        Connects to the specified Wi-Fi network.
        Does NOT provide visual feedback on screen unless there's an error.
        Logs messages to console via DisplayManager.
        """
        if self.wlan.isconnected():
            ip_info = self.wlan.ifconfig()
            self.display_manager.add_log_message(f"Already connected. IP: {ip_info[0]}")
            return True

        self.display_manager.add_log_message(f"Attempting connection to SSID: {self.ssid}...")
        
        # --- REMOVED: Initial "Connecting WiFi..." screen display ---
        # No screen update here to keep screen blank during successful connection attempt

        if self.led:
            self.led.value(1)  # Turn LED on during connection attempt

        self.wlan.connect(self.ssid, self.password)

        start_time = time.time()
        # Loop without refreshing screen, just waiting for connection
        while not self.wlan.isconnected() and (time.time() - start_time) < timeout_seconds:
            # No display updates in this loop to minimize flashes
            time.sleep(1) # Still pause to avoid busy-waiting

        if self.wlan.isconnected():
            ip_info = self.wlan.ifconfig()
            self.display_manager.add_log_message(f"WiFi Connected! IP: {ip_info[0]}")
            
            if self.led:
                self.led.value(0) # Turn LED off on success
            
            # --- REMOVED: "WiFi Connected!" screen display ---
            # main.py will now handle displaying the datetime screen on successful boot
            return True
        else:
            self.display_manager.add_log_message("WiFi Connection Failed!")
            if self.led:
                self.led.value(0) # Turn LED off on failure
            self.display_manager.show_connection_error() # ONLY display feedback on error
            return False

    def is_connected(self):
        """Checks if the Wi-Fi interface is currently connected."""
        return self.wlan.isconnected()