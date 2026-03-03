@echo off
cd /d "%~dp0"
echo Instalando dependencias...
pip install -r requirements.txt -q
echo.
echo Compilando EXE...
python build_exe.py
echo.
if exist "dist\Poxi Utilities - Videos, Fotos y Audio.exe" (
    echo Listo: dist\Poxi Utilities - Videos, Fotos y Audio.exe
) else (
    echo Error: no se genero el EXE.
)
pause
