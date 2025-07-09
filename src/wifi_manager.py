# wifi_manager.py (Version 0.1.4 - `country` parameter removed permanently)

import network
import time
import machine

class WifiManager:
    """
    Manages Wi-Fi connections.
    Requires a DisplayManager instance for visual feedback.
    """
    def __init__(self, ssid, password, display_manager, led_pin=None): # 'country' parameter removed from signature
        self.ssid = ssid
        self.password = password
        self.display_manager = display_manager 
        self.wlan = network.WLAN(network.STA_IF)
        self.led = None
        if led_pin:
            self.led = machine.Pin(led_pin, machine.Pin.OUT)
            self.led.value(0) 

        self.wlan.active(True) # Activate WLAN interface when manager is initialized
        # The wlan.config(country=...) line has been permanently removed.

    def connect_to_wifi(self, timeout_seconds=20):
        """
        Connects to the specified Wi-Fi network.
        Provides visual feedback via the DisplayManager and an optional LED.
        """
        if self.wlan.isconnected():
            ip_info = self.wlan.ifconfig()
            self.display_manager.add_log_message(f"Already connected. IP: {ip_info[0]}")
            return True

        self.display_manager.add_log_message(f"Connecting to WiFi SSID: {self.ssid}...")
        
        self.display_manager.clear_display_full_refresh()
        self.display_manager.display.set_pen(self.display_manager.BLACK)
        self.display_manager.display.text("Connecting WiFi...", 5, 5, scale=2)
        self.display_manager.display.text(f"SSID: {self.ssid}", 5, 30, scale=1)
        self.display_manager.display.update()

        if self.led:
            self.led.value(1) 

        self.wlan.connect(self.ssid, self.password)

        start_time = time.time()
        while not self.wlan.isconnected() and (time.time() - start_time) < timeout_seconds:
            remaining_time = timeout_seconds - (time.time() - start_time)
            
            self.display_manager.clear_display_full_refresh()
            self.display_manager.display.set_pen(self.display_manager.BLACK)
            self.display_manager.display.text("Connecting WiFi...", 5, 5, scale=2)
            self.display_manager.display.text(f"SSID: {self.ssid}", 5, 30, scale=1)
            self.display_manager.display.text(f"Time Left: {remaining_time:.0f}s", 5, 60, scale=1)
            self.display_manager.display.update()
            
            time.sleep(1)

        if self.wlan.isconnected():
            ip_info = self.wlan.ifconfig()
            self.display_manager.add_log_message(f"WiFi Connected! IP: {ip_info[0]}")
            
            if self.led:
                self.led.value(0) 
            
            self.display_manager.clear_display_full_refresh()
            self.display_manager.display.set_pen(self.display_manager.BLACK)
            self.display_manager.display.text("WiFi Connected!", 5, 5, scale=2)
            self.display_manager.display.update()
            time.sleep(1) 
            
            return True
        else:
            self.display_manager.add_log_message("WiFi Connection Failed!")
            if self.led:
                self.led.value(0) 
            self.display_manager.show_connection_error() 
            return False

    def is_connected(self):
        """Checks if the Wi-Fi interface is currently connected."""
        return self.wlan.isconnected()