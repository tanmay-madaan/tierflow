// Base URL configuration:
// 1. Check for custom Vite environment variable (VITE_API_BASE_URL)
// 2. In local development (DEV), default to local FastAPI backend (http://localhost:8000)
// 3. In production, default to deployed Render backend (https://tierflow-api.onrender.com)
const RAW_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tierflow-api.onrender.com');

export const BASE_URL = RAW_BASE_URL.replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(message, status = null, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  let res;
  try {
    res = await fetch(url, options);
  } catch (netErr) {
    console.error(`Network error connecting to ${url}:`, netErr);
    throw new ApiError(
      `Unable to reach backend at ${BASE_URL}. If the backend was sleeping on Render, please allow 30-50 seconds for cold start and try again.`,
      0
    );
  }

  if (!res.ok) {
    let message = `Server returned status ${res.status} (${res.statusText})`;
    let errData = null;
    try {
      errData = await res.json();
      if (errData?.detail) {
        message = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      } else if (errData?.error) {
        message = typeof errData.error === 'string' ? errData.error : (errData.error.message || JSON.stringify(errData.error));
      }
    } catch {
      try {
        const text = await res.text();
        if (text) message = text;
      } catch {}
    }
    throw new ApiError(message, res.status, errData);
  }

  return await res.json();
}

export const api = {
  async queryModel(query, demoMode = false, executionMode = null) {
    const payload = { query, demo_mode: demoMode };
    if (executionMode) {
      payload.execution_mode = executionMode;
    }
    return await request('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  },

  async routeQuery(query) {
    return await request('/route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
  },

  async getMetrics() {
    try {
      return await request('/metrics');
    } catch (err) {
      console.warn("getMetrics failed:", err.message);
      return null;
    }
  },

  async getExperiments(limit = 100) {
    try {
      return await request(`/experiments?limit=${limit}`);
    } catch (err) {
      console.warn("getExperiments failed:", err.message);
      return [];
    }
  },

  async getModelDistribution() {
    try {
      return await request('/model-distribution');
    } catch (err) {
      console.warn("getModelDistribution failed:", err.message);
      return null;
    }
  },

  async getClassifierMetrics() {
    try {
      return await request('/classifier-metrics');
    } catch (err) {
      console.warn("getClassifierMetrics failed:", err.message);
      return null;
    }
  },

  async getHealth() {
    try {
      return await request('/health');
    } catch (err) {
      console.warn("getHealth failed:", err.message);
      return null;
    }
  },

  async getLatestBenchmark() {
    try {
      return await request('/benchmark/latest');
    } catch (err) {
      console.warn("getLatestBenchmark failed:", err.message);
      return null;
    }
  },

  async getBenchmarkManifest() {
    try {
      return await request('/benchmark/manifest');
    } catch (err) {
      console.warn("getBenchmarkManifest failed:", err.message);
      return null;
    }
  },

  async runBenchmark(executionMode = "demo", limit = null) {
    return await request('/benchmark/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ execution_mode: executionMode, limit })
    });
  }
};
