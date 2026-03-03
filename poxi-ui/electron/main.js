const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow = null;
let backendProcess = null;
let pendingConversionFinish = null;

function getBackendPath() {
  const isDev = !app.isPackaged;
  if (isDev) {
    const scriptPath = path.join(__dirname, '..', '..', 'converter_backend.py');
    if (fs.existsSync(scriptPath)) return { type: 'python', path: scriptPath };
  } else {
    const exePath = path.join(process.resourcesPath, 'backend', 'converter_backend.exe');
    if (fs.existsSync(exePath)) return { type: 'exe', path: exePath };
    const fallback = path.join(app.getAppPath(), '..', 'backend', 'converter_backend.exe');
    if (fs.existsSync(fallback)) return { type: 'exe', path: fallback };
  }
  return null;
}

function createWindow() {
  const isDev = !app.isPackaged;
  const iconPath = path.join(__dirname, '..', '..', 'Poxi V4 SUPER PERFECT redondo.ico');
  mainWindow = new BrowserWindow({
    width: 640,
    height: 820,
    minWidth: 520,
    minHeight: 600,
    title: 'Poxi Utilities - Video y Fotos',
    backgroundColor: '#0f1729',
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    show: false,
  });
  mainWindow.once('ready-to-show', () => mainWindow.show());

  Menu.setApplicationMenu(null);

  const devUrl = process.env.VITE_DEV_SERVER_URL || 'http://127.0.0.1:5173';
  if (isDev) {
    mainWindow.loadURL(devUrl).catch(() => {
      mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
    });
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('selectFiles', async (_, { tab } = {}) => {
  const filters = {
    video: [{ name: 'Vídeo', extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm', 'm4v'] }],
    audio: [{ name: 'Audio', extensions: ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac'] }],
    image: [{ name: 'Imagen', extensions: ['dng', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'tif', 'webp'] }],
  };
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: filters[tab] || [{ name: 'Todos', extensions: ['*'] }],
  });
  return canceled ? [] : filePaths;
});

ipcMain.handle('selectOutputDir', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
  });
  return canceled ? null : filePaths[0];
});

function ensureBackend() {
  if (backendProcess) return backendProcess;
  const backend = getBackendPath();
  if (!backend) {
    throw new Error('Backend no encontrado. Ejecuta desde la carpeta del proyecto o empaqueta con backend.');
  }
  if (backend.type === 'python') {
    backendProcess = spawn(process.platform === 'win32' ? 'python' : 'python3', [backend.path], {
      cwd: path.dirname(backend.path),
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
    });
  } else {
    backendProcess = spawn(backend.path, [], {
      cwd: path.dirname(backend.path),
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
    });
  }
  backendProcess.on('error', () => {});
  backendProcess.on('exit', () => { backendProcess = null; });
  return backendProcess;
}

const CONVERSION_TIMEOUT_MS = 15 * 60 * 1000;

ipcMain.handle('runBackendCommand', async (_, cmd) => {
  return new Promise((resolve) => {
    let resolved = false;
    let timeoutId = null;
    const finish = (result) => {
      if (resolved) return;
      resolved = true;
      pendingConversionFinish = null;
      if (timeoutId) clearTimeout(timeoutId);
      resolve(result);
    };
    pendingConversionFinish = finish;
    try {
      const proc = ensureBackend();
      const send = (obj) => {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('backend:message', obj);
        }
      };
      const onData = (chunk) => {
        const lines = chunk.toString().split('\n').filter(Boolean);
        for (const line of lines) {
          try {
            const msg = JSON.parse(line);
            send(msg);
            if (msg.type === 'done') {
              proc.stdout.removeListener('data', onData);
              finish({ success: true, outputPath: msg.output_path || msg.outputPath });
            }
            if (msg.type === 'error') {
              proc.stdout.removeListener('data', onData);
              finish({ success: false, error: msg.message });
            }
          } catch (_) {}
        }
      };
      proc.stdout.on('data', onData);
      proc.once('error', (err) => finish({ success: false, error: err.message }));
      timeoutId = setTimeout(() => {
        proc.stdout.removeListener('data', onData);
        finish({
          success: false,
          error: 'La conversión ha tardado demasiado. El archivo puede estar dañado o ser incompatible. Prueba con un solo archivo.',
        });
      }, CONVERSION_TIMEOUT_MS);
      proc.stdin.write(JSON.stringify(cmd) + '\n');
    } catch (e) {
      finish({ success: false, error: e.message });
    }
  });
});

ipcMain.handle('cancelConversion', () => {
  if (pendingConversionFinish) {
    pendingConversionFinish({ success: false, error: 'Conversión cancelada por el usuario.' });
  }
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
});

ipcMain.handle('getTargetFormats', async (_, sourceExt) => {
  try {
    const proc = ensureBackend();
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => resolve([]), 3000);
      proc.stdout.once('data', (chunk) => {
        clearTimeout(timeout);
        try {
          const msg = JSON.parse(chunk.toString().split('\n')[0]);
          if (msg.type === 'target_formats') resolve(msg.formats || []);
          else resolve([]);
        } catch (_) { resolve([]); }
      });
      proc.stdin.write(JSON.stringify({ action: 'get_target_formats', source_ext: sourceExt }) + '\n');
    });
  } catch (_) {
    return [];
  }
});

ipcMain.handle('openOutputFolder', async (_, outputPath) => {
  if (outputPath) shell.showItemInFolder(outputPath);
});

ipcMain.handle('getFilePreview', async (_, filePath) => {
  try {
    if (!filePath || typeof filePath !== 'string') return null;
    const ext = path.extname(filePath).toLowerCase();
    const imageExts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'];
    if (!imageExts.includes(ext) || !fs.existsSync(filePath)) return null;
    const stat = fs.statSync(filePath);
    if (stat.size > 3 * 1024 * 1024) return null;
    const buf = fs.readFileSync(filePath);
    const b64 = buf.toString('base64');
    const mime = ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' : ext === '.png' ? 'image/png' : ext === '.gif' ? 'image/gif' : ext === '.webp' ? 'image/webp' : ext === '.tiff' || ext === '.tif' ? 'image/tiff' : 'image/bmp';
    return `data:${mime};base64,${b64}`;
  } catch {
    return null;
  }
});
