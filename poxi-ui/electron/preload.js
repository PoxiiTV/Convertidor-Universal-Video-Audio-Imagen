const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('poxi', {
  selectFiles: (tab = 'video') => ipcRenderer.invoke('selectFiles', { tab }),
  selectOutputDir: () => ipcRenderer.invoke('selectOutputDir'),
  runBackendCommand: (cmd) => ipcRenderer.invoke('runBackendCommand', cmd),
  getTargetFormats: (sourceExt) => ipcRenderer.invoke('getTargetFormats', sourceExt),
  openOutputFolder: (path) => ipcRenderer.invoke('openOutputFolder', path),
  getFilePreview: (path) => ipcRenderer.invoke('getFilePreview', path),
  cancelConversion: () => ipcRenderer.invoke('cancelConversion'),
  onBackendMessage: (callback) => {
    ipcRenderer.on('backend:message', (_, msg) => callback(msg));
  },
});
