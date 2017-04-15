import time
import threading
import random
from collections import deque

from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED

# Color config
BACKGROUND_COLOR = (0, 0, 0)
RAINBOW_COLOR = deque([
    (143, 0, 255), (75, 0, 130),
    (0, 0, 255), (0, 255, 0),
    (255, 255, 0), (255, 127, 0),
    (255, 0, 0), (243, 64, 147)
])

# Sense config
SENSE = SenseHat()
SENSE_DEFAULT_ROTATION = 180 # Default rotation, set_rotation
SENSE_LOW_LIGHT = True # Default brightness, low_light
SENSE_LED_UPDATE_INTERVAL = 0.125 # Default LED update speed

# Add or subtract integer.
def switch_values(height_set):
    for index, value in enumerate(height_set):
        if value >= 8:
            height_set[index] = value - random.randint(2, 3)
        elif value <= 1:
            height_set[index] = value + random.randint(1, 2)
        else:
            if bool(random.getrandbits(1)):
                height_set[index] = value + 1
            else:
                height_set[index] = value - 1

    return height_set

# Create matrix set.
def create_matrix(color_set, horizon_start_height):
    matrix_set = SENSE.get_pixels()

    for hori in range(8):
        color = color_set[hori]
        vert_offset = 0

        for vert in range(8):
           if horizon_start_height[hori] > vert:
               matrix_set[hori + (vert * 8)] = color
           else:
               matrix_set[hori + (vert * 8)] = BACKGROUND_COLOR

    return (matrix_set, horizon_start_height)

# Apply matrix set to sense.
def apply_matrix(color_set=RAINBOW_COLOR):
    global SENSE_LED_UPDATE_INTERVAL
    horizon_start_height = [random.randint(1, 8) for i in range(8)]

    while True:
        horizon_start_height = switch_values(horizon_start_height)
        matrix, horizon_start_height = create_matrix(color_set, horizon_start_height)

        SENSE.set_pixels(matrix)
        time.sleep(SENSE_LED_UPDATE_INTERVAL)

# Get event and apply action to sense.
def apply_joystick_event():
    global SENSE_LED_UPDATE_INTERVAL
    sense_current_rotation = SENSE_DEFAULT_ROTATION

    while True:
        for event in SENSE.stick.get_events():
            # On pressed
            if event.action == ACTION_PRESSED:
                # Right direction
                if event.direction == "right":
                    RAINBOW_COLOR.rotate(-1)
                # Left direction
                elif event.direction == "left":
                    RAINBOW_COLOR.rotate(1)
                # Middle direction
                elif event.direction == "middle" and event.action == ACTION_PRESSED:
                    if sense_current_rotation >= 0 and sense_current_rotation < 270:
                        sense_current_rotation += 90
                        SENSE.set_rotation(sense_current_rotation)
                    else:
                        sense_current_rotation = 0
                        SENSE.set_rotation(sense_current_rotation)
                # Up direction
                elif event.direction == "up":
                    if SENSE_LED_UPDATE_INTERVAL <= 1.000:
                        SENSE_LED_UPDATE_INTERVAL += 0.125
                # DOWN direction
                elif event.direction == "down":
                    if SENSE_LED_UPDATE_INTERVAL > 0.125:
                        SENSE_LED_UPDATE_INTERVAL -= 0.125

        time.sleep(0.2) # Need sleep to prevent overhead.

if __name__ == '__main__':
    SENSE.set_rotation(SENSE_DEFAULT_ROTATION)
    SENSE.low_light = SENSE_LOW_LIGHT
    SENSE.clear()

    try:
        t_matrix = threading.Thread(target=apply_matrix)
        t_joystick = threading.Thread(target=apply_joystick_event)

        t_joystick.daemon = True # Demonize joystick event function

        t_joystick.start()
        t_matrix.start()
    except Exception as e:
        print(e)