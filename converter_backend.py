"""
Backend headless: lee comandos JSON por stdin y escribe progreso/resultado por stdout.
Usado por la app Electron. Ejecutar: python converter_backend.py
"""

import json
import sys
import threading
from pathlib import Path

# Importar solo el núcleo (sin GUI)
from converter_core import (
    get_ext,
    get_target_formats,
    detect_category,
    FORMAT_LABELS,
    LABEL_TO_EXT,
    convert_file,
    convert_image,
    compress_video,
    compress_audio,
    compress_image,
    resize_image,
)


def send(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False), flush=True)


def run_command(cmd: dict) -> None:
    action = cmd.get("action")
    if not action:
        send({"type": "error", "message": "Falta 'action'"})
        return
    done_ev = threading.Event()
    result_holder = {"output": None, "error": None}

    def on_done(out: str):
        result_holder["output"] = out
        done_ev.set()

    def on_error(msg: str):
        result_holder["error"] = msg
        done_ev.set()

    def on_progress(pct: int):
        send({"type": "progress", "percent": pct})

    if action == "convert_media":
        inp = cmd.get("input_path")
        out = cmd.get("output_path")
        if not inp or not out:
            send({"type": "error", "message": "Faltan input_path u output_path"})
            return
        convert_file(
            inp, out,
            on_progress=on_progress, on_done=on_done, on_error=on_error,
            audio_sample_rate=cmd.get("audio_sample_rate"),
            audio_bitrate_k=cmd.get("audio_bitrate_k"),
            audio_bit_depth=cmd.get("audio_bit_depth"),
        )
    elif action == "convert_image":
        inp = cmd.get("input_path")
        out = cmd.get("output_path")
        if not inp or not out:
            send({"type": "error", "message": "Faltan input_path u output_path"})
            return
        convert_image(inp, out, on_progress=on_progress, on_done=on_done, on_error=on_error)
    elif action == "compress_video":
        inp = cmd.get("input_path")
        out = cmd.get("output_path")
        crf = cmd.get("crf", 28)
        if not inp or not out:
            send({"type": "error", "message": "Faltan input_path u output_path"})
            return
        compress_video(inp, out, crf=crf, on_progress=on_progress, on_done=on_done, on_error=on_error)
    elif action == "compress_audio":
        inp = cmd.get("input_path")
        out = cmd.get("output_path")
        bitrate = cmd.get("bitrate_k", 128)
        if not inp or not out:
            send({"type": "error", "message": "Faltan input_path u output_path"})
            return
        compress_audio(inp, out, bitrate_k=bitrate, on_progress=on_progress, on_done=on_done, on_error=on_error)
    elif action == "compress_image":
        inp = cmd.get("input_path")
        out = cmd.get("output_path")
        quality = cmd.get("quality", 80)
        if not inp or not out:
            send({"type": "error", "message": "Faltan input_path u output_path"})
            return
        compress_image(inp, out, quality=quality, on_progress=on_progress, on_done=on_done, on_error=on_error)
    elif action == "resize_image":
        inp = cmd.get("input_path")
        out = cmd.get("output_path")
        if not inp or not out:
            send({"type": "error", "message": "Faltan input_path u output_path"})
            return
        resize_image(
            inp, out,
            width=cmd.get("width"),
            height=cmd.get("height"),
            scale_percent=cmd.get("scale_percent"),
            keep_aspect=cmd.get("keep_aspect", True),
            on_progress=on_progress, on_done=on_done, on_error=on_error,
        )
    elif action == "get_target_formats":
        ext = cmd.get("source_ext", "")
        targets = get_target_formats(ext)
        labels = []
        seen = set()
        for t in targets:
            lb = FORMAT_LABELS.get(t, t.upper().lstrip("."))
            if lb not in seen:
                seen.add(lb)
                labels.append(lb)
        send({"type": "target_formats", "formats": labels})
        return
    else:
        send({"type": "error", "message": f"Acción desconocida: {action}"})
        return

    done_ev.wait()
    if result_holder["error"]:
        send({"type": "error", "message": result_holder["error"]})
    else:
        send({"type": "done", "output_path": result_holder["output"]})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            cmd = json.loads(line)
            run_command(cmd)
        except json.JSONDecodeError as e:
            send({"type": "error", "message": str(e)})
        except Exception as e:
            send({"type": "error", "message": str(e)})


if __name__ == "__main__":
    main()
