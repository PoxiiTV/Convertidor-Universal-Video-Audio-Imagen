@echo off
cd /d "%~dp0"
echo [1/3] Compilando backend Python...
python build_backend.py
if errorlevel 1 (
    echo Error al compilar el backend.
    pause
    exit /b 1
)
echo.
echo [2/3] Instalando dependencias de la UI (si hace falta)...
cd poxi-ui
if not exist node_modules call npm install
echo.
echo [3/3] Compilando Electron...
call npm run dist
cd ..
echo.
echo Generados en poxi-ui\release\
if exist "poxi-ui\release\Poxi Utilities - Video y Fotos 1.0.0.exe" (
    echo  - Portable: Poxi Utilities - Video y Fotos 1.0.0.exe
)
if exist "poxi-ui\release\Poxi Utilities - Video y Fotos Setup 1.0.0.exe" (
    echo  - Instalador: Poxi Utilities - Video y Fotos Setup 1.0.0.exe
)
pause
