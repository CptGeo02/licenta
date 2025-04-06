import tkinter as tk
import cv2
import serial
import struct

def create_slider(label, parent, default):
    slider = tk.Scale(
        parent,
        from_=0,
        to=180,
        orient="horizontal",
        label=f"Slider {label}",
        tickinterval=20
    )
    slider.set(default)
    return slider

def send_values(arduino, ox_slider, oy_slider, previous_values):
    ox = ox_slider.get()
    oy = oy_slider.get()

    if ox != previous_values['ox'] or oy != previous_values['oy']:
        previous_values['ox'] = ox
        previous_values['oy'] = oy
        message = f"{ox}_{oy}"
        arduino.write(message.encode())
        print(f"Trimis către Arduino: {message}")

def build_servo_test_gui():
    root = tk.Tk()
    root.title("Test Servos")

    # Conectare Arduino
    arduino = serial.Serial('COM4', 921600, timeout=1)

    # Variabile pentru trimitere condiționată
    previous_values = {'ox': 90, 'oy': 90}

    # Frame pentru slider
    slider_frame = tk.Frame(root)
    slider_frame.pack(pady=20)

    ox_slider = create_slider("Ox", slider_frame, 90)
    ox_slider.pack(pady=10)
    oy_slider = create_slider("Oy", slider_frame, 90)
    oy_slider.pack(pady=10)

    # Buton trimitere
    send_button = tk.Button(
        root,
        text="Send Values",
        command=lambda: send_values(arduino, ox_slider, oy_slider, previous_values)
    )
    send_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    build_servo_test_gui()
