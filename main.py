import sys
import argparse
import tkinter as tk
from src.gui.main_gui import MainApp
from src.web.main_web import MainWeb  

def run_local_gui():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

def run_web_interface():
    main_web = MainWeb()  # Creăm o instanță a clasei MainWeb
    main_web.run()  # Apelăm metoda run pentru a porni aplicația web

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select UI mode for AI Restaurant Monitoring System.")
    parser.add_argument("--interface", choices=["local", "web"], required=True, help="Choose 'local' for the desktop GUI or 'web' for the web interface.")

    args = parser.parse_args()

    if args.interface == "local":
        run_local_gui()
    elif args.interface == "web":
        run_web_interface()
