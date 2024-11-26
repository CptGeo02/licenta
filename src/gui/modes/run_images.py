from src.libs import *
from src.utils.image_utils import *

def run_images(self):
    """
    Rulează procesul de încărcare și afișare a imaginilor pe un thread separat.
    """
    self.images = load_images('data/images/')
    self.image_index = 0

    if self.images:
        while not self.stop_event.is_set():
            img_path = os.path.join('data/images/', self.images[self.image_index])
            self.current_frame = cv2.imread(img_path)
            if self.current_frame is not None:
                self.update_frame()
            
            # Avansează la următoarea imagine (poți schimba logica de avansare)
            self.image_index = (self.image_index + 1) % len(self.images)