from src.libs import *
from src.reports.manual_report_generator import ManualReportGenerator

class StatisticsCalendarFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.title("Select Date Range for Statistics")
        self.parent.geometry("600x600")

        self.report_dir = "data/outputs/daily_report"
        self.min_date, self.max_date = self.get_date_range()

        tk.Label(self, text="Select Start Date:").pack(pady=10)
        self.start_calendar = Calendar(self, date_pattern="yyyy-mm-dd", mindate=self.min_date, maxdate=self.max_date)
        self.start_calendar.pack()

        tk.Label(self, text="Select End Date:").pack(pady=10)
        self.end_calendar = Calendar(self, date_pattern="yyyy-mm-dd", mindate=self.min_date, maxdate=self.max_date)
        self.end_calendar.pack()

        self.generate_button = tk.Button(self, text="Generate Statistics", command=self.generate_statistics)
        self.generate_button.pack(pady=20)

    def get_date_range(self):
        try:
            folder_dates = []
            for folder_name in os.listdir(self.report_dir):
                folder_path = os.path.join(self.report_dir, folder_name)
                if os.path.isdir(folder_path):
                    try:
                        folder_date = datetime.strptime(folder_name, "%Y-%m-%d").date()
                        folder_dates.append(folder_date)
                    except ValueError:
                        continue
            if not folder_dates:
                raise ValueError("No valid date folders found.")
            return min(folder_dates), max(folder_dates)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to determine date range: {e}")
            self.parent.destroy()

    def generate_statistics(self):
        try:
            start_date = self.start_calendar.get_date()
            end_date = self.end_calendar.get_date()
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date_obj > end_date_obj:
                messagebox.showerror("Error", "Start date must be earlier than end date.")
                return

            relevant_files = []
            for folder_name in os.listdir(self.report_dir):
                folder_date = datetime.strptime(folder_name, "%Y-%m-%d").date()
                if start_date_obj <= folder_date <= end_date_obj:
                    folder_path = os.path.join(self.report_dir, folder_name)
                    for file_name in os.listdir(folder_path):
                        if file_name == "average_statistics.json":
                            relevant_files.append(os.path.join(folder_path, file_name))

            if not relevant_files:
                messagebox.showinfo("No Data", "No JSON files found for the selected date range.")
                return

            generator = ManualReportGenerator()
            report_path = generator.process_json_files(relevant_files, start_date, end_date)
            messagebox.showinfo("Success", f"Report generated successfully at: {report_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate statistics: {e}")
