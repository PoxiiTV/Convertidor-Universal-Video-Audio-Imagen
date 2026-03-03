"""
Script para compilar Convertidor en un EXE portable (un solo archivo).
Ejecutar: python build_exe.py
Salida: dist/Convertidor.exe
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    icon_path = root / "Poxi V4 SUPER PERFECT redondo.ico"
    # En Windows PyInstaller usa ";" para separar ruta y destino en --add-data
    add_data_sep = ";" if os.name == "nt" else ":"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Poxi Utilities - Videos, Fotos y Audio",
        "--clean",
        "--noconfirm",
        "--distpath", str(root / "dist"),
        "--workpath", str(root / "build"),
        "--specpath", str(root),
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "rawpy",
        "--hidden-import", "numpy",
        "--collect-all", "customtkinter",
        "--collect-all", "rawpy",
    ]
    if icon_path.is_file():
        cmd.extend(["--icon", str(icon_path)])
        # Incluir el .ico dentro del EXE para que la ventana lo use (barra de tareas, título)
        cmd.extend(["--add-data", str(icon_path) + add_data_sep + "."])
    cmd.append(str(root / "converter.py"))
    subprocess.run(cmd, check=True)
    print("\nListo. EXE generado en: dist/Poxi Utilities - Videos, Fotos y Audio.exe")

if __name__ == "__main__":
    main()
