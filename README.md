# FancyFit

A GUI FitProgram that allows to build custom functions and fit a 2D dataset with multiple components.



Version 0.2.0-beta

This is a beta version and still needs a lot of work. Not all functions are (fully) functional.



Data import is limited to three separate files for x,y and Z so far.

You can build your own function by using plain text in the "FunctionBuilder". Sympy is used to convert the text into python code.



It requires my fittools package which is not publicly available. I'm working on a demo version that is independent of personal modules.

The bundled .exe should work regardless.



Bundle as windows .exe:

pyinstaller --windowed --icon=icon.ico --distpath WindowsApp --workpath build  --name FancyFit main.py

