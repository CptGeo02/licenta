from src.libs import *
from src.gui.modes.run_camera import run_camera
from src.gui.modes.run_video import run_video
from src.detectors.yolo_detector import YoloDetector
from src.gui.frames.display_frame import display_frame
from src.gui.frames.schedule_frame import ScheduleFrame
from src.gui.frames.calendar_selector_frame import CalendarSelectorFrame
from src.gui.frames.move_camera_frame import MoveCameraFrame

class AdminGUI(tk.Toplevel):
    def __init__(self, main_gui):
        super().__init__()
        self.name="admin"
        self.main_gui = main_gui 
        self.title("AI Restaurant Monitoring System")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.prev_time = time.time()
        self.last_time = time.time()  # Momentul în care a fost actualizat ultima dată
        # Inițializează YOLO Detector cu un model implicit
        self.current_model = "models/yolov8n.pt"
        self.detector = YoloDetector()
        self.selected_camera = 0
        self.video_resolution = (640, 480)
        # Creează un frame pentru butoane
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)

        self.button_back = ttk.Button(self.button_frame, text="Back", command=self.go_back)
        self.button_back.grid(row=0, column=0, padx=5, pady=5)
        
        # Button: Move Camera
        self.move_camera_btn = ttk.Button(self.button_frame, text="Move Camera", command=self.open_move_camera)
        self.move_camera_btn.grid(row=0, column=1, padx=5, pady=5)

        # Adăugarea elementelor în button_frame utilizând grid
        self.start_camera_btn = ttk.Button(self.button_frame, text="Start Live Camera", command=self.start_camera)
        self.start_camera_btn.grid(row=0, column=2, padx=5, pady=5)

        self.select_video_btn = ttk.Button(self.button_frame, text="Select Video", command=self.select_video)
        self.select_video_btn.grid(row=0, column=3, padx=5, pady=5)

        self.images_btn = ttk.Button(self.button_frame, text="Show Images", command=self.show_images)
        self.images_btn.grid(row=0, column=4, padx=5, pady=5)

        # Butoane de navigare, detectare și resetare mese
        self.previous_btn = ttk.Button(self.button_frame, text="Previous", command=self.previous_image, state="disabled")
        self.previous_btn.grid(row=0, column=5, padx=5, pady=5)

        self.next_btn = ttk.Button(self.button_frame, text="Next", command=self.next_image, state="disabled")
        self.next_btn.grid(row=0, column=6, padx=5, pady=5)

        self.detect_all_btn = ttk.Button(self.button_frame, text="Detect all", command=self.detect_all, state="disabled")
        self.detect_all_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # Crearea butonului în interfața Tkinter
        self.export_button = ttk.Button(self.button_frame, text="Export Parameters", command=self.export_parameters)
        self.export_button.grid(row=1, column=0, padx=5, pady=5)

        self.detect_tables_btn = ttk.Button(self.button_frame, text="Detect Tables", command=self.detect_tables, state="disabled")
        self.detect_tables_btn.grid(row=1, column=1, padx=5, pady=5)

        self.set_tables_btn = ttk.Button(self.button_frame, text="Set Tables", command=self.set_tables, state="disabled")
        self.set_tables_btn.grid(row=1, column=2, padx=5, pady=5)

        self.reset_tables_btn = ttk.Button(self.button_frame, text="Reset Tables", command=self.reset_tables, state="disabled")
        self.reset_tables_btn.grid(row=1, column=3, padx=5, pady=5)

        self.stop_detection_btn = ttk.Button(self.button_frame, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.stop_detection_btn.grid(row=1, column=4, padx=5, pady=5)

        # Add a button to open the schedule window
        self.open_schedule_button = ttk.Button(self.button_frame, text="Set Weekly Schedule", command=self.open_schedule_window)
        self.open_schedule_button.grid(row=1, column=5, padx=5, pady=5)
        # Add Generate Statistics Button
        self.btn_generate_statistics = ttk.Button(self.button_frame, text="Generate Statistics", command=self.open_statistics_calendar)
        self.btn_generate_statistics.grid(row=1, column=6, padx=5, pady=5)
        
        # Selector de porturi COM
        self.serial_port_var = tk.StringVar(value="Select COM Port")
        self.com_selector = ttk.OptionMenu(
            self.button_frame,
            self.serial_port_var,
            "Select COM Port",
            *self.get_serial_ports(),
            command=self.set_selected_com_port
        )
        self.com_selector.config(width=20)
        self.com_selector.grid(row=2, column=0, padx=5, pady=5)

        # Obține camerele disponibile
        self.camera_list = self.get_available_cameras()
        self.move_camera_frame = None
        
        # Variabila pentru selectorul de camere
        self.camera_var = tk.StringVar(value="Select Camera")  # Valoare implicită
        self.camera_selector = ttk.OptionMenu(
            self.button_frame,
            self.camera_var,
            "Select Camera",  # Opțiunea implicită
            *self.camera_list,  # Opțiuni de camere
            command=self.update_camera
        )
        self.camera_selector.config(width=20)
        self.camera_selector.grid(row=2, column=1, padx=5, pady=5)


        self.video_format_var = StringVar(value="480p")  # Valoare implicită
        self.video_format_selector = ttk.OptionMenu(
            self.button_frame,
            self.video_format_var,
            "Select Format",  # Valoare implicită
            "480p", "720p", "1080p",  # Opțiuni de formate
            command=self.update_video_format
        )

        self.video_format_selector.config(width=15)
        self.video_format_selector.grid(row=2, column=2, padx=5, pady=5)
        
        # Selector de model YOLO
        self.model_var = StringVar(value=self.current_model)
        self.model_selector = ttk.OptionMenu(
            self.button_frame,
            self.model_var,
            "Select Model",  # Valoarea implicită afișată
            *self.get_model_files(),
            command=self.change_model
        )
        self.model_selector.config(width=15)
        self.model_selector.grid(row=2, column=3, padx=5, pady=5)

        self.auto_detect_enabled = BooleanVar(value=False)
        self.auto_detect_switch = Checkbutton(
            self.button_frame,
            text="Auto-Detect",
            variable=self.auto_detect_enabled,
            onvalue=True,
            offvalue=False,
            state="disabled"
        )
        self.auto_detect_switch.grid(row=2, column=4, padx=5, pady=5)

        self.illumination_enabled = BooleanVar(value=False)
        self.illumination_switch = Checkbutton(
        self.button_frame,
        text="Light Correction",
        variable=self.illumination_enabled,
        onvalue=True,
        offvalue=False
        )
        self.illumination_switch.grid(row=2, column=5, padx=5, pady=5)
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
        self.clahe_clip_var = tk.DoubleVar(value=2.0)
        self.clahe_tile_var = tk.IntVar(value=8)
        self.create_slider_special(
            parent=sliders_frame,
            label_text="CLAHE Clip Limit:",
            variable=self.clahe_clip_var,
            command=self.update_clahe_clip,
            default_value=2.0,
            column=3
        )

        self.create_slider_special(
            parent=sliders_frame,
            label_text="CLAHE Tile Size:",
            variable=self.clahe_tile_var,
            command=self.update_clahe_tile,
            default_value=8,
            column=4
        )

        self.info_label = tk.Label(self, text="Tables: 0 | People: 0")
        self.info_label.pack(side=tk.TOP, fill=tk.X)
        
        # Etichetă pentru scorul de frame
        self.score_label = tk.Label(self, text="Frame Score: 0.00")
        self.score_label.pack(side=tk.TOP, fill=tk.X)
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

        self.selected_com_port = None
        self.video_source = None
        self.current_frame = None
        self.running = False

        self.camera_thread = None
        self.video_thread = None
        self.image_thread = None

        self.images = []
        self.image_index = 0
        self.stop_event = threading.Event()

        self.update_frame()
        apply_modern_style(self)

    def create_slider_special(self, parent, label_text, variable, command, default_value, column):
        """
        Creează un slider generic cu etichetă, tooltip și afișarea valorii curente.
        Asigură intervale sigure pentru CLAHE (contrast și tile size).
        """
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=column, padx=10)

        label = ttk.Label(frame, text=label_text)
        label.pack(pady=5)

        # Determinăm limitele în funcție de tipul variabilei și label
        if isinstance(variable, tk.DoubleVar) and "Clip" in label_text:
            from_, to_ = 1.0, 5.0  # CLAHE Clip Limit recomandat
            tooltip_text = "Clip Limit controlează cât de puternic se aplică contrastul local. Valori mai mari evidențiază detaliile, dar pot genera zgomot vizual."
        elif isinstance(variable, tk.IntVar) and "Tile" in label_text:
            from_, to_ = 4, 32     # CLAHE Tile Size (X=Y) recomandat
            tooltip_text = "Dimensiunea Tile controlează granularitatea corecției locale. Tile mai mic = contrast local fin, Tile mai mare = efect global."
        else:
            from_, to_ = 0.0, 1.0
            tooltip_text = "Slider generic."

        slider = ttk.Scale(
            frame,
            from_=from_,
            to=to_,
            orient="horizontal",
            length=150,
            variable=variable,
            command=command,
        )
        slider.pack(pady=5)

        value_label = ttk.Label(frame, text=f"{default_value:.2f}" if isinstance(default_value, float) else str(default_value))
        value_label.pack(pady=5)

        # Tooltip informativ
        Hovertip(label, tooltip_text, hover_delay=300)

        # Salvează eticheta pentru actualizare dinamică
        variable.value_label = value_label
                
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

    def set_selected_com_port(self, selected_port):
        """Salvează portul COM selectat pentru controlul camerei."""
        self.selected_com_port = selected_port
        print(f"[INFO] Selected COM port: {self.selected_com_port}")
          
    def open_move_camera(self):
        """
        Deschide frame-ul Move Camera într-un Toplevel nou și transmite COM-ul selectat.
        """
        move_camera_window = tk.Toplevel(self)
        move_camera_window.title("Move Camera")
        selected_port = self.selected_com_port if self.selected_com_port else "COM6"
        self.move_camera_frame = MoveCameraFrame(self, move_camera_window)
        self.move_camera_frame.set_serial_port(selected_port)
        self.move_camera_frame.pack(fill="both", expand=True)

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

    def update_button_states(self, selected_btn):
            if selected_btn == "camera":
                self.auto_detect_switch.config(state="normal")
                self.detect_all_btn.config(state="normal")
                self.start_camera_btn.config(state="disabled")
                self.select_video_btn.config(state="normal")
                self.images_btn.config(state="normal")
                self.previous_btn.config(state="disabled")
                self.next_btn.config(state="disabled")

            if selected_btn == "video":
                self.auto_detect_switch.config(state="normal")
                self.detect_all_btn.config(state="normal")
                self.start_camera_btn.config(state="normal")
                self.select_video_btn.config(state="disabled")
                self.images_btn.config(state="normal")
                self.previous_btn.config(state="disabled")
                self.next_btn.config(state="disabled")

            if selected_btn == "show_images":
                self.auto_detect_switch.config(state="normal")
                self.detect_all_btn.config(state="normal")         
                self.start_camera_btn.config(state="normal")
                self.select_video_btn.config(state="normal")
                self.images_btn.config(state="disabled")
                self.previous_btn.config(state="normal")
                self.next_btn.config(state="normal")

            if selected_btn == "detect_all":
                self.detect_tables_btn.config(state="normal")
                self.set_tables_btn.config(state="disabled")
                self.reset_tables_btn.config(state="disabled")
                self.stop_detection_btn.config(state="normal")

            if selected_btn == "detect_tables":    
                self.detect_tables_btn.config(state="disabled")
                self.set_tables_btn.config(state="normal")
                self.reset_tables_btn.config(state="disabled")
                self.stop_detection_btn.config(state="normal")

            if selected_btn == "set_tables":
                self.detect_tables_btn.config(state="disabled")
                self.set_tables_btn.config(state="disabled")
                self.reset_tables_btn.config(state="normal")
                self.stop_detection_btn.config(state="normal")
                
            if selected_btn == "reset_tables":
                self.detect_tables_btn.config(state="disabled")
                self.set_tables_btn.config(state="normal")
                self.reset_tables_btn.config(state="disabled")
                self.stop_detection_btn.config(state="normal")
            
            if selected_btn == "stop_detection":
                self.detect_tables_btn.config(state="normal")
                self.set_tables_btn.config(state="disabled")
                self.reset_tables_btn.config(state="disabled")
                self.stop_detection_btn.config(state="disabled")

    def start_camera(self):
        self.stop_running_thread()
        self.stop_event.clear()
        self.running = True
        self.camera_thread = threading.Thread(target=run_camera, args=(self,))
        self.camera_thread.start()

        self.update_button_states('camera')
        

    def select_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])

        if video_path:
            self.stop_running_thread()
            self.stop_event.clear()
            self.running = True
            self.video_source = video_path
            self.video_thread = threading.Thread(target=run_video, args=(self,))
            self.video_thread.start()

        self.update_button_states('video')
            

    def show_images(self):
        """Pornește afișarea unei singure imagini într-un thread separat."""
        self.stop_running_thread()
        self.stop_event.clear()  # Resetare stop_event

        self.images = load_images('data/images/')
        self.image_index = 0

        if self.images:
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)

        self.update_button_states('show_images')

    def next_image(self):
        if self.images:
            self.image_index = (self.image_index + 1) % len(self.images)
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)

    def previous_image(self):
        if self.images:
            self.image_index = (self.image_index - 1) % len(self.images)
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)
            
    def detect_all(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = False
        self.detector.detecting_all = True
        self.update_button_states('detect_all')

    def detect_tables(self):
        self.detector.detecting_tables_only = True
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.update_button_states('detect_tables')

    def set_tables(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = True
        self.detector.detecting_all = False
        self.current_frame = self.detector.set_table_ids()
        self.detector.table_manager.create_new_files()
        self.detector.table_manager.start_auto_save()
        self.detector.people_manager.create_new_files()
        self.detector.people_manager.start_auto_save()
        self.update_button_states('set_tables')
        
        
    def reset_tables(self):
        self.detector.detecting_tables_only = True
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.detector.reset_table_manager()
        self.update_button_states('reset_tables')

    def stop_detection(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.detector.reset_table_manager()
        self.update_button_states('stop_detection')

    def update_status_label(self):
        status_report = self.detector.get_tables_status_report()
        self.status_label.config(text=status_report)

    def update_frame(self):
        """Actualizează și afișează cadrul la fiecare 17 ms."""
        display_frame(self, self.current_frame)
        self.after(17, self.update_frame)  # Reapelează funcția la fiecare 17 ms

    def stop_running_thread(self):
        """Oprește orice thread activ înainte de a porni unul nou."""
        self.stop_detection()
        self.stop_event.set()  # Semnalăm oprirea thread-urilors
        self.running = False
        # Oprire thread cameră
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join()
            self.camera_thread = None
            print("[INFO] camera_thread has stopped in Admin mode")
        # Oprire thread video
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join()
            self.video_thread = None  
            print("[INFO] video_thread has stopped in Admin mode")

    def on_close(self):
        """Curăță toate apelurile 'after' și închide aplicația."""
        self.stop_running_thread()
        self.after_cancel(self.update_frame)
        self.after_cancel(self.start_info_update)
        self.destroy()  # Închide aplicația

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
            return self.generate_time_options('00:00:00', '10:00:00', 30)
        elif status_type == 'ready to order':
            return self.generate_time_options('00:00:00', '01:00:00', 5)
        elif status_type == 'eating':
            return self.generate_time_options('00:00:00', '06:00:00', 30)
        elif status_type == 'need to clean':
            return self.generate_time_options('00:00:00', '02:00:00', 5)
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
        self.score_label.config(
            text=f"Frame Score: {self.detector.frame_score:.2f}" if self.detector.detecting_tables_only
              or self.detector.done_setting_tables or self.detector.detecting_all else "Frame Score: 0.00")

        
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

    def get_serial_ports(self):
        """Returnează o listă cu porturile seriale disponibile pe sistem."""
        ports = list_ports.comports()
        return [port.device for port in ports]
    
    def open_statistics_calendar(self):
        """Function to open the statistics calendar window in a new window."""
        statistics_window = tk.Toplevel()  # Creează o fereastră de tip Toplevel
        statistics_window.title("Select Date Range for Statistics")  # Titlul ferestrei
        statistics_window.geometry("600x400")  # Setează dimensiunile ferestrei

        # Creează frame-ul pentru calendar și alte componente
        statistics_frame = CalendarSelectorFrame(statistics_window)  # Pass the Toplevel window to CalendarSelectorFrame
        statistics_frame.pack(fill="both", expand=True, padx=10, pady=10)  # Adaugă frame-ul în fereastră

    def update_video_format(self, selected_format):
            """Actualizează dimensiunea video și afișează în consolă."""
            if selected_format == "480p":
                self.video_resolution = (640, 480)  # Rezoluție 480p
            elif selected_format == "720p":
                self.video_resolution = (1280, 720)  # Rezoluție HD
            elif selected_format == "1080p":
                self.video_resolution = (1920, 1080)  # Rezoluție FullHD
            # Afișează dimensiunea selectată în consolă
            print(f"Selected video format: {self.video_resolution[0]}x{self.video_resolution[1]} pixels")

    def get_available_cameras(self):
            """Detectează camerele video disponibile și le returnează ca o listă."""
            camera_list = []
            for i in range(10):
                    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                    if cap is not None and cap.isOpened():
                        camera_list.append(f"Camera {i}")
                        cap.release()
            return camera_list
    
    def update_clahe_clip(self, _):
        value = self.clahe_clip_var.get()
        self.clahe_clip_var.value_label.config(text=f"{value:.2f}")

    def update_clahe_tile(self, _):
        value = self.clahe_tile_var.get()
        self.clahe_tile_var.value_label.config(text=str(value))
        
    def update_camera(self, selected_camera):
        """Actualizează camera aleasă și afișează în consolă."""
        if selected_camera != "Select Camera":
            print(f"Selected camera: {selected_camera}")
            self.selected_camera = int(selected_camera[-1])
        else:
            print("No camera selected")

    def go_back(self):
        """Închide această fereastră și revine la MainGUI."""
        self.stop_running_thread()
        self.destroy()  # Închide fereastra curentă
        self.main_gui.deiconify()  # Afișează din nou MainGUI

    def export_parameters(self):
        # Crearea directorului dacă nu există
        config_dir = "data/config"
        os.makedirs(config_dir, exist_ok=True)
        
        # Crearea numelui de fișier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_filename = f"config_{timestamp}.json"
        config_path = os.path.join(config_dir, config_filename)

        # Structura datelor
        config_data = {
            "selected_camera": self.selected_camera,
            "selected_model": self.model_var.get(),
            "video_resolution": self.video_resolution,
            "max_times": {
                "available": self.time_available.get(),
                "ready_to_order": self.time_ready.get(),
                "eating": self.time_eating.get(),
                "need_to_clean": self.time_clean.get()
            },
            "max_people": int(self.max_people_var.get()),
            "overlap_threshold": round(float(self.overlap_threshold_var.get()),2),
            "red_threshold": round(float(self.red_threshold_var.get()),2),
            "blue_threshold": round(float(self.blue_threshold_var.get()),2),
            "illumination_enabled": bool(self.illumination_enabled),
            "clahe_clip_var": round(float(self.clahe_clip_var.get()),2),
            "clahe_tile_var": int(self.clahe_tile_var.get())
        }
        
        # Salvare în JSON
        with open(config_path, "w") as json_file:
            json.dump(config_data, json_file, indent=4)
        
        print(f"Configurația a fost salvată în {config_path}")

if __name__ == "__main__":
    app = AdminGUI()
    app.mainloop()
