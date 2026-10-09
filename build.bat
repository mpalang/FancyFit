@echo off

call conda activate fancyfit

rmdir /s /q build dist 2>nul

pyinstaller ^
  --name FancyFit ^
  --windowed ^
  --clean ^
  --noconfirm ^
  --distpath "%~dp0..\FancyFit_Release" ^
  --workpath build ^
  --specpath build ^
  --icon="%~dp0icon.ico" ^
  --hidden-import scipy._external.array_api_compat.numpy.fft main.py

if errorlevel 1 (
    echo BUILD FAILED
    pause
    exit /b 1
)
