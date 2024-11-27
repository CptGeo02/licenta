from src.libs import *
from src.gui.modes.run_camera import run_camera
from src.gui.modes.run_video import run_video
from src.utils.image_utils import *
from src.detectors.yolo_detector import YoloDetector
from src.utils.json_to_excel import JsonToExcel
from src.gui.frames.display_frame import display_live_frame
from src.gui.frames.schedule_frame import ScheduleFrame
from src.gui.frames.calendar_frame import StatisticsCalendar
from src.gui.frames.move_camera_frame import MoveCameraFrame

class UserGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Restaurant Monitoring System")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.prev_time = time.time()
        self.last_time = time.time()  # Momentul în care a fost actualizat ultima dată
        # Inițializează YOLO Detector cu un model implicit
        self.current_model = "models/yolov8n.pt"
        self.detector = YoloDetector()

        # Creează un frame pentru butoane
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)

        # Button: Auto Set Camera
        auto_set_btn = ttk.Button(self.button_frame, text="Auto Set Camera", command=self.auto_set_camera)
        auto_set_btn.grid(row=0, column=0, padx=5, pady=5)
        # Button: Move Camera
        move_camera_btn = ttk.Button(self.button_frame, text="Move Camera", command=self.open_move_camera)
        move_camera_btn.grid(row=0, column=1, padx=5, pady=5)

        self.detect_tables_btn = ttk.Button(self.button_frame, text="Detect Tables", command=self.detect_tables, state="normal")
        self.detect_tables_btn.grid(row=0, column=2, padx=5, pady=5)

        self.set_tables_btn = ttk.Button(self.button_frame, text="Set Tables", command=self.set_tables, state="disabled")
        self.set_tables_btn.grid(row=0, column=3, padx=5, pady=5)

        self.reset_tables_btn = ttk.Button(self.button_frame, text="Reset Tables", command=self.reset_tables, state="disabled")
        self.reset_tables_btn.grid(row=0, column=4, padx=5, pady=5)

        self.stop_detection_btn = ttk.Button(self.button_frame, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.stop_detection_btn.grid(row=0, column=5, padx=5, pady=5)

        # Add a button to open the schedule window
        self.open_schedule_button = ttk.Button(self.button_frame, text="Set Weekly Schedule", command=self.open_schedule_window)
        self.open_schedule_button.grid(row=0, column=6, padx=5, pady=5)
        # Add Generate Statistics Button
        self.btn_generate_statistics = ttk.Button(self.button_frame, text="Generate Statistics", command=self.open_statistics_calendar)
        self.btn_generate_statistics.grid(row=0, column=7, padx=5, pady=5)
        # Creează un frame pentru butoane
        self.max_frame = ttk.Frame(self)
        self.max_frame.pack(pady=10)

        # Variabile pentru timpii selectați pentru fiecare status
        self.time_available = tk.StringVar(value='Select Max Time Available')
        self.time_ready = tk.StringVar(value='Select Max Time Waiting')
        self.time_eating = tk.StringVar(value='Select Max Time Eating')
        self.time_clean = tk.StringVar(value='Select Max Time Clean')
        self.max_people_var = tk.StringVar(value='')

        # Crearea selectoarelor
        self.create_time_selectors()

        # Crearea input-ului pentru numărul maxim de oameni
        self.create_people_number_input()

        self.info_label = tk.Label(self, text="Tables: 0 | People: 0")
        self.info_label.pack(side=tk.TOP, fill=tk.X)
        self.start_info_update()

        self.canvas = Canvas(self, width=1920, height=1080)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label = ttk.Label(self.canvas)
        self.label.pack()

        self.status_label = ttk.Label(self, text="", wraplength=1000)
        self.status_label.pack(side=tk.TOP, pady=10)

        self.video_source = None
        self.current_frame = None
        self.running = False
        self.frame_thread = None
        self.images = []
        self.image_index = 0
        self.stop_event = threading.Event()

        
        self.stop_running_thread()
        self.running = True
        self.stop_event.clear()
        self.frame_thread = threading.Thread(target=run_camera, args=(self,))
        self.frame_thread.start()
        self.update_frame()

        apply_modern_style(self)

    def auto_set_camera(self):
        # Placeholder function for Auto Set Camera
        print("Auto Set Camera function called.")

    def open_move_camera(self):
        # Open Move Camera frame
        move_camera_window = tk.Toplevel(self)
        move_camera_window.title("Move Camera")
        move_camera_frame = MoveCameraFrame(move_camera_window)
        move_camera_frame.pack(fill="both", expand=True)
        
    def detect_tables(self):
        self.detector.detecting_tables_only = True
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.set_tables_btn.config(state="normal")
        self.reset_tables_btn.config(state="disabled")
        self.stop_detection_btn.config(state="normal")

    def set_tables(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = True
        self.detector.detecting_all = False
        self.current_frame = self.detector.set_table_ids()
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="normal")
        self.stop_detection_btn.config(state="normal")
        self.detector.table_manager.create_new_files()
        self.detector.table_manager.start_auto_save()
        self.detector.people_manager.create_new_files()
        self.detector.people_manager.start_auto_save()
        
        
    def reset_tables(self):
        self.detector.detecting_tables_only = True
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.detector.reset_table_manager()
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="disabled")

    def stop_detection(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.detector.reset_table_manager()
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="disabled")

    def update_status_label(self):
        status_report = self.detector.get_tables_status_report()
        self.status_label.config(text=status_report)

    def update_frame(self):
            # Obține timpul curent
            current_time = time.time()
            
            # Calculează timpul necesar pentru a ajunge la 16.67 ms (1/60 FPS)
            elapsed_time = current_time - self.last_time
            if elapsed_time >= 0.01667:  # Dacă au trecut cel puțin 16.67 ms
                if self.current_frame is not None:
                    display_live_frame(self, self.current_frame)  # Afișează cadrul
                
                # Actualizează timpul ultimei actualizări
                self.last_time = current_time
            
            # Reapelează funcția după 1 ms, pentru a verifica timpul
            self.after(1, self.update_frame)

    def stop_running_thread(self):
        if self.frame_thread and self.frame_thread.is_alive():
            self.stop_event.set()
            self.frame_thread.join()
        self.running = False

    def generate_time_options(self, start_time, end_time, step_minutes):
        """
        Generăm intervalele de timp între start_time și end_time cu pasul step_minutes.
        """
        start = datetime.strptime(start_time, "%H:%M:%S")
        end = datetime.strptime(end_time, "%H:%M:%S")
        step = timedelta(minutes=step_minutes)

        times = []
        current_time = start
        while current_time <= end:
            times.append(current_time.strftime("%H:%M:%S"))
            current_time += step

        return times

    def get_time_options(self, status_type):
        """
        Funcție care returnează timpii disponibili pentru un anumit tip de status.
        """
        if status_type == 'available':
            return self.generate_time_options('00:30:00', '10:00:00', 30)
        elif status_type == 'ready to order':
            return self.generate_time_options('00:05:00', '01:00:00', 5)
        elif status_type == 'eating':
            return self.generate_time_options('00:30:00', '06:00:00', 30)
        elif status_type == 'need to clean':
            return self.generate_time_options('00:05:00', '02:00:00', 5)
        else:
            return []
        
    def create_time_selectors(self):
        """
        Crează selectoarele de timp pentru fiecare status al mesei.
        """
        # Selector pentru "available"
        self.available_selector = self.create_time_selector('available', self.time_available)
        
        # Selector pentru "ready to order"
        self.ready_selector = self.create_time_selector('ready to order', self.time_ready)
        
        # Selector pentru "eating"
        self.eating_selector = self.create_time_selector('eating', self.time_eating)
        
        # Selector pentru "need to clean"
        self.clean_selector = self.create_time_selector('need to clean', self.time_clean)

    def create_time_selector(self, status_type, time_var):
        """
        Creează un selector de timp pentru un anumit tip de status.
        """
        time_options = self.get_time_options(status_type)
        selector = ttk.OptionMenu(
            self.max_frame, 
            time_var,
            f"Select max {status_type} time",
            *time_options, 
            command=lambda _: self.update_time_status(status_type, time_var)
        )
        # Configurarea selectoarelor cu lățime și plasare
        selector.config(width=35)
        selector.pack(side=tk.LEFT, padx=5, pady=5)
        return selector

    def update_time_status(self, status_type, time_var):
        """
        Funcție de comandă care salvează timpul ales pentru un anumit status.
        """
        time = time_var.get()
        print(f"Selected time for {status_type}: {time}")
        self.detector.table_manager.set_max_time(status_type, time)
        # Aici poți salva valorile în variabilele corespunzătoare sau le poți folosi în aplicație.

    def create_people_number_input(self):
        # Setează valoarea inițială a câmpului de input din PeopleManager
        self.max_people_var = tk.StringVar(value=str(self.detector.people_manager.get_max_people_number()))
        people_entry = ttk.Entry(self.max_frame, textvariable=self.max_people_var, width=10, justify='center')

        # Validare: doar cifre
        validate_command = (self.register(self.validate_unsigned_int), '%P')
        people_entry.config(validate='key', validatecommand=validate_command)

        # Event pentru a actualiza valoarea când utilizatorul apasă Enter
        label = ttk.Label(self.max_frame, text="Max People:")
        label.pack(side=tk.LEFT, padx=5)

        people_entry.bind('<Return>', self.update_max_people)
        people_entry.pack(side=tk.LEFT, padx=5)

    def validate_unsigned_int(self, value):
        """
        Permite doar valori unsigned int în câmpul de input.
        """
        if value == "":
            return True  # Permite câmp gol temporar
        return value.isdigit()

    def update_max_people(self, event=None):
        """
        Actualizează valoarea maximă de persoane în PeopleManager.
        """
        try:
            max_people = int(self.max_people_var.get())
            self.detector.people_manager.set_max_people_number(max_people)
            print(f"Max people number updated to: {max_people}")
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please enter a positive integer.")
            # Resetează la valoarea actuală
            self.max_people_var.set(str(self.detector.people_manager.get_max_people_number()))

    def start_info_update(self):
        """Inițiază actualizarea periodică a informațiilor."""
        self.update_info()  # Actualizează imediat
        self.after(1000, self.start_info_update)  # Reapelează peste 1 secundă

    def update_info(self):
        """Actualizează textul pentru numărul de mese și persoane detectate."""
        self.info_label.config(
            text=f"Tables: {self.detector.tables_number} | "
                 f"People: {self.detector.people_number}"
        )

    def open_schedule_window(self):
        """Function to open the schedule frame in a new window."""
        schedule_window = tk.Toplevel()
        schedule_window.title("Set Weekly Schedule")
        schedule_window.geometry("600x400")  # Adjust size as needed
        frame = ScheduleFrame(schedule_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

    def open_statistics_calendar(self):
        """Function to open the statistics calendar window in a new window."""
        statistics_window = tk.Toplevel()  # Creează o fereastră de tip Toplevel
        statistics_window.title("Select Date Range for Statistics")  # Titlul ferestrei
        statistics_window.geometry("600x400")  # Setează dimensiunile ferestrei

        # Creează frame-ul pentru calendar și alte componente
        statistics_frame = StatisticsCalendar(statistics_window)  # Pass the Toplevel window to StatisticsCalendar
        statistics_frame.pack(fill="both", expand=True, padx=10, pady=10)  # Adaugă frame-ul în fereastră

    def on_close(self):
        """Curăță toate apelurile 'after' și închide aplicația."""
        self.after_cancel(self.update_frame)
        self.after_cancel(self.start_info_update)
        self.destroy()  # Închide aplicația

if __name__ == "__main__":
    app = UserGUI()
    app.mainloop()
