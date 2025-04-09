_B='Overloaded on Init'
_A=None
import os
_SYSNAME=os.uname().sysname
PLATFORM_BUILD=_SYSNAME if _SYSNAME in('microbit','Linux')else'micropython'
compat_ind=1
i2c_err_str='PiicoDev could not communicate with module at address 0x{:02X}, check wiring'
compat_str='\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'
_i2c_freq=400000
def set_i2c_freq(freq=400000):
	global _i2c_freq
	if freq<400000:print('\x1b[91mWarning: minimum freq 400kHz is recommended if using OLED module.\x1b[0m')
	_i2c_freq=freq
from machine import I2C,Pin
from utime import sleep_ms
from asyncio import sleep_ms as a_sleep_ms
class PiicoI2C:
	def __init__(A,bus=_A,freq=_A,sda=_A,scl=_A):
		E=scl;D=sda;C=bus;B=freq
		if _SYSNAME=='esp32'and(C is _A or D is _A or E is _A):raise Exception('Please input bus, machine.pin SDA, and SCL objects to use ESP32')
		if B is _A:B=_i2c_freq
		if not isinstance(B,int):raise ValueError('freq must be an Int')
		if C is not _A and D is not _A and E is not _A:print('Using supplied bus, sda, and scl to create machine.I2C() with freq: {} Hz'.format(B));A.i2c=I2C(C,freq=B,sda=D,scl=E)
		elif C is _A and D is _A and E is _A:A.i2c=I2C(0,scl=Pin(9),sda=Pin(8),freq=B)
		else:raise Exception('Please provide at least bus, sda, and scl')
		A.writeto_mem=A.i2c.writeto_mem;A.readfrom_mem=A.i2c.readfrom_mem
	def writeto_mem(A,addr,memaddr,buf,*,addrsize=8):raise NotImplementedError(_B)
	def readfrom_mem(A,addr,memaddr,nbytes,*,addrsize=8):raise NotImplementedError(_B)
	def write8(A,addr,reg,data):
		if reg is _A:A.i2c.writeto(addr,data)
		else:A.i2c.writeto(addr,reg+data)
	def read16(A,addr,reg):A.i2c.writeto(addr,reg,False);return A.i2c.readfrom(addr,2)
	def scan(A):print([hex(A)for A in A.i2c.scan()])
_bus_cache={}
def create_unified_i2c(bus=_A,freq=_A,sda=_A,scl=_A,suppress_warnings=True):
	global _bus_cache;A=f"{bus}{sda}{scl}"
	if A in _bus_cache:return _bus_cache[A]
	else:B=PiicoI2C(bus=bus,freq=freq,sda=sda,scl=scl);_bus_cache[A]=B;return B