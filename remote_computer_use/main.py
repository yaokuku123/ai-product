import sys
import logging
from webssh.main import main

if __name__ == "__main__":
    # Set the default port to 8080 if not specified
    # The user wants to connect via http 8080
    if not any(arg.startswith("--port=") or arg == "--port" for arg in sys.argv):
        sys.argv.append("--port=8080")

    # Optional: Set logging level to info to see what's happening
    if not any(arg.startswith("--logging=") for arg in sys.argv):
        sys.argv.append("--logging=info")

    # Allow all origins (required for ngrok tunneling)
    # Note: '*' requires debug mode in some versions, but let's try to set it.
    if not any(arg.startswith("--origin=") for arg in sys.argv):
        sys.argv.append("--origin=*")
        # Debug mode is often required for wildcard origin
        if not any(arg.startswith("--debug") for arg in sys.argv):
            sys.argv.append("--debug")

    print("Starting WebSSH on port 8080...")
    print("Once started, you can access it at http://localhost:8080")
    print("For ngrok, run: ngrok http 8080")

    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
