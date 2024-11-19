from src.libs import *
def format_time(seconds):
    """Formatează timpul în formatul hh:mm:ss."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def convert_duration(duration_str):
        """Convertește durata în secunde."""
        if duration_str is not None:
            hours, minutes, seconds = map(int, duration_str.split(':'))
            return hours * 3600 + minutes * 60 + seconds
        else:
            return 0
