"""
Linux specific additions

    - 2025-04-05 G.Thompson - start async support, split module for different use cases
"""

from smbus2 import SMBus, i2c_msg
from time import sleep
from asyncio import sleep as a_sleep_s


def sleep_ms(t):
    sleep(t / 1000)


async def a_sleep_ms(t: int):
    await a_sleep_s(t / 1000)


compat_ind = 1
i2c_err_str = (
    "PiicoDev could not communicate with module at address 0x{:02X}, check wiring"
)
setup_i2c_str = ', run "sudo curl -L https://piico.dev/i2csetup | bash". Suppress this warning by setting suppress_warnings=True'


class PiicoI2C:
    # noinspection SpellCheckingInspection
    def __init__(self, bus=None, suppress_warnings=True):
        if not suppress_warnings:
            with open("/boot/config.txt") as config_file:
                if "dtparam=i2c_arm=on" in config_file.read():
                    pass
                else:
                    print("I2C is not enabled. To enable" + setup_i2c_str)
                config_file.close()
            with open("/boot/config.txt") as config_file:
                if "dtparam=i2c_arm_baudrate=400000" in config_file.read():
                    pass
                else:
                    print("Slow baudrate detected. If glitching occurs" + setup_i2c_str)
                config_file.close()
        if bus is None:
            bus = 1
        self.i2c = SMBus(bus)

    # noinspection SpellCheckingInspection
    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
        data = [None] * nbytes  # initialise empty list
        self.smbus_i2c_read(addr, memaddr, data, nbytes, addrsize=addrsize)
        return data

    # noinspection SpellCheckingInspection
    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8):
        self.smbus_i2c_write(addr, memaddr, buf, len(buf), addrsize=addrsize)

    # noinspection SpellCheckingInspection
    def smbus_i2c_write(self, address, reg, data_p, length, addrsize=8):
        ret_val = 0
        data = []
        for index in range(length):
            data.append(data_p[index])
        if addrsize == 8:
            msg_w = i2c_msg.write(address, [reg] + data)
        elif addrsize == 16:
            msg_w = i2c_msg.write(address, [reg >> 8, reg & 0xFF] + data)
        else:
            raise Exception("address must be 8 or 16 bits long only")
        self.i2c.i2c_rdwr(msg_w)
        return ret_val

    # noinspection SpellCheckingInspection
    def smbus_i2c_read(self, address, reg, data_p, length, addrsize=8):
        ret_val = 0
        if addrsize == 8:
            msg_w = i2c_msg.write(
                address, [reg]
            )  # warning this is set up for 16-bit addresses
        elif addrsize == 16:
            msg_w = i2c_msg.write(
                address, [reg >> 8, reg & 0xFF]
            )  # warning this is set up for 16-bit addresses
        else:
            raise Exception("address must be 8 or 16 bits long only")
        msg_r = i2c_msg.read(address, length)
        self.i2c.i2c_rdwr(msg_w, msg_r)
        if ret_val == 0:
            for index in range(length):
                data_p[index] = ord(msg_r.buf[index])
        return ret_val

    def write8(self, addr, reg, data):
        if reg is None:
            d = int.from_bytes(data, "big")
            self.i2c.write_byte(addr, d)
        else:
            r = int.from_bytes(reg, "big")
            d = int.from_bytes(data, "big")
            self.i2c.write_byte_data(addr, r, d)

    def read16(self, addr, reg):
        reg_int = int.from_bytes(reg, "big")
        return self.i2c.read_word_data(addr, reg_int).to_bytes(
            2, byteorder="little", signed=False
        )

    def scan(self):
        raise NotImplementedError(
            "See original branch, according to the IDE i2c.scan does not exist."
        )
