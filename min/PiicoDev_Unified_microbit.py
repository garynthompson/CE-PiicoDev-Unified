_A=None
import os
_SYSNAME=os.uname().sysname
_PLATFORM_BUILD=_SYSNAME if _SYSNAME in('microbit','Linux')else'micropython'
compat_ind=1
i2c_err_str='PiicoDev could not communicate with module at address 0x{:02X}, check wiring'
from microbit import i2c
from utime import sleep_ms
from asyncio import sleep_ms as a_sleep_ms
class PiicoI2C:
	def __init__(B,freq=_A):
		A=freq
		if A is not _A:print('Initialising I2C freq to {}'.format(A));microbit.i2c.init(freq=A)
	def writeto_mem(B,addr,memaddr,buf,*,addrsize=8):A=memaddr.to_bytes(addrsize//8,'big');i2c.write(addr,A+buf)
	def readfrom_mem(B,addr,memaddr,nbytes,*,addrsize=8):A=memaddr.to_bytes(addrsize//8,'big');i2c.write(addr,A,repeat=True);return i2c.read(addr,nbytes)
	def write8(A,addr,reg,data):
		if reg is _A:i2c.write(addr,data)
		else:i2c.write(addr,reg+data)
	def read16(A,addr,reg):i2c.write(addr,reg,repeat=True);return i2c.read(addr,2)
	def scan(A):print([hex(A)for A in A.i2c.scan()])
_i2c=_A
def create_unified_i2c(bus=_A,freq=_A,sda=_A,scl=_A,suppress_warnings=True):
	global _i2c
	if not _i2c:_i2c=PiicoI2C(freq=freq)
	return _i2c