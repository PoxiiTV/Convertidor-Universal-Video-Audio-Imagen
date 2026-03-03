# Poxi Utilities – Video y Fotos

App de conversión de archivos multimedia para Windows: vídeo, audio e imágenes. Interfaz moderna en Electron + React con modo oscuro azulado.

![Version](https://img.shields.io/badge/version-1.0.0-blue)

## Funcionalidades

### Vídeo
- **Convertir**: MP4, MOV, AVI, MKV, WebM, M4V ↔ extraer audio (MP3, WAV, M4A, AAC, OGG, FLAC)
- **Comprimir**: ajuste de calidad (CRF 18–33)

### Audio
- **Convertir**: MP3, WAV, M4A, AAC, OGG, FLAC (sample rate, bitrate, bits)
- **Comprimir**: conversión a MP3 con bitrate configurable

### Imagen
- **Convertir**: JPG, PNG, WebP, BMP, TIFF, GIF, DNG (RAW)
- **Comprimir**: calidad configurable (Ligera 90, Media 80, Alta 70, Máxima 60)
- **Redimensionar**: ancho, alto o escala % (con opción de mantener proporción)

## Características de la interfaz

- Tema oscuro azul (`#0f1729`)
- Arrastrar y soltar para seleccionar archivos
- Vista previa de imagen seleccionada (miniatura 64×64)
- Barra de progreso con “Archivo X de Y” en colas
- Modal integrado “Conversión finalizada” con botón “Abrir carpeta”
- Botón Cancelar para detener conversiones
- Timeout de 15 minutos para archivos problemáticos
- Validación de formatos (aviso si se mezclan vídeo/imagen)
- Sin menú superior en la app final

## Requisitos

- **Windows 10/11**
- **FFmpeg** (en el PATH) para vídeo y audio
- **Python 3.10+** (solo para desarrollo/compilación)

## Descargas

Los ejecutables están en la sección **Releases** del repositorio (Portable e Instalador). Son ~114 MB porque incluyen Electron y las dependencias. Para subirlos: crea una Release en GitHub y adjunta los `.exe` desde `poxi-ui/release/`.

## Uso rápido

1. Ejecuta `Poxi Utilities - Video y Fotos - Portable.exe` (no requiere instalación)
2. O instala con `Poxi Utilities - Video y Fotos - Setup.exe`
3. Selecciona archivos (arrastra o usa el botón)
4. Elige pestaña (Vídeo/Audio/Imagen) y modo (Convertir/Comprimir/Redimensionar)
5. Configura opciones y pulsa el botón de acción

## Desarrollo

### Backend (Python)

```bash
pip install -r requirements.txt
python build_backend.py   # Genera converter_backend.exe → poxi-ui/backend/
```

### Frontend (Electron + React)

```bash
cd poxi-ui
npm install
npm run electron:dev      # Modo desarrollo con recarga en caliente
```

### Build completo

```bash
build_electron.bat        # Desde la raíz: compila backend + genera EXE
```

O manualmente:

```bash
python build_backend.py
cd poxi-ui && npm run dist
```

Salida en `poxi-ui/release/`:
- `Poxi Utilities - Video y Fotos - Portable.exe`
- `Poxi Utilities - Video y Fotos - Setup.exe`

## Estructura del proyecto

```
├── converter_core.py      # Lógica de conversión (FFmpeg, Pillow, rawpy)
├── converter_backend.py   # Backend headless (stdin JSON → stdout JSON)
├── build_backend.py       # Script para generar converter_backend.exe
├── build_electron.bat     # Build completo Windows
├── poxi-ui/
│   ├── electron/          # Proceso principal Electron
│   │   ├── main.js
│   │   └── preload.js
│   ├── src/
│   │   ├── App.jsx        # UI React
│   │   └── index.css
│   ├── backend/           # converter_backend.exe (generado)
│   └── release/           # EXE finales (generados)
└── requirements.txt
```

## Licencia

MIT
