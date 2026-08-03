@echo off
setlocal

set APPNAME=FancyFit
set ENTRY=main.py
set ENVNAME=fancyfit

call conda activate %ENVNAME%
if errorlevel 1 (
    echo Could not activate %ENVNAME%
    pause
    exit /b 1
)

rmdir /s /q build dist 2>nul

pyinstaller ^
  --name %APPNAME% ^
  --windowed ^
  --clean ^
  --noconfirm ^
  --distpath WindowsApp ^
  --workpath build ^
  --specpath build ^
  --icon="%~dp0icon.ico" ^
  --hidden-import scipy._external.array_api_compat.numpy.fft main.py ^
  %ENTRY%

if errorlevel 1 (
    echo BUILD FAILED
    pause
    exit /b 1
)

endlocal