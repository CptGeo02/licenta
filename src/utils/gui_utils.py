import os
from tkinter import ttk

def load_images(folder_path):
    """Load all image files from a folder."""
    return [img for img in os.listdir(folder_path) if img.endswith(('.png', '.jpg', '.jpeg'))]

def apply_modern_style(self):
        """
        Configurează stilul modern pentru aplicația GUI.
        Include butoane albastre, fonturi curate și bordere subtile.
        """
        style = ttk.Style()
        style.theme_use("clam")  # Temă modernă de bază

        # Culoare pentru butoane
        modern_blue = "#007BFF"
        hover_blue = "#0056b3"  # Hover mai închis
        pressed_blue = "#004085"  # Apăsat
        text_white = "#FFFFFF"  # Text alb pentru contrast

        # Stil pentru TButton (butoane)
        style.configure(
            "TButton",
            font=("Helvetica", 12),  # Font modern, 12pt
            padding=10,  # Spațiu interior
            background=modern_blue,  # Culoarea de bază a butonului
            foreground=text_white,  # Text alb
            borderwidth=1,  # Border subțire
            relief="flat"  # Aspect plat
        )
        style.map(
            "TButton",
            background=[
                ("active", hover_blue),  # Culoare hover
                ("pressed", pressed_blue)  # Culoare la apăsare
            ],
            foreground=[
                ("disabled", "#A0A0A0")  # Text gri când e dezactivat
            ]
        )

        # Stil pentru TFrame (rame)
        style.configure(
            "TFrame",
            background="#F5F5F5"  # Alb modern pentru fundal
        )

        # Stil pentru TLabel (etichete)
        style.configure(
            "TLabel",
            font=("Helvetica", 11),  # Font modern, 11pt
            background="#F5F5F5",  # Alb modern
            foreground="#333333"  # Gri închis pentru text
        )

        # Stil pentru TEntry (casete de input)
        style.configure(
            "TEntry",
            font=("Helvetica", 11),
            padding=5,
            fieldbackground="#FFFFFF",  # Fundal alb curat
            foreground="#000000",  # Text negru
            borderwidth=1,
            relief="solid"
        )

        # Stil pentru TCombobox (combobox-uri)
        style.configure(
            "TCombobox",
            font=("Helvetica", 11),
            padding=5,
            fieldbackground="#FFFFFF",
            foreground="#000000",
            background="#FFFFFF",
            borderwidth=1
        )

        # Stil pentru TCheckbutton (checkbox-uri)
        style.configure(
            "TCheckbutton",
            font=("Helvetica", 11),
            background="#F5F5F5",
            foreground="#333333",
            padding=5
        )

        # Stil pentru TProgressbar (bare de progres)
        style.configure(
            "TProgressbar",
            thickness=10,
            background=modern_blue,
            troughcolor="#E0E0E0"  # Fundal gri deschis pentru trough
        )
        self.configure(background="#F5F5F5")
