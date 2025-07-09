# config_parser.py (Version 0.1.0)

def parse_config_toml(filename="config.toml"):
    """
    Parses a simple TOML configuration file for WiFi credentials.
    Expected format:
    [wifi]
    ssid = "your_ssid"
    password = "your_password"
    
    Returns a dictionary with 'wifi' key containing 'ssid' and 'password'.
    Returns an empty dict if the file is not found or a parsing error occurs.
    This parser is very basic and only handles string key-value pairs
    under a section header.
    """
    config = {}
    current_section = None
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue # Skip empty lines and comments

                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1].strip()
                    config[current_section] = {}
                elif '=' in line and current_section:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes for string values
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    config[current_section][key] = value
    except OSError as e:
        print(f"ERROR: Config file '{filename}' not found or cannot be read: {e}")
        # In a real app, you might log this to a display or specific error state
    except Exception as e:
        print(f"ERROR: Error parsing config file '{filename}': {e}")
        # In a real app, you might log this to a display
    
    return config