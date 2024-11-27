from src.libs import tk
import math

class MoveCameraFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

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

        # Draw Movable Inner Circle (Joystic Control Circle)
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

        # Bind Events
        self.canvas.bind("<B1-Motion>", self.move_joystick)  # Mouse held down and moving
        self.canvas.bind("<ButtonRelease-1>", self.reset_joystick)  # Mouse released

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

        # Normalize to range [-512, 511]
        x_val = int((dx / self.joystick_radius) * 511)
        y_val = int((-dy / self.joystick_radius) * 511)  # Negative for inverted Y-axis

        # Print values
        print(f"X: {x_val}, Y: {y_val}")

        # Start continuous update if not already running
        if not self.running:
            self.running = True
            self.continuous_update()

    def continuous_update(self):
        # Placeholder for continuous update logic
        if self.running:
            self.after(100, self.continuous_update)  # Adjust interval as needed

    def reset_joystick(self, event):
        # Reset the position of the inner circle to the center of the joystick
        self.canvas.coords(
            self.inner_circle,
            self.center - self.inner_radius,
            self.center - self.inner_radius,
            self.center + self.inner_radius,
            self.center + self.inner_radius,
        )

        # Reset values to (0, 0)
        print("X: 0, Y: 0")
        self.running = False