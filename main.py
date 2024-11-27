import sys
import argparse
from src.gui.main_gui import MainGUI
from src.web.main_web import MainWeb  

def run_local_gui():
    app = MainGUI()  # Creează o instanță a MainGUI
    app.mainloop()   # Rulează bucla principală a tkinter

def run_web_interface():
    main_web = MainWeb()  # Creăm o instanță a clasei MainWeb
    main_web.run()  # Apelăm metoda run pentru a porni aplicația web

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select UI mode for AI Restaurant Monitoring System.")
    parser.add_argument(
        "--interface",
        choices=["local", "web"],
        default="local",  # Setăm "local" ca valoare implicită
        help="Choose 'local' for the desktop GUI or 'web' for the web interface (default: local)."
    )

    args = parser.parse_args()

    if args.interface == "local":
        run_local_gui()
    elif args.interface == "web":
        run_web_interface()
