# boot.py (Version 0.1.0)
# This file is executed on every boot (including soft reboot)
import os
import sys
import time # Import time here for timestamp if desired

class BootManager:
    """
    Manages the initial boot process, including log redirection and
    execution of the main application script.
    """
    def __init__(self, log_file="boot_log.txt"):
        self.log_file = log_file
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self.log_fd = None

    def _setup_logging(self):
        """Redirects stdout and stderr to the specified log file."""
        try:
            # Open the log file in write mode ('w') to overwrite on each boot.
            # Use 'a' for append mode if you want to keep logs from multiple boots.
            self.log_fd = open(self.log_file, "w")
            sys.stdout = self.log_fd
            sys.stderr = self.log_fd

            print("--- Device Boot Started ---")
            print(f"Timestamp: {time.time()}")
            print(f"Log redirected to {self.log_file}") # New log message
        except Exception as e:
            # Fallback to serial if logging setup fails
            self._original_stdout.write(f"Error setting up boot_log.txt: {e}\r\n")
            sys.print_exception(e, self._original_stdout)
            # Ensure stdout/stderr are restored if logging failed
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self.log_fd = None # Indicate that logging failed

    def _run_main_application(self):
        """Attempts to import and execute main.py."""
        if self.log_fd: # Only log if logging was successfully set up
            print("Attempting to import main.py...")
        try:
            import main # This will execute your main.py script
            if self.log_fd:
                print("main.py imported successfully.")
        except Exception as e:
            if self.log_fd:
                print("\n--- Error during main.py import/execution ---")
                sys.print_exception(e) # Prints full traceback to log file
            # Also print to the original stdout/stderr (Thonny console) for live debugging
            self._original_stdout.write("\n--- Error printed to Thonny console ---\r\n")
            sys.print_exception(e, self._original_stdout)

    def _restore_logging(self):
        """Restores stdout/stderr and closes the log file."""
        if self.log_fd and not self.log_fd.closed:
            self.log_fd.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        print("--- Boot process completed or exited ---") # This message goes to Thonny console

    def run(self):
        """Orchestrates the boot sequence."""
        self._setup_logging()
        self._run_main_application()
        self._restore_logging()

# --- Instantiate and Run the BootManager ---
if __name__ == "__main__": # Standard Python entry point
    boot_manager = BootManager()
    boot_manager.run()