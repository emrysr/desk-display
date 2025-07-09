# toml_tester.py (Version 0.1.1)
# A simple script to test parsing of config.toml using ConfigManager.

# Removed sys.stdout redirection as it's not compatible with MicroPython's sys module.

try:
    from config_manager import ConfigManager
    import time # Just for a small delay if needed

    print("\n--- Starting TOML Config Tester ---")

    # Instantiate ConfigManager without a DisplayManager for this test.
    # It will log messages directly to the console via print().
    config_manager = ConfigManager() 

    # Load the config file
    parsed_config = config_manager.load_config()

    if parsed_config is not None:
        print("\n--- Parsed Config Content ---")
        for section, data in parsed_config.items():
            print(f"[{section}]")
            for key, value in data.items():
                print(f"  {key} = '{value}' (Type: {type(value).__name__})")
        print("--- End Parsed Config Content ---")
    else:
        print("\n--- Failed to parse config.toml ---")
        print("Please check console for errors from ConfigManager during loading.")

except ImportError as e:
    print(f"\nERROR: Could not import ConfigManager: {e}")
    print("Please ensure config_manager.py is in the same directory.")
except Exception as e:
    print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")
    # Using sys.print_exception for more detailed traceback in MicroPython
    import sys
    sys.print_exception(e)

finally:
    print("\n--- TOML Config Tester Finished ---")