// ==============================================================================
// Fake News Detector - Main Application Logic (Vanilla JS & API integrations)
// ==============================================================================

const API_BASE = '/api/v1';

// App state management
const state = {
  activePage: 'home',
  theme: 'dark',
  apiOnline: false,
  metrics: { accuracy: 0, precision: 0, recall: 0, f1_score: 0 },
  modelInfo: { model_name: 'None', vectorizer_type: 'N/A', max_features: 0, last_trained: 'Never' },
  history: [],
  historyLimit: 10,
  historyOffset: 0
};

// Elements cache
const els = {
  themeToggle: document.getElementById('themeToggle'),
  themeIcon: document.getElementById('themeIcon'),
  apiStatusDot: document.getElementById('apiStatusDot'),
  apiStatusText: document.getElementById('apiStatusText'),
  mainContent: document.getElementById('mainContent'),
  navButtons: document.querySelectorAll('[data-page]'),
  pageSections: document.querySelectorAll('.page-section'),
  
  // Home Stats
  statTotalRequests: document.getElementById('statTotalRequests'),
  statFakeRate: document.getElementById('statFakeRate'),
  statModelF1: document.getElementById('statModelF1'),
  statModelName: document.getElementById('statModelName'),
  modelInfoVec: document.getElementById('modelInfoVec'),
  modelInfoMax: document.getElementById('modelInfoMax'),
  modelInfoTrained: document.getElementById('modelInfoTrained'),
  
  // Predict Page
  predictForm: document.getElementById('predictForm'),
  predictText: document.getElementById('predictText'),
  predictBtn: document.getElementById('predictBtn'),
  predictSpinner: document.getElementById('predictSpinner'),
  predictBtnText: document.getElementById('predictBtnText'),
  predictResultCard: document.getElementById('predictResultCard'),
  resultInitialState: document.getElementById('resultInitialState'),
  resultOutputState: document.getElementById('resultOutputState'),
  resultLabel: document.getElementById('resultLabel'),
  resultConfidence: document.getElementById('resultConfidence'),
  resultProgressBar: document.getElementById('resultProgressBar'),
  resultSnippet: document.getElementById('resultSnippet'),
  
  // Upload Page
  uploadForm: document.getElementById('uploadForm'),
  fileInput: document.getElementById('fileInput'),
  dropzone: document.getElementById('dropzone'),
  selectedFileDetails: document.getElementById('selectedFileDetails'),
  fileNameDisplay: document.getElementById('fileNameDisplay'),
  fileSizeDisplay: document.getElementById('fileSizeDisplay'),
  clearFileBtn: document.getElementById('clearFileBtn'),
  uploadBtn: document.getElementById('uploadBtn'),
  uploadSpinner: document.getElementById('uploadSpinner'),
  uploadBtnText: document.getElementById('uploadBtnText'),
  uploadResultCard: document.getElementById('uploadResultCard'),
  uploadResultInitialState: document.getElementById('uploadResultInitialState'),
  uploadResultOutputState: document.getElementById('uploadResultOutputState'),
  uploadResultLabel: document.getElementById('uploadResultLabel'),
  uploadResultConfidence: document.getElementById('uploadResultConfidence'),
  uploadResultProgressBar: document.getElementById('uploadResultProgressBar'),
  uploadResultSnippet: document.getElementById('uploadResultSnippet'),
  
  // Metrics Page
  metricsAcc: document.getElementById('metricsAcc'),
  metricsPrec: document.getElementById('metricsPrec'),
  metricsRec: document.getElementById('metricsRec'),
  metricsF1: document.getElementById('metricsF1'),
  btnRetrain: document.getElementById('btnRetrain'),
  retrainSpinner: document.getElementById('retrainSpinner'),
  retrainBtnText: document.getElementById('retrainBtnText'),
  confusionMatrixImage: document.getElementById('confusionMatrixImage'),
  confusionMatrixFallback: document.getElementById('confusionMatrixFallback'),
  matTN: document.getElementById('matTN'),
  matFP: document.getElementById('matFP'),
  matFN: document.getElementById('matFN'),
  matTP: document.getElementById('matTP'),
  
  // History Page
  historyTableBody: document.getElementById('historyTableBody'),
  historyPaginationText: document.getElementById('historyPaginationText'),
  historyPrevBtn: document.getElementById('historyPrevBtn'),
  historyNextBtn: document.getElementById('historyNextBtn')
};

// Global chart variables
let distributionChart = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupNavigation();
  setupUploadDragDrop();
  setupEventHandlers();
  
  // Initial health check and API data loads
  checkApiHealth().then(() => {
    if (state.apiOnline) {
      loadModelInfo();
      loadModelMetrics();
      loadPredictionHistory();
    }
  });
  
  // Poll API health every 15 seconds
  setInterval(checkApiHealth, 15000);
});

// --- Theme Controls ---
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme);
}

function setTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute('data-bs-theme', theme);
  localStorage.setItem('theme', theme);
  
  if (theme === 'dark') {
    els.themeIcon.className = 'bi bi-sun-fill';
    els.themeToggle.className = 'btn btn-sm btn-outline-secondary';
  } else {
    els.themeIcon.className = 'bi bi-moon-fill';
    els.themeToggle.className = 'btn btn-sm btn-outline-dark';
  }
}

// --- Navigation Routing ---
function setupNavigation() {
  // Navigation sidebar buttons click listeners
  els.navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const page = btn.getAttribute('data-page');
      navigateTo(page);
    });
  });

  // Home Page quick nav links listeners
  document.querySelectorAll('[data-nav]').forEach(el => {
    el.addEventListener('click', () => {
      const page = el.getAttribute('data-nav');
      navigateTo(page);
    });
  });
}

function navigateTo(pageId) {
  state.activePage = pageId;
  
  // Update sidebar active classes
  els.navButtons.forEach(btn => {
    if (btn.getAttribute('data-page') === pageId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  
  // Toggle visible sections
  els.pageSections.forEach(section => {
    if (section.id === `page-${pageId}`) {
      section.classList.remove('d-none');
    } else {
      section.classList.add('d-none');
    }
  });

  // Perform dynamic page loading configurations
  if (pageId === 'home') {
    loadPredictionHistory();
    loadModelInfo();
  } else if (pageId === 'metrics') {
    loadModelMetrics();
    loadModelInfo();
  } else if (pageId === 'history') {
    loadPredictionHistory();
  }
}

// --- File Upload Drag & Drop UI ---
function setupUploadDragDrop() {
  const dropzone = els.dropzone;
  const fileInput = els.fileInput;
  
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    }, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    }, false);
  });
  
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  }, false);
  
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });
}

function handleFileSelected(file) {
  const allowed = ['txt', 'pdf', 'docx'];
  const ext = file.name.split('.').pop().toLowerCase();
  
  if (!allowed.includes(ext)) {
    alert(`File extension not allowed. Please upload a TXT, PDF, or DOCX document.`);
    clearFileSelection();
    return;
  }
  
  // Max size 5MB
  if (file.size > 5 * 1024 * 1024) {
    alert(`File exceeds size limit. Maximum allowed size is 5MB.`);
    clearFileSelection();
    return;
  }
  
  // Show file details UI
  els.fileNameDisplay.textContent = file.name;
  els.fileSizeDisplay.textContent = `${(file.size / 1024).toFixed(1)} KB`;
  els.selectedFileDetails.classList.remove('d-none');
  els.selectedFileDetails.classList.add('d-flex');
  els.dropzone.classList.add('d-none');
  els.uploadBtn.removeAttribute('disabled');
}

function clearFileSelection() {
  els.fileInput.value = '';
  els.selectedFileDetails.classList.add('d-none');
  els.selectedFileDetails.classList.remove('d-flex');
  els.dropzone.classList.remove('d-none');
  els.uploadBtn.setAttribute('disabled', 'true');
  
  // Reset result panel
  els.uploadResultInitialState.classList.remove('d-none');
  els.uploadResultOutputState.classList.add('d-none');
}

// --- API Integrations & Functions ---

async function checkApiHealth() {
  try {
    const response = await fetch('/health');
    const data = await response.json();
    
    if (response.ok) {
      state.apiOnline = true;
      els.apiStatusDot.className = 'status-indicator bg-success';
      els.apiStatusText.textContent = `API Online (${data.environment})`;
    } else {
      throw new Error('API reported degraded state.');
    }
  } catch (error) {
    state.apiOnline = false;
    els.apiStatusDot.className = 'status-indicator bg-danger';
    els.apiStatusText.textContent = 'API Offline';
  }
}

async function loadModelInfo() {
  try {
    const response = await fetch(`${API_BASE}/model-info`);
    if (!response.ok) throw new Error('Failed to load model details.');
    
    const info = await response.json();
    state.modelInfo = info;
    
    // Render stats
    els.statModelName.textContent = info.model_name;
    els.modelInfoVec.textContent = info.vectorizer_type;
    els.modelInfoMax.textContent = info.max_features;
    els.modelInfoTrained.textContent = info.last_trained;
  } catch (error) {
    console.error('Error fetching model-info:', error);
  }
}

async function loadModelMetrics() {
  try {
    const response = await fetch(`${API_BASE}/metrics`);
    if (!response.ok) {
      // Model might not be trained yet
      els.confusionMatrixFallback.classList.remove('d-none');
      els.confusionMatrixImage.classList.add('d-none');
      return;
    }
    
    const metrics = await response.json();
    state.metrics = metrics;
    
    // Update labels
    els.metricsAcc.textContent = `${(metrics.accuracy * 100).toFixed(1)}%`;
    els.metricsPrec.textContent = `${(metrics.precision * 100).toFixed(1)}%`;
    els.metricsRec.textContent = `${(metrics.recall * 100).toFixed(1)}%`;
    els.metricsF1.textContent = metrics.f1_score.toFixed(3);
    
    els.statModelF1.textContent = metrics.f1_score.toFixed(2);
    
    // Update numerical matrix
    if (metrics.confusion_matrix) {
      const cm = metrics.confusion_matrix;
      els.matTN.textContent = cm.tn;
      els.matFP.textContent = cm.fp;
      els.matFN.textContent = cm.fn;
      els.matTP.textContent = cm.tp;
      
      // Update image plot (reports directory is hosted by nginx/dev server or served static)
      // For local development check direct path or let it fetch static reports path if mounted
      els.confusionMatrixImage.src = `/reports/confusion_matrix.png?t=${Date.now()}`;
      els.confusionMatrixImage.onload = () => {
        els.confusionMatrixImage.classList.remove('opacity-0');
        els.confusionMatrixImage.classList.add('fade-in');
        els.confusionMatrixFallback.classList.add('d-none');
      };
      els.confusionMatrixImage.onerror = () => {
        els.confusionMatrixFallback.classList.remove('d-none');
        els.confusionMatrixImage.classList.add('d-none');
      };
    }
  } catch (error) {
    console.error('Error fetching model metrics:', error);
  }
}

async function loadPredictionHistory() {
  try {
    const url = `${API_BASE}/history?skip=${state.historyOffset}&limit=${state.historyLimit}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to load history logs.');
    
    const historyItems = await response.json();
    state.history = historyItems;
    
    renderHistoryTable();
    updatePaginationControls();
    
    // Draw home chart using the metrics distributions
    if (state.activePage === 'home') {
      renderDistributionChart(historyItems);
    }
  } catch (error) {
    console.error('Error loading prediction history:', error);
  }
}

function renderHistoryTable() {
  const container = els.historyTableBody;
  if (state.history.length === 0) {
    container.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No historical prediction runs logged.</td></tr>`;
    els.statTotalRequests.textContent = "0";
    els.statFakeRate.textContent = "0%";
    return;
  }
  
  let html = '';
  let fakeCount = 0;
  
  state.history.forEach(item => {
    const date = new Date(item.timestamp).toLocaleString();
    const isFake = item.predicted_label.toLowerCase().includes('fake');
    if (isFake) fakeCount++;
    
    const labelClass = isFake ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success';
    
    html += `
      <tr>
        <td><strong>#${item.id}</strong></td>
        <td><div class="text-truncate" style="max-width: 320px;" title="${item.text_snippet}">${item.text_snippet}</div></td>
        <td><span class="text-secondary">${item.file_name || 'Manual Text'}</span></td>
        <td><span class="badge ${labelClass}">${item.predicted_label}</span></td>
        <td><strong>${(item.confidence * 100).toFixed(1)}%</strong></td>
        <td><small class="text-muted">${date}</small></td>
      </tr>
    `;
  });
  
  container.innerHTML = html;
  
  // Update totals card
  els.statTotalRequests.textContent = state.history.length;
  const fakeRate = (fakeCount / state.history.length) * 100;
  els.statFakeRate.textContent = `${fakeRate.toFixed(0)}%`;
}

function updatePaginationControls() {
  // If we fetched the limit, there might be more
  const hasMore = state.history.length === state.historyLimit;
  
  els.historyPrevBtn.disabled = state.historyOffset === 0;
  els.historyNextBtn.disabled = !hasMore;
  
  const start = state.historyOffset + 1;
  const end = state.historyOffset + state.history.length;
  
  els.historyPaginationText.textContent = state.history.length > 0 
    ? `Showing logs ${start}-${end}` 
    : 'Showing logs 0-0';
}

function renderDistributionChart(history) {
  const canvas = document.getElementById('distributionChart');
  if (!canvas) return;
  
  let real = 0;
  let fake = 0;
  
  history.forEach(item => {
    if (item.predicted_label.toLowerCase().includes('fake')) {
      fake++;
    } else {
      real++;
    }
  });

  if (distributionChart) {
    distributionChart.destroy();
  }
  
  const ctx = canvas.getContext('2d');
  
  // Set chart styles based on active theme
  const textColor = state.theme === 'dark' ? '#94a3b8' : '#64748b';
  const gridColor = state.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
  
  distributionChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Real News Predictions', 'Fake News Predictions'],
      datasets: [{
        label: 'Prediction Counts',
        data: [real, fake],
        backgroundColor: [
          'rgba(16, 185, 129, 0.65)', // Success Green
          'rgba(239, 68, 68, 0.65)'   // Danger Red
        ],
        borderColor: [
          '#10b981',
          '#ef4444'
        ],
        borderWidth: 1.5,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: textColor,
            stepSize: 1
          },
          grid: {
            color: gridColor
          }
        },
        x: {
          ticks: {
            color: textColor
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// --- Setup Form Submission Handlers ---
function setupEventHandlers() {
  // Theme Toggle click handler
  els.themeToggle.addEventListener('click', () => {
    const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    
    // Re-draw distribution chart to reflect colors
    if (state.activePage === 'home' && state.history.length > 0) {
      renderDistributionChart(state.history);
    }
  });

  // Predict Text form handler
  els.predictForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const text = els.predictText.value.trim();
    if (text.length < 10) {
      alert("Please supply article body text (minimum 10 characters).");
      return;
    }
    
    // Loading State
    els.predictSpinner.classList.remove('d-none');
    els.predictBtn.setAttribute('disabled', 'true');
    els.predictBtnText.textContent = 'Analyzing Text...';
    
    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Prediction failed.');
      
      // Update UI Result
      renderPredictionResult(data, false);
    } catch (error) {
      alert(`Prediction Error: ${error.message}`);
    } finally {
      // Revert loading state
      els.predictSpinner.classList.add('d-none');
      els.predictBtn.removeAttribute('disabled');
      els.predictBtnText.innerHTML = '<i class="bi bi-shield-fill-check"></i> Analyze Article';
    }
  });

  // Upload Document file selector handlers
  els.clearFileBtn.addEventListener('click', clearFileSelection);
  
  // Upload Form submit handler
  els.uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = els.fileInput.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Loading State
    els.uploadSpinner.classList.remove('d-none');
    els.uploadBtn.setAttribute('disabled', 'true');
    els.uploadBtnText.textContent = 'Parsing & Classifying...';
    
    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Upload prediction failed.');
      
      // Update UI Result
      renderPredictionResult(data, true);
    } catch (error) {
      alert(`Document Analysis Error: ${error.message}`);
    } finally {
      // Revert loading state
      els.uploadSpinner.classList.add('d-none');
      els.uploadBtn.removeAttribute('disabled');
      els.uploadBtnText.innerHTML = '<i class="bi bi-cloud-arrow-up-fill"></i> Upload & Analyze';
    }
  });

  // Retrain Pipeline button click handler
  els.btnRetrain.addEventListener('click', async () => {
    els.retrainSpinner.classList.remove('d-none');
    els.btnRetrain.setAttribute('disabled', 'true');
    els.retrainBtnText.textContent = 'Retraining Pipeline...';
    
    try {
      const response = await fetch(`${API_BASE}/retrain`, { method: 'POST' });
      const data = await response.json();
      
      alert(data.message || 'Retraining triggered successfully.');
      
      // Poll model info every 5 seconds until it completes retraining
      const interval = setInterval(async () => {
        await loadModelInfo();
        await loadModelMetrics();
        if (state.modelInfo.status === 'Active') {
          clearInterval(interval);
          els.retrainSpinner.classList.add('d-none');
          els.btnRetrain.removeAttribute('disabled');
          els.retrainBtnText.innerHTML = '<i class="bi bi-arrow-repeat"></i> Retrain Model';
        }
      }, 5000);
      
    } catch (error) {
      alert(`Retrain trigger failed: ${error.message}`);
      els.retrainSpinner.classList.add('d-none');
      els.btnRetrain.removeAttribute('disabled');
      els.retrainBtnText.innerHTML = '<i class="bi bi-arrow-repeat"></i> Retrain Model';
    }
  });

  // History Pagination click handlers
  els.historyPrevBtn.addEventListener('click', () => {
    if (state.historyOffset >= state.historyLimit) {
      state.historyOffset -= state.historyLimit;
      loadPredictionHistory();
    }
  });

  els.historyNextBtn.addEventListener('click', () => {
    state.historyOffset += state.historyLimit;
    loadPredictionHistory();
  });
}

function renderPredictionResult(data, isUploadPage = false) {
  const isFake = data.label.toLowerCase().includes('fake');
  const badgeClass = isFake ? 'bg-danger' : 'bg-success';
  const confidencePercent = (data.confidence * 100).toFixed(1) + '%';
  
  if (!isUploadPage) {
    // Text Predict result update
    els.resultInitialState.classList.add('d-none');
    els.resultOutputState.classList.remove('d-none');
    
    els.resultLabel.textContent = data.label;
    els.resultLabel.className = `badge rounded-pill px-4 py-2 fs-5 ${badgeClass}`;
    
    els.resultConfidence.textContent = confidencePercent;
    els.resultProgressBar.style.width = confidencePercent;
    
    els.resultSnippet.textContent = `"${data.text_snippet}"`;
  } else {
    // File Upload result update
    els.uploadResultInitialState.classList.add('d-none');
    els.uploadResultOutputState.classList.remove('d-none');
    
    els.uploadResultLabel.textContent = data.label;
    els.uploadResultLabel.className = `badge rounded-pill px-4 py-2 fs-5 ${badgeClass}`;
    
    els.uploadResultConfidence.textContent = confidencePercent;
    els.uploadResultProgressBar.style.width = confidencePercent;
    
    els.uploadResultSnippet.textContent = `"${data.text_snippet}"`;
  }
}
