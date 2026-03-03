"""
Núcleo de conversión (sin GUI). Usado por converter.py y converter_backend.py.
"""

import subprocess
import sys
import threading
import re
from pathlib import Path

from PIL import Image
import numpy as np

SUBPROCESS_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0

VIDEO_FORMATS = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"]
AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"]
IMAGE_FORMATS = [".dng", ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"]
ALL_MEDIA_FORMATS = VIDEO_FORMATS + AUDIO_FORMATS
ALL_FORMATS = ALL_MEDIA_FORMATS + IMAGE_FORMATS

FORMAT_LABELS = {
    ".mp4": "MP4", ".mov": "MOV", ".avi": "AVI", ".mkv": "MKV", ".webm": "WebM", ".m4v": "M4V",
    ".mp3": "MP3", ".wav": "WAV", ".m4a": "M4A", ".aac": "AAC", ".ogg": "OGG", ".flac": "FLAC",
    ".dng": "DNG", ".jpg": "JPG", ".jpeg": "JPEG", ".png": "PNG", ".bmp": "BMP",
    ".gif": "GIF", ".tiff": "TIFF", ".tif": "TIFF", ".webp": "WebP",
}
LABEL_TO_EXT = {v: k for k, v in FORMAT_LABELS.items()}
LABEL_TO_EXT["TIFF"] = ".tiff"


def get_ext(path: str) -> str:
    return Path(path).suffix.lower()


def is_video(path: str) -> bool:
    return get_ext(path) in VIDEO_FORMATS


def is_audio(path: str) -> bool:
    return get_ext(path) in AUDIO_FORMATS


def is_image(path: str) -> bool:
    return get_ext(path) in IMAGE_FORMATS


def detect_category(ext: str) -> str:
    if ext in VIDEO_FORMATS:
        return "video"
    if ext in AUDIO_FORMATS:
        return "audio"
    if ext in IMAGE_FORMATS:
        return "image"
    return ""


def get_target_formats(source_ext: str) -> list[str]:
    cat = detect_category(source_ext)
    if cat == "video":
        video = [f for f in VIDEO_FORMATS if f != source_ext]
        return video + AUDIO_FORMATS
    if cat == "audio":
        return [f for f in AUDIO_FORMATS if f != source_ext]
    if cat == "image":
        out = [f for f in IMAGE_FORMATS if f != source_ext]
        if ".tiff" in out and ".tif" in out:
            out = [e for e in out if e != ".tif"]
        return out
    return []


def find_ffmpeg() -> str | None:
    for cmd in ("ffmpeg", "ffmpeg.exe"):
        try:
            subprocess.run(
                [cmd, "-version"],
                capture_output=True,
                check=True,
                creationflags=SUBPROCESS_FLAGS,
            )
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return None


def convert_file(
    input_path: str,
    output_path: str,
    on_progress=None,
    on_done=None,
    on_error=None,
    *,
    audio_sample_rate: int | None = None,
    audio_bitrate_k: int | None = None,
    audio_bit_depth: int | None = None,
) -> None:
    def run():
        try:
            ffmpeg = find_ffmpeg()
            if not ffmpeg:
                if on_error:
                    on_error("FFmpeg no encontrado. Instálalo desde ffmpeg.org")
                return
            inp_ext = get_ext(input_path)
            out_ext = get_ext(output_path)
            inp_cat = detect_category(inp_ext)
            out_cat = detect_category(out_ext)
            cmd = [ffmpeg, "-y", "-i", input_path]
            if inp_cat == "video" and out_cat == "audio":
                cmd.extend(["-vn"])
            if out_cat == "audio":
                if audio_sample_rate is not None:
                    cmd.extend(["-ar", str(audio_sample_rate)])
                if audio_bitrate_k is not None:
                    cmd.extend(["-b:a", f"{audio_bitrate_k}k"])
                if audio_bit_depth is not None and out_ext == ".wav":
                    if audio_bit_depth == 16:
                        cmd.extend(["-acodec", "pcm_s16le"])
                    elif audio_bit_depth == 24:
                        cmd.extend(["-acodec", "pcm_s24le"])
                    elif audio_bit_depth == 32:
                        cmd.extend(["-acodec", "pcm_f32le"])
            cmd.extend(["-progress", "pipe:1", output_path])
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=SUBPROCESS_FLAGS,
            )
            duration = None
            for line in proc.stdout:
                line = line.strip()
                if line.startswith("Duration:"):
                    m = re.search(r"Duration: (\d+):(\d+):(\d+)", line)
                    if m:
                        duration = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                if line.startswith("out_time_ms=") and duration and on_progress:
                    val = line.split("=")[1].strip()
                    if val and val != "N/A":
                        try:
                            t = int(val) / 1_000_000
                            on_progress(min(99, int(100 * t / duration)))
                        except (ValueError, ZeroDivisionError):
                            pass
            proc.wait()
            if proc.returncode == 0:
                if on_progress:
                    on_progress(100)
                if on_done:
                    on_done(output_path)
            else:
                if on_error:
                    on_error("Error en la conversión")
        except Exception as e:
            if on_error:
                on_error(str(e))
    threading.Thread(target=run, daemon=True).start()


def _load_image_to_rgb(input_path: str):
    ext = get_ext(input_path)
    if ext == ".dng":
        try:
            import rawpy
        except ImportError:
            raise RuntimeError("Para convertir DNG instala: pip install rawpy")
        with rawpy.imread(input_path) as raw:
            rgb = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB)
        return rgb
    img = Image.open(input_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return np.array(img)


def _save_image_from_rgb(rgb: np.ndarray, output_path: str, quality: int | None = None) -> None:
    ext = get_ext(output_path)
    pil = Image.fromarray(rgb.astype(np.uint8))
    fmt_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".bmp": "BMP", ".gif": "GIF", ".tiff": "TIFF", ".tif": "TIFF", ".webp": "WEBP"}
    fmt = fmt_map.get(ext, "PNG")
    save_kw = {}
    if fmt in ("JPEG", "WEBP"):
        save_kw["quality"] = quality if quality is not None else 95
    pil.save(output_path, format=fmt, **save_kw)


def convert_image(input_path: str, output_path: str, on_progress=None, on_done=None, on_error=None) -> None:
    def run():
        try:
            if on_progress:
                on_progress(10)
            rgb = _load_image_to_rgb(input_path)
            if on_progress:
                on_progress(70)
            _save_image_from_rgb(rgb, output_path)
            if on_progress:
                on_progress(100)
            if on_done:
                on_done(output_path)
        except Exception as e:
            if on_error:
                on_error(str(e))
    threading.Thread(target=run, daemon=True).start()


def compress_video(input_path: str, output_path: str, crf: int = 28, on_progress=None, on_done=None, on_error=None) -> None:
    def run():
        try:
            ffmpeg = find_ffmpeg()
            if not ffmpeg:
                if on_error:
                    on_error("FFmpeg no encontrado. Instálalo desde ffmpeg.org")
                return
            cmd = [
                ffmpeg, "-y", "-i", input_path,
                "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                "-progress", "pipe:1", output_path,
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, creationflags=SUBPROCESS_FLAGS)
            duration = None
            for line in proc.stdout:
                line = line.strip()
                if line.startswith("Duration:"):
                    m = re.search(r"Duration: (\d+):(\d+):(\d+)", line)
                    if m:
                        duration = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                if line.startswith("out_time_ms=") and duration and on_progress:
                    val = line.split("=")[1].strip()
                    if val and val != "N/A":
                        try:
                            t = int(val) / 1_000_000
                            on_progress(min(99, int(100 * t / duration)))
                        except (ValueError, ZeroDivisionError):
                            pass
            proc.wait()
            if proc.returncode == 0:
                if on_progress:
                    on_progress(100)
                if on_done:
                    on_done(output_path)
            else:
                if on_error:
                    on_error("Error al comprimir")
        except Exception as e:
            if on_error:
                on_error(str(e))
    threading.Thread(target=run, daemon=True).start()


def compress_audio(input_path: str, output_path: str, bitrate_k: int = 128, on_progress=None, on_done=None, on_error=None) -> None:
    def run():
        try:
            ffmpeg = find_ffmpeg()
            if not ffmpeg:
                if on_error:
                    on_error("FFmpeg no encontrado.")
                return
            cmd = [ffmpeg, "-y", "-i", input_path, "-b:a", f"{bitrate_k}k", "-progress", "pipe:1", output_path]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, creationflags=SUBPROCESS_FLAGS)
            for _ in proc.stdout:
                pass
            proc.wait()
            if proc.returncode == 0:
                if on_progress:
                    on_progress(100)
                if on_done:
                    on_done(output_path)
            else:
                if on_error:
                    on_error("Error al comprimir")
        except Exception as e:
            if on_error:
                on_error(str(e))
    threading.Thread(target=run, daemon=True).start()


def compress_image(input_path: str, output_path: str, quality: int = 80, on_progress=None, on_done=None, on_error=None) -> None:
    def run():
        try:
            if on_progress:
                on_progress(20)
            rgb = _load_image_to_rgb(input_path)
            if on_progress:
                on_progress(70)
            ext = get_ext(output_path)
            pil = Image.fromarray(rgb.astype(np.uint8))
            fmt_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP", ".tiff": "TIFF", ".tif": "TIFF"}
            fmt = fmt_map.get(ext, "JPEG")
            save_kw = {}
            if fmt in ("JPEG", "WEBP"):
                save_kw["quality"] = quality
            elif fmt == "PNG":
                save_kw["optimize"] = True
            pil.save(output_path, format=fmt, **save_kw)
            if on_progress:
                on_progress(100)
            if on_done:
                on_done(output_path)
        except Exception as e:
            if on_error:
                on_error(str(e))
    threading.Thread(target=run, daemon=True).start()


def resize_image(
    input_path: str,
    output_path: str,
    width: int | None = None,
    height: int | None = None,
    scale_percent: int | None = None,
    keep_aspect: bool = True,
    on_progress=None,
    on_done=None,
    on_error=None,
) -> None:
    def run():
        try:
            if on_progress:
                on_progress(15)
            rgb = _load_image_to_rgb(input_path)
            img = Image.fromarray(rgb)
            w, h = img.size
            if scale_percent is not None and scale_percent > 0:
                nw, nh = max(1, w * scale_percent // 100), max(1, h * scale_percent // 100)
            elif width is not None or height is not None:
                if keep_aspect:
                    if width is not None and height is not None:
                        r = min(width / w, height / h)
                        nw, nh = max(1, int(w * r)), max(1, int(h * r))
                    elif width is not None:
                        r = width / w
                        nw, nh = width, max(1, int(h * r))
                    else:
                        r = height / h
                        nw, nh = max(1, int(w * r)), height
                else:
                    nw = width if width is not None else w
                    nh = height if height is not None else h
            else:
                if on_error:
                    on_error("Indica ancho, alto o porcentaje")
                return
            resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
            if on_progress:
                on_progress(80)
            ext = get_ext(output_path)
            fmt_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP", ".bmp": "BMP", ".tiff": "TIFF", ".tif": "TIFF"}
            fmt = fmt_map.get(ext, "PNG")
            save_kw = {"quality": 90} if fmt in ("JPEG", "WEBP") else {}
            resized.save(output_path, format=fmt, **save_kw)
            if on_progress:
                on_progress(100)
            if on_done:
                on_done(output_path)
        except Exception as e:
            if on_error:
                on_error(str(e))
    threading.Thread(target=run, daemon=True).start()
