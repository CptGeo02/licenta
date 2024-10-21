from src.libs import *
from src.gui.run_camera import run_camera
from src.gui.run_video import run_video
from src.gui.display_image import display_image
from src.utils.image_utils import *
from src.detectors.yolo_detector import YoloDetector


class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Restaurant Monitoring System")
        self.master.geometry("800x600")

        # Inițializează YOLO Detector
        self.detector = YoloDetector()

        # Create a frame for buttons
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

    def start_camera(self):
        self.running = True
        threading.Thread(target=run_camera, args=(self,)).start()
        self.update_frame()

    def select_video(self):
        video_path = filedialog.askopenfilename()
        if video_path:
            self.video_source = video_path
            threading.Thread(target=run_video, args=(self,)).start()

    def show_images(self):
        self.images = load_images('data/images/')
        self.image_index = 0
        if self.images:
            display_image(self)  # Display the first image
        self.running = False

    def next_image(self):
        if self.images:
            self.image_index = (self.image_index + 1) % len(self.images)
            display_image(self)

    def previous_image(self):
        if self.images:
            self.image_index = (self.image_index - 1) % len(self.images)
            display_image(self)

    def update_frame(self):
        if self.current_frame is not None:
            display_image(self)
        self.master.after(100, self.update_frame)

if __name__ == "__main__":
    root = Tk()
    app = MainApp(root)
    root.mainloop()
