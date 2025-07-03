# wifi_manager.py
import network
import time
import ntptime
import machine

def connect_to_wifi(ssid, password, display=None, black_pen=None, led=None, timeout_seconds=20):
    """Connects to the specified Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    if led:
        led.value(1) # Turn on LED while connecting

    start_time = time.time()
    while not wlan.isconnected() and (time.time() - start_time) < timeout_seconds:
        print(f"Waiting for connection... {timeout_seconds - (time.time() - start_time):.0f}s remaining")
        if display and black_pen is not None: # Check if display object and color are passed
            # Update display with connection status
            display.set_pen(black_pen)
            display.clear()
            display.text("Connecting...", 5, 5, scale=1)
            display.text(f"SSID: {ssid}", 5, 20, scale=1)
            display.text(f"Time Left: {timeout_seconds - (time.time() - start_time):.0f}s", 5, 35, scale=1)
            display.update()
        time.sleep(1)

    if wlan.isconnected():
        print("--- Wi-Fi Connected Successfully! ---")
        print(f"Network Status: {wlan.status()}")
        ip_info = wlan.ifconfig()
        print(f"IP Address:      {ip_info[0]}")
        print(f"Subnet Mask:     {ip_info[1]}")
        print(f"Gateway:         {ip_info[2]}")
        print(f"DNS Server:      {ip_info[3]}")
        if led:
            led.value(0) # Turn off LED on success
        return True
    else:
        print("--- Wi-Fi Connection Failed! ---")
        if led:
            led.value(0) # Turn off LED on failure
        if display and black_pen is not None:
            display.set_pen(black_pen)
            display.clear()
            display.text("WiFi Failed!", 5, 5, scale=1)
            display.text("Check config/signal", 5, 20, scale=1)
            display.update()
            time.sleep(2)
        return False

def sync_time_ntp(display=None, black_pen=None):
    """Synchronizes the Pico's RTC with an NTP server."""
    ntp_synced = False
    try:
        print("Synchronizing time with NTP...")
        ntptime.host = "pool.ntp.org"
        ntptime.settime()
        print("Time synchronized successfully!")
        ntp_synced = True
    except Exception as e:
        print(f"Error syncing time with NTP: {e}")
        if display and black_pen is not None:
            display.set_pen(black_pen)
            display.clear()
            display.text("NTP Sync Failed!", 5, 5, scale=1)
            display.text(f"Error: {e}", 5, 20, scale=1)
            display.update()
            time.sleep(2)
    return ntp_synced