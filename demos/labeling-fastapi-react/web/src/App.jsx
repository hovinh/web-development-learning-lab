import { useEffect, useState } from 'react';
import { getItems, login, submitLabel } from './api/client';
import LoginForm from './components/LoginForm';
import ItemQueue from './components/ItemQueue';
import LabelPanel from './components/LabelPanel';

// localStorage, not just React state - a page refresh would otherwise
// throw the reviewer back to the login form. Compare
// demos/labeling-django/, where the browser's session cookie already
// survives a refresh with no code written for it at all.
const TOKEN_STORAGE_KEY = 'labeling-demo-token';

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  const [loginError, setLoginError] = useState(null);

  const [items, setItems] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Load (or reload) the queue whenever we have a token - on first
  // login, and again after logging out and back in as someone else.
  useEffect(() => {
    if (!token) return;

    getItems(token)
      .then((fetchedItems) => {
        setItems(fetchedItems);
        setLoadError(null);
        // Land on the first not-yet-labeled item rather than always
        // item zero, so returning to an in-progress queue picks up
        // where the reviewer left off.
        const firstPending = fetchedItems.find((item) => item.my_label === null);
        setSelectedId((firstPending ?? fetchedItems[0])?.id ?? null);
      })
      .catch((error) => setLoadError(error.message));
  }, [token]);

  const handleLogin = async (username, password) => {
    setLoginError(null);
    try {
      const { access_token: accessToken } = await login(username, password);
      localStorage.setItem(TOKEN_STORAGE_KEY, accessToken);
      setToken(accessToken);
    } catch {
      // login()/request() only throws for a non-2xx response here - a
      // wrong username/password is api/main.py's 401, surfaced as one
      // generic message rather than distinguishing "no such user" from
      // "wrong password" (which would leak which usernames exist).
      setLoginError('Wrong username or password.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setItems([]);
    setSelectedId(null);
  };

  const handleLabel = async (data) => {
    setSubmitting(true);
    try {
      const savedLabel = await submitLabel(token, selectedId, data);

      // Update this item in place rather than refetching the whole
      // queue - the API call already confirmed the write succeeded, so
      // there's nothing a refetch would tell us that we don't already
      // know from its response.
      const updatedItems = items.map((item) =>
        item.id === selectedId ? { ...item, my_label: savedLabel } : item,
      );
      setItems(updatedItems);

      // Auto-advance to the next not-yet-labeled item - the "instant,
      // no reloads" flow LabelPanel's keyboard shortcuts are built for.
      const currentIndex = updatedItems.findIndex((item) => item.id === selectedId);
      const nextPending = updatedItems
        .slice(currentIndex + 1)
        .find((item) => item.my_label === null);
      if (nextPending) setSelectedId(nextPending.id);
    } catch (error) {
      setLoadError(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (!token) {
    return <LoginForm onLogin={handleLogin} error={loginError} />;
  }

  const selectedItem = items.find((item) => item.id === selectedId) ?? null;

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white shadow-sm px-6 py-3 flex items-center justify-between">
        <h1 className="font-bold">Labeling queue</h1>
        <button onClick={handleLogout} className="text-sm text-slate-500 hover:text-slate-800">
          Log out
        </button>
      </header>

      <main className="max-w-4xl mx-auto p-6 grid grid-cols-[minmax(0,1fr)_minmax(0,1.5fr)] gap-6">
        {loadError && <p className="col-span-2 text-red-600 text-sm">{loadError}</p>}

        <ItemQueue items={items} selectedId={selectedId} onSelect={setSelectedId} />

        {selectedItem ? (
          <LabelPanel item={selectedItem} onLabel={handleLabel} submitting={submitting} />
        ) : (
          <p className="text-slate-500">
            {items.length === 0 ? 'No items assigned to you.' : 'Select an item from the queue.'}
          </p>
        )}
      </main>
    </div>
  );
}
