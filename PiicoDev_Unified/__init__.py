"""
PiicoDev.py: Unifies I2C drivers for different builds of MicroPython
Changelog:
    - 2021       M.Ruppe - Initial Unified Driver
    - 2022-10-13 P.Johnston - Add helptext to run i2csetup script on Raspberry Pi
    - 2022-10-14 M.Ruppe - Explicitly set default I2C initialisation parameters for machine-class (Raspberry Pi Pico + W)
    - 2023-01-31 L.Howell - Add minimal support for ESP32
    - 2023-05-17 M.Ruppe - Make I2CUnifiedMachine() more flexible on initialisation. Frequency is optional.
    - 2023-12-20 M.Taylor - added scan() function for quick userland test of connected i2c modules
    - 2025-04-05 G.Thompson - start async support, split module for different use cases
"""  # noqa

import os

_SYSNAME = os.uname().sysname
PLATFORM_BUILD = _SYSNAME if _SYSNAME in ("microbit", "Linux") else "micropython"
compat_ind = 1
i2c_err_str = (
    "PiicoDev could not communicate with module at address 0x{:02X}, check wiring"
)
compat_str = "\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n"

# The provided Python Minify fork will provide platform specific minified files.
# Each PiicoI2C class must implement the following function signatures
#
# def writeto_mem(self, addr, memaddr, buf, *, addrsize=8)  # noqa
# def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8)  # noqa
# def write8(self, addr, buf, stop=True)
# def read16(self, addr, nbytes, stop=True)  # noqa
# def __init__(self, bus=None, freq=None, sda=None, scl=None)

if PLATFORM_BUILD == "microbit":
    # noinspection PyUnresolvedReferences
    from microbit import i2c

    # noinspection PyUnresolvedReferences
    from utime import sleep_ms

    # noinspection PyUnresolvedReferences
    from asyncio import sleep_ms as a_sleep_ms

    # noinspection PyUnresolvedReferences,SpellCheckingInspection,PyMethodMayBeStatic
    class PiicoI2C:
        def __init__(self, freq=None):
            if freq is not None:
                print("Initialising I2C freq to {}".format(freq))
                # noinspection PyUnresolvedReferences
                microbit.i2c.init(freq=freq)

        def writeto_mem(self, addr, memaddr, buf, *, addrsize=8):
            ad = memaddr.to_bytes(addrsize // 8, "big")  # pad address for eg. 16 bit
            i2c.write(addr, ad + buf)

        def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
            ad = memaddr.to_bytes(addrsize // 8, "big")  # pad address for eg. 16 bit
            i2c.write(addr, ad, repeat=True)
            return i2c.read(addr, nbytes)

        def write8(self, addr, reg, data):
            if reg is None:
                i2c.write(addr, data)
            else:
                i2c.write(addr, reg + data)

        def read16(self, addr, reg):
            i2c.write(addr, reg, repeat=True)
            return i2c.read(addr, 2)

        def scan(self):
            print([hex(i) for i in self.i2c.scan()])

elif PLATFORM_BUILD == "Linux":
    from PiicoDev_Unified.linux import PiicoI2C, sleep_ms, a_sleep_ms

elif PLATFORM_BUILD == "micropython":
    # noinspection PyUnresolvedReferences
    from machine import I2C, Pin

    # noinspection PyUnresolvedReferences
    from utime import sleep_ms

    # noinspection PyUnresolvedReferences
    from asyncio import sleep_ms as a_sleep_ms

    # noinspection SpellCheckingInspection
    class PiicoI2C:

        def __init__(self, bus=None, freq=None, sda=None, scl=None):
            if _SYSNAME == "esp32" and (bus is None or sda is None or scl is None):
                raise Exception(
                    "Please input bus, machine.pin SDA, and SCL objects to use ESP32"
                )

            if freq is None:
                freq = 400_000
            if not isinstance(freq, int):
                raise ValueError("freq must be an Int")
            if freq < 400_000:
                print(
                    "\033[91mWarning: minimum freq 400kHz is recommended if using OLED module.\033[0m"
                )
            if bus is not None and sda is not None and scl is not None:
                print(
                    "Using supplied bus, sda, and scl to create machine.I2C() with freq: {} Hz".format(
                        freq
                    )
                )
                self.i2c = I2C(bus, freq=freq, sda=sda, scl=scl)
            elif bus is None and sda is None and scl is None:
                self.i2c = I2C(
                    0, scl=Pin(9), sda=Pin(8), freq=freq
                )  # RPi Pico in Expansion Board
            else:
                raise Exception("Please provide at least bus, sda, and scl")

            self.writeto_mem = self.i2c.writeto_mem
            self.readfrom_mem = self.i2c.readfrom_mem

        def writeto_mem(self, addr, memaddr, buf, *, addrsize=8):
            raise NotImplementedError("Overloaded on Init")

        def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
            raise NotImplementedError("Overloaded on Init")

        def write8(self, addr, reg, data):
            if reg is None:
                self.i2c.writeto(addr, data)
            else:
                self.i2c.writeto(addr, reg + data)

        def read16(self, addr, reg):
            self.i2c.writeto(addr, reg, False)
            return self.i2c.readfrom(addr, 2)

        def scan(self):
            print([hex(i) for i in self.i2c.scan()])

else:
    raise NotImplementedError(
        "This should never occur, this branch is here to support minification."
    )

# Platform unified create function, split for minification
if PLATFORM_BUILD == "microbit":

    _i2c = None

    # noinspection PyUnusedLocal
    def create_unified_i2c(
        bus=None, freq=None, sda=None, scl=None, suppress_warnings=True
    ):
        global _i2c
        if not _i2c:
            _i2c = PiicoI2C(freq=freq)

        return _i2c

elif PLATFORM_BUILD == "Linux":

    _bus_cache = {}

    # noinspection PyUnusedLocal
    def create_unified_i2c(
        bus=None, freq=None, sda=None, scl=None, suppress_warnings=True
    ):
        """
        bus is an int or a str, all other args are for different platforms.
        """
        global _bus_cache
        if bus in _bus_cache:
            return _bus_cache[bus]
        else:
            i2c = PiicoI2C(bus=bus, suppress_warnings=suppress_warnings)
            _bus_cache[bus] = i2c
            return i2c

elif PLATFORM_BUILD == "micropython":

    _bus_cache = {}

    # noinspection PyUnusedLocal
    def create_unified_i2c(
        bus=None, freq=None, sda=None, scl=None, suppress_warnings=True
    ):
        global _bus_cache
        bus_key = f"{bus}{freq}{sda}{scl}"
        if bus_key in _bus_cache:
            return _bus_cache[bus_key]
        else:
            i2c = PiicoI2C(bus=bus, freq=freq, sda=sda, scl=scl)
            _bus_cache[bus_key] = i2c
            return i2c

else:
    raise NotImplementedError("Again, should not get here.")
