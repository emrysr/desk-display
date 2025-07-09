# config_manager.py (Version 0.1.1 - Robust TOML Parsing)

import os
import re # Make sure re (regex) is imported

class ConfigManager:
    def __init__(self, display_manager_instance=None):
        self.config = {}
        self.config_file = 'config.toml'
        self.display_manager = display_manager_instance # For logging messages

    def _log(self, message):
        """Internal helper to log messages to display (if available) and console."""
        if self.display_manager:
            self.display_manager.add_log_message(message)
        print(message) # Always print to console/REPL

    def _parse_line(self, line):
        """
        Parses a single line from the TOML-like config file.
        Handles comments, sections, and key-value pairs (strings, ints, floats, bools).
        """
        # 1. Remove comments and trim leading/trailing whitespace
        # Split by the first '#' and take the part before it.
        line = line.split('#', 1)[0].strip() 
        
        if not line: # Line is now empty (was empty or only a comment)
            return None, None # Indicate nothing to parse

        # 2. Section header: [section_name]
        match_section = re.match(r'^\[([a-zA-Z0-9_]+)\]$', line)
        if match_section:
            return 'section', match_section.group(1)

        # 3. Key-value pair: key = value
        # This regex now captures the key and the raw value string
        match_kv = re.match(r'^\s*([a-zA-Z0-9_]+)\s*=\s*(.*)\s*$', line)
        if not match_kv:
            self._log(f"Warning: Unrecognized config line format: {line}")
            return None, None
        
        key = match_kv.group(1)
        value_raw = match_kv.group(2).strip() # Get the raw value part and strip whitespace

        # 4. Interpret the raw value's type
        # String (must be enclosed in double quotes)
        if value_raw.startswith('"') and value_raw.endswith('"'):
            return key, value_raw[1:-1] # Return the string with outer quotes removed
        
        # Integer
        # Check if it contains only digits (and an optional leading minus sign)
        if value_raw.isdigit() or (value_raw.startswith('-') and value_raw[1:].isdigit()):
             return key, int(value_raw)

        # Boolean (case insensitive)
        if value_raw.lower() == 'true':
            return key, True
        if value_raw.lower() == 'false':
            return key, False

        # Float (check for presence of a decimal point, then try conversion)
        try:
            if '.' in value_raw:
                return key, float(value_raw)
        except ValueError:
            pass # Not a float, continue to next check

        # Fallback: if none of the above, treat as a plain string (unquoted)
        # This can be useful for simpler config, but TOML strictly requires quotes for strings.
        # However, for robustness, we'll allow it but log a warning.
        self._log(f"Warning: Interpreting unquoted value '{value_raw}' for key '{key}' as string. TOML usually requires strings to be quoted.")
        return key, value_raw

    def load_config(self):
        """
        Loads configuration from the config.toml file.
        Returns a dictionary with sections and key-value pairs.
        """
        self.config = {}
        current_section = None
        
        self._log(f"Loading config from {self.config_file}...")

        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    key, value = self._parse_line(line)
                    
                    if key is None: # Skip unrecognized or empty lines
                        continue

                    if key == 'section':
                        current_section = value
                        self.config[current_section] = {}
                    elif current_section is not None:
                        self.config[current_section][key] = value
                    else:
                        self._log(f"Warning: Key-value pair '{key}={value}' found outside a section. Ignoring.")
            self._log("Config loaded successfully.")
            return self.config

        except OSError as e:
            self._log(f"Error opening/reading config file '{self.config_file}': {e}")
            return None
        except Exception as e:
            self._log(f"An unexpected error occurred during config parsing: {e}")
            return None