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

        self.canvas = Canvas(master, width=640, height=480)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label = Label(self.canvas)
        self.label.pack()

        self.video_source = None
        self.current_frame = None
        self.running = False
        self.image_thread = None
        self.images = []  # Loaded images
        self.image_index = 0  # Current image index

        # Adaugă un event pentru oprirea thread-ului în siguranță
        self.stop_event = threading.Event()

    def start_camera(self):
        # Oprește thread-ul precedent
        self.stop_running_thread()

        # Pornește camera live
        self.running = True
        self.stop_event.clear()
        self.image_thread = threading.Thread(target=run_camera, args=(self,))
        self.image_thread.start()

        # Actualizează canvas-ul cu frame-uri
        self.update_frame()

    def select_video(self):
        # Oprește thread-ul precedent
        self.stop_running_thread()

        # Selectează și pornește redarea video
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if video_path:
            self.video_source = video_path
            self.running = True
            self.stop_event.clear()
            self.image_thread = threading.Thread(target=run_video, args=(self,))
            self.image_thread.start()

            # Actualizează canvas-ul cu frame-uri
            self.update_frame()

    def show_images(self):
        # Oprește thread-ul precedent
        self.stop_running_thread()

        self.images = load_images('data/images/')
        self.image_index = 0
        self.running = False  # Oprește execuția anterioară
        if self.images:
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)  # Citește imaginea curentă
            if self.current_frame is not None:
                display_frame(self, self.current_frame)  # Folosește noua funcție display_frame

    def next_image(self):
        if self.images:
            self.image_index = (self.image_index + 1) % len(self.images)  # Incrementează indexul
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)  # Citește următoarea imagine
            if self.current_frame is not None:
                display_frame(self, self.current_frame)  # Afișează imaginea actualizată

    def previous_image(self):
        if self.images:
            self.image_index = (self.image_index - 1) % len(self.images)  # Decrementează indexul
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)  # Citește imaginea anterioară
            if self.current_frame is not None:
                display_frame(self, self.current_frame)  # Afișează imaginea actualizată

    def update_frame(self):
        if self.current_frame is not None:
            display_frame(self, self.current_frame)  # Afișează cadrul curent
        # Adaptează intervalul în funcție de viteza de detectare și afișare
        self.master.after(200, self.update_frame)

    def stop_running_thread(self):
        self.running = False
        self.stop_event.set()  # Setează eventul pentru a opri thread-ul
        if self.image_thread is not None and self.image_thread.is_alive():
            self.image_thread.join()  # Așteaptă ca thread-ul să se termine
        
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
