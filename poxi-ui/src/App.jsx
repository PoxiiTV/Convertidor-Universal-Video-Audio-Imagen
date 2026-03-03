import React, { useState, useEffect } from 'react';

const LABEL_TO_EXT = {
  MP4: '.mp4', MOV: '.mov', AVI: '.avi', MKV: '.mkv', WebM: '.webm', M4V: '.m4v',
  MP3: '.mp3', WAV: '.wav', M4A: '.m4a', AAC: '.aac', OGG: '.ogg', FLAC: '.flac',
  DNG: '.dng', JPG: '.jpg', JPEG: '.jpeg', PNG: '.png', BMP: '.bmp', GIF: '.gif', TIFF: '.tiff', WebP: '.webp',
};

const EXT_TO_LABEL = {
  '.mp4': 'MP4', '.mov': 'MOV', '.avi': 'AVI', '.mkv': 'MKV', '.webm': 'WebM', '.m4v': 'M4V',
  '.mp3': 'MP3', '.wav': 'WAV', '.m4a': 'M4A', '.aac': 'AAC', '.ogg': 'OGG', '.flac': 'FLAC',
  '.dng': 'DNG', '.jpg': 'JPG', '.jpeg': 'JPEG', '.png': 'PNG', '.bmp': 'BMP', '.gif': 'GIF', '.tiff': 'TIFF', '.tif': 'TIFF', '.webp': 'WebP',
};
const VIDEO_EXTS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'];
const AUDIO_EXTS = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'];
const IMAGE_EXTS = ['.dng', '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'];

function getExt(path) {
  return path.slice(path.lastIndexOf('.')).toLowerCase();
}

function getTargetFormatsForExt(ext) {
  if (VIDEO_EXTS.includes(ext)) {
    const videoLabels = VIDEO_EXTS.filter((e) => e !== ext).map((e) => EXT_TO_LABEL[e]);
    const audioLabels = AUDIO_EXTS.map((e) => EXT_TO_LABEL[e]);
    return [...videoLabels, ...audioLabels];
  }
  if (AUDIO_EXTS.includes(ext)) {
    return AUDIO_EXTS.filter((e) => e !== ext).map((e) => EXT_TO_LABEL[e]);
  }
  if (IMAGE_EXTS.includes(ext)) {
    const out = IMAGE_EXTS.filter((e) => e !== ext && !(ext === '.tiff' && e === '.tif'));
    return [...new Set(out.map((e) => EXT_TO_LABEL[e]))];
  }
  return [];
}

function App() {
  const [files, setFiles] = useState([]);
  const [outputDir, setOutputDir] = useState('');
  const [tab, setTab] = useState('video');
  const [mode, setMode] = useState('convert');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [busy, setBusy] = useState(false);
  const [queueIndex, setQueueIndex] = useState(0);

  const [videoFormat, setVideoFormat] = useState('MP4');
  const [videoCrf, setVideoCrf] = useState('28 (medio)');

  const [audioFormat, setAudioFormat] = useState('MP3');
  const [audioSampleRate, setAudioSampleRate] = useState('44100');
  const [audioBitrate, setAudioBitrate] = useState('320');
  const [audioBits, setAudioBits] = useState('24');
  const [audioCompressBitrate, setAudioCompressBitrate] = useState('128 kbps');

  const [imageFormat, setImageFormat] = useState('PNG');
  const [imageQuality, setImageQuality] = useState('Media (80)');
  const [resizeW, setResizeW] = useState('');
  const [resizeH, setResizeH] = useState('');
  const [resizeScale, setResizeScale] = useState('');
  const [resizeKeepAspect, setResizeKeepAspect] = useState(true);

  const [targetFormats, setTargetFormats] = useState([]);
  const [conversionDonePath, setConversionDonePath] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const api = window.poxi;
  if (!api) {
    return (
      <div>
        <h1>Poxi Utilities</h1>
        <p>Ejecuta esta app con Electron (npm run electron).</p>
      </div>
    );
  }

  useEffect(() => {
    api.onBackendMessage((msg) => {
      if (msg.type === 'progress') setProgress(msg.percent || 0);
    });
  }, []);

  useEffect(() => {
    if (!files.length || !api.getFilePreview) {
      setPreviewUrl(null);
      return;
    }
    const ext = getExt(files[0]);
    if (!IMAGE_EXTS.includes(ext)) {
      setPreviewUrl(null);
      return;
    }
    let cancelled = false;
    api.getFilePreview(files[0]).then((url) => {
      if (!cancelled) setPreviewUrl(url);
    });
    return () => { cancelled = true; };
  }, [files]);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!busy) setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    if (busy) return;
    const items = e.dataTransfer?.files;
    if (!items?.length) return;
    const exts = tab === 'video' ? [...VIDEO_EXTS, ...AUDIO_EXTS] : tab === 'audio' ? [...VIDEO_EXTS, ...AUDIO_EXTS] : IMAGE_EXTS;
    const paths = [];
    for (let i = 0; i < items.length; i++) {
      const f = items[i];
      const path = f.path || f.webkitRelativePath;
      if (path) {
        const ext = getExt(path);
        if (exts.includes(ext)) paths.push(path);
      }
    }
    if (paths.length) setFiles(paths);
  };

  const handleSelectFiles = async () => {
    const paths = await api.selectFiles(tab);
    if (paths && paths.length) setFiles(paths);
  };

  const handleSelectOutput = async () => {
    const dir = await api.selectOutputDir();
    if (dir) setOutputDir(dir);
  };

  useEffect(() => {
    if (files.length) {
      const ext = getExt(files[0]);
      const formats = getTargetFormatsForExt(ext);
      const extIsVideo = VIDEO_EXTS.includes(ext);
      const extIsAudio = AUDIO_EXTS.includes(ext);
      const extIsImage = IMAGE_EXTS.includes(ext);
      if (tab === 'video' && (extIsVideo || extIsAudio)) {
        setTargetFormats(formats);
      } else if (tab === 'audio' && (extIsVideo || extIsAudio)) {
        setTargetFormats(formats);
      } else if (tab === 'image' && extIsImage) {
        setTargetFormats(formats);
      } else {
        const defaults = { video: ['MP4', 'MOV', 'AVI', 'MKV', 'WebM', 'MP3'], audio: ['MP3', 'WAV', 'M4A', 'AAC', 'OGG', 'FLAC'], image: ['JPG', 'PNG', 'WebP', 'BMP', 'TIFF', 'GIF'] };
        setTargetFormats(defaults[tab] || []);
      }
    } else {
      const defaults = { video: ['MP4', 'MOV', 'AVI', 'MKV', 'WebM', 'MP3'], audio: ['MP3', 'WAV', 'M4A', 'AAC', 'OGG', 'FLAC'], image: ['JPG', 'PNG', 'WebP', 'BMP', 'TIFF', 'GIF'] };
      setTargetFormats(defaults[tab] || []);
    }
  }, [files, tab]);

  const outPath = (base, ext, suffix = '') => {
    const dir = outputDir || (files[0] ? files[0].replace(/\\/g, '/').replace(/\/[^/]+$/, '') : '');
    const name = base + (suffix ? suffix : '') + ext;
    return dir ? `${dir}/${name}` : name;
  };

  const runOne = async (inputPath) => {
    const base = inputPath.replace(/\\/g, '/').split('/').pop().replace(/\.[^.]+$/, '');
    const ext = getExt(inputPath);
    let cmd = {};

    if (tab === 'video') {
      if (mode === 'convert') {
        const targetExt = LABEL_TO_EXT[videoFormat] || '.mp4';
        cmd = {
          action: 'convert_media',
          input_path: inputPath,
          output_path: outPath(base, targetExt),
        };
      } else {
        const crfMap = { '18 (alta calidad)': 18, '23 (buena)': 23, '28 (medio)': 28, '33 (más compresión)': 33 };
        cmd = {
          action: 'compress_video',
          input_path: inputPath,
          output_path: outPath(base, ext, '_comprimido'),
          crf: crfMap[videoCrf] ?? 28,
        };
      }
    } else if (tab === 'audio') {
      if (mode === 'convert') {
        const targetExt = LABEL_TO_EXT[audioFormat] || '.mp3';
        cmd = {
          action: 'convert_media',
          input_path: inputPath,
          output_path: outPath(base, targetExt),
          audio_sample_rate: parseInt(audioSampleRate, 10) || 44100,
          audio_bitrate_k: targetExt === '.wav' ? undefined : (parseInt(audioBitrate, 10) || 320),
          audio_bit_depth: targetExt === '.wav' ? (parseInt(audioBits, 10) || 24) : undefined,
        };
      } else {
        const brMap = { '96 kbps': 96, '128 kbps': 128, '192 kbps': 192, '256 kbps': 256 };
        cmd = {
          action: 'compress_audio',
          input_path: inputPath,
          output_path: outPath(base, '.mp3', '_comprimido'),
          bitrate_k: brMap[audioCompressBitrate] ?? 128,
        };
      }
    } else {
      if (mode === 'convert') {
        const targetExt = LABEL_TO_EXT[imageFormat] || '.png';
        cmd = {
          action: 'convert_image',
          input_path: inputPath,
          output_path: outPath(base, targetExt),
        };
      } else if (mode === 'compress') {
        const qMap = {
          'Máxima (60)': 60,
          'Alta (70)': 70,
          'Media (80)': 80,
          'Ligera (90)': 90,
        };
        cmd = {
          action: 'compress_image',
          input_path: inputPath,
          output_path: outPath(base, ext, '_comprimido'),
          quality: qMap[imageQuality] ?? 80,
        };
      } else {
        let w = parseInt(resizeW, 10) || null;
        let h = parseInt(resizeH, 10) || null;
        let scale = parseInt(resizeScale, 10) || null;
        if (!w && !h && !scale) {
          setStatus('Indica ancho, alto o %');
          return;
        }
        cmd = {
          action: 'resize_image',
          input_path: inputPath,
          output_path: outPath(base, ext, '_resized'),
          width: w,
          height: h,
          scale_percent: scale,
          keep_aspect: resizeKeepAspect,
        };
      }
    }

    setProgress(0);
    const result = await api.runBackendCommand(cmd);
    setProgress(100);
    if (result.success) {
      setStatus(`Guardado: ${result.outputPath?.split(/[/\\]/).pop() || ''}`);
      const nextIndex = queueIndex + 1;
      if (nextIndex < files.length) {
        setQueueIndex(nextIndex);
        setTimeout(() => runOne(files[nextIndex]), 400);
      } else {
        setBusy(false);
        setQueueIndex(0);
        setStatus('');
        setProgress(0);
        if (result.outputPath) setConversionDonePath(result.outputPath);
      }
    } else {
      setBusy(false);
      setQueueIndex(0);
      setStatus('');
      setProgress(0);
      alert(result.error || 'Error');
    }
  };

  const handleAction = () => {
    if (!files.length) {
      alert('Selecciona al menos un archivo.');
      return;
    }
    const ext = getExt(files[0]);
    const isVideo = VIDEO_EXTS.includes(ext);
    const isAudio = AUDIO_EXTS.includes(ext);
    const isImage = IMAGE_EXTS.includes(ext);
    const extLabel = EXT_TO_LABEL[ext] || ext.toUpperCase();

    if (tab === 'video' && !isVideo && !isAudio) {
      alert(`Tienes un archivo ${extLabel} (imagen) seleccionado y estás en la pestaña Vídeo. Para convertir imágenes, usa la pestaña "Imagen" o selecciona archivos de vídeo/audio.`);
      return;
    }
    if (tab === 'audio' && !isVideo && !isAudio) {
      alert(`Tienes un archivo ${extLabel} (imagen) seleccionado y estás en la pestaña Audio. Para convertir imágenes, usa la pestaña "Imagen" o selecciona archivos de vídeo/audio.`);
      return;
    }
    if (tab === 'image' && !isImage) {
      const tipo = isVideo ? 'vídeo' : isAudio ? 'audio' : 'desconocido';
      alert(`Tienes un archivo ${extLabel} (${tipo}) seleccionado y quieres convertirlo a un formato de imagen. Selecciona archivos de imagen (JPG, PNG, DNG, etc.) o cambia a la pestaña "Vídeo" o "Audio".`);
      return;
    }

    setBusy(true);
    setQueueIndex(0);
    runOne(files[0]);
  };

  const handleOpenOutputFolder = () => {
    if (conversionDonePath && api.openOutputFolder) api.openOutputFolder(conversionDonePath);
    setConversionDonePath(null);
  };

  return (
    <>
      {conversionDonePath && (
        <div className="modal-overlay" onClick={() => setConversionDonePath(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon">✓</div>
            <h2 className="modal-title">Conversión finalizada</h2>
            <p className="modal-message">El archivo se ha guardado correctamente.</p>
            <p className="modal-path">{conversionDonePath}</p>
            <div className="modal-actions">
              <button type="button" className="btn btn-primary" onClick={handleOpenOutputFolder}>
                Abrir carpeta de salida
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setConversionDonePath(null)}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="header">
        <h1>Poxi Utilities</h1>
        <p className="subtitle">Vídeo · Audio · Imagen · Convertir · Comprimir · Redimensionar</p>
      </div>

      <div
        className={`card drop-zone ${dragOver ? 'drop-zone-active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="row">
          <button type="button" className="btn btn-secondary" onClick={handleSelectFiles} disabled={busy}>
            Seleccionar archivos
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleSelectOutput} disabled={busy}>
            Carpeta de salida
          </button>
        </div>
        {files.length > 0 && (
          <div className="file-preview-row">
            {previewUrl ? (
              <div className="file-preview-thumb">
                <img src={previewUrl} alt="Vista previa" />
              </div>
            ) : (
              <div className="file-preview-icon">
                {VIDEO_EXTS.includes(getExt(files[0])) ? '🎬' : AUDIO_EXTS.includes(getExt(files[0])) ? '🎵' : '🖼️'}
              </div>
            )}
            <div className="file-list">
              {files.length} archivo(s): {files.slice(0, 2).map((f) => f.split(/[/\\]/).pop()).join(', ')}{files.length > 2 ? '…' : ''}
            </div>
          </div>
        )}
        {files.length === 0 && (
          <div className="file-list file-list-empty">
            {dragOver ? 'Suelta los archivos aquí' : 'Ningún archivo seleccionado. Arrastra archivos o usa el botón.'}
          </div>
        )}
      </div>

      <div className="tabs">
        {['video', 'audio', 'image'].map((t) => (
          <button
            key={t}
            type="button"
            className={`tab ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t === 'video' ? 'Vídeo' : t === 'audio' ? 'Audio' : 'Imagen'}
          </button>
        ))}
      </div>

      {tab === 'video' && (
        <>
          <div className="modes">
            {['convert', 'compress'].map((m) => (
              <button
                key={m}
                type="button"
                className={`mode ${mode === m ? 'active' : ''}`}
                onClick={() => setMode(m)}
              >
                {m === 'convert' ? 'Convertir' : 'Comprimir'}
              </button>
            ))}
          </div>
          <div className="card">
            {mode === 'convert' && (
              <div className="row">
                <span className="label">Formato:</span>
                <select className="select" value={videoFormat} onChange={(e) => setVideoFormat(e.target.value)}>
                  {(targetFormats.length ? targetFormats : ['MP4', 'MOV', 'AVI', 'MKV', 'WebM', 'MP3']).map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>
            )}
            {mode === 'compress' && (
              <div className="row">
                <span className="label">CRF:</span>
                <select className="select" value={videoCrf} onChange={(e) => setVideoCrf(e.target.value)}>
                  <option value="18 (alta calidad)">18 (alta calidad)</option>
                  <option value="23 (buena)">23 (buena)</option>
                  <option value="28 (medio)">28 (medio)</option>
                  <option value="33 (más compresión)">33 (más compresión)</option>
                </select>
              </div>
            )}
            <div className="action-row">
              <button type="button" className="btn btn-primary" onClick={handleAction} disabled={busy}>
                {mode === 'convert' ? 'Convertir' : 'Comprimir'}
              </button>
            </div>
          </div>
        </>
      )}

      {tab === 'audio' && (
        <>
          <div className="modes">
            {['convert', 'compress'].map((m) => (
              <button key={m} type="button" className={`mode ${mode === m ? 'active' : ''}`} onClick={() => setMode(m)}>
                {m === 'convert' ? 'Convertir' : 'Comprimir'}
              </button>
            ))}
          </div>
          <div className="card">
            {mode === 'convert' && (
              <>
                <div className="row">
                  <span className="label">Formato:</span>
                  <select className="select" value={audioFormat} onChange={(e) => setAudioFormat(e.target.value)}>
                    {(targetFormats.length ? targetFormats : ['MP3', 'WAV', 'M4A', 'AAC', 'OGG', 'FLAC']).map((f) => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                </div>
                <div className="row">
                  <span className="label">Hz:</span>
                  <select className="select" value={audioSampleRate} onChange={(e) => setAudioSampleRate(e.target.value)}>
                    <option value="22050">22050</option>
                    <option value="44100">44100</option>
                    <option value="48000">48000</option>
                    <option value="96000">96000</option>
                    <option value="192000">192000</option>
                  </select>
                  {LABEL_TO_EXT[audioFormat] === '.wav' ? (
                    <>
                      <span className="label">Bits:</span>
                      <select className="select" value={audioBits} onChange={(e) => setAudioBits(e.target.value)}>
                        <option value="16">16</option>
                        <option value="24">24</option>
                        <option value="32">32</option>
                      </select>
                    </>
                  ) : (
                    <>
                      <span className="label">kbps:</span>
                      <select className="select" value={audioBitrate} onChange={(e) => setAudioBitrate(e.target.value)}>
                        <option value="128">128</option>
                        <option value="192">192</option>
                        <option value="256">256</option>
                        <option value="320">320</option>
                      </select>
                    </>
                  )}
                </div>
              </>
            )}
            {mode === 'compress' && (
              <div className="row">
                <span className="label">Bitrate:</span>
                <select className="select" value={audioCompressBitrate} onChange={(e) => setAudioCompressBitrate(e.target.value)}>
                  <option value="96 kbps">96 kbps</option>
                  <option value="128 kbps">128 kbps</option>
                  <option value="192 kbps">192 kbps</option>
                  <option value="256 kbps">256 kbps</option>
                </select>
              </div>
            )}
            <div className="action-row">
              <button type="button" className="btn btn-primary" onClick={handleAction} disabled={busy}>
                {mode === 'convert' ? 'Convertir' : 'Comprimir'}
              </button>
            </div>
          </div>
        </>
      )}

      {tab === 'image' && (
        <>
          <div className="modes">
            {['convert', 'compress', 'resize'].map((m) => (
              <button key={m} type="button" className={`mode ${mode === m ? 'active' : ''}`} onClick={() => setMode(m)}>
                {m === 'convert' ? 'Convertir' : m === 'compress' ? 'Comprimir' : 'Redimensionar'}
              </button>
            ))}
          </div>
          <div className="card">
            {mode === 'convert' && (
              <div className="row">
                <span className="label">Formato:</span>
                <select className="select" value={imageFormat} onChange={(e) => setImageFormat(e.target.value)}>
                  {(targetFormats.length ? targetFormats : ['JPG', 'PNG', 'WebP', 'BMP', 'TIFF', 'GIF']).map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>
            )}
            {mode === 'compress' && (
              <div className="row">
                <span className="label">Compresión:</span>
                <select className="select" value={imageQuality} onChange={(e) => setImageQuality(e.target.value)}>
                  <option value="Ligera (90)">Ligera (90)</option>
                  <option value="Media (80)">Media (80)</option>
                  <option value="Alta (70)">Alta (70)</option>
                  <option value="Máxima (60)">Máxima (60)</option>
                </select>
              </div>
            )}
            {mode === 'resize' && (
              <>
                <div className="row">
                  <span className="label">Ancho:</span>
                  <input type="text" className="input" placeholder="px" value={resizeW} onChange={(e) => setResizeW(e.target.value)} />
                  <span className="label">Alto:</span>
                  <input type="text" className="input" placeholder="px" value={resizeH} onChange={(e) => setResizeH(e.target.value)} />
                </div>
                <div className="row">
                  <span className="label">Escala %:</span>
                  <input type="text" className="input" placeholder="50" value={resizeScale} onChange={(e) => setResizeScale(e.target.value)} />
                  <label className="checkbox-row">
                    <input type="checkbox" checked={resizeKeepAspect} onChange={(e) => setResizeKeepAspect(e.target.checked)} />
                    Mantener proporción
                  </label>
                </div>
              </>
            )}
            <div className="action-row">
              <button type="button" className="btn btn-primary" onClick={handleAction} disabled={busy}>
                {mode === 'convert' ? 'Convertir' : mode === 'compress' ? 'Comprimir' : 'Redimensionar'}
              </button>
            </div>
          </div>
        </>
      )}

      <div className="progress-wrap">
        {busy && files.length > 1 && (
          <div className="progress-queue">Archivo {queueIndex + 1} de {files.length}</div>
        )}
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="progress-footer">
          <span className="status">{status || (busy ? 'Procesando…' : '')}</span>
          {busy && api.cancelConversion && (
            <button type="button" className="btn btn-cancel" onClick={() => api.cancelConversion()}>
              Cancelar
            </button>
          )}
        </div>
      </div>
    </>
  );
}

export default App;
