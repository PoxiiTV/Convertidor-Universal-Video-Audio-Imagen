"""
Convertidor de Audio, Vídeo e Imágenes - GUI con CustomTkinter
La lógica de conversión está en converter_core.py
"""

import sys
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from converter_core import (
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    IMAGE_FORMATS,
    ALL_FORMATS,
    FORMAT_LABELS,
    LABEL_TO_EXT,
    get_ext,
    detect_category,
    get_target_formats,
    convert_file,
    convert_image,
    compress_video,
    compress_audio,
    compress_image,
    resize_image,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ConvertidorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Poxi Utilities - Videos, Fotos y Audio")
        self.geometry("580x560")
        self.minsize(520, 500)

        self.colors = {
            "bg": "#0d0d0d",
            "fg": "#e0e0e0",
            "accent": "#3b82f6",
            "card": "#161616",
        }
        self.configure(fg_color=self.colors["bg"])

        self.files: list[str] = []
        self.output_dir: str = ""
        self.current_tab = "Vídeo"
        self.current_mode = "Convertir"

        self._build_ui()
        self._set_icon()

    def _set_icon(self):
        icon_name = "Poxi V4 SUPER PERFECT redondo.ico"
        if getattr(sys, "frozen", False):
            # Ejecutando como EXE: icono extraído por PyInstaller en _MEIPASS
            icon_path = Path(sys._MEIPASS) / icon_name
        else:
            icon_path = Path(__file__).resolve().parent / icon_name
        if icon_path.is_file():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

    def _build_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=16)

        # Título
        ctk.CTkLabel(
            main,
            text="Convertidor",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["fg"],
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            main,
            text="Vídeo · Audio · Imagen · Convertir · Comprimir · Redimensionar",
            font=ctk.CTkFont(size=12),
            text_color="#6b7280",
        ).pack(anchor="w", pady=(0, 12))

        # Archivos y carpeta (común)
        file_card = ctk.CTkFrame(
            main, fg_color=self.colors["card"], corner_radius=10,
            border_width=1, border_color="#2a2a2a",
        )
        file_card.pack(fill="x", pady=(0, 12))
        row = ctk.CTkFrame(file_card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=12)
        ctk.CTkButton(
            row, text="Seleccionar archivos", command=self._select_files,
            fg_color="#262626", hover_color="#333", text_color=self.colors["fg"],
            height=36, corner_radius=8,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            row, text="Carpeta de salida", command=self._select_output_dir,
            fg_color="#262626", hover_color="#333", text_color=self.colors["fg"],
            height=36, corner_radius=8,
        ).pack(side="left")
        self.file_label = ctk.CTkLabel(
            file_card, text="Ningún archivo seleccionado",
            font=ctk.CTkFont(size=13), text_color="#9ca3af", wraplength=480,
        )
        self.file_label.pack(fill="x", padx=16, pady=(0, 12))

        # Pestañas: Vídeo | Audio | Imagen
        self.tabview = ctk.CTkTabview(main, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("Vídeo")
        self.tabview.add("Audio")
        self.tabview.add("Imagen")
        self.tabview.set("Vídeo")

        # Contenido por pestaña
        self._build_video_tab()
        self._build_audio_tab()
        self._build_image_tab()

        # Barra progreso y estado (común)
        self.progress = ctk.CTkProgressBar(
            main, fg_color="#262626", progress_color=self.colors["accent"]
        )
        self.progress.pack(fill="x", pady=(8, 0))
        self.status_label = ctk.CTkLabel(
            main, text="", font=ctk.CTkFont(size=12), text_color="#6b7280",
        )
        self.status_label.pack(pady=(4, 0))

        self.action_btn = None  # se asigna en cada _build_*_tab

    def _build_video_tab(self):
        tab = self.tabview.tab("Vídeo")
        self.video_mode = ctk.StringVar(value="Convertir")
        seg = ctk.CTkSegmentedButton(
            tab, values=["Convertir", "Comprimir"], variable=self.video_mode,
            command=self._on_video_mode,
            fg_color="#262626", selected_color=self.colors["accent"],
            selected_hover_color="#2563eb", unselected_hover_color="#333",
        )
        seg.pack(fill="x", pady=(0, 12))
        self.video_options = ctk.CTkFrame(tab, fg_color="transparent")
        self.video_options.pack(fill="both", expand=True)
        self._fill_video_convert_options()
        self._fill_video_compress_options()
        self._on_video_mode("Convertir")

    def _on_video_mode(self, value):
        self.current_tab = "Vídeo"
        self.current_mode = value
        for w in self.video_options.winfo_children():
            w.pack_forget()
        if value == "Convertir":
            self.video_convert_frame.pack(fill="x", pady=(0, 12))
            self.video_action_btn.pack(anchor="e", pady=(8, 0))
        else:
            self.video_compress_frame.pack(fill="x", pady=(0, 12))
            self.video_compress_btn.pack(anchor="e", pady=(8, 0))

    def _fill_video_convert_options(self):
        self.video_convert_frame = ctk.CTkFrame(self.video_options, fg_color="transparent")
        row = ctk.CTkFrame(self.video_convert_frame, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Formato destino:", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 8))
        self.video_format_var = ctk.StringVar(value="MP4")
        self.video_format_menu = ctk.CTkOptionMenu(
            row, values=["MP4", "MOV", "AVI", "MKV", "WebM", "MP3", "WAV", "M4A"],
            variable=self.video_format_var, width=100,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        )
        self.video_format_menu.pack(side="left")
        self.video_action_btn = ctk.CTkButton(
            self.video_options,
            text="Convertir",
            command=lambda: self._run_action("Vídeo", "Convertir"),
            fg_color=self.colors["accent"], hover_color="#2563eb", height=38, corner_radius=8, width=120,
        )

    def _fill_video_compress_options(self):
        self.video_compress_frame = ctk.CTkFrame(self.video_options, fg_color="transparent")
        row = ctk.CTkFrame(self.video_compress_frame, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Compresión (CRF):", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 8))
        self.video_crf_var = ctk.StringVar(value="28")
        crf_menu = ctk.CTkOptionMenu(
            row, values=["18 (alta calidad)", "23 (buena)", "28 (medio)", "33 (más compresión)"],
            variable=self.video_crf_var, width=180,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        )
        crf_menu.pack(side="left")
        ctk.CTkLabel(
            self.video_compress_frame,
            text="Mismo formato de salida. CRF mayor = archivo más pequeño.",
            font=ctk.CTkFont(size=11), text_color="#6b7280",
        ).pack(anchor="w", pady=(6, 0))
        self.video_compress_btn = ctk.CTkButton(
            self.video_options,
            text="Comprimir",
            command=lambda: self._run_action("Vídeo", "Comprimir"),
            fg_color=self.colors["accent"], hover_color="#2563eb", height=38, corner_radius=8, width=120,
        )

    def _build_audio_tab(self):
        tab = self.tabview.tab("Audio")
        self.audio_mode = ctk.StringVar(value="Convertir")
        seg = ctk.CTkSegmentedButton(
            tab, values=["Convertir", "Comprimir"], variable=self.audio_mode,
            command=self._on_audio_mode,
            fg_color="#262626", selected_color=self.colors["accent"],
            selected_hover_color="#2563eb", unselected_hover_color="#333",
        )
        seg.pack(fill="x", pady=(0, 12))
        self.audio_options = ctk.CTkFrame(tab, fg_color="transparent")
        self.audio_options.pack(fill="both", expand=True)
        self._fill_audio_convert_options()
        self._fill_audio_compress_options()
        self._on_audio_mode("Convertir")

    def _on_audio_mode(self, value):
        self.current_tab = "Audio"
        self.current_mode = value
        for w in self.audio_options.winfo_children():
            w.pack_forget()
        if value == "Convertir":
            self.audio_convert_frame.pack(fill="x", pady=(0, 12))
            self.audio_action_btn.pack(anchor="e", pady=(8, 0))
        else:
            self.audio_compress_frame.pack(fill="x", pady=(0, 12))
            self.audio_compress_btn.pack(anchor="e", pady=(8, 0))

    def _fill_audio_convert_options(self):
        self.audio_convert_frame = ctk.CTkFrame(self.audio_options, fg_color="transparent")
        row0 = ctk.CTkFrame(self.audio_convert_frame, fg_color="transparent")
        row0.pack(fill="x")
        ctk.CTkLabel(row0, text="Formato destino:", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 8))
        self.audio_format_var = ctk.StringVar(value="MP3")
        self.audio_format_menu = ctk.CTkOptionMenu(
            row0, values=["MP3", "WAV", "M4A", "AAC", "OGG", "FLAC"],
            variable=self.audio_format_var, width=100,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
            command=self._on_audio_format_change,
        )
        self.audio_format_menu.pack(side="left")
        row1 = ctk.CTkFrame(self.audio_convert_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(row1, text="Frecuencia (Hz):", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 8))
        self.audio_samplerate_var = ctk.StringVar(value="44100")
        self.audio_samplerate_menu = ctk.CTkOptionMenu(
            row1, values=["22050", "44100", "48000", "96000", "192000"],
            variable=self.audio_samplerate_var, width=100,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        )
        self.audio_samplerate_menu.pack(side="left", padx=(0, 16))
        self.audio_bitrate_label = ctk.CTkLabel(row1, text="Bitrate (kbps):", font=ctk.CTkFont(size=13), text_color="#9ca3af")
        self.audio_bitrate_label.pack(side="left", padx=(0, 8))
        self.audio_bitrate_convert_var = ctk.StringVar(value="320")
        self.audio_bitrate_convert_menu = ctk.CTkOptionMenu(
            row1, values=["128", "192", "256", "320"],
            variable=self.audio_bitrate_convert_var, width=80,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        )
        self.audio_bitrate_convert_menu.pack(side="left")
        self.audio_bits_label = ctk.CTkLabel(row1, text="Bits (WAV):", font=ctk.CTkFont(size=13), text_color="#9ca3af")
        self.audio_bits_var = ctk.StringVar(value="24")
        self.audio_bits_menu = ctk.CTkOptionMenu(
            row1, values=["16", "24", "32"],
            variable=self.audio_bits_var, width=60,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        )
        self._on_audio_format_change(self.audio_format_var.get())
        self.audio_action_btn = ctk.CTkButton(
            self.audio_options,
            text="Convertir",
            command=lambda: self._run_action("Audio", "Convertir"),
            fg_color=self.colors["accent"], hover_color="#2563eb", height=38, corner_radius=8, width=120,
        )

    def _on_audio_format_change(self, value: str):
        """Muestra Bitrate para MP3/M4A/etc y Bits para WAV según el formato elegido."""
        ext = LABEL_TO_EXT.get(value, ".mp3")
        if ext == ".wav":
            self.audio_bitrate_label.pack_forget()
            self.audio_bitrate_convert_menu.pack_forget()
            self.audio_bits_label.pack(side="left", padx=(0, 8))
            self.audio_bits_menu.pack(side="left")
        else:
            self.audio_bits_label.pack_forget()
            self.audio_bits_menu.pack_forget()
            self.audio_bitrate_label.pack(side="left", padx=(0, 8))
            self.audio_bitrate_convert_menu.pack(side="left")

    def _fill_audio_compress_options(self):
        self.audio_compress_frame = ctk.CTkFrame(self.audio_options, fg_color="transparent")
        row = ctk.CTkFrame(self.audio_compress_frame, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Bitrate:", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 8))
        self.audio_bitrate_var = ctk.StringVar(value="128")
        ctk.CTkOptionMenu(
            row, values=["96 kbps", "128 kbps", "192 kbps", "256 kbps"],
            variable=self.audio_bitrate_var, width=120,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        ).pack(side="left")
        self.audio_compress_btn = ctk.CTkButton(
            self.audio_options,
            text="Comprimir",
            command=lambda: self._run_action("Audio", "Comprimir"),
            fg_color=self.colors["accent"], hover_color="#2563eb", height=38, corner_radius=8, width=120,
        )

    def _build_image_tab(self):
        tab = self.tabview.tab("Imagen")
        self.image_mode = ctk.StringVar(value="Convertir")
        seg = ctk.CTkSegmentedButton(
            tab, values=["Convertir", "Comprimir", "Redimensionar"], variable=self.image_mode,
            command=self._on_image_mode,
            fg_color="#262626", selected_color=self.colors["accent"],
            selected_hover_color="#2563eb", unselected_hover_color="#333",
        )
        seg.pack(fill="x", pady=(0, 12))
        self.image_options = ctk.CTkFrame(tab, fg_color="transparent")
        self.image_options.pack(fill="both", expand=True)
        self._fill_image_convert_options()
        self._fill_image_compress_options()
        self._fill_image_resize_options()
        self._on_image_mode("Convertir")

    def _on_image_mode(self, value):
        self.current_tab = "Imagen"
        self.current_mode = value
        for w in self.image_options.winfo_children():
            w.pack_forget()
        if value == "Convertir":
            self.image_convert_frame.pack(fill="x", pady=(0, 12))
            self.image_convert_btn.pack(anchor="e", pady=(8, 0))
        elif value == "Comprimir":
            self.image_compress_frame.pack(fill="x", pady=(0, 12))
            self.image_compress_btn.pack(anchor="e", pady=(8, 0))
        else:
            self.image_resize_frame.pack(fill="x", pady=(0, 12))
            self.image_resize_btn.pack(anchor="e", pady=(8, 0))

    def _fill_image_convert_options(self):
        self.image_convert_frame = ctk.CTkFrame(self.image_options, fg_color="transparent")
        row = ctk.CTkFrame(self.image_convert_frame, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Formato destino:", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 8))
        self.image_format_var = ctk.StringVar(value="PNG")
        self.image_format_menu = ctk.CTkOptionMenu(
            row, values=["JPG", "PNG", "WebP", "BMP", "TIFF", "GIF"],
            variable=self.image_format_var, width=100,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        )
        self.image_format_menu.pack(side="left")
        self.image_convert_btn = ctk.CTkButton(
            self.image_options,
            text="Convertir",
            command=lambda: self._run_action("Imagen", "Convertir"),
            fg_color=self.colors["accent"], hover_color="#2563eb", height=38, corner_radius=8, width=120,
        )

    def _fill_image_compress_options(self):
        self.image_compress_frame = ctk.CTkFrame(self.image_options, fg_color="transparent")
        row = ctk.CTkFrame(self.image_compress_frame, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Calidad (1-100):", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 8))
        self.image_quality_var = ctk.StringVar(value="80")
        ctk.CTkOptionMenu(
            row, values=["60 (más compresión)", "70", "80", "90 (mejor calidad)"],
            variable=self.image_quality_var, width=180,
            fg_color="#262626", button_color="#333", button_hover_color="#444",
        ).pack(side="left")
        self.image_compress_btn = ctk.CTkButton(
            self.image_options,
            text="Comprimir",
            command=lambda: self._run_action("Imagen", "Comprimir"),
            fg_color=self.colors["accent"], hover_color="#2563eb", height=38, corner_radius=8, width=120,
        )

    def _fill_image_resize_options(self):
        self.image_resize_frame = ctk.CTkFrame(self.image_options, fg_color="transparent")
        row1 = ctk.CTkFrame(self.image_resize_frame, fg_color="transparent")
        row1.pack(fill="x")
        ctk.CTkLabel(row1, text="Ancho:", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 6))
        self.resize_width_var = ctk.StringVar(value="")
        ctk.CTkEntry(row1, textvariable=self.resize_width_var, width=80, placeholder_text="px").pack(side="left", padx=(0, 12))
        ctk.CTkLabel(row1, text="Alto:", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 6))
        self.resize_height_var = ctk.StringVar(value="")
        ctk.CTkEntry(row1, textvariable=self.resize_height_var, width=80, placeholder_text="px").pack(side="left", padx=(0, 12))
        row2 = ctk.CTkFrame(self.image_resize_frame, fg_color="transparent")
        row2.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row2, text="O escala %:", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(side="left", padx=(0, 6))
        self.resize_scale_var = ctk.StringVar(value="")
        ctk.CTkEntry(row2, textvariable=self.resize_scale_var, width=60, placeholder_text="50").pack(side="left")
        self.resize_keep_aspect_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            row2, text="Mantener proporción", variable=self.resize_keep_aspect_var,
            fg_color=self.colors["accent"], checkmark_color="white",
        ).pack(side="left", padx=(16, 0))
        self.image_resize_btn = ctk.CTkButton(
            self.image_options,
            text="Redimensionar",
            command=lambda: self._run_action("Imagen", "Redimensionar"),
            fg_color=self.colors["accent"], hover_color="#2563eb", height=38, corner_radius=8, width=120,
        )

    def _select_files(self):
        tab = self.tabview.get()
        if tab == "Vídeo":
            types = [("Vídeo", " ".join(f"*{e}" for e in VIDEO_FORMATS)), ("Todos", "*.*")]
        elif tab == "Audio":
            types = [("Audio", " ".join(f"*{e}" for e in AUDIO_FORMATS)), ("Todos", "*.*")]
        else:
            types = [("Imagen", " ".join(f"*{e}" for e in IMAGE_FORMATS)), ("Todos", "*.*")]
        files = filedialog.askopenfilenames(title="Seleccionar archivos", filetypes=types)
        if files:
            self.files = list(files)
            names = [Path(f).name for f in self.files[:3]]
            txt = ", ".join(names)
            if len(self.files) > 3:
                txt += f" +{len(self.files) - 3} más"
            self.file_label.configure(text=txt)
        self._update_format_menus()

    def _update_format_menus(self):
        if not self.files:
            return
        ext = get_ext(self.files[0])
        targets = get_target_formats(ext)
        labels = []
        seen = set()
        for t in targets:
            lb = FORMAT_LABELS.get(t, t.upper().lstrip("."))
            if lb not in seen:
                seen.add(lb)
                labels.append(lb)
        tab = self.tabview.get()
        if tab == "Vídeo" and ext in VIDEO_FORMATS:
            self.video_format_menu.configure(values=labels)
            if labels and LABEL_TO_EXT.get(self.video_format_var.get()) not in targets:
                self.video_format_var.set(labels[0])
        elif tab == "Audio" and ext in AUDIO_FORMATS:
            self.audio_format_menu.configure(values=labels)
            if labels and LABEL_TO_EXT.get(self.audio_format_var.get()) not in targets:
                self.audio_format_var.set(labels[0])
        elif tab == "Imagen" and ext in IMAGE_FORMATS:
            self.image_format_menu.configure(values=labels)
            if labels and LABEL_TO_EXT.get(self.image_format_var.get()) not in targets:
                self.image_format_var.set(labels[0])

    def _select_output_dir(self):
        folder = filedialog.askdirectory(title="Carpeta de salida")
        if folder:
            self.output_dir = folder
            self.status_label.configure(text=f"Salida: {folder}")

    def _get_target_ext_from_var(self, var: ctk.StringVar) -> str:
        val = var.get()
        return LABEL_TO_EXT.get(val, "." + val.lower() if not val.startswith(".") else val)

    def _run_action(self, tab_name: str, mode: str):
        if not self.files:
            messagebox.showwarning("Sin archivos", "Selecciona al menos un archivo.")
            return
        if not self.output_dir:
            self.output_dir = str(Path(self.files[0]).parent)
        ext = get_ext(self.files[0])
        cat = detect_category(ext)

        if tab_name == "Vídeo":
            if cat != "video":
                messagebox.showerror("Error", "En la pestaña Vídeo selecciona archivos de vídeo.")
                return
            if mode == "Convertir":
                target_ext = self._get_target_ext_from_var(self.video_format_var)
                self._do_convert_media(self.files[0], target_ext)
            else:
                crf_map = {"18 (alta calidad)": 18, "23 (buena)": 23, "28 (medio)": 28, "33 (más compresión)": 33}
                crf = crf_map.get(self.video_crf_var.get(), 28)
                out_path = str(Path(self.output_dir) / (Path(self.files[0]).stem + "_comprimido" + ext))
                self._do_compress_video(self.files[0], out_path, crf)
            return
        if tab_name == "Audio":
            if cat != "audio":
                messagebox.showerror("Error", "En la pestaña Audio selecciona archivos de audio.")
                return
            if mode == "Convertir":
                target_ext = self._get_target_ext_from_var(self.audio_format_var)
                try:
                    sr = int(self.audio_samplerate_var.get())
                except ValueError:
                    sr = 44100
                bitrate_k = None
                bit_depth = None
                if target_ext == ".wav":
                    try:
                        bit_depth = int(self.audio_bits_var.get())
                    except ValueError:
                        bit_depth = 24
                else:
                    try:
                        bitrate_k = int(self.audio_bitrate_convert_var.get())
                    except ValueError:
                        bitrate_k = 320
                self._do_convert_media(
                    self.files[0], target_ext,
                    audio_sample_rate=sr, audio_bitrate_k=bitrate_k, audio_bit_depth=bit_depth,
                )
            else:
                br_map = {"96 kbps": 96, "128 kbps": 128, "192 kbps": 192, "256 kbps": 256}
                bitrate = br_map.get(self.audio_bitrate_var.get(), 128)
                out_path = str(Path(self.output_dir) / (Path(self.files[0]).stem + "_comprimido.mp3"))
                self._do_compress_audio(self.files[0], out_path, bitrate)
            return
        if tab_name == "Imagen":
            if cat != "image":
                messagebox.showerror("Error", "En la pestaña Imagen selecciona archivos de imagen.")
                return
            if mode == "Convertir":
                target_ext = self._get_target_ext_from_var(self.image_format_var)
                self._do_convert_image(self.files[0], target_ext)
            elif mode == "Comprimir":
                q_map = {"60 (más compresión)": 60, "70": 70, "80": 80, "90 (mejor calidad)": 90}
                quality = q_map.get(self.image_quality_var.get(), 80)
                out_path = str(Path(self.output_dir) / (Path(self.files[0]).stem + "_comprimido" + ext))
                self._do_compress_image(self.files[0], out_path, quality)
            else:
                try:
                    w = int(self.resize_width_var.get().strip()) if self.resize_width_var.get().strip() else None
                except ValueError:
                    w = None
                try:
                    h = int(self.resize_height_var.get().strip()) if self.resize_height_var.get().strip() else None
                except ValueError:
                    h = None
                try:
                    scale = int(self.resize_scale_var.get().strip()) if self.resize_scale_var.get().strip() else None
                except ValueError:
                    scale = None
                if w is None and h is None and scale is None:
                    messagebox.showwarning("Redimensionar", "Indica ancho, alto o porcentaje de escala.")
                    return
                out_path = str(Path(self.output_dir) / (Path(self.files[0]).stem + "_resized" + ext))
                self._do_resize_image(self.files[0], out_path, width=w, height=h, scale_percent=scale, keep_aspect=self.resize_keep_aspect_var.get())
            return

    def _do_convert_media(
        self,
        inp: str,
        target_ext: str,
        *,
        audio_sample_rate: int | None = None,
        audio_bitrate_k: int | None = None,
        audio_bit_depth: int | None = None,
    ):
        base = Path(inp).stem
        out_path = str(Path(self.output_dir) / (base + target_ext))
        self._disable_and_show_progress()
        def on_done(o):
            self.after(0, lambda: self._finish_ok(o))
        def on_err(m):
            self.after(0, lambda: self._finish_error(m))
        def on_prog(p):
            self.after(0, lambda: self.progress.set(p / 100))
        convert_file(
            inp, out_path,
            on_progress=on_prog, on_done=on_done, on_error=on_err,
            audio_sample_rate=audio_sample_rate,
            audio_bitrate_k=audio_bitrate_k,
            audio_bit_depth=audio_bit_depth,
        )

    def _do_convert_image(self, inp: str, target_ext: str):
        base = Path(inp).stem
        out_path = str(Path(self.output_dir) / (base + target_ext))
        self._disable_and_show_progress()
        def on_done(o):
            self.after(0, lambda: self._finish_ok(o))
        def on_err(m):
            self.after(0, lambda: self._finish_error(m))
        def on_prog(p):
            self.after(0, lambda: self.progress.set(p / 100))
        convert_image(inp, out_path, on_progress=on_prog, on_done=on_done, on_error=on_err)

    def _do_compress_video(self, inp: str, out_path: str, crf: int):
        self._disable_and_show_progress()
        def on_done(o):
            self.after(0, lambda: self._finish_ok(o))
        def on_err(m):
            self.after(0, lambda: self._finish_error(m))
        def on_prog(p):
            self.after(0, lambda: self.progress.set(p / 100))
        compress_video(inp, out_path, crf=crf, on_progress=on_prog, on_done=on_done, on_error=on_err)

    def _do_compress_audio(self, inp: str, out_path: str, bitrate: int):
        self._disable_and_show_progress()
        def on_done(o):
            self.after(0, lambda: self._finish_ok(o))
        def on_err(m):
            self.after(0, lambda: self._finish_error(m))
        def on_prog(p):
            self.after(0, lambda: self.progress.set(p / 100))
        compress_audio(inp, out_path, bitrate_k=bitrate, on_progress=on_prog, on_done=on_done, on_error=on_err)

    def _do_compress_image(self, inp: str, out_path: str, quality: int):
        self._disable_and_show_progress()
        def on_done(o):
            self.after(0, lambda: self._finish_ok(o))
        def on_err(m):
            self.after(0, lambda: self._finish_error(m))
        def on_prog(p):
            self.after(0, lambda: self.progress.set(p / 100))
        compress_image(inp, out_path, quality=quality, on_progress=on_prog, on_done=on_done, on_error=on_err)

    def _do_resize_image(self, inp: str, out_path: str, width=None, height=None, scale_percent=None, keep_aspect=True):
        self._disable_and_show_progress()
        def on_done(o):
            self.after(0, lambda: self._finish_ok(o))
        def on_err(m):
            self.after(0, lambda: self._finish_error(m))
        def on_prog(p):
            self.after(0, lambda: self.progress.set(p / 100))
        resize_image(inp, out_path, width=width, height=height, scale_percent=scale_percent, keep_aspect=keep_aspect, on_progress=on_prog, on_done=on_done, on_error=on_err)

    def _disable_and_show_progress(self):
        self.progress.set(0)
        self.status_label.configure(text="Procesando...")
        for btn in [
            getattr(self, "video_action_btn", None),
            getattr(self, "video_compress_btn", None),
            getattr(self, "audio_action_btn", None),
            getattr(self, "audio_compress_btn", None),
            getattr(self, "image_convert_btn", None),
            getattr(self, "image_compress_btn", None),
            getattr(self, "image_resize_btn", None),
        ]:
            if btn is not None:
                btn.configure(state="disabled")

    def _finish_ok(self, out: str):
        self.progress.set(1.0)
        self.status_label.configure(text=f"Guardado: {Path(out).name}")
        for btn in [
            getattr(self, "video_action_btn", None),
            getattr(self, "video_compress_btn", None),
            getattr(self, "audio_action_btn", None),
            getattr(self, "audio_compress_btn", None),
            getattr(self, "image_convert_btn", None),
            getattr(self, "image_compress_btn", None),
            getattr(self, "image_resize_btn", None),
        ]:
            if btn is not None:
                btn.configure(state="normal")
        if len(self.files) > 1:
            self.files = self.files[1:]
            self.after(500, self._run_next_in_queue)
        else:
            messagebox.showinfo("Listo", f"Archivo guardado:\n{out}")

    def _run_next_in_queue(self):
        self.progress.set(0)
        self.status_label.configure(text="Siguiente archivo...")
        tab = self.tabview.get()
        mode = self.video_mode.get() if tab == "Vídeo" else (self.audio_mode.get() if tab == "Audio" else self.image_mode.get())
        self._run_action(tab, mode)

    def _finish_error(self, msg: str):
        self.status_label.configure(text="")
        for btn in [
            getattr(self, "video_action_btn", None),
            getattr(self, "video_compress_btn", None),
            getattr(self, "audio_action_btn", None),
            getattr(self, "audio_compress_btn", None),
            getattr(self, "image_convert_btn", None),
            getattr(self, "image_compress_btn", None),
            getattr(self, "image_resize_btn", None),
        ]:
            if btn is not None:
                btn.configure(state="normal")
        messagebox.showerror("Error", msg)


def main():
    app = ConvertidorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
