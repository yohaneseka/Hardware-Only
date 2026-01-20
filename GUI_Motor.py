import tkinter as tk
from tkinter import ttk, messagebox
import lgpio
import time
import threading

# =====================
# GPIO CONFIG
# =====================
CHIP = 0
IN1, IN2, IN3, IN4 = 17, 18, 27, 22
PINS = [IN1, IN2, IN3, IN4]

chip = lgpio.gpiochip_open(CHIP)

for p in PINS:
    lgpio.gpio_claim_output(chip, p, 0)

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
# MOTOR LOGIC
# =====================
def move_steps(steps):
    global current_position, motor_busy
    motor_busy = True

    direction = 1 if steps > 0 else -1
    steps = abs(steps)

    for _ in range(steps):
        for s in (SEQ if direction == 1 else reversed(SEQ)):
            for pin, val in zip(PINS, s):
                lgpio.gpio_write(chip, pin, val)
            time.sleep(STEP_DELAY)
        current_position += direction

    for p in PINS:
        lgpio.gpio_write(chip, p, 0)

    motor_busy = False
    root.after(0, update_position_label)

def safe_move(steps):
    if not motor_busy:
        threading.Thread(target=move_steps, args=(steps,), daemon=True).start()
    else:
        messagebox.showwarning("Warning", "Motor is busy!")

# =====================
# BUTTON ACTIONS
# =====================
def fast_up():
    try:
        steps = int(fast_entry.get())
        safe_move(steps)
    except ValueError:
        messagebox.showerror("Error", "Invalid step value")

def fast_down():
    try:
        steps = int(fast_entry.get())
        safe_move(-steps)
    except ValueError:
        messagebox.showerror("Error", "Invalid step value")

def fine_up():
    try:
        steps = int(fine_entry.get())
        safe_move(steps)
    except ValueError:
        messagebox.showerror("Error", "Invalid step value")

def fine_down():
    try:
        steps = int(fine_entry.get())
        safe_move(-steps)
    except ValueError:
        messagebox.showerror("Error", "Invalid step value")

def update_position_label():
    pos_label.config(text=f"Position: {current_position} step")

def on_closing():
    for p in PINS:
        lgpio.gpio_write(chip, p, 0)
    lgpio.gpiochip_close(chip)
    root.destroy()

# =====================
# GUI SETUP
# =====================
root = tk.Tk()
root.title("Microscope Z-Axis Control (Raspberry Pi)")
root.geometry("350x450")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_closing)

frame = ttk.Frame(root, padding=15)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Microscope Motor Control",
          font=("Arial", 14, "bold")).pack(pady=5)

# FAST MOVE
fast_frame = ttk.LabelFrame(frame, text="FAST MOVE", padding=10)
fast_frame.pack(fill="x", pady=5)

ttk.Label(fast_frame, text="Steps:").pack()
fast_entry = ttk.Entry(fast_frame, width=15, justify="center")
fast_entry.insert(0, "2000")
fast_entry.pack(pady=5)

ttk.Button(fast_frame, text="▲ FAST UP", command=fast_up).pack(pady=2, fill="x")
ttk.Button(fast_frame, text="▼ FAST DOWN", command=fast_down).pack(pady=2, fill="x")

# FINE MOVE
fine_frame = ttk.LabelFrame(frame, text="FINE MOVE", padding=10)
fine_frame.pack(fill="x", pady=5)

ttk.Label(fine_frame, text="Steps:").pack()
fine_entry = ttk.Entry(fine_frame, width=15, justify="center")
fine_entry.insert(0, "100")
fine_entry.pack(pady=5)

ttk.Button(fine_frame, text="▲ FINE UP", command=fine_up).pack(pady=2, fill="x")
ttk.Button(fine_frame, text="▼ FINE DOWN", command=fine_down).pack(pady=2, fill="x")

# Position
pos_frame = ttk.LabelFrame(frame, text="Position Info", padding=10)
pos_frame.pack(fill="x", pady=5)

pos_label = ttk.Label(pos_frame, text="Position: 0 step", font=("Arial", 10, "bold"))
pos_label.pack(pady=5)

root.mainloop()
