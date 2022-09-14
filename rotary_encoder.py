# rotary_encoder object

import board
from adafruit_seesaw import seesaw, rotaryio, digitalio

class RotaryEncoder(object):
    """Class enapsulates Adafruit rotary encoder.

    Initialization Args:
      i2c: I2C interface object (default is board default).
      button_num: Logical pin number for encoder button.
      on_change: Optional callback function.  When encoder moves, this function
        is called with the *change* (+ or -) in encoder position.
      on_press: Optional callback function.  When button state changes, this 
        function is called with boolean argument as new button state (True=pressed).
    """
    
    def __init__(self, i2c=None, button_num=24, on_change=None, on_press=None):
        # Store callbacks.
        self.on_change = on_change
        self.on_press = on_press
        if i2c == None:
            i2c = board.I2C()
        self.ss = seesaw.Seesaw(i2c, addr=0x36)
        self.ss.pin_mode(button_num, self.ss.INPUT_PULLUP)
        self.button = digitalio.DigitalIO(self.ss, button_num)
        self.button_held = False
        self.encoder = rotaryio.IncrementalEncoder(self.ss)
        self.last_position = 0

    def update(self):
        position = (self.encoder.position & 0xFFFF)
        if position > 32767:
            position -= 65536
        if position != self.last_position:
            #print("Position: {}".format(position))
            if self.on_change != None:
                # Send delta, not absolute position.
                self.on_change(position - self.last_position)
            self.last_position = position
        if not self.button.value and not self.button_held:
            self.button_held = True
            if self.on_press != None:
                self.on_press(self.button_held)
        if self.button.value and self.button_held:
            self.button_held = False
            if self.on_press != None:
                self.on_press(self.button_held)

    def position(self):
        self.update()
        return self.last_position

    def pressed(self):
        self.update()
        return self.button_held
