from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip

# Funcție pentru descărcarea videoclipului la calitatea maximă disponibilă
def download_video(youtube_url, output_path="video.mp4"):
    try:
        # Creează obiectul YouTube
        yt = YouTube(youtube_url)
        
        # Alege stream-ul cu cea mai mare rezoluție video
        stream = yt.streams.get_highest_resolution()
        
        # Descarcă video-ul
        print(f"Downloading {yt.title} ...")
        stream.download(filename=output_path)
        print("Download completed!")
        
        return output_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Funcție pentru a extrage primele 10 ore din videoclip
def extract_first_10_hours(input_video, output_video="first_10_hours.mp4"):
    try:
        clip = VideoFileClip(input_video)
        
        # Verifică durata video-ului
        video_duration = clip.duration  # in seconds
        ten_hours_in_seconds = 10 * 60 * 60
        
        # Dacă video-ul e mai scurt decât 10 ore, folosește durata lui
        end_time = min(ten_hours_in_seconds, video_duration)
        
        # Extrage partea dorită
        new_clip = clip.subclip(0, end_time)
        
        # Salvează noul video
        new_clip.write_videofile(output_video, codec="libx264")
        print(f"Saved the first {end_time / 3600} hours to {output_video}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Link-ul videoclipului YouTube
youtube_url = "https://www.youtube.com/watch?v=FzD8t6ObXOI&ab_channel=MARUNUMA"

# Descarcă video-ul
downloaded_video = download_video(youtube_url)

# Extrage primele 10 ore din video dacă descărcarea a fost reușită
if downloaded_video:
    extract_first_10_hours(downloaded_video)
