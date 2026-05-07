// web-client/js/api-service.js
// Servicio de comunicación con la API del backend

const API_BASE = window.location.origin;

const ApiService = {

  /**
   * Realiza una consulta médica multiagente
   */
  async consultar(sintomas, nombrePaciente = null, edad = 0) {
    const response = await fetch(`${API_BASE}/consultar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sintomas,
        nombre_paciente: nombrePaciente || null,
        edad: parseInt(edad) || 0,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Error ${response.status} del servidor`);
    }

    return response.json();
  },

  /**
   * Obtiene el historial de consultas recientes
   */
  async obtenerHistorial(limite = 8) {
    const response = await fetch(`${API_BASE}/historial?limite=${limite}`);
    if (!response.ok) throw new Error('No se pudo cargar el historial');
    return response.json();
  },

  /**
   * Obtiene las estadísticas del sistema
   */
  async obtenerEstadisticas() {
    const response = await fetch(`${API_BASE}/estadisticas`);
    if (!response.ok) throw new Error('No se pudo cargar estadísticas');
    return response.json();
  },

  /**
   * Verifica el estado de salud del sistema
   */
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(4000) });
      return response.ok ? response.json() : null;
    } catch {
      return null;
    }
  },
};
