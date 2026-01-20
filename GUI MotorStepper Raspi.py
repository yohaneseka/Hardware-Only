import tkinter as tk
from tkinter import ttk, messagebox
import RPi.GPIO as GPIO
import time
import threading

# =====================
# GPIO CONFIG
# =====================
GPIO.setmode(GPIO.BCM)

IN1, IN2, IN3, IN4 = 17, 18, 27, 22
pins = [IN1, IN2, IN3, IN4]

for p in pins:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

# Stepper sequence (half-step)
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

step_delay = 0.002
position = 0

# =====================
# MOTOR FUNCTION
# =====================
def move(steps, direction):
    global position
    seq = SEQ if direction == 1 else reversed(SEQ)

    for _ in range(abs(steps)):
        for s in seq:
            for pin, val in zip(pins, s):
                GPIO.output(pin, val)
            time.sleep(step_delay)

        position += direction

    for p in pins:
        GPIO.output(p, 0)

# =====================
# BUTTON ACTIONS
# =====================
def fast_up():
    steps = int(fast_entry.get())
    threading.Thread(target=move, args=(steps, 1)).start()
    update_position()

def fast_down():
    steps = int(fast_entry.get())
    threading.Thread(target=move, args=(steps, -1)).start()
    update_position()

def fine_up():
    steps = int(fine_entry.get())
    threading.Thread(target=move, args=(steps, 1)).start()
    update_position()

def fine_down():
    steps = int(fine_entry.get())
    threading.Thread(target=move, args=(steps, -1)).start()
    update_position()

def update_position():
    pos_label.config(text=f"Position: {position} step")

def on_closing():
    GPIO.cleanup()
    root.destroy()

# =====================
# GUI
# =====================
root = tk.Tk()
root.title("Microscope Z-Axis Control (Raspberry Pi)")
root.geometry("350x420")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_closing)

frame = ttk.Frame(root, padding=15)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Microscope Motor Control",
          font=("Arial", 14, "bold")).pack(pady=5)

# FAST
fast_frame = ttk.LabelFrame(frame, text="FAST MOVE", padding=10)
fast_frame.pack(fill="x", pady=5)

fast_entry = ttk.Entry(fast_frame, justify="center")
fast_entry.insert(0, "2000")
fast_entry.pack(pady=5)

ttk.Button(fast_frame, text="▲ FAST UP", command=fast_up).pack(fill="x")
ttk.Button(fast_frame, text="▼ FAST DOWN", command=fast_down).pack(fill="x")

# FINE
fine_frame = ttk.LabelFrame(frame, text="FINE MOVE", padding=10)
fine_frame.pack(fill="x", pady=5)

fine_entry = ttk.Entry(fine_frame, justify="center")
fine_entry.insert(0, "100")
fine_entry.pack(pady=5)

ttk.Button(fine_frame, text="▲ FINE UP", command=fine_up).pack(fill="x")
ttk.Button(fine_frame, text="▼ FINE DOWN", command=fine_down).pack(fill="x")

# POSITION
pos_frame = ttk.LabelFrame(frame, text="Position", padding=10)
pos_frame.pack(fill="x", pady=5)

pos_label = ttk.Label(pos_frame, text="Position: 0 step",
                      font=("Arial", 10, "bold"))
pos_label.pack()

root.mainloop()
