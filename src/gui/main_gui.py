from src.libs import *
from src.gui.run_camera import run_camera
from src.gui.run_video import run_video
from src.gui.display_frame import display_frame  # Modificat
from src.utils.image_utils import *
from src.detectors.yolo_detector import YoloDetector

class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Restaurant Monitoring System")
        self.master.geometry("800x600")

        # Inițializează YOLO Detector
        self.detector = YoloDetector()

        # Creează un frame pentru butoane
        self.button_frame = Frame(master)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        self.start_camera_btn = Button(self.button_frame, text="Start Live Camera", command=self.start_camera)
        self.start_camera_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.select_video_btn = Button(self.button_frame, text="Select Video", command=self.select_video)
        self.select_video_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.images_btn = Button(self.button_frame, text="Show Images", command=self.show_images)
        self.images_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_btn = Button(self.button_frame, text="Next", command=self.next_image)
        self.next_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.previous_btn = Button(self.button_frame, text="Previous", command=self.previous_image)
        self.previous_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.exit_btn = Button(self.button_frame, text="Exit", command=master.quit)
        self.exit_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Adaugă un switch pentru activarea YOLO
        self.auto_detect_enabled = BooleanVar(value=False)
        self.auto_detect_switch = Checkbutton(self.button_frame, text="Auto-Detect", variable=self.auto_detect_enabled, onvalue=True, offvalue=False)
        self.auto_detect_switch.pack(side=tk.LEFT, padx=5, pady=5)

        # Adaugă butoanele pentru detectarea și setarea meselor
        self.detect_tables_btn = Button(self.button_frame, text="Detect Tables", command=self.detect_tables)
        self.detect_tables_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_tables_btn = Button(self.button_frame, text="Set Tables", command=self.set_tables)
        self.set_tables_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.canvas = Canvas(master, width=640, height=480)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label = Label(self.canvas)
        self.label.pack()

        self.status_label = Label(master, text="", wraplength=780)  # Label pentru statusul meselor
        self.status_label.pack(side=tk.BOTTOM, pady=10)  # Afișează la baza ferestrei

        self.video_source = None
        self.current_frame = None
        self.running = False
        self.image_thread = None
        self.images = []  # Loaded images
        self.image_index = 0  # Current image index

        # Adaugă un event pentru oprirea thread-ului în siguranță
        self.stop_event = threading.Event()

    def start_camera(self):
        self.stop_running_thread()
        self.running = True
        self.stop_event.clear()
        self.image_thread = threading.Thread(target=run_camera, args=(self,))
        self.image_thread.start()
        self.auto_detect_switch.config(state=tk.NORMAL)  # Activează butonul "Auto-Detect"
        self.update_frame()

    def select_video(self):
        self.stop_running_thread()
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if video_path:
            self.video_source = video_path
            self.running = True
            self.stop_event.clear()
            self.image_thread = threading.Thread(target=run_video, args=(self,))
            self.image_thread.start()
            self.auto_detect_switch.config(state=tk.NORMAL)  # Activează butonul "Auto-Detect"
            self.update_frame()

    def show_images(self):
        self.stop_running_thread()
        self.images = load_images('data/images/')
        self.image_index = 0
        self.running = False
        self.auto_detect_switch.config(state=tk.NORMAL)  # Activează butonul "Auto-Detect"
        if self.images:
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)
            if self.current_frame is not None:
                display_frame(self, self.current_frame)

    def detect_tables(self):
        """
        Activează detectarea doar a meselor fără ID.
        """
        self.detector.detecting_tables_only = True
        display_frame(self, self.current_frame)

    def set_tables(self):
        """
        Alocă ID-uri meselor detectate și inițializează detectarea completă.
        """
        self.detector.done_setting_tables = True
        self.current_frame = self.detector.set_table_ids()
        display_frame(self, self.current_frame)  # Actualizează GUI cu frame-ul procesat

    def update_status_label(self):
        """
        Obține statusul tuturor meselor și actualizează label-ul de status.
        """
        status_report = self.detector.get_tables_status_report()
        self.status_label.config(text=status_report)

    def update_frame(self):
        if self.current_frame is not None:
            display_frame(self, self.current_frame)  # Afișează doar cadrul, fără detecție
        self.master.after(200, self.update_frame)

    def stop_running_thread(self):
        """Oprește thread-ul curent de afișare a imaginilor în mod sigur."""
        if self.image_thread and self.image_thread.is_alive():
            self.stop_event.set()  # Trimite semnalul de oprire
            self.image_thread.join()  # Așteaptă ca thread-ul să se termine
        self.running = False
        # Dezactivează switch-ul de "Auto-Detect" (dacă este necesar)
        self.auto_detect_switch.config(state=tk.DISABLED)

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
