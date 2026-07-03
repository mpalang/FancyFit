# FancyFit

A GUI FitProgram that allows to build custom functions and fit a 2D dataset with multiple components.



Version 0.1.0-beta

This is a beta version and still needs a lot of work. Not all functions are (fully) functional.

So far it needs my fittools package which is not publicly available. I'm working on a demo version that is independent of personal modules.

The bundled .exe should work regardless.



Bundle as windows .exe:

pyinstaller --windowed --icon=icon.ico --distpath WindowsApp --workpath build  --name FancyFit main.py --collect-all scipy



Find out why scipy doesn't import everything necessary on its own now! (Didn't have that issue before)

