# radio.py
#
# Drive the si4703 radio with a rotary controller volume control.

import time

import digitalio
import board

import si470x
import rotary_encoder

# Setup radio
i2c = board.I2C()
si4703 = si470x.SI4703(i2c=i2c, tuning=93.90)
volume = rotary_encoder.RotaryEncoder(i2c=i2c, on_change=si4703.change_volume)

while True:
    # Maybe change radio volume.
    volume.update()
    time.sleep(0.1)
