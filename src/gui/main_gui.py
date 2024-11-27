from src.gui.user_gui import UserGUI
from src.gui.admin_gui import AdminGUI
from src.libs import *

class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main GUI")
        self.geometry("400x300")
        self.create_widgets()
        apply_modern_style(self)

    def create_widgets(self):
        label = tk.Label(self, text="Choose Interface", font=("Arial", 16))
        label.pack(pady=20)

        button_user = ttk.Button(self, text="User", command=self.launch_user_gui)
        button_user.pack(pady=10)

        button_admin = ttk.Button(self, text="Admin", command=self.launch_admin_gui)
        button_admin.pack(pady=10)

    def launch_user_gui(self):
        """Lansează interfața UserGUI."""
        self.destroy()  # Închide fereastra principală
        user_gui = UserGUI()
        user_gui.mainloop()

    def launch_admin_gui(self):
        """Lansează interfața AdminGUI."""
        self.destroy()  # Închide fereastra principală
        admin_gui = AdminGUI()
        admin_gui.mainloop()

if __name__ == "__main__":
    app = MainGUI()
    app.mainloop()
