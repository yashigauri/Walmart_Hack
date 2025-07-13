# open_frontend.py
import webbrowser
import os

# Path to your frontend.html (adjust this if it's in a different location)
frontend_path = os.path.abspath("frontend.html")

# Open in default browser
webbrowser.open(f"file://{frontend_path}")
