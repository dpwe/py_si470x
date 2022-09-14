# py_si470x
Python class encapsulating si4702/si4703 fm receiver chip on R-Pi running blinka (circuitpython-like).

`si470x.py` implements `class SI4703` which handles the initialization and communication with an SI4702/4703 connected over the default I2C bus (`board.I2C()`).  The SI470x RST line must also be connected to a GPIO, this is on `board.D23` by default, but can be overridden with an initialization argument.

`rotary_encoder.py` contains a class wrapping the [Adafruit Stemma QT Rotary Encoder](https://www.adafruit.com/product/4991)

`radio.py` is a minimal program that boots an SI4703, tunes it to 93.9 MHz (WNYC!), and allows the volume to be controlled by a rotary encoder.

This works with the [Sparkfun FM Tuner Basic Breakout](https://www.sparkfun.com/products/11083), where the analog output(s) are connected to an audio amp (e.g. [this](https://www.adafruit.com/product/2130)) to make the actual radio sound.

RDS support (which is perhaps the main attraction of the SI4703) will be added at a later date.
