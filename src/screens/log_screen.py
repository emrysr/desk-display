# screens/log_screen.py
# This module is responsible for rendering the log messages screen.

def render(display_manager):
    """
    Renders the current log messages to the display buffer and updates.

    Args:
        display_manager: An instance of DisplayManager for drawing operations and log access.
    """
    if not display_manager.display:
        display_manager.add_log_message("Error: Display not initialized for log screen rendering.")
        return

    display_manager.clear_display_buffer()
    y_offset = 5
    for msg in display_manager.log_messages: # Access logs from display_manager instance
        display_manager.display.set_pen(display_manager.BLACK)
        display_manager.display.text(msg, 5, y_offset, scale=1) # Using scale 1 for small font
        y_offset += 15 # Line height for scale 1 text + gap
    display_manager.display.update()