import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import tempfile
import matplotlib.ticker as ticker
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
import json
from openpyxl import Workbook
from datetime import datetime

class JsonToExcel:
    def __init__(self, json_file, excel_file):
        self.json_file = json_file
        self.excel_file = excel_file

    def load_json(self):
        """Încarcă datele din JSON."""
        with open(self.json_file, 'r') as file:
            return json.load(file)

    def save_to_excel(self, data):
        """Salvează datele și graficele în Excel."""
        # Crearea DataFrame-ului
        table_statuses = data['table_statuses']
        df = pd.DataFrame(table_statuses)

        # Adăugăm intervalele de timp
        df = self.add_time_slot(df)

        # Crearea unui workbook nou cu openpyxl
        workbook = Workbook()

        # Scrierea datelor brute în sheet-ul 'Raw Data'
        sheet = workbook.active
        sheet.title = 'Raw Data'
        for r, row in df.iterrows():
            sheet.append(row.values.tolist())

        # Identificarea meselor ineficiente
        inefficient_tables = self.identify_inefficient_tables(df)
        sheet = workbook.create_sheet('Inefficient Tables')
        sheet.append(['Table ID', 'Status', 'Total Duration'])
        for table_id in inefficient_tables:
            table_data = df[df['table_id'] == table_id]
            total_duration = table_data['duration'].apply(self.convert_duration).sum()
            sheet.append([table_id, 'Inefficient', self.format_duration(total_duration)])

        # Calcularea duratei medii a ciclului meselor
        table_cycle_durations = self.calculate_table_cycle_duration(df)
        sheet = workbook.create_sheet('Table Cycle Duration')
        sheet.append(['Table ID', 'Cycle Duration'])
        for table_id, duration in table_cycle_durations.items():
            sheet.append([table_id, self.format_duration(duration)])

        # Calcularea mediilor și generarea histogramelor pentru medii
        avg_durations = self.calculate_avg_durations(df)
        self.generate_average_histogram(avg_durations, workbook)

        # Generarea histogramei și adăugarea ei pe un sheet nou
        self.generate_histogram(df, workbook)

        # Adăugare Status Analysis
        self.generate_status_analysis(df, workbook)

        # Salvarea fișierului Excel
        workbook.save(self.excel_file)

    def generate_histogram(self, df, workbook):
        """Generează histograma și o adaugă în Excel."""
        statuses = {'need to clean': 'red', 'available': 'green', 'ready to order': 'orange', 'eating': 'blue'}
        table_durations = {table_id: {status: 0 for status in statuses} for table_id in df['table_id'].unique()}

        # Calcularea duratelor totale pentru fiecare status al fiecărei mese
        for _, row in df.iterrows():
            table_id = row['table_id']
            status = row['status']
            duration = self.convert_duration(row['duration'])
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

    def generate_average_histogram(self, avg_durations, workbook):
        """Generează o histogramă pe baza mediilor și un grafic procentual, apoi le adaugă în același sheet din Excel."""
        statuses = {'need to clean': 'red', 'available': 'green', 'ready to order': 'orange', 'eating': 'blue'}

        # Pregătim datele pentru histogramă
        labels = []
        values = []
        colors = []
        for status, avg in avg_durations.items():
            if avg > 0:
                labels.append(status)
                values.append(avg)
                colors.append(statuses[status])

        # Creăm histograma
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(labels, values, color=colors)
        ax.set_title('Average Durations by Status')
        ax.set_ylabel('Duration (seconds)')
        ax.set_xlabel('Status')

        # Salvăm histograma temporar
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile_hist:
            plt.savefig(tmpfile_hist.name, format='png')
            plt.close()

            # Adăugăm histograma în sheet
            ws = workbook.create_sheet('Average Analysis')
            img_hist = Image(tmpfile_hist.name)
            ws.add_image(img_hist, 'A1')  # Poziționăm histograma în stânga

        # Creăm graficul procentual
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.set_title('Percentage of Average Durations by Status')

        # Salvăm graficul procentual temporar
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile_pie:
            plt.savefig(tmpfile_pie.name, format='png')
            plt.close()

            # Adăugăm graficul pie chart în dreapta histogramei
            img_pie = Image(tmpfile_pie.name)
            ws.add_image(img_pie, 'P1')  # Poziționăm imaginea în coloana K, pe același rând

    def generate_status_analysis(self, df, workbook):
        """
        Generează un sheet cu:
        1. Timpul maxim și minim pentru fiecare status.
        2. O diagramă de tip box plot care arată distribuția timpilor pentru fiecare status.
        """
        import seaborn as sns

        # Creăm un sheet nou
        ws = workbook.create_sheet('Status Analysis')

        # 1. Calculăm timpii maximi și minimi pentru fiecare status
        statuses = df['status'].unique()
        ws.append(['Status', 'Max Duration', 'Min Duration'])  # Header
        for status in statuses:
            # Convertim durata în secunde pentru calcul
            status_data = df[df['status'] == status]
            if not status_data.empty:
                max_duration = status_data['duration'].apply(self.convert_duration).max()
                min_duration = status_data['duration'].apply(self.convert_duration).min()
                ws.append([status, self.format_duration(max_duration), self.format_duration(min_duration)])
            else:
                ws.append([status, "N/A", "N/A"])

        # 2. Generăm un box plot pentru distribuția timpilor
        fig, ax = plt.subplots(figsize=(10, 6))
        df['duration_seconds'] = df['duration'].apply(self.convert_duration)  # Adăugăm o coloană temporară
        sns.boxplot(x='status', y='duration_seconds', data=df, hue='status', palette='Set2', ax=ax, legend=False)

        ax.set_title('Duration Distribution by Status')
        ax.set_ylabel('Duration (seconds)')
        ax.set_xlabel('Status')

        # Salvăm graficul box plot temporar
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile_boxplot:
            plt.savefig(tmpfile_boxplot.name, format='png')
            plt.close()

            # Adăugăm graficul în sheet
            img_boxplot = Image(tmpfile_boxplot.name)
            ws.add_image(img_boxplot, 'E1')  # Poziționăm box plot-ul în sheet

    def calculate_avg_durations(self, df):
        """Calculează media duratelor pentru fiecare status, pe baza datelor din DataFrame."""
        statuses = ['need to clean', 'available', 'ready to order', 'eating']
        avg_durations = {}

        # Calculăm suma și numărul de intrări pentru fiecare status
        for status in statuses:
            filtered_data = df[df['status'] == status]
            if not filtered_data.empty:
                total_duration = filtered_data['duration'].apply(self.convert_duration).sum()
                avg_duration = total_duration / len(filtered_data)
                avg_durations[status] = avg_duration
            else:
                avg_durations[status] = 0  # Dacă nu sunt date pentru acest status, media este 0

        return avg_durations
    
    def identify_inefficient_tables(self, df, threshold=1800):
        """Identifică mesele ineficiente pe baza duratei în statusurile 'need to clean' sau 'available'."""
        inefficient_tables = []
        for table_id in df['table_id'].unique():
            table_data = df[df['table_id'] == table_id]
            need_to_clean_duration = table_data[table_data['status'] == 'need to clean']['duration'].apply(self.convert_duration).sum()
            available_duration = table_data[table_data['status'] == 'available']['duration'].apply(self.convert_duration).sum()

            if need_to_clean_duration > threshold or available_duration > threshold:
                inefficient_tables.append(table_id)
        return inefficient_tables
        
    def add_time_slot(self, df):
        """Adaugă intervalul orar pentru fiecare intrare pe baza duratei."""
        from datetime import datetime

        def get_time_slot(row):
            """Extrage intervalul orar pe baza orei de început."""
            # Convertește start_time în datetime, ținând cont că formatul este 'yyyy-mm-dd hh:mm:ss'
            start_time = datetime.strptime(row['start_time'], '%Y-%m-%d %H:%M:%S')  # Folosește formatul complet
            hour = start_time.hour  # Extrage ora
            if hour < 6:
                return 'Night'
            elif hour < 12:
                return 'Morning'
            elif hour < 18:
                return 'Afternoon'
            else:
                return 'Evening'


        df['time_slot'] = df.apply(get_time_slot, axis=1)
        return df
    
    def calculate_table_cycle_duration(self, df):
        """Calculază durata medie totală a ciclului unei mese."""
        table_cycle_durations = {}
        for table_id in df['table_id'].unique():
            table_data = df[df['table_id'] == table_id]
            available_to_clean_duration = 0
            is_in_cycle = False
            for _, row in table_data.iterrows():
                if row['status'] == 'available':
                    is_in_cycle = True
                if is_in_cycle:
                    available_to_clean_duration += self.convert_duration(row['duration'])
                if row['status'] == 'need to clean' and is_in_cycle:
                    break
            table_cycle_durations[table_id] = available_to_clean_duration
        return table_cycle_durations

    @staticmethod
    def convert_duration(duration_str):
        """Convertește durata în secunde."""
        hours, minutes, seconds = map(int, duration_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    
    @staticmethod
    def format_duration(seconds):
        """Formatează durata în hh:mm:ss."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    