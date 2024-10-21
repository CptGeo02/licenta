from src.libs import *

def load_images(folder_path):
    """Load all image files from a folder."""
    return [img for img in os.listdir(folder_path) if img.endswith(('.png', '.jpg', '.jpeg'))]
