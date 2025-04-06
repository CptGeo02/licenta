from src.libs import *

class ManualReportGenerator:
    def __init__(self, report_dir="data/outputs/daily_report"):
        self.report_dir = report_dir

    def generate(self, start_date, end_date):
        relevant_files = self.collect_files(start_date, end_date)
        if not relevant_files:
            raise ValueError("No JSON files found for the selected date range.")
        return self.process_json_files(relevant_files, start_date, end_date)

    def collect_files(self, start_date, end_date):
        relevant_files = []
        for folder_name in os.listdir(self.report_dir):
            try:
                folder_date = datetime.strptime(folder_name, "%Y-%m-%d").date()
                if start_date <= folder_date <= end_date:
                    folder_path = os.path.join(self.report_dir, folder_name)
                    for file_name in os.listdir(folder_path):
                        if file_name == "average_statistics.json":
                            relevant_files.append(os.path.join(folder_path, file_name))
            except ValueError:
                continue
        return relevant_files

    def process_json_files(self, json_files, start_date, end_date):
        combined_data = {}

        for file_path in json_files:
            with open(file_path, "r") as f:
                data = json.load(f)
                for date, stats in data.items():
                    if isinstance(stats, dict):
                        if date not in combined_data:
                            combined_data[date] = stats
                        else:
                            for field, value in stats.items():
                                if isinstance(value, (int, float)):
                                    combined_data[date][field] = combined_data[date].get(field, 0) + value
                                else:
                                    combined_data[date][field] = value

        output_dir = f"data/outputs/{start_date}_{end_date}"
        os.makedirs(output_dir, exist_ok=True)
        general_stats_file = os.path.join(output_dir, "general_stats.json")

        with open(general_stats_file, "w") as f:
            json.dump(combined_data, f, indent=4)

        fields_data = {self.clean_column_name(field): {} for field in next(iter(combined_data.values())).keys()}
        for date, stats in combined_data.items():
            for field, value in stats.items():
                cleaned_field = self.clean_column_name(field)
                fields_data[cleaned_field][date] = value

        sorted_dates = sorted(next(iter(fields_data.values())).keys())
        report_file = os.path.join(output_dir, "general_statistic.xlsx")
        wb = Workbook()
        ws_data = wb.active
        ws_data.title = "Data Statistics"
        ws_data.append(["Date"] + list(fields_data.keys()))

        for date in sorted_dates:
            row = [date] + [fields_data[field].get(date, 0) for field in fields_data.keys()]
            ws_data.append(row)
        ws_data.auto_filter.ref = ws_data.dimensions

        ws_histograms = wb.create_sheet("Histograms")
        row_offset = 1
        max_charts_per_row = 3
        for idx, (field, data) in enumerate(fields_data.items()):
            values = [data[date] for date in sorted_dates]
            x = np.arange(len(sorted_dates))
            trend = np.polyfit(x, values, 1)
            trend_line = np.polyval(trend, x)

            plt.figure(figsize=(10, 5))
            plt.bar(sorted_dates, values, color='steelblue', alpha=0.7, label=field)
            plt.plot(sorted_dates, trend_line, color='red', linestyle='--', label="Trend Line")
            plt.xlabel("Date")
            plt.ylabel(field)
            plt.title(f"{field} Histogram")
            plt.legend()
            histogram_path = os.path.join(output_dir, f"{field}_histogram.png")
            plt.savefig(histogram_path)
            plt.close()

            img = ExcelImage(histogram_path)
            img.width = 600
            img.height = 400
            col_letter = get_column_letter((idx % max_charts_per_row) * 12 + 1)
            ws_histograms.add_image(img, f"{col_letter}{row_offset}")

            if (idx + 1) % max_charts_per_row == 0:
                row_offset += 25

        apply_modern_design(ws_data)
        apply_modern_design(ws_histograms)
        wb.save(report_file)
        return report_file

    def clean_column_name(self, name):
        import re
        return re.sub(r'[^A-Za-z0-9_]+', '_', name).strip()
