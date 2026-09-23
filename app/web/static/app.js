const MAX_FILE_BYTES = 10 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['txt', 'docx', 'pdf'];
const referenceState = [];
let scanState = null;
let currentScanId = null;
let composerBusy = false;
let toastTimer = null;

const byId = id => document.getElementById(id);
const percent = value => `${Math.round(Number(value || 0) * 100)}%`;

const panelDetails = {
  overview: ['Overview', 'Similarity overview'],
  evidence: ['Evidence', 'Passage evidence'],
  history: ['History', 'Scan history'],
  library: ['Source library', 'Source library'],
  project: ['Build progress', 'Project progress'],
};

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

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Date unavailable' : date.toLocaleString([], {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
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
  if (!ALLOWED_EXTENSIONS.includes(extensionOf(file.name))) return 'Use a TXT, DOCX, or PDF file.';
  if (file.size > MAX_FILE_BYTES) return 'The file is larger than 10 MB.';
  if (file.size === 0) return 'The file is empty.';
  return null;
}

function fileRow(item, removable = true) {
  const detail = item.message || (item.status === 'ready' ? `${formatBytes(item.file.size)} · Ready` : item.status);
  return `
    <article class="file-item ${item.status}" data-file-id="${item.id}">
      <span class="file-type">${escapeHtml(extensionOf(item.file.name).toUpperCase())}</span>
      <span class="file-copy"><strong>${escapeHtml(item.file.name)}</strong><small>${escapeHtml(detail)}</small></span>
      ${removable && item.status !== 'uploading' ? `<button class="file-remove" type="button" data-remove="${item.id}" aria-label="Remove ${escapeHtml(item.file.name)}">×</button>` : '<span></span>'}
      <i class="file-progress" style="width:${item.progress || 0}%"></i>
    </article>`;
}

function updateScanButton() {
  const hasText = byId('scan-text').value.trim().length > 0;
  const hasFile = scanState?.status === 'ready';
  byId('scan-submit').disabled = composerBusy || (!hasText && !hasFile);
}

function renderScanQueue() {
  byId('scan-queue').innerHTML = scanState ? fileRow(scanState) : '';
  updateScanButton();
}

function renderReferenceQueue() {
  byId('reference-queue').innerHTML = referenceState.map(item => fileRow(item)).join('');
  byId('reference-submit').disabled = !referenceState.some(item => item.status === 'ready');
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

function setupComposerDropzone() {
  const dropzone = byId('scan-dropzone');
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
  dropzone.addEventListener('drop', event => {
    const file = [...event.dataTransfer.files][0];
    if (file) setScanFile(file);
  });
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

function setGreeting() {
  const hour = new Date().getHours();
  byId('greeting').textContent = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
}

function closeSidebar() {
  byId('sidebar').classList.remove('open');
  byId('sidebar-scrim').classList.remove('show');
}

function openPanel(panelName, options = {}) {
  const contentName = panelName === 'evidence' ? 'overview' : panelName;
  document.querySelectorAll('[data-panel-content]').forEach(panel => {
    panel.classList.toggle('active', panel.dataset.panelContent === contentName);
  });
  document.querySelectorAll('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.panel === panelName));
  const [label, title] = panelDetails[panelName] || panelDetails.overview;
  byId('current-panel-name').textContent = label;
  byId('dashboard-title').textContent = title;
  closeSidebar();
  if (panelName === 'evidence') {
    requestAnimationFrame(() => byId('matches').scrollIntoView({ behavior: 'smooth', block: 'start' }));
  } else if (!options.preserveScroll) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function openDashboard(panelName = 'overview') {
  byId('welcome-view').classList.add('hidden');
  byId('dashboard-view').classList.remove('hidden');
  document.body.classList.add('dashboard-active');
  openPanel(panelName);
}

function showWelcome() {
  closeSidebar();
  byId('dashboard-view').classList.add('hidden');
  byId('welcome-view').classList.remove('hidden');
  document.body.classList.remove('dashboard-active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  setTimeout(() => byId('scan-text').focus(), 180);
}

async function loadHealth() {
  try {
    const data = await fetch('/api/health').then(readJson);
    const label = data.semantic_requested && data.semantic_available ? 'Hybrid model active' : 'Lexical model active';
    byId('model-status').textContent = label;
    byId('sidebar-model-status').textContent = label;
  } catch {
    byId('model-status').textContent = 'Server unavailable';
    byId('sidebar-model-status').textContent = 'Server unavailable';
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
  } catch {
    byId('updated').textContent = 'Tracker unavailable';
  }
}

function updateSourceCounters(count) {
  byId('corpus-count').textContent = count;
  byId('welcome-source-count').textContent = count;
  byId('composer-source-count').textContent = count;
  byId('nav-source-count').textContent = count;
  byId('source-ready-badge').classList.toggle('empty', count === 0);
}

async function loadReferences() {
  try {
    const data = await fetch('/api/references').then(readJson);
    updateSourceCounters(data.count);
    byId('corpus-list').innerHTML = data.documents.length
      ? data.documents.map(item => `<li data-type="${escapeHtml(item.extension.replace('.', '').toUpperCase())}"><span>${escapeHtml(item.name)}</span><small>${formatBytes(item.size_bytes)}</small></li>`).join('')
      : '<li class="empty-row">No sources yet. Add the documents you want Proofline to compare against.</li>';
  } catch {
    byId('corpus-list').innerHTML = '<li class="empty-row">Could not load the source library.</li>';
  }
}

async function loadHistory() {
  const history = byId('scan-history');
  try {
    const data = await fetch('/api/scans?limit=20').then(readJson);
    byId('clear-history').disabled = data.scans.length === 0;
    history.innerHTML = data.scans.length
      ? data.scans.map(item => `
        <article class="history-item">
          <span class="history-score">${percent(item.overall_score)}</span>
          <span class="history-copy"><strong>${escapeHtml(item.submitted_document)}</strong><small><time datetime="${escapeHtml(item.created_at)}">${escapeHtml(formatDate(item.created_at))}</time> · ${escapeHtml(item.model_mode)} · ${item.matched_passages} match${item.matched_passages === 1 ? '' : 'es'}</small></span>
          <span class="history-actions">
            <button class="history-view" type="button" data-scan-id="${escapeHtml(item.id)}">View evidence</button>
            <a href="${escapeHtml(item.report_url)}" download>Word report</a>
            <button class="history-delete" type="button" data-delete-scan="${escapeHtml(item.id)}" aria-label="Delete saved scan for ${escapeHtml(item.submitted_document)}">Delete</button>
          </span>
        </article>`).join('')
      : '<p class="history-empty">No saved scans yet. Your first completed analysis will appear here.</p>';
  } catch {
    byId('clear-history').disabled = true;
    history.innerHTML = '<p class="history-empty">Could not load saved scan history.</p>';
  }
}

function signalBar(label, value) {
  return `<span class="signal"><b>${label}</b><em>${percent(value)}</em><i style="--value:${percent(value)}"></i></span>`;
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

function passageFlags(match) {
  const flags = [];
  if (match.is_quotation) flags.push('Quotation detected');
  if (match.has_citation) flags.push('Citation detected');
  if (match.excluded_from_overall) flags.push('Excluded from overall score');
  return flags.length ? `<div class="match-flags">${flags.map(flag => `<span>${escapeHtml(flag)}</span>`).join('')}</div>` : '';
}

function scoreDescription(score) {
  if (score >= .8) return 'High-priority review';
  if (score >= .46) return 'Review recommended';
  if (score >= .2) return 'Some similar evidence';
  return 'Low similarity';
}

function renderResults(data) {
  currentScanId = data.scan_id || null;
  const score = Number(data.overall_score || 0);
  const reviewable = Number.isFinite(data.reviewable_passages) ? data.reviewable_passages : data.total_passages;
  const excluded = Number.isFinite(data.excluded_passages) ? data.excluded_passages : 0;
  const matchLabel = `${data.matched_passages} evidence match${data.matched_passages === 1 ? '' : 'es'}`;
  const excludedLabel = excluded ? ` · ${excluded} cited quotation${excluded === 1 ? '' : 's'} excluded` : '';

  byId('results-section').classList.remove('empty-results-state');
  byId('result-document-title').textContent = data.submitted_document || 'Similarity result';
  byId('result-summary').textContent = `${matchLabel} across ${data.total_passages} analysed passage${data.total_passages === 1 ? '' : 's'}${excludedLabel}.`;
  byId('overall-score').textContent = percent(score);
  byId('score-trend').textContent = scoreDescription(score);
  byId('score-bar').style.width = percent(score);
  byId('metric-matches').textContent = data.matched_passages;
  byId('metric-passages').textContent = reviewable;
  byId('metric-model').textContent = String(data.model_mode || 'Lexical').replace('weighted_', '').replace('_', ' ');
  byId('nav-match-count').textContent = data.matched_passages;
  byId('warnings').innerHTML = (data.warnings || []).map(text => `<p class="warning">${escapeHtml(text)}</p>`).join('');

  byId('matches').innerHTML = data.matches.length ? data.matches.map((match, index) => `
    <article class="match">
      <header class="match-head">
        <div class="match-source"><span class="source-file-icon">${String(index + 1).padStart(2, '0')}</span><strong>${escapeHtml(match.source_document)}</strong></div>
        <span class="risk risk-${escapeHtml(match.review_band)}">${match.review_band === 'excluded' ? 'EXCLUDED' : `${escapeHtml(match.review_band.toUpperCase())} PRIORITY`}</span>
      </header>
      <div class="match-passages">
        <div class="passage"><label>Submitted passage</label><p>${escapeHtml(match.submitted)}</p>${passageFlags(match)}</div>
        <div class="passage"><label>Matching source passage</label><p>${escapeHtml(match.source)}</p></div>
      </div>
      <div class="match-meta">${resultSignals(match)}</div>
    </article>`).join('') : '<div class="dashboard-empty"><span class="empty-spark">✓</span><h3>No passage crossed the review threshold</h3><p>The document still remains available in your local scan history.</p></div>';

  const reportLink = byId('report-download');
  if (data.report_url) {
    reportLink.href = data.report_url;
    reportLink.classList.remove('hidden');
  } else {
    reportLink.classList.add('hidden');
  }
  openDashboard('overview');
}

function setComposerBusy(busy) {
  composerBusy = busy;
  byId('scan-text').disabled = busy;
  byId('scan-attach').disabled = busy;
  const label = byId('scan-submit').querySelector('span');
  label.textContent = busy ? 'Analysing...' : 'Check similarity';
  updateScanButton();
}

function pastedTextFile(text) {
  const stamp = new Date().toISOString().replaceAll(':', '-').slice(0, 16);
  return new File([text], `pasted-text-${stamp}.txt`, { type: 'text/plain' });
}

byId('scan-text').addEventListener('input', updateScanButton);
byId('scan-attach').addEventListener('click', () => byId('scan-file').click());
byId('scan-file').addEventListener('change', event => {
  const file = event.target.files[0];
  if (file) setScanFile(file);
  event.target.value = '';
});

byId('scan-queue').addEventListener('click', event => {
  if (!event.target.closest('[data-remove]')) return;
  scanState = null;
  renderScanQueue();
});

byId('reference-queue').addEventListener('click', event => {
  const id = event.target.closest('[data-remove]')?.dataset.remove;
  if (!id) return;
  const index = referenceState.findIndex(item => item.id === id);
  if (index >= 0) referenceState.splice(index, 1);
  renderReferenceQueue();
});

byId('scan-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (composerBusy) return;
  const text = byId('scan-text').value.trim();
  const file = scanState?.status === 'ready' ? scanState.file : text ? pastedTextFile(text) : null;
  if (!file) return;

  setComposerBusy(true);
  if (scanState) {
    scanState.status = 'uploading';
    scanState.message = 'Uploading and analysing...';
    renderScanQueue();
  }
  byId('scan-status').textContent = 'Comparing passages with your source library...';

  try {
    const data = await uploadWithProgress(file, '/api/scan', progress => {
      if (!scanState) return;
      scanState.progress = progress;
      renderScanQueue();
    });
    if (scanState) {
      scanState.status = 'complete';
      scanState.progress = 100;
      scanState.message = `Complete · ${data.matched_passages} matches`;
    }
    byId('scan-status').textContent = '';
    renderResults(data);
    await loadHistory();
    byId('scan-text').value = '';
    scanState = null;
    renderScanQueue();
  } catch (error) {
    if (scanState) {
      scanState.status = 'error';
      scanState.message = error.message;
      renderScanQueue();
    }
    byId('scan-status').textContent = error.message;
    showToast(error.message);
  } finally {
    setComposerBusy(false);
  }
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

byId('scan-history').addEventListener('click', async event => {
  const deleteButton = event.target.closest('[data-delete-scan]');
  if (deleteButton) {
    const confirmed = window.confirm('Delete this saved scan record? This cannot be undone.');
    if (!confirmed) return;
    deleteButton.disabled = true;
    try {
      await fetch(`/api/scans/${encodeURIComponent(deleteButton.dataset.deleteScan)}`, { method: 'DELETE' }).then(readJson);
      if (currentScanId === deleteButton.dataset.deleteScan) currentScanId = null;
      await loadHistory();
      showToast('Saved scan deleted.');
    } catch (error) {
      showToast(error.message);
      deleteButton.disabled = false;
    }
    return;
  }

  const button = event.target.closest('[data-scan-id]');
  if (!button) return;
  button.disabled = true;
  try {
    const data = await fetch(`/api/scans/${encodeURIComponent(button.dataset.scanId)}`).then(readJson);
    renderResults(data);
  } catch (error) {
    showToast(error.message);
  } finally {
    button.disabled = false;
  }
});

byId('clear-history').addEventListener('click', async () => {
  const confirmed = window.confirm('Clear every saved scan record? This cannot be undone.');
  if (!confirmed) return;
  const button = byId('clear-history');
  button.disabled = true;
  try {
    const data = await fetch('/api/scans', { method: 'DELETE' }).then(readJson);
    currentScanId = null;
    await loadHistory();
    showToast(`${data.deleted} saved scan record${data.deleted === 1 ? '' : 's'} deleted.`);
  } catch (error) {
    showToast(error.message);
    button.disabled = false;
  }
});

document.querySelectorAll('[data-open-panel]').forEach(button => button.addEventListener('click', () => openDashboard(button.dataset.openPanel)));
document.querySelectorAll('[data-go-home]').forEach(element => element.addEventListener('click', event => {
  event.preventDefault();
  showWelcome();
}));
document.querySelectorAll('[data-panel]').forEach(button => button.addEventListener('click', () => openPanel(button.dataset.panel)));
byId('new-scan').addEventListener('click', showWelcome);
byId('sidebar-open').addEventListener('click', () => {
  byId('sidebar').classList.add('open');
  byId('sidebar-scrim').classList.add('show');
});
byId('sidebar-close').addEventListener('click', closeSidebar);
byId('sidebar-scrim').addEventListener('click', closeSidebar);

setupComposerDropzone();
setupDropzone('reference-dropzone', 'reference-file', addReferenceFiles);
setGreeting();
loadHealth();
loadProgress();
loadReferences();
loadHistory();
updateScanButton();

async function loadInitialView() {
  const parameters = new URLSearchParams(window.location.search);
  const scanId = parameters.get('scan');
  const requestedPanel = parameters.get('panel');
  if (scanId) {
    try {
      const data = await fetch(`/api/scans/${encodeURIComponent(scanId)}`).then(readJson);
      renderResults(data);
    } catch (error) {
      showToast(error.message);
      openDashboard('history');
    }
  } else if (requestedPanel && panelDetails[requestedPanel]) {
    openDashboard(requestedPanel);
  }
}

loadInitialView();
