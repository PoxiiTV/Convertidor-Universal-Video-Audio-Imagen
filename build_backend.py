"""
Compila solo el backend headless (converter_backend.exe) para usarlo con Electron.
Salida: dist/converter_backend.exe. Copia a poxi-ui/backend/ si existe.
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # headless, pero sin --windowed para ver errores si falla
        "--name", "converter_backend",
        "--clean", "--noconfirm",
        "--distpath", str(root / "dist"),
        "--workpath", str(root / "build"),
        "--specpath", str(root),
        "--hidden-import", "rawpy",
        "--hidden-import", "numpy",
        "--collect-all", "rawpy",
        str(root / "converter_backend.py"),
    ]
    subprocess.run(cmd, check=True)
    backend_exe = root / "dist" / "converter_backend.exe"
    poxi_backend = root / "poxi-ui" / "backend"
    if backend_exe.is_file():
        poxi_backend.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(backend_exe, poxi_backend / "converter_backend.exe")
        print("Copiado a poxi-ui/backend/")
    print("Backend EXE:", backend_exe)

if __name__ == "__main__":
    main()
