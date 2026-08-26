const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
const API_ROOT = API_BASE.replace(/\/api\/?$/, '');

// Optional admin token for edit/delete (set VITE_ADMIN_TOKEN when ADMIN_TOKEN
// is configured on the backend; both empty = open local dev mode).
function adminHeaders() {
  const token = import.meta.env.VITE_ADMIN_TOKEN || '';
  return token ? { 'X-Admin-Token': token } : {};
}

async function callApi(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    return { error: error.message || 'Unexpected API failure' };
  }
}

export const api = {
  getHealth: () => callApi(`${API_ROOT}/health`),
  processMeeting: (payload) =>
    callApi('/meetings/process', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getTasks: () => callApi('/tasks'),
  updateTaskStatus: (taskId, status) =>
    callApi(`/tasks/${taskId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  editTask: (taskId, fields) =>
    callApi(`/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(fields),
      headers: adminHeaders(),
    }),
  deleteTask: (taskId) =>
    callApi(`/tasks/${taskId}`, {
      method: 'DELETE',
      headers: adminHeaders(),
    }),
  accelerateDemoDelay: () =>
    callApi('/tasks/demo/accelerate', {
      method: 'POST',
    }),
  getLogs: () => callApi('/logs'),
  getAnalytics: () => callApi('/analytics'),
  runMonitoring: () =>
    callApi('/monitoring/run', {
      method: 'POST',
    }),
  runFullDemo: () =>
    callApi('/demo/run-script', {
      method: 'POST',
    }),
  resetDemoData: () =>
    callApi('/demo/reset', {
      method: 'POST',
    }),
};
