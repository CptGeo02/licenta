from src.libs import *

class MoveCameraFrame(tk.Frame):
    def __init__(self, app, parent, serial_port='COM7', baud_rate=921600):
        super().__init__(parent)
        self.parent = parent  # Referință la fereastra părinte
        self.app = app
        # Joystick canvas size
        self.canvas_size = 300
        self.joystick_radius = 100
        self.inner_radius = 20
        self.center = self.canvas_size // 2
        self.max_score = 0
        self.max_x = 90
        self.max_y = 90
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg="lightblue")
        self.canvas.pack(pady=10)
        self.last_sent_x = None
        self.last_sent_y = None
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

        # Auto Set Camera Button
        auto_set_button = tk.Button(self, text="Auto Set Camera", command=self.start_auto_set_camera)
        auto_set_button.pack(pady=10)

        # Update loop for continuous value generation
        self.running = False
        self.auto_camera_active = False

        # State for auto camera
        self.auto_x_index = 0
        self.auto_y_index = 0

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
        try:
            data = f"{x_val}_{y_val}\n"
            self.arduino.write(data.encode('utf-8'))
            print(f"Trimis către Arduino: {data.strip()}")

            # Actualizăm ultimele coordonate trimise
        except Exception as e:
            self.last_sent_x = x_val
            self.last_sent_y = y_val
            print(f"Eroare la transmiterea datelor: {e}")

    def get_last_sent_coordinates(self):
        """
        Returnează ultimele coordonate X și Y trimise către Arduino.
        """
        return self.last_sent_x, self.last_sent_y

    def continuous_update(self):
        # Placeholder for continuous update logic
        if self.running:
            self.after(100, self.continuous_update)  # Adjust interval as needed

    def auto_set_camera(self):
        """
        Mișcă camera în formă de spirală pentru a acoperi toată aria vizuală,
        de sus până jos, detectând mesele.
        """
        try:
            step_size = 4 

            x_range = list(range(20, 160, step_size))
            y_range = list(range(60, 100, step_size))

            # Verificăm dacă auto_y_index depășește limita
            if self.auto_y_index >= len(y_range):
                self.send_to_arduino(self.max_x, self.max_y)
                self.auto_camera_active = False
                print("Auto set camera finished.")
                return

            # Verificăm și resetăm auto_x_index înainte de acces
            if self.auto_x_index >= len(x_range):
                self.auto_x_index = 0
                self.auto_y_index += 1
                if self.auto_y_index >= len(y_range):
                    self.send_to_arduino(self.max_x, self.max_y)
                    self.auto_camera_active = False
                    print("Auto set camera finished.")
                    return

            # Determinăm direcția mișcării pe axa X
            x_iter = x_range if self.auto_y_index % 2 == 0 else list(reversed(x_range))
            x = x_iter[self.auto_x_index]
            y = y_range[self.auto_y_index]

            # Verificăm dacă numărul de mese a crescut
            current_score = self.app.detector.frame_score
            if current_score > self.max_score:
                self.max_score = current_score
                self.max_x, self.max_y = x, y
                print(f"MAXIM LA: X={x}, Y={y}")

            # Trimitem doar coordonatele spiralate
            self.send_to_arduino(x, y)
            print(f"Mișcare camera la coordonate: X={x}, Y={y}")

            # Incrementează indexul pentru următorul pas
            self.auto_x_index += 1

        except Exception as e:
            print(f"Eroare în funcția auto_set_camera: {e}")


    def start_auto_set_camera(self):
        """
        Începe procesul de auto setare a camerei, reapelând funcția la fiecare 100ms.
        """
        if not self.auto_camera_active:
            self.auto_camera_active = True
            self.auto_x_index = 0
            self.auto_y_index = 0
            self.max_score = -1  # Resetăm scorul maxim
            self.max_x, self.max_y = 0, 0  # Resetăm coordonatele
            self.auto_set_camera_loop()


    def auto_set_camera_loop(self):
        if not self.auto_camera_active:
            return  # Oprire sigură
        self.auto_set_camera()
        self.after(200, self.auto_set_camera_loop)  # Creștem timpul de așteptare pentru a evita suprasolicitarea


    def stop_auto_set_camera(self):
        """
        Oprește procesul de auto setare a camerei.
        """
        self.auto_camera_active = False

# Test GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Move Camera Frame")
    app = MoveCameraFrame(root, serial_port='COM4', baud_rate=921600)
    app.pack()
    root.mainloop()
