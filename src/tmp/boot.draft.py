# boot.py (Version 0.1.3)
# This file is executed on every boot (including soft reboot)

# This version of boot.py will only open and write to 'boot_log.txt'
# if an error occurs during the import/execution of main.py.
# This prevents file system activity during the sensitive early boot phase
# that could interfere with Wi-Fi initialization.

import sys
import time # For timestamping the error log

class BootManager:
    """
    Manages the initial boot process, focusing on conditionally logging
    errors during main.py execution to a file.
    """
    def __init__(self, log_file="boot_log.txt"):
        self.log_file = log_file
        # Store original stdout/stderr for fallback/console output
        self._original_stdout = sys.stdout 
        self._original_stderr = sys.stderr
        # File descriptor for log will only be opened if an error occurs
        self.log_fd = None

    def _setup_console_output(self):
        """
        Ensures console output is directed to Thonny/serial.
        (No file redirection here, only in case of error).
        """
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self._original_stdout.write("\n--- Device Boot Initiated ---\r\n") # This goes to console

    def _open_error_log_file(self):
        """
        Attempts to open the dedicated error log file in append mode.
        """
        try:
            # Use 'a' for append mode, less disruptive than 'w'
            self.log_fd = open(self.log_file, "a")
            self.log_fd.write(f"\n--- Critical Boot Error: {time.time()} ---\n")
            self._original_stdout.write(f"Error log file '{self.log_file}' opened for writing.\r\n")
            return True
        except Exception as e:
            self._original_stdout.write(f"CRITICAL: Could not open boot error log file: {e}\r\n")
            sys.print_exception(e, self._original_stdout)
            self.log_fd = None # Ensure it's None if opening failed
            return False

    def _run_main_application(self):
        """
        Attempts to import and execute main.py.
        Catches exceptions and conditionally logs them to file.
        """
        try:
            self._original_stdout.write("Attempting to import main.py...\r\n")
            import main # This will execute your main.py script
            self._original_stdout.write("main.py imported successfully.\r\n")
        except Exception as e:
            # An error occurred during main.py import/execution!
            self._original_stdout.write("\n--- Error during main.py import/execution ---\r\n")
            sys.print_exception(e, self._original_stdout) # Print to console immediately

            # Now, attempt to log this error to the file
            if self._open_error_log_file(): # Try to open the file
                self.log_fd.write("\n") # Add a newline before the traceback
                sys.print_exception(e, self.log_fd) # Print full traceback to log file
                self.log_fd.write("\n--- End of Error ---\n")
                self.log_fd.close() # Close the file immediately after writing
                self.log_fd = None # Reset fd

    def run(self):
        """Orchestrates the conditional boot sequence."""
        self._setup_console_output() # Always ensure console is working
        self._run_main_application() # Run main, with conditional error logging
        self._original_stdout.write("--- Boot process completed ---\r\n") # Final message to console

# --- Instantiate and Run the BootManager ---
if __name__ == "__main__": # Standard Python entry point
    boot_manager = BootManager()
    boot_manager.run()