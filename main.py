# main.py

from src.gui.main_gui import MainApp
from src.libs import tk

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
