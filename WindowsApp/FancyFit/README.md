# FancyFit

**A GUI FitProgram that allows to build custom functions and fit a 2D dataset with multiple components.**

contact: moritzpalang@gmail.com

*Version 0.3.0-beta*

This is a beta version and still needs some work. Not all functions are (fully) functional.


Takes x,y and Z data from three different csv files (are read with np.genfromtxt). Z is two dimensional and needs to match x and y dimensions. Z is automatically transposed if axis are flipped.

User settings are saved in a user folder (most likely: user\AppData\Local\SmoereApps\FancyFit)
This should contain settings.json, functions.json and a log folder.
- settings.json contains user settings and can be edited here. These will be loaded on startup.
- functions.json contains user functions.
- log contains error and app logs. If an error occurs you can copy the last entry in error.log and send it to me.

Common parameters specifies which parameters are treated as the same for all functions. The p0 and bound settings of the first function are used. The parameter names do matter! If you want them to be independent they can't be in the common parameters field or need a different name.

Functions can be (numerically) convoluted with any function if 'use irf' is selected in settings. A separate IRF tab will appear in the functions panel.

You can build your own function by using plain text in the "FunctionBuilder". Sympy is used to convert the text into python code. Please test the function with it's bounds before saving.
I added some custom functions for convenience:
<!-- ed: exponential decay -->
<!-- so: second order decay (geminate) -->
edcg: exponential decay convolved with gauss
