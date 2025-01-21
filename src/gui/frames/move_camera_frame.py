from src.libs import tk
import math
import serial

class MoveCameraFrame(tk.Frame):
    def __init__(self, parent, serial_port='COM4', baud_rate=921600):
        super().__init__(parent)
        self.parent = parent  # Referință la fereastra părinte

        # Joystick canvas size
        self.canvas_size = 300
        self.joystick_radius = 100
        self.inner_radius = 20
        self.center = self.canvas_size // 2

        # Create Canvas
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg="lightblue")
        self.canvas.pack(pady=10)

        # Draw Joystick Base
        self.canvas.create_oval(
            self.center - self.joystick_radius,
            self.center - self.joystick_radius,
            self.center + self.joystick_radius,
            self.center + self.joystick_radius,
            fill="white",
            outline="black",
            width=2,
        )

        # Draw Movable Inner Circle (Joystick Control Circle)
        self.inner_circle = self.canvas.create_oval(
            self.center - self.inner_radius,
            self.center - self.inner_radius,
            self.center + self.inner_radius,
            self.center + self.inner_radius,
            fill="gray",
            outline="black",
        )

        # Initialize the current position of the inner circle
        self.current_x = 0
        self.current_y = 0

        # Close existing serial connection if active
        if hasattr(self, 'arduino') and self.arduino and self.arduino.is_open:
            print("Closing existing serial connection.")
            self.arduino.close()

        # Initialize serial communication
        try:
            self.arduino = serial.Serial(serial_port, baud_rate, timeout=1)
            print(f"Serial port {serial_port} opened successfully.")
        except serial.SerialException as e:
            self.arduino = None
            print(f"Failed to open serial port {serial_port}: {e}")

        # Bind Events
        self.canvas.bind("<B1-Motion>", self.move_joystick)  # Mouse held down and moving

        # Reset Button
        reset_button = tk.Button(self, text="Reset Position", command=self.reset_position)
        reset_button.pack(pady=10)

        # Update loop for continuous value generation
        self.running = False

    def move_joystick(self, event):
        # Calculate the new position based on mouse cursor
        dx = event.x - self.center
        dy = event.y - self.center
        distance = math.sqrt(dx**2 + dy**2)

        # Limit the movement to the joystick radius
        if distance > self.joystick_radius:
            dx = dx / distance * self.joystick_radius
            dy = dy / distance * self.joystick_radius

        # Update the position of the inner circle
        self.canvas.coords(
            self.inner_circle,
            self.center + dx - self.inner_radius,
            self.center + dy - self.inner_radius,
            self.center + dx + self.inner_radius,
            self.center + dy + self.inner_radius,
        )

        # Normalize to range [0, 180]
        x_val = int(((dx + self.joystick_radius) / (2 * self.joystick_radius)) * 180)
        y_val = int(((self.joystick_radius - dy) / (2 * self.joystick_radius)) * 180)  # Inverted Y-axis

        # Print values
        print(f"X: {x_val}, Y: {y_val}")

        # Send values to Arduino
        if self.arduino:
            self.send_to_arduino(x_val, y_val)

        # Start continuous update if not already running
        if not self.running:
            self.running = True
            self.continuous_update()

    def reset_position(self):
        """
        Reset joystick position to center and send `90_90` to Arduino.
        """
        # Reset the inner circle to the center
        self.canvas.coords(
            self.inner_circle,
            self.center - self.inner_radius,
            self.center - self.inner_radius,
            self.center + self.inner_radius,
            self.center + self.inner_radius,
        )

        # Send default values to Arduino
        default_x = 90
        default_y = 90
        print("Resetting joystick to center: X: 90, Y: 90")
        if self.arduino:
            self.send_to_arduino(default_x, default_y)

    def send_to_arduino(self, x_val, y_val):
        """
        Trimite valorile X și Y sub forma unui string "<valueX>_<valueY>" către Arduino prin USB.
        """
        try:
            data = f"{x_val}_{y_val}\n"  # Formatează ca string și adaugă newline pentru delimitare
            self.arduino.write(data.encode('utf-8'))  # Trimite string-ul ca bytes
            print(f"Trimis către Arduino: {data.strip()}")
        except Exception as e:
            print(f"Eroare la transmiterea datelor: {e}")

    def continuous_update(self):
        # Placeholder for continuous update logic
        if self.running:
            self.after(100, self.continuous_update)  # Adjust interval as needed

# Test GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Move Camera Frame")
    app = MoveCameraFrame(root, serial_port='COM4', baud_rate=921600)
    app.pack()
    root.mainloop()
