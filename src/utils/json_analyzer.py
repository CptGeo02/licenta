import json
import matplotlib.pyplot as plt
import numpy as np

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
            print(f"Failed to load JSON file: {e}")
            return False

    def plot_data(self):
        """Construiește histogramă din datele încărcate."""
        if not self.data:
            print("No data to plot!")
            return

        # Preia informațiile din fișierul JSON
        table_statuses = self.data['table_statuses']
        
        # Creează o listă cu mesele și statusurile acestora
        tables = []
        statuses = {'need to clean': 'red', 'available': 'green', 'ready to order': 'orange', 'eating': 'blue'}
        table_durations = {table_id: {status: 0 for status in statuses} for table_id in set(entry['table_id'] for entry in table_statuses)}

        # Adună durata fiecărui status pentru fiecare masă
        for entry in table_statuses:
            table_id = entry['table_id']
            status = entry['status']
            duration = self.convert_duration(entry['duration'])
            if status in table_durations[table_id]:
                table_durations[table_id][status] += duration

        # Pregătește datele pentru plot
        table_ids = sorted(table_durations.keys())  # Ordonați mesele pentru a le afișa într-o ordine consistentă
        status_names = list(statuses.keys())
        
        # Construiește histogramă
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.2  # Lățimea barelor
        index = np.arange(len(table_ids))  # Pozițiile meselor pe axa X

        # Adaugă bare pentru fiecare status
        for i, status in enumerate(status_names):
            durations = [table_durations[table_id][status] for table_id in table_ids]
            ax.bar(index + i * bar_width, durations, bar_width, color=statuses[status], label=status)

        # Setează etichetele axelor și titlul
        ax.set_xlabel('Table ID')
        ax.set_ylabel('Duration (seconds)')
        ax.set_title('Table Status Duration Histogram')
        ax.set_xticks(index + bar_width * (len(status_names) - 1) / 2)
        ax.set_xticklabels([f"Table {table_id}" for table_id in table_ids], rotation=45)
        ax.legend()

        plt.tight_layout()
        plt.show()

    def convert_duration(self, duration_str):
        """Convertește durata în secunde pentru a putea fi folosită în grafic."""
        hours, minutes, seconds = map(int, duration_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
"""
# Exemplu de utilizare
plotter = JsonAnalyzer()
if plotter.load_json('path_to_your_file.json'):  # Înlocuiește cu calea fișierului JSON
    plotter.plot_data()
"""