const MAX_FILE_BYTES = 10 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['txt', 'docx', 'pdf'];
const referenceState = [];
let scanState = null;
let toastTimer = null;

const percent = value => `${Math.round(value * 100)}%`;
const byId = id => document.getElementById(id);

function escapeHtml(value) {
  const element = document.createElement('div');
  element.textContent = String(value ?? '');
  return element.innerHTML;
}

function formatBytes(value) {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function extensionOf(filename) {
  return filename.includes('.') ? filename.split('.').pop().toLowerCase() : '';
}

function makeId() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`;
}

function showToast(message) {
  const toast = byId('toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3200);
}

function validateFile(file) {
  if (!ALLOWED_EXTENSIONS.includes(extensionOf(file.name))) {
    return 'Use a TXT, DOCX, or PDF file.';
  }
  if (file.size > MAX_FILE_BYTES) return 'The file is larger than 10 MB.';
  if (file.size === 0) return 'The file is empty.';
  return null;
}

function fileRow(item, removable = true) {
  const detail = item.message || (item.status === 'ready' ? `${formatBytes(item.file.size)} / Ready` : item.status);
  return `
    <article class="file-item ${item.status}" data-file-id="${item.id}">
      <span class="file-type">${escapeHtml(extensionOf(item.file.name).toUpperCase())}</span>
      <span class="file-copy"><strong>${escapeHtml(item.file.name)}</strong><small>${escapeHtml(detail)}</small></span>
      ${removable && item.status !== 'uploading' ? `<button class="file-remove" type="button" data-remove="${item.id}" aria-label="Remove ${escapeHtml(item.file.name)}">&#10005;</button>` : '<span></span>'}
      <i class="file-progress" style="width:${item.progress || 0}%"></i>
    </article>`;
}

function renderReferenceQueue() {
  byId('reference-queue').innerHTML = referenceState.map(item => fileRow(item)).join('');
  byId('reference-submit').disabled = !referenceState.some(item => item.status === 'ready');
}

function renderScanQueue() {
  byId('scan-queue').innerHTML = scanState ? fileRow(scanState) : '';
  byId('scan-submit').disabled = !scanState || scanState.status !== 'ready';
}

function addReferenceFiles(files) {
  for (const file of files) {
    const error = validateFile(file);
    if (error) {
      showToast(`${file.name}: ${error}`);
      continue;
    }
    const duplicate = referenceState.some(item => item.file.name === file.name && item.file.size === file.size);
    if (!duplicate) referenceState.push({ id: makeId(), file, status: 'ready', progress: 0, message: '' });
  }
  renderReferenceQueue();
}

function setScanFile(file) {
  const error = validateFile(file);
  if (error) {
    showToast(error);
    return;
  }
  scanState = { id: makeId(), file, status: 'ready', progress: 0, message: '' };
  renderScanQueue();
}

function setupDropzone(dropzoneId, inputId, onFiles) {
  const dropzone = byId(dropzoneId);
  const input = byId(inputId);
  dropzone.addEventListener('click', () => input.click());
  dropzone.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      input.click();
    }
  });
  input.addEventListener('change', () => {
    onFiles([...input.files]);
    input.value = '';
  });
  for (const eventName of ['dragenter', 'dragover']) {
    dropzone.addEventListener(eventName, event => {
      event.preventDefault();
      dropzone.classList.add('dragging');
    });
  }
  for (const eventName of ['dragleave', 'drop']) {
    dropzone.addEventListener(eventName, event => {
      event.preventDefault();
      dropzone.classList.remove('dragging');
    });
  }
  dropzone.addEventListener('drop', event => onFiles([...event.dataTransfer.files]));
}

function uploadWithProgress(file, endpoint, onProgress) {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    const body = new FormData();
    body.append('file', file);
    request.open('POST', endpoint);
    request.upload.addEventListener('progress', event => {
      if (event.lengthComputable) onProgress(Math.round((event.loaded / event.total) * 100));
    });
    request.addEventListener('load', () => {
      let data = {};
      try { data = JSON.parse(request.responseText || '{}'); } catch { data = {}; }
      if (request.status >= 200 && request.status < 300) resolve(data);
      else reject(new Error(data.detail || 'The upload could not be completed.'));
    });
    request.addEventListener('error', () => reject(new Error('The server could not be reached.')));
    request.send(body);
  });
}

async function readJson(response) {
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'The request failed.');
  return data;
}

async function loadHealth() {
  try {
    const data = await fetch('/api/health').then(readJson);
    byId('model-status').textContent = data.semantic_requested && data.semantic_available
      ? 'Hybrid model active'
      : 'Lexical model active';
  } catch {
    byId('model-status').textContent = 'Server unavailable';
  }
}

async function loadProgress() {
  try {
    const data = await fetch('/api/progress').then(readJson);
    byId('overall-percent').textContent = `${data.overall_percent}%`;
    byId('overall-bar').style.width = `${data.overall_percent}%`;
    byId('updated').textContent = `Tracker updated ${data.updated}`;
    byId('objectives').innerHTML = data.objectives.map(item => `
      <article class="objective">
        <div class="objective-head"><h3>Objective ${item.id}: ${escapeHtml(item.title)}</h3><span class="badge">${escapeHtml(item.status.replaceAll('_', ' '))}</span></div>
        <p>Next: ${escapeHtml(item.next)}</p>
        <div class="mini-progress"><i style="width:${item.percent}%"></i></div>
      </article>`).join('');
  } catch (error) {
    byId('updated').textContent = 'Tracker unavailable';
  }
}

async function loadReferences() {
  try {
    const data = await fetch('/api/references').then(readJson);
    byId('corpus-count').textContent = data.count;
    byId('corpus-list').innerHTML = data.documents.length
      ? data.documents.map(item => `<li data-type="${escapeHtml(item.extension.replace('.', '').toUpperCase())}"><span>${escapeHtml(item.name)}</span><small>${formatBytes(item.size_bytes)}</small></li>`).join('')
      : '<li class="empty-row">No sources added yet.</li>';
  } catch {
    byId('corpus-list').innerHTML = '<li class="empty-row">Could not load the source library.</li>';
  }
}

byId('reference-queue').addEventListener('click', event => {
  const id = event.target.closest('[data-remove]')?.dataset.remove;
  if (!id) return;
  const index = referenceState.findIndex(item => item.id === id);
  if (index >= 0) referenceState.splice(index, 1);
  renderReferenceQueue();
});

byId('scan-queue').addEventListener('click', event => {
  if (!event.target.closest('[data-remove]')) return;
  scanState = null;
  renderScanQueue();
});

byId('reference-form').addEventListener('submit', async event => {
  event.preventDefault();
  const ready = referenceState.filter(item => item.status === 'ready');
  byId('reference-submit').disabled = true;
  for (const item of ready) {
    item.status = 'uploading';
    item.message = 'Uploading...';
    renderReferenceQueue();
    try {
      const data = await uploadWithProgress(item.file, '/api/references', progress => {
        item.progress = progress;
        renderReferenceQueue();
      });
      item.status = 'complete';
      item.progress = 100;
      item.message = data.duplicate ? 'Already in library' : `${data.passages} passages added`;
    } catch (error) {
      item.status = 'error';
      item.message = error.message;
    }
    renderReferenceQueue();
  }
  const completed = ready.filter(item => item.status === 'complete').length;
  byId('reference-status').textContent = completed ? `${completed} source file${completed === 1 ? '' : 's'} ready.` : 'No files were added.';
  await loadReferences();
});

byId('scan-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (!scanState || scanState.status !== 'ready') return;
  scanState.status = 'uploading';
  scanState.message = 'Uploading and analysing...';
  renderScanQueue();
  byId('scan-status').textContent = 'Comparing passages with the source library...';
  try {
    const data = await uploadWithProgress(scanState.file, '/api/scan', progress => {
      scanState.progress = progress;
      renderScanQueue();
    });
    scanState.status = 'complete';
    scanState.progress = 100;
    scanState.message = `Complete / ${data.matched_passages} matches`;
    renderScanQueue();
    renderResults(data);
    byId('scan-status').textContent = `Completed with the ${data.model_mode}.`;
  } catch (error) {
    scanState.status = 'error';
    scanState.message = error.message;
    renderScanQueue();
    byId('scan-status').textContent = error.message;
  }
});

function signalBar(label, value) {
  return `<span class="signal"><b>${label}</b><i style="--value:${percent(value)}"></i><em>${percent(value)}</em></span>`;
}

function resultSignals(match) {
  const signals = [
    ['Word', match.word_cosine_score],
    ['Character', match.character_jaccard_score],
    ['Lexical', match.lexical_score],
  ];
  if (Number.isFinite(match.semantic_score)) signals.push(['Semantic', match.semantic_score]);
  if (Number.isFinite(match.hybrid_score)) signals.push(['Hybrid', match.hybrid_score]);
  return signals.map(([label, value]) => signalBar(label, value)).join('');
}

function renderResults(data) {
  const results = byId('results-section');
  results.classList.remove('hidden');
  byId('overall-score').textContent = percent(data.overall_score);
  results.querySelector('.score-ring').style.setProperty('--score', percent(data.overall_score));
  byId('result-summary').textContent = `${data.matched_passages} of ${data.total_passages} reviewable passages produced a match.`;
  byId('warnings').innerHTML = data.warnings.map(text => `<p class="warning">${escapeHtml(text)}</p>`).join('');
  byId('matches').innerHTML = data.matches.length ? data.matches.map(match => `
    <article class="match">
      <div class="match-passages">
        <div class="passage"><label>Submitted passage</label><p>${escapeHtml(match.submitted)}</p></div>
        <div class="passage"><label>Source / ${escapeHtml(match.source_document)}</label><p>${escapeHtml(match.source)}</p></div>
      </div>
      <div class="match-meta">
        <span class="risk risk-${match.review_band}">${match.review_band.toUpperCase()} REVIEW RISK</span>
        <div class="signal-bars">
          ${resultSignals(match)}
        </div>
      </div>
    </article>`).join('') : '<div class="empty-results">No passage exceeded the current review threshold.</div>';
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

setupDropzone('reference-dropzone', 'reference-file', addReferenceFiles);
setupDropzone('scan-dropzone', 'scan-file', files => files[0] && setScanFile(files[0]));
loadHealth();
loadProgress();
loadReferences();
