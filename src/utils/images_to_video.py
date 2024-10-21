import cv2
import os

# Calea către folderul cu imaginile
image_folder = 'data\\images'
# Numele fișierului video de ieșire
output_video = 'output_video.mp4'

# Obține o listă cu toate fișierele de imagine
images = [img for img in os.listdir(image_folder) if img.endswith(".png")]

# Sortează imaginile (în cazul în care sunt numerotate)
images.sort()

# Preia dimensiunea primei imagini
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

# Setează codec-ul și inițializează VideoWriter-ul
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_video, fourcc, 30, (width, height))

# Adaugă fiecare imagine în video
for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

# Eliberează resursele
cv2.destroyAllWindows()
video.release()
