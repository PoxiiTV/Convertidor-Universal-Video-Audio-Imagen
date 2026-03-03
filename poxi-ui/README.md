# Poxi Utilities - Video y Fotos (Electron + React)

Interfaz moderna en Electron + React. La conversión real la hace el backend en Python (mismo código que el convertidor clásico).

## Requisitos

- Node.js 18+
- Python 3.10+ (para desarrollo; el EXE final lleva el backend empaquetado)
- FFmpeg en el PATH (para vídeo/audio)

## Desarrollo

1. **Backend (primera vez o si cambias lógica Python)**  
   En la raíz del proyecto (`CONVERTIDOR CASERO`):
   ```bash
   pip install -r requirements.txt
   python build_backend.py
   ```
   Esto genera `dist/converter_backend.exe` y lo copia a `poxi-ui/backend/`.

2. **Instalar dependencias de la UI**
   ```bash
   cd poxi-ui
   npm install
   ```

3. **Arrancar en modo desarrollo**
   ```bash
   npm run electron:dev
   ```
   Se abre Electron y usa `converter_backend.py` del proyecto (necesitas Python en PATH).

## Build del EXE (portable)

1. En la raíz del proyecto, generar el backend:
   ```bash
   python build_backend.py
   ```
   (Así queda `poxi-ui/backend/converter_backend.exe`.)

2. En `poxi-ui`:
   ```bash
   npm run dist
   ```
   El ejecutable portable estará en `poxi-ui/release/`.

## Estructura

- `electron/main.js`: ventana Electron, diálogos, spawn del backend.
- `electron/preload.js`: API expuesta al renderer (`window.poxi`).
- `src/App.jsx`: UI React (pestañas Vídeo / Audio / Imagen, modos, progreso).
- El backend (`converter_backend.exe` o `converter_backend.py`) recibe comandos JSON por stdin y devuelve progreso/resultado por stdout.
