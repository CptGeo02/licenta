from src.libs import *
from src.gui.run_camera import run_camera
from src.gui.run_video import run_video
from src.gui.display_frame import display_frame
from src.utils.image_utils import *
from src.detectors.yolo_detector import YoloDetector
from src.utils.json_analyzer import JsonAnalyzer
from src.utils.json_to_excel import JsonToExcel

class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Restaurant Monitoring System")
        self.master.geometry("1200x1000")

        self.prev_time = time.time()
        self.last_time = time.time()  # Momentul în care a fost actualizat ultima dată
        # Inițializează YOLO Detector cu un model implicit
        self.current_model = "Select model"
        self.detector = YoloDetector()
        self.json_analyzer = JsonAnalyzer()
        # Creează un frame pentru butoane
        self.button_frame = Frame(master)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # Selector de model YOLO
        self.model_var = StringVar(value=self.current_model)
        self.model_selector = OptionMenu(
            self.button_frame, 
            self.model_var, 
            *self.get_model_files(), 
            command=self.change_model
        )

        # Butoane principale de moduri
        self.start_camera_btn = Button(self.button_frame, text="Start Live Camera", command=self.start_camera)
        self.start_camera_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.select_video_btn = Button(self.button_frame, text="Select Video", command=self.select_video)
        self.select_video_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.images_btn = Button(self.button_frame, text="Show Images", command=self.show_images)
        self.images_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.model_selector.config(width=15)
        self.model_selector.pack(side=tk.LEFT, padx=5, pady=5)

        # Butoane de navigare, detectare și resetare mese
        self.previous_btn = Button(self.button_frame, text="Previous", command=self.previous_image, state="disabled")
        self.previous_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_btn = Button(self.button_frame, text="Next", command=self.next_image, state="disabled")
        self.next_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.detect_all_btn = Button(self.button_frame, text="Detect all", command=self.detect_all, state="disabled")
        self.detect_all_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.auto_detect_enabled = BooleanVar(value=False)
        self.auto_detect_switch = Checkbutton(self.button_frame, text="Auto-Detect", variable=self.auto_detect_enabled, onvalue=True, offvalue=False, state="disabled")
        self.auto_detect_switch.pack(side=tk.LEFT, padx=5, pady=5)

        self.detect_tables_btn = Button(self.button_frame, text="Detect Tables", command=self.detect_tables, state="disabled")
        self.detect_tables_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_tables_btn = Button(self.button_frame, text="Set Tables", command=self.set_tables, state="disabled")
        self.set_tables_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_tables_btn = Button(self.button_frame, text="Reset Tables", command=self.reset_tables, state="disabled")
        self.reset_tables_btn.pack(side=tk.LEFT, padx=5, pady=5)

         # Buton pentru analiza fișierului JSON
        self.analyze_json_btn = Button(self.button_frame, text="Generate Statistics", command=self.analyze_json)
        self.analyze_json_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Frame pentru afișarea informațiilor de performanță
        self.performance_frame = tk.Frame(master)
        self.performance_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Etichete pentru afișarea performanței
        self.fps_label = tk.Label(self.performance_frame, text="FPS: Calculating...", font=("Arial", 12))
        self.fps_label.pack(pady=5)

        self.cpu_label = tk.Label(self.performance_frame, text="CPU Usage: Calculating...", font=("Arial", 12))
        self.cpu_label.pack(pady=5)

        self.gpu_label = tk.Label(self.performance_frame, text="GPU Usage: Not Available", font=("Arial", 12))
        self.gpu_label.pack(pady=5)

        self.ram_label = tk.Label(self.performance_frame, text="RAM Usage: Calculating...", font=("Arial", 12))
        self.ram_label.pack(pady=5)

        # Atribute pentru calculul FPS
        self.prev_time = time.time()
        self.fps = 0

        # Actualizare periodică a informațiilor de performanță
        self.update_performance()
        # Alți parametri de inițializare
        self.canvas = Canvas(master, width=640, height=480)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label = Label(self.canvas)
        self.label.pack()

        self.status_label = Label(master, text="", wraplength=780)
        self.status_label.pack(side=tk.BOTTOM, pady=10)

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

    def analyze_json(self):
        """Permite utilizatorului să selecteze un fișier JSON și să analizeze datele."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        
        if file_path:
            if self.json_analyzer.load_json(file_path):
                #self.json_analyzer.plot_data()
                # Exemplu de utilizare
                json_file = file_path  
                excel_file = 'data/outputs/table_status_analysis.xlsx'

                analyzer = JsonToExcel(json_file, excel_file)
                data = analyzer.load_json()
                analyzer.save_to_excel(data)

                print(f"Fișierul Excel a fost generat: {excel_file}")
           
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
        self.master.after(1000, self.update_performance)

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

        if self.selected_mode == "show_images":
            self.auto_detect_switch.config(state="disabled")
            self.detect_tables_btn.config(state="disabled")
            self.set_tables_btn.config(state="disabled")
            self.reset_tables_btn.config(state="disabled")

        self.previous_btn.config(state="normal" if self.selected_mode == 'show_images' else "disabled")
        self.next_btn.config(state="normal" if self.selected_mode == 'show_images' else "disabled")

        self.master.after(200, self.update_button_states)

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

    def detect_tables(self):
        self.detector.detecting_tables_only = True
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.set_tables_btn.config(state="normal")
        self.reset_tables_btn.config(state="disabled")

    def set_tables(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = True
        self.detector.detecting_all = False
        self.current_frame = self.detector.set_table_ids()
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="normal")
        self.detector.table_manager.create_new_files()
        self.detector.table_manager.start_auto_save()

    def reset_tables(self):
        self.detector.detecting_tables_only = True
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
            self.master.after(1, self.update_frame)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
