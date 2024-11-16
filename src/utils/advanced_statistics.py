import json
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
from openpyxl.drawing.image import Image

class AdvancedStatistics:
    def __init__(self, json_file, excel_file):
        self.json_file = json_file
        self.excel_file = excel_file
        self.df = pd.DataFrame()

    def load_data(self):
        """Încarcă datele din JSON și le procesează într-un DataFrame."""
        data = self.load_json()
        table_statuses = data['table_statuses']
        self.df = pd.DataFrame(table_statuses)
        
        # Convertirea duratei în secunde
        self.df['duration_seconds'] = self.df['duration'].apply(self.convert_duration)

        # Calcularea timpului final pentru fiecare rând
        self.df['start_time'] = pd.to_datetime(self.df['start_time'])
        self.df['end_time'] = self.df['start_time'] + pd.to_timedelta(self.df['duration_seconds'], unit='s')

    def load_json(self):
        """Încarcă datele din fișierul JSON."""
        with open(self.json_file, 'r') as file:
            return json.load(file)

    def save_to_excel(self):
        """Salvează datele procesate și histograma într-un fișier Excel."""
        with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
            # Scrierea datelor brute în Excel
            self.df.to_excel(writer, index=False, sheet_name='Raw Data')
            workbook = writer.book
            
            # Generare histogramă și adăugare în Excel
            self.generate_histogram(workbook)

    def generate_histogram(self, workbook):
        """Generează histograma pe baza duratei meselor pentru fiecare status și o adaugă în fișierul Excel."""
        statuses = {'need to clean': 'red', 'available': 'green', 'ready to order': 'orange', 'eating': 'blue'}
        table_durations = {table_id: {status: 0 for status in statuses} for table_id in self.df['table_id'].unique()}

        # Calcularea duratelor totale pentru fiecare status al fiecărei mese
        for _, row in self.df.iterrows():
            table_id = row['table_id']
            status = row['status']
            duration = row['duration_seconds']
            table_durations[table_id][status] += duration

        # Pregătirea datelor pentru histogramă
        table_ids = sorted(table_durations.keys())
        status_names = list(statuses.keys())
        bar_width = 0.2
        index = range(len(table_ids))

        # Crearea graficului
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, status in enumerate(status_names):
            durations = [table_durations[table_id][status] for table_id in table_ids]
            ax.bar([x + i * bar_width for x in index], durations, bar_width, color=statuses[status], label=status)

        ax.set_xlabel('Table ID')
        ax.set_ylabel('Duration (seconds)')
        ax.set_title('Table Status Duration Histogram')
        ax.set_xticks([x + bar_width * 1.5 for x in index])
        ax.set_xticklabels([f"Table {table_id}" for table_id in table_ids], rotation=45)
        ax.legend()
        plt.tight_layout()

        # Salvează graficul temporar
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            plt.savefig(tmpfile.name, format='png')
            plt.close()

            # Adaugă graficul în Excel
            ws = workbook.create_sheet('Histogram')
            img = Image(tmpfile.name)
            ws.add_image(img, 'A1')

    def calculate_statistics(self):
        """Calcularea statisticilor avansate pe baza datelor încărcate."""
        # Calcularea numărului de mese per status
        status_counts = self.df['status'].value_counts()

        # Calcularea duratei totale per status
        status_durations = self.df.groupby('status')['duration_seconds'].sum()

        # Calcularea mediei duratei per status
        status_avg_duration = self.df.groupby('status')['duration_seconds'].mean()

        return {
            'status_counts': status_counts.to_dict(),
            'status_durations': status_durations.to_dict(),
            'status_avg_duration': status_avg_duration.to_dict()
        }

    @staticmethod
    def convert_duration(duration_str):
        """Convertește durata în secunde."""
        hours, minutes, seconds = map(int, duration_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

# Exemplu de utilizare a clasei AdvancedStatistics
if __name__ == "__main__":
    json_file = "data/outputs/table_status_changes.json"  # Înlocuiește cu calea fișierului tău JSON
    excel_file = "data/outputs/table_status_analysis.xlsx"  # Înlocuiește cu calea fișierului Excel dorit

    analyzer = AdvancedStatistics(json_file, excel_file)
    analyzer.load_data()  # Încarcă și procesează datele
    analyzer.save_to_excel()  # Salvează datele și histograma într-un fișier Excel

    # Calculează statistici
    stats = analyzer.calculate_statistics()
    print("Statistici avansate:")
    print("Număr de mese per status:", stats['status_counts'])
    print("Durata totală per status:", stats['status_durations'])
    print("Durata medie per status:", stats['status_avg_duration'])
