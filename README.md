# Core Electronics Unified PiicoDev Library
*Unifies the I2C drivers for different implementations of MicroPython*

For information on how to use this library, refer to the [methods documentation](https://github.com/CoreElectronics/CE-PiicoDev-Unified/blob/main/doc/METHODS.md).

For information on how to contribute, refer to the [contribution guidelines](https://github.com/CoreElectronics/CE-PiicoDev-Unified/blob/main/doc/CONTRIBUTING.md).

# Gary's Mod

Gary's branch is a fork of the Core-Electronics PiicoDev libraries
set up to suit my own projects.  

While forking projects and deviating from project intents is suboptimal, 
in this case it might be easier as my needs do not seem to 
reflect those of the community.  Instead, I am creating a sub-ecosystem
of the PiicoDev devices I have used in my own projects.

My primary focus and testing is the RPI Pico and Full RPI hardware.  I 
also want to experiment with other options that might minimise code for
those on more constrained systems, but I am not testing these.

Changes:

* Asyncio support:  While not needed for an I2C bus as it should be very
  fast, it is needed for ethernet protocols.  The problem is that
  if asyncio is used, all sleep statements need to be asyncio.sleep and
  not thread/time sleep statements.  This impacts some of the PiicoDev
  code.  As there are fairly fundamental changes, separate async versions
  of modules will be provided where needed.

* MIP is best used with a single module as there is not a proper packaging
  mechanism (although one does exist in my own raik_integrations project).
  However, it can be assumed that if MIP is being used then it will be on 
  a micropython device and not a linux one.  As such, all linux functionality
  can be split out into a package that can be imported using uv / pip / poetry / etc...
  Minified versions will be the micropython versions only.

* Black is used for formatting