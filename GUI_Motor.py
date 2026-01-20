import tkinter as tk
from tkinter import ttk
import LGPIO.GPIO as GPIO
import time
import threading

# =====================
# GPIO SETUP
# =====================
GPIO.setmode(GPIO.BCM)

IN1, IN2, IN3, IN4 = 17, 18, 27, 22
PINS = [IN1, IN2, IN3, IN4]

for p in PINS:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

# Half-step sequence
SEQ = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
]

STEP_DELAY = 0.002

current_position = 0
motor_busy = False

# =====================
# MOTOR CONTROL
# =====================
def move_steps(steps):
    global current_position, motor_busy
    motor_busy = True

    direction = 1 if steps > 0 else -1
    steps = abs(steps)

    for _ in range(steps):
        for s in (SEQ if direction == 1 else reversed(SEQ)):
            for pin, val in zip(PINS, s):
                GPIO.output(pin, val)
            time.sleep(STEP_DELAY)

        current_position += direction

    for p in PINS:
        GPIO.output(p, 0)

    motor_busy = False

# =====================
# SLIDER CALLBACK
# =====================
def slider_changed(val):
    global current_position, motor_busy

    target = int(float(val))
    delta = target - current_position

    pos_label.config(text=f"Position: {current_position} step")

    if delta != 0 and not motor_busy:
        threading.Thread(target=move_steps, args=(delta,), daemon=True).start()

# =====================
# CLEAN EXIT
# =====================
def on_close():
    GPIO.cleanup()
    root.destroy()

# =====================
# GUI
# =====================
root = tk.Tk()
root.title("Microscope Z-Axis Control (Slider)")
root.geometry("350x300")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_close)

frame = ttk.Frame(root, padding=15)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Z-Axis Control",
          font=("Arial", 14, "bold")).pack(pady=10)

slider = ttk.Scale(
    frame,
    from_=-5000,
    to=5000,
    orient="vertical",
    command=slider_changed
)
slider.set(0)
slider.pack(pady=10, fill="y")

pos_label = ttk.Label(frame, text="Position: 0 step",
                      font=("Arial", 11, "bold"))
pos_label.pack(pady=10)

ttk.Label(frame, text="↑ UP\n↓ DOWN",
          font=("Arial", 9)).pack()

root.mainloop()

