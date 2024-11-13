import json
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import messagebox
import os

class JsonAnalyzer:
    def __init__(self):
        self.data = None

    def load_json(self, file_path):
        """Încarcă fișierul JSON."""
        try:
            with open(file_path, 'r') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {e}")
            return False

    def plot_data(self):
        """Construiește grafice din datele încărcate."""
        if not self.data:
            messagebox.showerror("Error", "No data to plot!")
            return

        try:
            # Exemplu de analiză a datelor
            timestamps = [entry['timestamp'] for entry in self.data]
            durations = [entry['duration'] for entry in self.data]

            # Crearea graficului
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, durations, marker='o', linestyle='-', color='b')
            plt.xlabel('Timestamp')
            plt.ylabel('Duration (hh:mm:ss)')
            plt.title('Table Status Duration Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot data: {e}")
