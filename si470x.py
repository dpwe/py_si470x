# si4702 control via adafruit i2c
import time
import board
import digitalio

class SI4703(object):

  def __init__(self, i2c=None, i2c_addr=0x10, reset_pin=board.D23, tuning=None):
    if i2c is None:
      i2c = board.I2C()
    self.i2c = i2c
    self.i2c_addr = i2c_addr
    self.reset_pin = reset_pin
    self.volume = 0
    self.tuning = tuning
    self.reinitialize()

  def reinitialize(self):
    # Powerup sequence.
    self.reset()
    self.initialize()
    if self.tuning:
      self.tune(self.tuning)
    
  def reset(self):
    # Boot si4703 into i2c mode by pulling reset low while i2c SDA is low.
    reset_pin = digitalio.DigitalInOut(self.reset_pin)
    reset_pin.direction = digitalio.Direction.OUTPUT
    reset_pin.value = True
    # Pin glitches at start up.  Let it settle.
    time.sleep(0.500)
    # Pull reset low for 1ms.
    reset_pin.value = False
    time.sleep(0.001)
    reset_pin.value = True
    time.sleep(0.005)

  def powerup(self, enable=True):
    # After RdSpi/si4703.c:si_power().
    regs = self.getregs()
    if enable:
      regs[2] = 0x01  # PWR_ENABLE
      regs[4] |= 0x1800  # RDS | DE
      regs[4] &= 0xFF3F  # !BLNDADJ
      regs[5] = 0x0C10  # SEEKTH12 | BAND0 | SPACE100
      regs[6] &= 0xFF00
      regs[6] |= 0x024F  # RDSPRF | SKSNR 4, SKCNT 15
    else:
      regs[2] = 0x41  # PWR_DISABLE | PWR_ENABLE
    self.setregs(regs)
    time.sleep(0.110)
  
  def initialize(self):
    regs = self.getregs()
    #print("init:", list(hex(r) for r in regs))
    # Enable oscillator.
    regs[7] |= 0x8000
    self.setregs(regs)
    time.sleep(0.5)  # recommended delay.
    regs = self.getregs()
    #print("+osc:", list(hex(r) for r in regs))
    # Power down, then power up.
    self.powerup(False)
    self.powerup(True)
    regs = self.getregs()
    #print("+pwr:", list(hex(r) for r in regs))

  def tune(self, freq):
    self.tuning = freq
    regs = self.getregs()
    band_range = [(87.5, 107.0), (76.0, 108.0), (76.0, 90.0)][(regs[5] >> 6) & 3]
    spacing = [0.05, 0.1, 0.2][(regs[5] >> 4) & 3]
    chan_index = int(round((freq - band_range[0]) / spacing))
    #print("Freq", freq, "index", chan_index)
    regs[3] = 0x8000 + chan_index
    self.setregs(regs)
  
  def getregs(self):
    result = bytearray(32)
    self.i2c.readfrom_into(self.i2c_addr, result)
    regs = []
    for r in range(16):
      # si4702 returns registers as 10-15, then 0-9, big-endian.
      reg_index = (r + 6) % 16
      regs.append(256 * result[2*reg_index] + result[2*reg_index + 1])
    return regs

  def setregs(self, regs):
    # Only write regs 2..7, automatically starts at 2
    data = bytearray(12)
    for r in range(2, 8):
      data[2*r - 4] = regs[r] // 256
      data[2*r - 3] = regs[r] % 256
    self.i2c.writeto(self.i2c_addr, data, stop=False)

  def set_volume(self, vol):
    #print("si470x set_volume", vol)
    if vol < 0:
      vol = 0
    #if vol > 30:
    #  vol = 30
    regs = self.getregs()
    if vol > 15:
      #regs[6] |= 0x0100  # VOLEXT
      #vol -= 15
      vol = 15
    #else:
    #  regs[6] &= 0xFEFF  # !VOLEXT
    if vol:
      regs[2] |= 0xC000  # DSMUTE | DMUTE
    else:
      regs[2] &= 0x3FFF  # !(DSMUTE | DMUTE)
    # Volume is bottom nybble of reg 5
    regs[5] = (regs[5] & 0xFFF0) + vol
    self.setregs(regs)
    self.volume = vol

  def change_volume(self, delta):
    self.set_volume(self.volume + delta)
