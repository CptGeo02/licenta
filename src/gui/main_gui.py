from src.libs import *
from src.gui.run_camera import run_camera
from src.gui.run_video import run_video
from src.gui.display_frame import display_frame
from src.utils.image_utils import *
from src.detectors.yolo_detector import YoloDetector

class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Restaurant Monitoring System")
        self.master.geometry("1200x1000")

        # Inițializează YOLO Detector
        self.detector = YoloDetector()

        # Creează un frame pentru butoane
        self.button_frame = Frame(master)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # Butoane principale de moduri
        self.start_camera_btn = Button(self.button_frame, text="Start Live Camera", command=self.start_camera)
        self.start_camera_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.select_video_btn = Button(self.button_frame, text="Select Video", command=self.select_video)
        self.select_video_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.images_btn = Button(self.button_frame, text="Show Images", command=self.show_images)
        self.images_btn.pack(side=tk.LEFT, padx=5, pady=5)

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

    def update_button_states(self):
        # Blochează toate butoanele dacă niciun mod nu este selectat
        mode_selected = self.selected_mode is not None
        if mode_selected:
            self.auto_detect_switch.config(state="normal")
            self.detect_tables_btn.config(state="normal")
            self.detect_all_btn.config(state="normal")

        # Activați/dezactivați "Detect Tables" pe baza modului și opțiunii "Auto-Detect"
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


        # Activați butoanele pentru "Previous" și "Next" doar în modul 'show_images'
        self.previous_btn.config(state="normal" if self.selected_mode == 'show_images' else "disabled")
        self.next_btn.config(state="normal" if self.selected_mode == 'show_images' else "disabled")

        # Apelează din nou funcția după un interval de 200ms
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
        """
        Activează detectarea doar a meselor fără ID.
        """
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = False
        self.detector.detecting_all = True
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="disabled")

    def detect_tables(self):
        """
        Activează detectarea doar a meselor fără ID.
        """
        self.detector.detecting_tables_only = True
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.set_tables_btn.config(state="normal")
        self.reset_tables_btn.config(state="disabled")

    def set_tables(self):
        """
        Alocă ID-uri meselor detectate și inițializează detectarea completă.
        """
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = True
        self.detector.detecting_all = False
        self.current_frame = self.detector.set_table_ids()
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="normal")

    def reset_tables(self):
        self.detector.detecting_tables_only = False
        self.detector.done_setting_tables = False
        self.detector.detecting_all = False
        self.detector.reset_table_manager()
        self.set_tables_btn.config(state="disabled")
        self.reset_tables_btn.config(state="disabled")
            
    def update_status_label(self):
        """
        Obține statusul tuturor meselor și actualizează label-ul de status.
        """
        status_report = self.detector.get_tables_status_report()
        self.status_label.config(text=status_report)

    def update_frame(self):
        if self.current_frame is not None:
            display_frame(self, self.current_frame)
        self.master.after(200, self.update_frame)

    def stop_running_thread(self):
        """Oprește thread-ul curent de afișare a imaginilor în mod sigur."""
        if self.frame_thread and self.frame_thread.is_alive():
            self.stop_event.set()  # Trimite semnalul de oprire
            self.frame_thread.join()  # Așteaptă ca thread-ul să se termine
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

# Lansare aplicație
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
