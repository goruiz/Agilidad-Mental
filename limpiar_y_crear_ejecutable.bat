@echo off
echo ========================================
echo Limpiando archivos antiguos...
echo ========================================

REM Eliminar carpetas de compilaciones anteriores
if exist "build" (
    echo Eliminando carpeta build...
    rmdir /s /q "build"
)

if exist "dist" (
    echo Eliminando carpeta dist...
    rmdir /s /q "dist"
)

if exist "*.spec" (
    echo Eliminando archivos .spec antiguos...
    del /q "*.spec"
)

if exist "__pycache__" (
    echo Eliminando __pycache__...
    rmdir /s /q "__pycache__"
)

echo.
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
