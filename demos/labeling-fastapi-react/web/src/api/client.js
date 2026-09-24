/**
 * All HTTP calls to the FastAPI backend, kept together in one module so
 * components stay about UI - same shape react-hooks/README.md's own
 * src/api/movies.js example prescribes (a BASE URL, a request() helper,
 * named exports per endpoint).
 */

// Read from an environment variable, not hard-coded, so the same built
// front end can point at a different API URL without a code change -
// see ../../.env.example. Vite only exposes env vars prefixed VITE_ to
// browser code. The fallback matches ../../README.md's default
// uvicorn command, so `npm install && npm run dev` works with no setup
// step beyond copying .env.example if the default ever needs to change.
const BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

/**
 * Shared fetch wrapper: builds the full URL, and turns a non-2xx
 * response into a thrown Error with the API's own error message
 * (FastAPI's HTTPException body is `{"detail": "..."}`) - fetch() only
 * rejects on a network failure, never on a 4xx/5xx status, so callers
 * would otherwise have to check response.ok themselves every time.
 * @param {string} path
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` };
}

/**
 * POST /auth/login - FastAPI's OAuth2PasswordRequestForm expects a
 * form-encoded body (username=...&password=...), not JSON, which is why
 * this one call builds its body differently from the rest below.
 * @param {string} username
 * @param {string} password
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
export const login = (username, password) =>
  request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username, password }),
  });

/** GET /items - the current reviewer's queue. */
export const getItems = (token) => request('/items', { headers: authHeaders(token) });

/** GET /items/{itemId} - 404s if it isn't assigned to this reviewer. */
export const getItem = (token, itemId) =>
  request(`/items/${itemId}`, { headers: authHeaders(token) });

/**
 * POST /items/{itemId}/label - create or update this reviewer's label.
 * @param {string} token
 * @param {number} itemId
 * @param {{decision: string, corrected_label?: string, note?: string}} data
 */
export const submitLabel = (token, itemId, data) =>
  request(`/items/${itemId}/label`, {
    method: 'POST',
    headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

/** GET /admin/labels - 403s unless the token belongs to an admin user. */
export const getAdminLabels = (token) =>
  request('/admin/labels', { headers: authHeaders(token) });
