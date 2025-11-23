@echo off
echo ========================================
echo Creando ejecutable de Agilidad RMmath
echo ========================================
echo.

echo Paso 1: Instalando PyInstaller...
pip install pyinstaller

echo.
echo Paso 2: Creando ejecutable...
pyinstaller --onefile --windowed --icon=logo.ico --add-data "logo.ico;." --add-data "logo.jpg;." --name "Agilidad RMmath" agilidad_mental.py

echo.
echo ========================================
echo Proceso completado!
echo El ejecutable esta en: dist\Agilidad RMmath.exe
echo ========================================
pause
