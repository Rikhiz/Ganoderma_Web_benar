const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const previewRow = document.getElementById('previewRow');
const previewImg = document.getElementById('previewImg');
const resultSlot = document.getElementById('resultSlot');
const detections = document.getElementById('detections');
const detectionList = document.getElementById('detectionList');
const errorBanner = document.getElementById('errorBanner');
const actions = document.getElementById('actions');
const resetBtn = document.getElementById('resetBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) handleFile(fileInput.files[0]);
});

resetBtn.addEventListener('click', () => {
  fileInput.value = '';
  previewRow.hidden = true;
  detections.hidden = true;
  errorBanner.hidden = true;
  actions.hidden = true;
});

function handleFile(file) {
  errorBanner.hidden = true;
  detections.hidden = true;
  actions.hidden = true;

  const objectUrl = URL.createObjectURL(file);
  previewImg.src = objectUrl;
  previewRow.hidden = false;

  resultSlot.innerHTML = `
    <div class="scan-state">
      <svg viewBox="0 0 60 60" width="52" height="52" class="spinner">
        <circle cx="30" cy="30" r="14" fill="none" stroke="currentColor" stroke-width="2" opacity="0.25"/>
        <circle cx="30" cy="30" r="14" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="30 60" stroke-linecap="round"/>
        <circle cx="30" cy="30" r="22" fill="none" stroke="currentColor" stroke-width="1.4" opacity="0.15"/>
      </svg>
      <p>Menjalankan model…</p>
    </div>`;

  const formData = new FormData();
  formData.append('image', file);

  fetch('/predict', { method: 'POST', body: formData })
    .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
      if (!ok || data.error) {
        showError(data.error || 'Terjadi kesalahan tak terduga.');
        resultSlot.innerHTML = `<p style="color:var(--bark); font-size:0.85rem;">Tidak ada hasil</p>`;
        return;
      }
      resultSlot.innerHTML = `<img src="${data.result_image}" alt="Hasil deteksi">`;
      renderDetections(data.detections || []);
      actions.hidden = false;
    })
    .catch((err) => {
      showError('Tidak bisa terhubung ke server lokal. Pastikan app.py sedang berjalan.');
      resultSlot.innerHTML = `<p style="color:var(--bark); font-size:0.85rem;">Tidak ada hasil</p>`;
    });
}

function renderDetections(list) {
  detectionList.innerHTML = '';
  if (!list.length) {
    detectionList.innerHTML = '<li class="empty">Tidak ada objek terdeteksi pada citra ini.</li>';
  } else {
    list.forEach((d) => {
      const li = document.createElement('li');
      li.innerHTML = `<span class="det-label">${d.label}</span><span class="det-conf">${d.confidence}%</span>`;
      detectionList.appendChild(li);
    });
  }
  detections.hidden = false;
}

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
}

function checkModelStatus() {
  fetch('/model-status')
    .then((res) => res.json())
    .then((data) => {
      if (data.model_found) {
        statusDot.classList.add('ok');
        statusText.textContent = 'Model siap';
      } else {
        statusDot.classList.add('bad');
        statusText.textContent = 'best.pt tidak ditemukan';
      }
    })
    .catch(() => {
      statusDot.classList.add('bad');
      statusText.textContent = 'Server tidak terhubung';
    });
}

checkModelStatus();
