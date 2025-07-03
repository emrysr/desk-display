# boot.py
# This file is executed on every boot (including soft reboot)
import os
import sys
import time # Import time here for timestamp if desired, or remove timestamp

# Define a log file path
LOG_FILE = "boot_log.txt"

try:
    # Open the log file in write mode ('w') to overwrite on each boot for clean debugging.
    # Use 'a' for append mode if you want to keep logs from multiple boots.
    log_fd = open(LOG_FILE, "w")
    # Redirect stdout and stderr to the log file
    sys.stdout = log_fd
    sys.stderr = log_fd

    # Print a clear start message to the log
    print("--- Device Boot Started ---")
    print(f"Timestamp: {time.time()}") # Using time for a precise timestamp in the log

except Exception as e:
    # Fallback to serial if logging setup fails (unlikely, but good practice)
    sys.__stdout__.write(f"Error setting up boot_log.txt: {e}\r\n")
    sys.print_exception(e, sys.__stdout__)
    # Ensure stdout/stderr are restored if logging failed
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

# Now attempt to import and run your main application logic
try:
    print("Attempting to import main.py...") # Log this step
    import main # This will execute your main.py script
    print("main.py imported successfully.") # Log success
except Exception as e:
    # If an error occurs in main.py, it will be caught here and logged
    print("\n--- Error during main.py import/execution ---")
    sys.print_exception(e) # This prints the full traceback to the redirected stdout (boot_log.txt)
    # Also print to the original stdout/stderr (Thonny console) if connected, for live debugging
    sys.__stdout__.write("\n--- Error printed to Thonny console ---\r\n")
    sys.print_exception(e, sys.__stdout__)

finally:
    # IMPORTANT: Always restore stdout and stderr at the end of boot.py,
    # so subsequent Thonny interactions work normally, and to ensure log file is flushed/closed.
    if 'log_fd' in locals() and not log_fd.closed:
        log_fd.close()
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    print("--- Boot process completed or exited ---") # This message will go to Thonny console if connected