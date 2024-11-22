import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


class ScheduleFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.schedule_data = {}
        self.create_widgets()

    def create_widgets(self):
        # Header Row
        tk.Label(self, text="Day of Week", width=15, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self, text="Workday Length", width=15, anchor="w").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self, text="Start Time", width=10, anchor="w").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self, text="End Time", width=10, anchor="w").grid(row=0, column=3, padx=5, pady=5)

        self.entries = []

        # Rows for each day
        for i, day in enumerate(self.days):
            var_open = tk.BooleanVar(value=True)
            self.schedule_data[day] = {
                "is_open": var_open,
                "work_length": tk.StringVar(value="8 h"),
                "start_time": tk.StringVar(value="09:00"),
                "end_time": tk.StringVar(value="17:00"),
            }

            # Checkbox for Open/Closed
            checkbox = tk.Checkbutton(self, text=day, variable=var_open, command=lambda d=day: self.toggle_day(d))
            checkbox.grid(row=i + 1, column=0, sticky="w", padx=5, pady=5)

            # Workday Length Entry
            work_length = ttk.Entry(self, textvariable=self.schedule_data[day]["work_length"], width=10)
            work_length.grid(row=i + 1, column=1, padx=5, pady=5)
            work_length.bind("<Return>", lambda e, d=day: self.update_end_time(d))  # Update End Time

            # Start Time Entry
            start_time = ttk.Entry(self, textvariable=self.schedule_data[day]["start_time"], width=10)
            start_time.grid(row=i + 1, column=2, padx=5, pady=5)

            # End Time Entry
            end_time = ttk.Entry(self, textvariable=self.schedule_data[day]["end_time"], width=10)
            end_time.grid(row=i + 1, column=3, padx=5, pady=5)
            end_time.bind("<Return>", lambda e, d=day: self.update_work_length(d))  # Update Workday Length

            # Add to entries list for toggling
            self.entries.append((work_length, start_time, end_time))

        # Submit Button
        set_schedule_button = ttk.Button(self, text="Set Schedule", command=self.submit_schedule)
        set_schedule_button.grid(row=len(self.days) + 1, column=0, columnspan=4, pady=10)

    def toggle_day(self, day):
        """Enable or disable widgets based on the 'is_open' checkbox."""
        data = self.schedule_data[day]
        index = self.days.index(day)
        state = "normal" if data["is_open"].get() else "disabled"
        for widget in self.entries[index]:
            widget.config(state=state)

    def update_end_time(self, day):
        """Update End Time based on Workday Length and Start Time."""
        try:
            start_time = self.schedule_data[day]["start_time"].get()
            work_length = self.schedule_data[day]["work_length"].get()

            # Parse Start Time
            start_time_obj = datetime.strptime(start_time, "%H:%M")

            # Extract hours from Work Length
            work_hours = int(work_length.replace("h", "").strip())

            # Calculate End Time
            end_time_obj = start_time_obj + timedelta(hours=work_hours)
            self.schedule_data[day]["end_time"].set(end_time_obj.strftime("%H:%M"))

        except Exception as e:
            print(f"Error updating end time for {day}: {e}")

    def update_work_length(self, day):
        """Update Workday Length based on Start Time and End Time."""
        try:
            start_time = self.schedule_data[day]["start_time"].get()
            end_time = self.schedule_data[day]["end_time"].get()

            # Parse Start and End Times
            start_time_obj = datetime.strptime(start_time, "%H:%M")
            end_time_obj = datetime.strptime(end_time, "%H:%M")

            # Calculate Work Length
            duration = end_time_obj - start_time_obj
            hours = duration.total_seconds() // 3600
            self.schedule_data[day]["work_length"].set(f"{int(hours)} h")

        except Exception as e:
            print(f"Error updating work length for {day}: {e}")

    def submit_schedule(self):
        """Print the schedule to the console."""
        for day, data in self.schedule_data.items():
            if data["is_open"].get():
                print(f"{day}: Open, Workday Length: {data['work_length'].get()}, "
                      f"Start Time: {data['start_time'].get()}, End Time: {data['end_time'].get()}")
            else:
                print(f"{day}: Closed")

# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main GUI")
    root.mainloop()
