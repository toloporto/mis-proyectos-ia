// web-client/js/app.js
// Lógica principal del frontend — Sistema Multiagente Médico

// ============================================================
// ESTADO DE LA APLICACIÓN
// ============================================================
const state = {
  consultando: false,
  ultimaConsulta: null,
};

// ============================================================
// REFERENCIAS AL DOM
// ============================================================
const $ = (id) => document.getElementById(id);

const dom = {
  form:          $('consultaForm'),
  sintomas:      $('sintomas'),
  nombre:        $('nombre'),
  edad:          $('edad'),
  btnConsultar:  $('btnConsultar'),
  loading:       $('loadingCard'),
  resultado:     $('resultadoSection'),
  error:         $('errorCard'),
  urgenciaBadge: $('urgenciaBadge'),
  triageBody:    $('triageBody'),
  diagnosticoBody: $('diagnosticoBody'),
  tratamientoBody: $('tratamientoBody'),
  resultMeta:    $('resultMeta'),
  historialList: $('historialList'),
  statTotal:     $('statTotal'),
  statTiempo:    $('statTiempo'),
  statusDot:     $('statusDot'),
  statusText:    $('statusText'),
};

// Pipeline steps
const pipelineSteps = [
  $('step-triage'),
  $('step-diagnostico'),
  $('step-tratamiento'),
];
const pipelineConns = [
  $('conn-1'),
  $('conn-2'),
];

// ============================================================
// PIPELINE ANIMADO
// ============================================================
function setPipelineIdle() {
  pipelineSteps.forEach(s => s && s.classList.remove('active', 'done'));
  pipelineConns.forEach(c => c && c.classList.remove('active', 'done'));
}

function setPipelineStep(stepIndex) {
  pipelineSteps.forEach((s, i) => {
    if (!s) return;
    s.classList.remove('active', 'done');
    if (i < stepIndex) s.classList.add('done');
    if (i === stepIndex) s.classList.add('active');
  });
  pipelineConns.forEach((c, i) => {
    if (!c) return;
    c.classList.remove('active', 'done');
    if (i < stepIndex) c.classList.add('done');
    if (i === stepIndex) c.classList.add('active');
  });
}

function setPipelineDone() {
  pipelineSteps.forEach(s => s && (s.classList.remove('active'), s.classList.add('done')));
  pipelineConns.forEach(c => c && (c.classList.remove('active'), c.classList.add('done')));
}

// ============================================================
// MENSAJES DE LOADING ROTATIVOS
// ============================================================
const mensajesLoading = [
  '🟡 Agente Triage clasificando urgencia...',
  '⚡ Diagnóstico y Tratamiento ejecutándose en paralelo...',
  '🔵 Analizando posibles diagnósticos...',
  '🟢 Elaborando recomendaciones de tratamiento...',
  '💾 Guardando consulta en base de datos...',
  '⏳ El modelo phi3 está procesando tu consulta...',
];

let loadingInterval = null;

function startLoadingAnimation() {
  let idx = 0;
  const el = $('loadingText');
  if (el) el.textContent = mensajesLoading[0];

  setPipelineStep(0);

  loadingInterval = setInterval(() => {
    idx = (idx + 1) % mensajesLoading.length;
    if (el) el.textContent = mensajesLoading[idx];

    // Animar pipeline según el mensaje
    if (idx <= 1) setPipelineStep(0);
    else if (idx <= 3) setPipelineStep(1);
    else setPipelineStep(2);
  }, 4000);
}

function stopLoadingAnimation() {
  if (loadingInterval) {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }
}

// ============================================================
// RENDERIZADO DE RESULTADOS
// ============================================================
function renderizarResultado(data) {
  const nivel = (data.nivel_urgencia || 'MODERADO').toLowerCase();

  // Badge de urgencia
  const iconos = { leve: '✅', moderado: '⚠️', grave: '🔴', emergencia: '🚨' };
  dom.urgenciaBadge.className = `urgencia-badge ${nivel}`;
  dom.urgenciaBadge.innerHTML = `${iconos[nivel] || '⚠️'} ${data.nivel_urgencia || 'MODERADO'}`;

  // Contenido de cada agente
  dom.triageBody.textContent     = data.triage     || 'No disponible';
  dom.diagnosticoBody.textContent = data.diagnostico || 'No disponible';
  dom.tratamientoBody.textContent = data.tratamiento || 'No disponible';

  // Meta (tiempo + caché + protocolo)
  const tiempoStr = data.from_cache
    ? '<span class="badge-cache">⚡ Desde caché</span>'
    : `⏱️ ${data.tiempo_procesamiento}s`;

  const protocoloStr = data.protocolo !== 'normal'
    ? `| Protocolo: <strong>${data.protocolo}</strong>`
    : '';

  dom.resultMeta.innerHTML = `${tiempoStr} | Modelo: ${data.modelo} ${protocoloStr}`;

  // Mostrar sección
  dom.resultado.classList.add('visible');
  setPipelineDone();

  state.ultimaConsulta = data;
}

// ============================================================
// MANEJO DE ERRORES
// ============================================================
function mostrarError(mensaje) {
  dom.error.textContent = `❌ ${mensaje}`;
  dom.error.classList.add('visible');
  setTimeout(() => dom.error.classList.remove('visible'), 6000);
}

function ocultarError() {
  dom.error.classList.remove('visible');
}

// ============================================================
// ENVÍO DEL FORMULARIO
// ============================================================
dom.form.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (state.consultando) return;

  const sintomas = dom.sintomas.value.trim();
  if (!sintomas || sintomas.length < 5) {
    mostrarError('Describe tus síntomas con al menos 5 caracteres.');
    return;
  }

  // Iniciar estado de carga
  state.consultando = true;
  ocultarError();
  dom.resultado.classList.remove('visible');
  dom.loading.classList.add('visible');
  dom.btnConsultar.disabled = true;

  startLoadingAnimation();

  try {
    const data = await ApiService.consultar(
      sintomas,
      dom.nombre.value.trim() || null,
      dom.edad.value || 0
    );

    renderizarResultado(data);
    await cargarHistorial();
    await cargarEstadisticas();

  } catch (err) {
    mostrarError(err.message || 'Error inesperado. Verifica que Ollama esté corriendo.');
    setPipelineIdle();
  } finally {
    stopLoadingAnimation();
    dom.loading.classList.remove('visible');
    dom.btnConsultar.disabled = false;
    state.consultando = false;
  }
});

// Ctrl+Enter para enviar
dom.sintomas.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'Enter') {
    dom.form.dispatchEvent(new Event('submit'));
  }
});

// ============================================================
// HISTORIAL
// ============================================================
async function cargarHistorial() {
  try {
    const data = await ApiService.obtenerHistorial(6);
    const consultas = data.consultas || [];

    if (!consultas.length) {
      dom.historialList.innerHTML = '<div class="historial-empty">Sin consultas registradas aún</div>';
      return;
    }

    dom.historialList.innerHTML = consultas.map((c) => {
      const nivel = (c.nivel_urgencia || 'moderado').toLowerCase();
      const fecha = c.created_at ? c.created_at.substring(0, 16).replace('T', ' ') : '';
      const sintomas = (c.sintomas || '').substring(0, 48) + (c.sintomas?.length > 48 ? '…' : '');

      return `
        <div class="historial-item" onclick="rellenarConsulta(${JSON.stringify(c.sintomas)})">
          <div class="historial-sintomas">${sintomas}</div>
          <div class="historial-meta">
            <span>${fecha}</span>
            <span class="historial-nivel ${nivel}">${c.nivel_urgencia || 'N/D'}</span>
          </div>
        </div>
      `;
    }).join('');

  } catch {
    dom.historialList.innerHTML = '<div class="historial-empty">Error cargando historial</div>';
  }
}

// Rellena el textarea con una consulta histórica
function rellenarConsulta(sintomas) {
  dom.sintomas.value = sintomas;
  dom.sintomas.focus();
  dom.sintomas.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ============================================================
// ESTADÍSTICAS
// ============================================================
async function cargarEstadisticas() {
  try {
    const stats = await ApiService.obtenerEstadisticas();
    if (dom.statTotal)  dom.statTotal.textContent  = stats.consultas_totales ?? '0';
    if (dom.statTiempo) dom.statTiempo.textContent = stats.tiempo_medio_segundos
      ? `${stats.tiempo_medio_segundos}s`
      : '—';
  } catch {
    // Silencioso — las stats son informativas
  }
}

// ============================================================
// HEALTH CHECK (indicador de estado)
// ============================================================
async function verificarSalud() {
  const health = await ApiService.checkHealth();
  if (!dom.statusDot || !dom.statusText) return;

  if (health && health.ollama === 'conectado') {
    dom.statusDot.style.background = 'var(--leve)';
    dom.statusDot.style.boxShadow  = '0 0 8px var(--leve)';
    dom.statusText.textContent = `${health.modelo_activo} • Listo`;
  } else {
    dom.statusDot.style.background = 'var(--grave)';
    dom.statusDot.style.boxShadow  = '0 0 8px var(--grave)';
    dom.statusText.textContent = 'Ollama desconectado';
  }
}

// ============================================================
// INICIALIZACIÓN
// ============================================================
(async function init() {
  await Promise.all([
    verificarSalud(),
    cargarHistorial(),
    cargarEstadisticas(),
  ]);
})();
