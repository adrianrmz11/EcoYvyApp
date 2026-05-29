/* ── State ──────────────────────────────────────────────────────────────────── */
let totalPoints  = 0;
let totalCO2     = 0;
let totalReports = 0;
const LEVELS = [
  [0,    "EcoPrincipiante"],
  [200,  "EcoAprendiz"],
  [600,  "EcoActivista"],
  [1500, "EcoHéroe"],
  [3000, "EcoLeyenda"],
];

/* ── DOM refs ───────────────────────────────────────────────────────────────── */
const uploadForm     = document.getElementById("uploadForm");
const photoInput     = document.getElementById("photoInput");
const photoPreview   = document.getElementById("photoPreview");
const dropContent    = document.getElementById("dropContent");
const dropZone       = document.getElementById("dropZone");
const materialInput  = document.getElementById("materialInput");
const itemCount      = document.getElementById("itemCount");
const analyzeBtn     = document.getElementById("analyzeBtn");
const loadingOverlay = document.getElementById("loadingOverlay");
const emptyState     = document.getElementById("emptyState");
const resultCard     = document.getElementById("resultCard");
const badgesCard     = document.getElementById("badgesCard");
const historyCard    = document.getElementById("historyCard");
const historyBody    = document.getElementById("historyBody");

/* ── Helpers ─────────────────────────────────────────────────────────────────  */
const show = el => el.classList.remove("d-none");
const hide = el => el.classList.add("d-none");

/* ── Photo drag & drop ──────────────────────────────────────────────────────── */
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", ()  => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) loadPreview(file);
});
dropZone.addEventListener("click", e => {
  if (e.target.closest("button")) return;
  photoInput.click();
});
photoInput.addEventListener("change", () => {
  if (photoInput.files[0]) loadPreview(photoInput.files[0]);
});

function loadPreview(file) {
  const reader = new FileReader();
  reader.onload = e => {
    photoPreview.src = e.target.result;
    show(photoPreview);
    hide(dropContent);
    const dt = new DataTransfer();
    dt.items.add(file);
    photoInput.files = dt.files;
  };
  reader.readAsDataURL(file);
}

/* ── Material selector ──────────────────────────────────────────────────────── */
document.getElementById("materialGrid").addEventListener("click", e => {
  const btn = e.target.closest(".mat-btn");
  if (!btn) return;
  document.querySelectorAll(".mat-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  materialInput.value = btn.dataset.value;
});

/* ── Counter ────────────────────────────────────────────────────────────────── */
function adjustCount(delta) {
  itemCount.value = Math.max(1, Math.min(50, parseInt(itemCount.value) + delta));
}

/* ── Form submit → AJAX ─────────────────────────────────────────────────────── */
uploadForm.addEventListener("submit", async e => {
  e.preventDefault();

  if (!photoInput.files[0]) {
    alert("Por favor selecciona una imagen primero.");
    return;
  }

  show(loadingOverlay);
  analyzeBtn.disabled = true;

  try {
    const res = await fetch("/api/analyze", {
      method: "POST", body: new FormData(uploadForm),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || "Error del servidor");
    }
    displayResults(await res.json());
  } catch (err) {
    alert("Error al analizar: " + err.message);
  } finally {
    hide(loadingOverlay);
    analyzeBtn.disabled = false;
  }
});

/* ── Display results ────────────────────────────────────────────────────────── */
function displayResults(data) {
  hide(emptyState);
  show(resultCard);
  show(badgesCard);
  show(historyCard);

  document.getElementById("rIcon").textContent     = data.icon;
  document.getElementById("rMaterial").textContent = data.label;
  document.getElementById("rWeight").textContent   = data.weight_kg + " kg";
  document.getElementById("rCO2").textContent      = `${data.co2_saved_kg} kg (±${data.co2_margin} kg)`;
  document.getElementById("rTrees").textContent    = data.trees_saved;
  document.getElementById("rLocation").textContent = data.location;
  document.getElementById("rEquivalence").textContent = "🌍 CO₂ avoided: " + data.co2_saved_kg + " kg · Waste recovered: " + data.weight_kg + " kg";

  const pct = Math.round(data.confidence * 100);
  document.getElementById("rConfBadge").textContent = pct + "% confidence";
  document.getElementById("rConfBar").style.width   = pct + "%";
  document.getElementById("rConfLabel").textContent = `Confidence: ${pct}%`;

  animateCounter("rPoints", 0, data.ecopoints, 800);

  totalPoints  += data.ecopoints;
  totalCO2     += data.co2_saved_kg;
  totalReports += 1;
  updateStatsBar();
  addHistoryRow(data);
  checkBadges();

  resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/* ── Stats bar ──────────────────────────────────────────────────────────────── */
function updateStatsBar() {
  document.getElementById("totalPoints").textContent  = totalPoints.toLocaleString();
  document.getElementById("totalCO2").textContent     = totalCO2.toFixed(3);
  document.getElementById("totalReports").textContent = totalReports;

  let level = LEVELS[0][1];
  for (const [threshold, name] of LEVELS)
    if (totalPoints >= threshold) level = name;
  document.getElementById("userLevel").textContent = level;
}

/* ── History ────────────────────────────────────────────────────────────────── */
function addHistoryRow(data) {
  const row = historyBody.insertRow(0);
  row.innerHTML = `
    <td>${data.icon} <strong>${data.label}</strong></td>
    <td>${data.weight_kg} kg</td>
    <td>${data.co2_saved_kg} kg</td>
    <td><strong>${data.ecopoints}</strong></td>
    <td><span class="status-mrv">✅ MRV</span></td>
  `;
}

/* ── Badges ─────────────────────────────────────────────────────────────────── */
function checkBadges() {
  if (totalPoints  >= 1000) earn("badge1k");
  if (totalCO2     >= 5)    earn("badgeCO2");
  if (totalReports >= 5)    earn("badge5x");
}
function earn(id) {
  const el = document.getElementById(id);
  if (el && !el.classList.contains("earned")) el.classList.add("earned");
}

/* ── Reset ──────────────────────────────────────────────────────────────────── */
function resetForm() {
  uploadForm.reset();
  hide(photoPreview);
  photoPreview.src = "";
  show(dropContent);
  document.querySelectorAll(".mat-btn").forEach((b, i) =>
    b.classList.toggle("active", i === 0));
  materialInput.value = "plastic";
  hide(resultCard);
}

/* ── Share ──────────────────────────────────────────────────────────────────── */
function shareResult() {
  const text = `🌿 ¡Acabo de reciclar con #EcoYvy y gané ${document.getElementById("rPoints").textContent} EcoPoints!`;
  if (navigator.share) navigator.share({ title: "EcoYvy", text });
  else { navigator.clipboard?.writeText(text); alert("Logro copiado al portapapeles 📋"); }
}

/* ── Animated counter ───────────────────────────────────────────────────────── */
function animateCounter(id, from, to, duration) {
  const el = document.getElementById(id);
  const start = performance.now();
  (function step(now) {
    const p = Math.min((now - start) / duration, 1);
    el.textContent = Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3)));
    if (p < 1) requestAnimationFrame(step);
  })(start);
}
