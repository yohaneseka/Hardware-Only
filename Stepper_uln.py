import time

# NOTE:
# GPIO code is intended to run on Raspberry Pi only.
# Do not run on Windows.

try:
    import gpiod
except ImportError:
    print("This script must be run on Raspberry Pi OS")
    exit(1)

chip = gpiod.Chip('gpiochip0')

pins = [17, 18, 27, 22]
lines = chip.get_lines(pins)
lines.request(consumer="stepper", type=gpiod.LINE_REQ_DIR_OUT)

sequence = [
    [1,0,0,0],
    [0,1,0,0],
    [0,0,1,0],
    [0,0,0,1]
]

try:
    while True:
        for step in sequence:
            lines.set_values(step)
            time.sleep(0.01)

except KeyboardInterrupt:
    lines.set_values([0,0,0,0])
