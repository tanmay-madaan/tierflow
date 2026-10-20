const BASE_URL = 'https://tierflow-api.onrender.com';

export const api = {
  async queryModel(query, demoMode = false, executionMode = null) {
    try {
      const payload = { query, demo_mode: demoMode };
      if (executionMode) {
        payload.execution_mode = executionMode;
      }
      const res = await fetch(`${BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("queryModel error:", err);
      return null;
    }
  },

  async routeQuery(query) {
    try {
      const res = await fetch(`${BASE_URL}/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("routeQuery error:", err);
      return null;
    }
  },

  async getMetrics() {
    try {
      const res = await fetch(`${BASE_URL}/metrics`);
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("getMetrics error:", err);
      return null;
    }
  },

  async getExperiments(limit = 100) {
    try {
      const res = await fetch(`${BASE_URL}/experiments?limit=${limit}`);
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("getExperiments error:", err);
      return [];
    }
  },

  async getModelDistribution() {
    try {
      const res = await fetch(`${BASE_URL}/model-distribution`);
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("getModelDistribution error:", err);
      return null;
    }
  },

  async getClassifierMetrics() {
    try {
      const res = await fetch(`${BASE_URL}/classifier-metrics`);
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("getClassifierMetrics error:", err);
      return null;
    }
  },

  async getHealth() {
    try {
      const res = await fetch(`${BASE_URL}/health`);
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("getHealth error:", err);
      return null;
    }
  },

  async getLatestBenchmark() {
    try {
      const res = await fetch(`${BASE_URL}/benchmark/latest`);
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("getLatestBenchmark error:", err);
      return null;
    }
  },

  async getBenchmarkManifest() {
    try {
      const res = await fetch(`${BASE_URL}/benchmark/manifest`);
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("getBenchmarkManifest error:", err);
      return null;
    }
  },

  async runBenchmark(executionMode = "demo", limit = null) {
    try {
      const res = await fetch(`${BASE_URL}/benchmark/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ execution_mode: executionMode, limit })
      });
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (err) {
      console.error("runBenchmark error:", err);
      return null;
    }
  }
};
