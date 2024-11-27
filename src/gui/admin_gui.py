from src.libs import *
from src.gui.modes.run_camera import run_camera
from src.gui.modes.run_video import run_video
from src.utils.image_utils import *
from src.detectors.yolo_detector import YoloDetector
from src.utils.json_to_excel import JsonToExcel
from src.gui.frames.display_frame import display_frame
from src.gui.frames.schedule_frame import ScheduleFrame
from src.gui.frames.calendar_frame import StatisticsCalendar

class AdminGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Restaurant Monitoring System")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")

        self.prev_time = time.time()
        self.last_time = time.time()  # Momentul în care a fost actualizat ultima dată
        # Inițializează YOLO Detector cu un model implicit
        self.current_model = "models/yolov8n.pt"
        self.detector = YoloDetector()

        # Creează un frame pentru butoane
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)

        # Adăugarea elementelor în button_frame utilizând grid
        self.start_camera_btn = ttk.Button(self.button_frame, text="Start Live Camera", command=self.start_camera)
        self.start_camera_btn.grid(row=0, column=0, padx=5, pady=5)

        self.select_video_btn = ttk.Button(self.button_frame, text="Select Video", command=self.select_video)
        self.select_video_btn.grid(row=0, column=1, padx=5, pady=5)

        self.images_btn = ttk.Button(self.button_frame, text="Show Images", command=self.show_images)
        self.images_btn.grid(row=0, column=2, padx=5, pady=5)

        # Selector de model YOLO
        self.model_var = StringVar(value=self.current_model)
        self.model_selector = ttk.OptionMenu(
            self.button_frame,
            self.model_var,
            "Select model",  # Valoarea implicită afișată
            *self.get_model_files(),
            command=self.change_model
        )
        self.model_selector.config(width=15)
        self.model_selector.grid(row=0, column=3, padx=5, pady=5)

        # Butoane de navigare, detectare și resetare mese
        self.previous_btn = ttk.Button(self.button_frame, text="Previous", command=self.previous_image, state="disabled")
        self.previous_btn.grid(row=0, column=4, padx=5, pady=5)

        self.next_btn = ttk.Button(self.button_frame, text="Next", command=self.next_image, state="disabled")
        self.next_btn.grid(row=0, column=5, padx=5, pady=5)

        self.detect_all_btn = ttk.Button(self.button_frame, text="Detect all", command=self.detect_all, state="disabled")
        self.detect_all_btn.grid(row=0, column=6, padx=5, pady=5)

        self.auto_detect_enabled = BooleanVar(value=False)
        self.auto_detect_switch = Checkbutton(
            self.button_frame,
            text="Auto-Detect",
            variable=self.auto_detect_enabled,
            onvalue=True,
            offvalue=False,
            state="disabled"
        )
        self.auto_detect_switch.grid(row=0, column=7, padx=5, pady=5)

        self.detect_tables_btn = ttk.Button(self.button_frame, text="Detect Tables", command=self.detect_tables, state="disabled")
        self.detect_tables_btn.grid(row=1, column=0, padx=5, pady=5)

        self.set_tables_btn = ttk.Button(self.button_frame, text="Set Tables", command=self.set_tables, state="disabled")
        self.set_tables_btn.grid(row=1, column=1, padx=5, pady=5)

        self.reset_tables_btn = ttk.Button(self.button_frame, text="Reset Tables", command=self.reset_tables, state="disabled")
        self.reset_tables_btn.grid(row=1, column=2, padx=5, pady=5)

        self.stop_detection_btn = ttk.Button(self.button_frame, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.stop_detection_btn.grid(row=1, column=3, padx=5, pady=5)

        # Buton pentru analiza fișierului JSON
        self.analyze_json_btn = ttk.Button(self.button_frame, text="Analyze Records", command=self.analyze_json)
        self.analyze_json_btn.grid(row=1, column=4, padx=5, pady=5)

        # Add a button to open the schedule window
        self.open_schedule_button = ttk.Button(self.button_frame, text="Set Weekly Schedule", command=self.open_schedule_window)
        self.open_schedule_button.grid(row=1, column=5, padx=5, pady=5)
                # Add Generate Statistics Button
        self.btn_generate_statistics = ttk.Button(self.button_frame, text="Generate Statistics", command=self.open_statistics_calendar)
        self.btn_generate_statistics.grid(row=1, column=6, padx=5, pady=5)
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


        # Frame pentru afișarea informațiilor de performanță
        self.performance_frame = ttk.Frame(self)
        self.performance_frame.pack(pady=10)

        # Adăugarea etichetelor în performance_frame, utilizând grid
        self.fps_label = ttk.Label(self.performance_frame, text="FPS: Calculating...")
        self.fps_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.cpu_label = ttk.Label(self.performance_frame, text="CPU Usage: Calculating...")
        self.cpu_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.gpu_label = ttk.Label(self.performance_frame, text="GPU Usage: Not Available")
        self.gpu_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

        self.ram_label = ttk.Label(self.performance_frame, text="RAM Usage: Calculating...")
        self.ram_label.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

        # Frame pentru toate sliderele
        sliders_frame = ttk.Frame(self)
        sliders_frame.pack(pady=10)

        # Variabile pentru slidere
        self.overlap_threshold_var = tk.DoubleVar(value=0.2)
        self.red_threshold_var = tk.DoubleVar(value=0.1)
        self.blue_threshold_var = tk.DoubleVar(value=0.1)

        # Slider pentru Overlap Threshold
        self.create_slider(
            parent=sliders_frame,
            label_text="Overlap Threshold:",
            variable=self.overlap_threshold_var,
            command=self.update_overlap_threshold,
            default_value=0.2,
            column=0,
        )

        # Slider pentru Red Threshold
        self.create_slider(
            parent=sliders_frame,
            label_text="Red Threshold:",
            variable=self.red_threshold_var,
            command=self.update_red_threshold,
            default_value=0.1,
            column=1,
        )

        # Slider pentru Blue Threshold
        self.create_slider(
            parent=sliders_frame,
            label_text="Blue Threshold:",
            variable=self.blue_threshold_var,
            command=self.update_blue_threshold,
            default_value=0.1,
            column=2,
        )

        self.info_label = tk.Label(self, text="Tables: 0 | People: 0")
        self.info_label.pack(side=tk.TOP, fill=tk.X)
        self.start_info_update()

        # Atribute pentru calculul FPS
        self.prev_time = time.time()
        self.fps = 0

        # Actualizare periodică a informațiilor de performanță
        self.update_performance()
        # Alți parametri de inițializare
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

        # Inițializează starea modurilor și a apelului pentru actualizarea stării butoanelor
        self.selected_mode = None  # Stochează modurile 'camera', 'video' sau 'show_images'
        self.update_button_states()
        apply_modern_style(self)

    def analyze_json(self):
        """Permite utilizatorului să selecteze fișierele JSON pentru analiză și salvează rezultatul într-un fișier Excel."""
        # Directorul pentru salvarea raportului Excel
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Creează calea completă a folderului
        excel_output_dir = os.path.join("data", "outputs", "daily_report", current_date)
        os.makedirs(excel_output_dir, exist_ok=True)  # Creează folderul dacă nu există


        # Selecția fișierului pentru people_records
        print("Selectați fișierul JSON pentru people_records.")
        people_json_file = filedialog.askopenfilename(
            title="Selectați fișierul JSON pentru People",
            initialdir='data/outputs/people_records',
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
        )

        # Selecția fișierului pentru table_records
        print("Selectați fișierul JSON pentru table_records.")
        table_json_file = filedialog.askopenfilename(
            title="Selectați fișierul JSON pentru Tables",
            initialdir='data/outputs/table_records',
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
        )

        # Verificăm dacă ambele fișiere au fost selectate
        if not people_json_file or not table_json_file:
            print("Selecția fișierelor a fost anulată.")
            return

        # Salvarea fișierului Excel
        excel_file = os.path.join(excel_output_dir, 'table_status_analysis.xlsx')

        # Utilizăm JsonToExcel pentru analiza fișierelor JSON
        try:
            analyzer = JsonToExcel(table_json_file, people_json_file, excel_file)
            analyzer.save_to_excel()
            print(f"Fișierul Excel a fost generat cu succes: {excel_file}")
            analyzer.save_average_statistics()
            print(f"Fișierul JSON a fost generat cu succes")
        except Exception as e:
            print(f"Eroare la generarea fișierului Excel: {e}")
                
    def update_performance(self):
        # Exemplu de calcul FPS
        # Afișare FPS
        self.fps_label.config(text=f"FPS: {self.fps:.2f}")

        # Utilizare CPU și RAM folosind psutil
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.ram_label.config(text=f"RAM Usage: {ram_usage}%")

        # Verificare și afișare utilizare GPU dacă este disponibil
        if torch.cuda.is_available():
            gpu_usage, gpu_memory_used, gpu_memory_free = self.get_gpu_usage()
            if gpu_usage is not None:
                self.gpu_label.config(
                    text=f"GPU Usage: {gpu_usage}% (Used: {gpu_memory_used}/{gpu_memory_free} MB)"
                )

        # Programare actualizare periodică a informațiilor (la fiecare 1 secundă)
        self.after(1000, self.update_performance)

    def get_gpu_usage(self):
        try:
            # Apelăm nvidia-smi pentru a obține date despre GPU
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used,memory.free,utilization.gpu', '--format=csv,noheader,nounits'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            # Extragem valorile din rezultatul comenzii
            output = result.stdout.strip().split('\n')[0].split(', ')
            memory_used = int(output[0])  # MB
            memory_free = int(output[1])  # MB
            gpu_usage = int(output[2])  # procentaj utilizare GPU
            return gpu_usage, memory_used, memory_free
        except Exception as e:
            print(f"Error getting GPU usage: {e}")
            return None, None, None

    def get_model_files(self):
        """Returnează o listă de fișiere YOLO disponibile în folderul models."""
        model_files = [f for f in os.listdir("models") if f.endswith(".pt")]
        return model_files

    def change_model(self, model_name):
        """Schimbă modelul YOLO utilizat."""
        self.current_model = model_name
        self.detector.load_model(os.path.join("models", self.current_model))
        self.status_label.config(text=f"Modelul a fost schimbat la {model_name}")

    def update_button_states(self):
        mode_selected = self.selected_mode is not None
        if mode_selected:
            self.auto_detect_switch.config(state="normal")
            self.detect_tables_btn.config(state="normal")
            self.detect_all_btn.config(state="normal")          

        if mode_selected and self.auto_detect_enabled.get():
            self.detect_tables_btn.config(state="disabled")
            self.set_tables_btn.config(state="disabled")
            self.reset_tables_btn.config(state="disabled")
            self.detect_all_btn.config(state="disabled")
            self.stop_detection_btn.config(state="disabled")

        if self.selected_mode == "show_images":
            self.auto_detect_switch.config(state="disabled")
            self.detect_tables_btn.config(state="disabled")
            self.set_tables_btn.config(state="disabled")
            self.reset_tables_btn.config(state="disabled")

        self.previous_btn.config(state="normal" if self.selected_mode == 'show_images' else "disabled")
        self.next_btn.config(state="normal" if self.selected_mode == 'show_images' else "disabled")

        self.after(200, self.update_button_states)

    def start_camera(self):
        self.selected_mode = 'camera'
        self.auto_detect_switch.config(state="normal")
        self.stop_running_thread()
        self.running = True
        self.stop_event.clear()
        self.frame_thread = threading.Thread(target=run_camera, args=(self,))
        self.frame_thread.start()
        self.update_frame()

    def select_video(self):
        self.selected_mode = 'video'
        self.stop_running_thread()
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])

        if video_path:
            self.video_source = video_path
            self.running = True
            self.stop_event.clear()
            self.frame_thread = threading.Thread(target=run_video, args=(self,))
            self.frame_thread.start()
            self.update_frame()

    def show_images(self):
        self.selected_mode = 'show_images'
        self.stop_running_thread()
        self.images = load_images('data/images/')
        self.image_index = 0
        self.running = False

        if self.images:
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)
            if self.current_frame is not None:
                display_frame(self, self.current_frame)

    def detect_all(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = False
        self.detector.detecting_all = True
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="disabled")
        self.stop_detection_btn.config(state="normal")

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
                    display_frame(self, self.current_frame)  # Afișează cadrul
                
                # Actualizează timpul ultimei actualizări
                self.last_time = current_time
            
            # Reapelează funcția după 1 ms, pentru a verifica timpul
            self.after(1, self.update_frame)

    def stop_running_thread(self):
        if self.frame_thread and self.frame_thread.is_alive():
            self.stop_event.set()
            self.frame_thread.join()
        self.running = False

    def next_image(self):
        if self.images:
            self.image_index = (self.image_index + 1) % len(self.images)
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)
            if self.current_frame is not None:
                display_frame(self, self.current_frame)

    def previous_image(self):
        if self.images:
            self.image_index = (self.image_index - 1) % len(self.images)
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)
            if self.current_frame is not None:
                display_frame(self, self.current_frame)

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
        
    def create_slider(self, parent, label_text, variable, command, default_value, column):
        """
        Creează un slider generic cu etichetă și afișarea valorii curente.
        """
        frame = ttk.Frame(parent)  # Frame pentru fiecare slider
        frame.grid(row=0, column=column, padx=10)  # Poziționează slider-ul pe coloană

        label = ttk.Label(frame, text=label_text)  # Eticheta slider-ului
        label.pack(pady=5)

        slider = ttk.Scale(
            frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            length=150,  # Lungimea slider-ului
            variable=variable,
            command=command,
        )
        slider.pack(pady=5)

        value_label = ttk.Label(frame, text=f"{default_value:.2f}")  # Valoarea curentă
        value_label.pack(pady=5)

        # Salvează eticheta pentru actualizare dinamică
        variable.value_label = value_label

    def update_overlap_threshold(self, _):
        """
        Actualizează valoarea overlap_threshold din detector.
        """
        new_threshold = self.overlap_threshold_var.get()
        self.detector.overlap_threshold = new_threshold
        self.overlap_threshold_var.value_label.config(text=f"{new_threshold:.2f}")

    def update_red_threshold(self, _):
        """
        Actualizează valoarea red_threshold pentru toate mesele.
        """
        new_threshold = self.red_threshold_var.get()
        self.detector.table_manager.set_red_threshold_for_all_tables(new_threshold)
        self.red_threshold_var.value_label.config(text=f"{new_threshold:.2f}")

    def update_blue_threshold(self, _):
        """
        Actualizează valoarea blue_threshold pentru toate mesele.
        """
        new_threshold = self.blue_threshold_var.get()
        self.detector.table_manager.set_blue_threshold_for_all_tables(new_threshold)
        self.blue_threshold_var.value_label.config(text=f"{new_threshold:.2f}")

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

if __name__ == "__main__":
    app = AdminGUI()
    app.mainloop()
