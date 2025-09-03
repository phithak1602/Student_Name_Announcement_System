@echo off
title Installing Python Libraries
echo ==========================================
echo  Installing Required Python Libraries
echo ==========================================
echo.

echo Installing libraries...
echo.

pip install paho-mqtt mysql-connector-python ultralytics opencv-python Pillow numpy PyQt5 gTTS pydub pygame

echo.
echo ==========================================
if %errorlevel% equ 0 (
    echo Installation completed successfully!
    echo All libraries have been installed.
) else (
    echo Installation failed!
    echo Please check your Python and pip installation.
)
echo ==========================================
echo.
echo Press any key to exit...
pause >nul