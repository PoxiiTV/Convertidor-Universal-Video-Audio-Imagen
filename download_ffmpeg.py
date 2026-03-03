"""
Descarga FFmpeg (essentials) para Windows y lo coloca en poxi-ui/ffmpeg/.
Así la app funciona sin que el usuario instale FFmpeg.
Ejecutar antes de build_electron.bat
"""
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

FFMPEG_URL = "https://github.com/GyanD/codexffmpeg/releases/download/2026-03-01-git-862338fe31/ffmpeg-2026-03-01-git-862338fe31-essentials_build.zip"
# Alternativa: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

def main():
    root = Path(__file__).resolve().parent
    out_dir = root / "poxi-ui" / "ffmpeg"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = root / "ffmpeg-temp.zip"

    print("Descargando FFmpeg essentials...")
    try:
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
    except Exception as e:
        print(f"Error descargando: {e}")
        print("Prueba manual: https://www.gyan.dev/ffmpeg/builds/")
        print("Extrae ffmpeg.exe a poxi-ui/ffmpeg/")
        return 1

    print("Extrayendo...")
    with zipfile.ZipFile(zip_path, "r") as z:
        for name in z.namelist():
            if name.endswith("/ffmpeg.exe") or name.endswith("\\ffmpeg.exe"):
                with z.open(name) as src:
                    dest = out_dir / "ffmpeg.exe"
                    with open(dest, "wb") as f:
                        f.write(src.read())
                break
    zip_path.unlink(missing_ok=True)
    print(f"Listo: {out_dir / 'ffmpeg.exe'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
