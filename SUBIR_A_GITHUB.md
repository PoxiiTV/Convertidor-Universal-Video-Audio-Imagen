# Cómo subir Poxi Utilities a GitHub

## 1. Crear el repositorio en GitHub

1. Entra en [github.com](https://github.com) y crea un **nuevo repositorio**
2. Nombre sugerido: `poxi-utilities` o `Poxi-Utilities`
3. Descripción: `Conversor de vídeo, audio e imágenes para Windows`
4. Elige **público**
5. No añadas README, .gitignore ni LICENSE (ya existen en el proyecto)
6. Haz clic en **Create repository**

## 2. Configurar Git (si es la primera vez)

```bash
git config --global user.email "tu@email.com"
git config --global user.name "Tu Nombre"
```

## 3. Subir el código

Git ya está inicializado y los archivos están en staging. Solo falta el commit y el push:

```bash
cd "F:\CONVERTIDOR CASERO"

git commit -m "Poxi Utilities v1.0.0 - Conversor de video, audio e imagenes"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

**Sustituye** `TU_USUARIO` y `TU_REPO` por tu usuario de GitHub y el nombre del repositorio.

## 4. Subir los ejecutables (.exe)

Los .exe (~114 MB cada uno) no van en el repo por el límite de 100 MB de GitHub. Publícalos en **Releases**:

1. En tu repositorio, ve a **Releases** → **Create a new release**
2. Tag: `v1.0.0`
3. Título: `v1.0.0`
4. Descripción (ejemplo):

   ```
   ## Descargas
   - **Portable**: Poxi Utilities - Videos, Fotos y Audio - Portable.exe (no requiere instalación)
   - **Instalador**: Poxi Utilities - Videos, Fotos y Audio - Setup.exe
   ```

5. Arrastra los dos archivos desde `poxi-ui/release/` a la zona de adjuntos
6. Publica la release

## 5. Actualizar el README

En el README, sustituye la sección de descargas por algo como:

```markdown
## Descargas

[Releases](https://github.com/TU_USUARIO/TU_REPO/releases) – Portable e Instalador
```

Luego haz commit y push de ese cambio.
