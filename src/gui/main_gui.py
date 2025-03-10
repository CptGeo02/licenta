import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from src.gui.user_gui import UserGUI
from src.gui.admin_gui import AdminGUI
from src.libs import *

ADMIN_PASSWORD = "1234"  # Setează parola corectă pentru accesul admin

class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI restaurant")
        self.geometry("400x300")
        self.create_widgets()
        apply_modern_style(self)

    def create_widgets(self):
        label = tk.Label(self, text="Choose Interface", font=("Arial", 16))
        label.pack(pady=20)

        button_user = ttk.Button(self, text="User", command=self.launch_user_gui)
        button_user.pack(pady=10)

        button_admin = ttk.Button(self, text="Admin", command=self.request_admin_password)
        button_admin.pack(pady=10)

    def launch_user_gui(self):
        """Lansează interfața UserGUI și ascunde fereastra principală."""
        self.withdraw()  # Ascunde fereastra MainGUI
        user_gui = UserGUI(self)  # Trimite referința către MainGUI
        user_gui.mainloop()

    def launch_admin_gui(self):
        """Lansează interfața AdminGUI și ascunde fereastra principală."""
        self.withdraw()  # Ascunde fereastra MainGUI
        admin_gui = AdminGUI(self)  # Trimite referința către MainGUI
        admin_gui.mainloop()

    def request_admin_password(self):
        """Solicită parola și verifică dacă este corectă înainte de a lansa interfața admin."""
        password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show="*")
        
        if password == ADMIN_PASSWORD:
            self.launch_admin_gui()
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")

if __name__ == "__main__":
    app = MainGUI()
    app.mainloop()
