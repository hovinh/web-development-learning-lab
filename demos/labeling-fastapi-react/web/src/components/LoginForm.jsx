import { useState } from 'react';

/**
 * Username/password form - the client-side half of the JWT login flow.
 * Compare demos/labeling-django/labeling/templates/registration/login.html,
 * which needed zero JS and zero client-side state at all: Django's
 * session cookie is set by the server and the browser just carries it
 * automatically on every request afterwards.
 *
 * @param {{ onLogin: (username: string, password: string) => Promise<void>, error: string | null }} props
 */
export default function LoginForm({ onLogin, error }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onLogin(username, password);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-lg shadow-sm p-6 w-full max-w-sm flex flex-col gap-3"
      >
        <h1 className="text-xl font-bold mb-2">Log in</h1>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <label className="text-sm font-medium">
          Username
          <input
            className="mt-1 w-full border rounded px-3 py-2"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoFocus
          />
        </label>

        <label className="text-sm font-medium">
          Password
          <input
            type="password"
            className="mt-1 w-full border rounded px-3 py-2"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>

        <button
          type="submit"
          disabled={submitting}
          className="mt-2 bg-blue-600 text-white rounded px-3 py-2 font-medium disabled:opacity-60"
        >
          {submitting ? 'Logging in...' : 'Log in'}
        </button>
      </form>
    </div>
  );
}
