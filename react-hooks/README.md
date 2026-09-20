# react-hooks

Notes for working through *Beginning React with Hooks* (Greg Lim).

Follows this repo's default convention: one subfolder per stage/chapter,
each self-contained. See the root [README.md](../README.md) for the
full list of stages across all books.

Stages so far: none yet — this folder holds the book's concept notes
below; stage subfolders (each with its own `README.md`) get added as the
book's projects are built.

The book's scope, which the sections below follow in order:

1. Creating and using components
2. Bindings, props, state and events
3. Working with components
4. Conditional rendering
5. Building forms with hooks
6. Connecting to an API to persist data

Sections marked **(beyond the book)** are extra background for later,
not part of that list.

> Code samples are general React, not copied from the book, so names and
> project details will differ from it.

## What React actually is

[**React**](https://react.dev/) is a JavaScript **library** (not a full
framework like Angular) for building user interfaces out of small,
reusable pieces called **components**. It only cares about the *view*
layer: routing, HTTP calls and global state management come from
separate libraries you choose yourself (React Router, `fetch`/axios,
Context/Redux, ...).

Its core idea is **declarative UI**: you describe what the screen should
look like *for the current data*, and React works out the minimal DOM
changes needed whenever that data changes. You never hand-write
`document.getElementById(...).textContent = ...` again.

- **Virtual DOM:** React keeps a lightweight in-memory copy of the UI,
  diffs it against the previous render when state changes, and only
  touches the real DOM where something actually differs.
- **One-way data flow:** data goes down from parent to child through
  **props**; children tell parents something happened by calling a
  function the parent passed down.

Like Angular (see [`angular-typescripts-beginner/`](../angular-typescripts-beginner/README.md)),
a React app is normally a **single-page application**: one HTML shell,
with JavaScript re-rendering the page in the browser.

## Why Hooks

Older React had two kinds of component: **class components** (had state
and lifecycle methods, but needed `this`, constructors and binding) and
**function components** (simple, but stateless). **Hooks** (React 16.8)
let plain functions have state and side effects, so classes are no
longer needed for new code. The book teaches this modern, function-only
style.

Hooks are special functions whose names start with `use`. Two rules
(enforced by the `eslint-plugin-react-hooks` lint rules):

1. Only call hooks **at the top level** of a component — never inside
   loops, conditions or nested functions, because React tracks hooks by
   the *order* they're called in.
2. Only call hooks from **function components or other custom hooks**,
   not from regular JavaScript functions.

## Setting up

### Node.js

React's tooling (dev server, JSX compiler, bundler, test runner) runs on
[**Node.js**](https://nodejs.org/), the same prerequisite as the Angular
book. If `node -v` and `npm -v` already work from that setup, nothing
more is needed. See the [Angular README's Node section](../angular-typescripts-beginner/README.md#nodejs)
for the install steps and the nvm-windows troubleshooting note.

### Creating a project

The book likely uses **Create React App**:

```bash
npx create-react-app my-app
cd my-app
npm start          # dev server on http://localhost:3000 with hot reload
```

`npx` runs a package without installing it globally. Create React App is
now deprecated by the React team; **[Vite](https://vite.dev/)** is the
current lightweight replacement and gives the same result faster:

```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install
npm run dev        # dev server on http://localhost:5173
```

Either way the layout is similar: `src/index.js` (or `main.jsx`) mounts
the root `<App />` component into the `<div id="root">` of a single
`index.html`; everything else is components under `src/`.

Each React project keeps its own `package.json`/`node_modules` inside its
stage folder, per this repo's [JavaScript conventions](../docs/javascript.md).

## JSX

**JSX** is HTML-like syntax written inside JavaScript. It isn't valid
JavaScript on its own; a compiler (Babel) turns each tag into a
`React.createElement(...)` call.

```jsx
function Greeting() {
  const name = 'Ada';
  const items = ['one', 'two'];
  return (
    <div className="greeting">                 {/* className, not class */}
      <h1>Hello, {name}!</h1>                  {/* {} embeds any JS expression */}
      <ul>
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}
```

- A component **returns one root element**. Wrap siblings in a
  `<div>` or an empty fragment `<>...</>` (renders no extra DOM node).
- Attributes are camelCase JavaScript names: `className`, `htmlFor`,
  `onClick`, `tabIndex`. Inline styles take an object:
  `style={{ color: 'red' }}`.
- Every tag must be closed, including `<img />` and `<input />`.
- Component names **start with a capital** (`<Movie />`); lowercase
  names are treated as plain HTML tags.
- Only *expressions* go inside `{}` — no `if`/`for` statements. Use
  ternaries, `&&`, and `.map()` instead (see below).

## Components and props

A component is a function that takes one `props` object and returns
JSX. Components nest, so a page is a tree of them.

```jsx
function Movie({ title, year }) {              // destructure props in the parameter
  return <p>{title} ({year})</p>;
}

function App() {
  return <Movie title="Alien" year={1979} />;  // strings in quotes, everything else in {}
}
```

- Props are **read-only**. A component must never modify what it is
  given; changing something means changing state in whoever owns it.
- `props.children` holds whatever is written between a component's tags,
  which makes wrapper components (cards, layouts) easy:
  `<Card><p>Inside</p></Card>`.
- **Default values** use destructuring defaults: `function Rating({ max = 5 })`.
- **One component per file**, named after the component, exported with
  `export default`, and imported where used.

## Bindings, props, state and events: how they fit together

React has no template binding syntax like Angular's `[prop]`/`(event)`/
`[(ngModel)]`. Everything is plain JavaScript inside `{}`, and the four
ideas work as one loop:

| Idea | React form | Direction |
| --- | --- | --- |
| Binding a value | `{title}`, `src={url}`, `className={cls}` | data → view |
| Props | `<Movie title="Alien" />` | parent → child |
| State | `const [x, setX] = useState(...)` | component's own memory |
| Events | `onClick={handler}` | view → code |
| "Two-way" binding | `value={x}` + `onChange={e => setX(...)}` | both, written out by hand |

The loop: state is rendered into the view → the user triggers an event
→ the handler calls a state setter → React re-renders with the new
state. A child that needs to change the parent's data is handed a
**function prop** by the parent (`onDelete={handleDelete}`) and calls it.

## Working with components

- **Split by responsibility.** When a component gets long or a piece of
  JSX repeats, extract it into its own component in its own file, e.g.
  `App` → `MovieList` → `Movie`. `App` owns data and handlers;
  small leaf components just render props.
- **Lift state up.** Keep state in the closest common parent of everything
  that needs it, pass values down as props and setters/handlers down as
  function props.
  ```jsx
  function MovieList() {
    const [movies, setMovies] = useState([]);
    const remove = (id) => setMovies(movies.filter((m) => m.id !== id));
    return movies.map((m) => <Movie key={m.id} movie={m} onDelete={remove} />);
  }

  function Movie({ movie, onDelete }) {          // stateless: renders props, reports events
    return <li>{movie.title} <button onClick={() => onDelete(movie.id)}>x</button></li>;
  }
  ```
- **Arrow wrapper for arguments.** `onClick={() => onDelete(movie.id)}`
  passes the id; `onClick={onDelete(movie.id)}` would call it during
  render.
- **Composition with `children`** for wrappers (`<Card>...</Card>`),
  rather than inheritance.
- **Folder layout:** `src/components/` for components (one file each,
  optionally with a same-named `.css`), `src/App.js` as the root.
- **Sharing state via a hook** (`useState` in the parent) is enough for a
  small app; don't reach for Context or Redux until props are being
  passed through many layers.

## Conditional rendering and lists

```jsx
{isLoading ? <Spinner /> : <MovieList movies={movies} />}   // either/or
{error && <p className="error">{error}</p>}                 // show only if truthy

<ul>
  {movies.map((m) => <Movie key={m.id} {...m} />)}          // one element per item
</ul>
```

- Every element in a mapped list needs a **`key`**: a stable, unique id
  (a database id, not the array index if items can be reordered or
  deleted). It lets React match old and new items during diffing.
- `{0 && <X />}` renders the number `0`, not nothing — compare
  explicitly (`count > 0 && ...`) when the value could be a number.
- **Early return** keeps JSX flat when a whole component depends on a
  condition: `if (loading) return <p>Loading…</p>;`.
- Store the outcome in a variable when there are more than two branches:
  ```jsx
  let content;
  if (status === 'loading') content = <Spinner />;
  else if (status === 'error') content = <ErrorMessage />;
  else content = <MovieList movies={movies} />;
  return <main>{content}</main>;
  ```
- Returning `null` from a component renders nothing. To toggle a
  component in place, keep a boolean in state and flip it in a handler:
  `const [open, setOpen] = useState(false);` … `{open && <Details />}`.
- Conditionally applying a class is also conditional rendering:
  `className={done ? 'movie done' : 'movie'}`.

## State with `useState`

**State** is data a component owns and remembers between renders.
Changing it tells React to re-render that component.

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);           // [current value, setter], initial value 0

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}
```

- Never assign to state directly (`count = 5`) — always call the setter,
  or React won't know to re-render.
- **State updates are asynchronous / batched:** the variable keeps its
  old value for the rest of the current render. When the next value
  depends on the previous one, pass a function: `setCount((c) => c + 1)`.
- **Objects and arrays must be replaced, not mutated:** React compares
  by reference, so mutating in place won't re-render.
  ```jsx
  setMovies([...movies, newMovie]);                       // add
  setMovies(movies.filter((m) => m.id !== id));           // remove
  setMovies(movies.map((m) => m.id === id ? { ...m, seen: true } : m));  // update one
  ```
- A component can call `useState` several times; prefer several small
  pieces of state over one giant object.
- **Lifting state up:** when two siblings need the same data, move the
  state into their closest common parent and pass it down as props
  (plus a setter function for children that need to change it).

## Handling events and forms

Event handlers are camelCase props taking a function: `onClick`,
`onChange`, `onSubmit`. Pass the function itself — `onClick={handle}` —
not a call to it (`onClick={handle()}` would run during render).

**Controlled inputs**: the input's value lives in state, so React is the
single source of truth.

```jsx
function SearchForm({ onSearch }) {
  const [term, setTerm] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();                    // stop the browser's full-page form submit
    onSearch(term);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={term} onChange={(e) => setTerm(e.target.value)} />
      <button type="submit">Search</button>
    </form>
  );
}
```

- Setting `value` without an `onChange` makes the input read-only.
- For several fields, keep one state object and update by field name:
  `setForm({ ...form, [e.target.name]: e.target.value })`.

### Building forms with hooks

A complete form uses `useState` for the values, and usually a second
piece of state for validation errors. Each input's `name` matches a key
in the state object so one `handleChange` serves every field.

```jsx
function MovieForm({ onSave }) {
  const empty = { title: '', year: '', watched: false };
  const [form, setForm] = useState(empty);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === 'checkbox' ? checked : value });
  };

  const validate = () => {
    const found = {};
    if (!form.title.trim()) found.title = 'Title is required';
    if (!/^\d{4}$/.test(form.year)) found.year = 'Enter a 4-digit year';
    return found;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length === 0) {      // no errors: submit and reset
      onSave(form);
      setForm(empty);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" value={form.title} onChange={handleChange} />
      {errors.title && <span className="error">{errors.title}</span>}

      <input name="year" value={form.year} onChange={handleChange} />
      {errors.year && <span className="error">{errors.year}</span>}

      <label>
        <input type="checkbox" name="watched"
               checked={form.watched} onChange={handleChange} /> Watched
      </label>
      <button type="submit">Save</button>
    </form>
  );
}
```

- Checkboxes bind `checked`, not `value`; `<select>` and `<textarea>` use
  `value` like a text input.
- Input values are always **strings**; convert with `Number(...)` before
  saving numbers.
- The same form can serve both *add* and *edit*: initialise state from an
  optional `movie` prop (`useState(movie ?? empty)`).
- A `useForm` custom hook (state + `handleChange` + `reset`) removes this
  boilerplate once several forms repeat it — see Custom hooks below.
- Alternatively, **uncontrolled** inputs read their value on submit via
  `useRef`; simpler for tiny forms, but you can't validate as the user
  types.

## Side effects with `useEffect`

Rendering must be a pure calculation from props and state. Anything else
— fetching data, timers, subscriptions, touching `document.title` — is a
**side effect** and belongs in `useEffect`, which runs *after* the
component has rendered.

```jsx
useEffect(() => {
  document.title = `${count} clicks`;          // runs after render
  return () => { /* optional cleanup */ };     // runs before the next effect and on unmount
}, [count]);                                    // dependency array
```

The **dependency array** controls when it re-runs:

| Second argument | Runs |
| --- | --- |
| omitted | after **every** render |
| `[]` | once, after the first render (on mount) |
| `[a, b]` | after the first render and whenever `a` or `b` changed |

- List **every** reactive value (props, state) the effect uses in the
  array; the lint rule `react-hooks/exhaustive-deps` warns when you miss
  one, which is the usual cause of stale-data bugs.
- **Cleanup** functions are how you clear timers
  (`return () => clearInterval(id)`), remove event listeners and close
  subscriptions, so nothing leaks after the component unmounts.
- In development, React's Strict Mode intentionally mounts, unmounts and
  re-mounts each component once to expose missing cleanup, so an effect
  can appear to run twice. That is expected and doesn't happen in
  production builds.

### Fetching data

```jsx
function MovieList() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;                        // avoid setting state after unmount/re-run
    async function load() {
      try {
        const res = await fetch('https://example.com/api/movies');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!ignore) setMovies(data);
      } catch (err) {
        if (!ignore) setError(err.message);
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    load();
    return () => { ignore = true; };
  }, []);

  if (loading) return <p>Loading…</p>;
  if (error) return <p>Error: {error}</p>;
  return <ul>{movies.map((m) => <li key={m.id}>{m.title}</li>)}</ul>;
}
```

- The effect callback itself **can't be `async`** (it must return either
  nothing or a cleanup function), so define an async function inside and
  call it.
- The three-state pattern (`loading` / `error` / `data`) is how almost
  every fetching component is shaped. Libraries such as TanStack Query
  package it up once you outgrow it.

## Connecting to an API to persist data

State lives in browser memory and disappears on refresh. To **persist**
data, the app talks to a server over HTTP (a REST API — like the Flask
one in [`rest-apis-flask/`](../rest-apis-flask/README.md)) that stores it
in a database. The usual CRUD mapping:

| Action | HTTP | Call |
| --- | --- | --- |
| Read all | `GET /movies` | `fetch(url)` |
| Create | `POST /movies` | `fetch(url, { method: 'POST', body })` |
| Update | `PUT`/`PATCH /movies/:id` | `fetch(url + '/' + id, { method: 'PUT', body })` |
| Delete | `DELETE /movies/:id` | `fetch(url + '/' + id, { method: 'DELETE' })` |

For practice without writing a backend, [`json-server`](https://github.com/typicode/json-server)
turns a `db.json` file into exactly this REST API
(`npx json-server --watch db.json --port 3001`).

Keep the HTTP calls together in one small module so components stay
about UI:

```js
// src/api/movies.js
const BASE = 'http://localhost:3001/movies';

async function request(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);      // fetch only rejects on network failure
  return res.status === 204 ? null : res.json();
}
const json = { 'Content-Type': 'application/json' };

export const getMovies   = ()         => request(BASE);
export const createMovie = (movie)    => request(BASE, { method: 'POST', headers: json, body: JSON.stringify(movie) });
export const updateMovie = (id, data) => request(`${BASE}/${id}`, { method: 'PUT', headers: json, body: JSON.stringify(data) });
export const deleteMovie = (id)       => request(`${BASE}/${id}`, { method: 'DELETE' });
```

Wire it to state: **load** in `useEffect`, and for each write, **call the
API first, then update state with what the server returned** so screen
and database stay in step.

```jsx
function MovieApp() {
  const [movies, setMovies] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => { getMovies().then(setMovies).catch((e) => setError(e.message)); }, []);

  const add = async (movie) => {
    try {
      const saved = await createMovie(movie);          // server assigns the id
      setMovies([...movies, saved]);
    } catch (e) { setError(e.message); }
  };

  const remove = async (id) => {
    try {
      await deleteMovie(id);
      setMovies(movies.filter((m) => m.id !== id));
    } catch (e) { setError(e.message); }
  };

  return (
    <>
      {error && <p className="error">{error}</p>}
      <MovieForm onSave={add} />
      <MovieList movies={movies} onDelete={remove} />
    </>
  );
}
```

- **Body must be a string:** `JSON.stringify(obj)` plus the
  `Content-Type: application/json` header, or the server can't parse it.
- **CORS:** a browser blocks calls to a different origin
  (`localhost:3000` → `localhost:3001`) unless the server sends CORS
  headers (`json-server` does; with Flask add `flask-cors`). A dev-server
  `"proxy"` in `package.json` (CRA) or `server.proxy` (Vite) avoids it.
- **Pessimistic vs optimistic updates:** the version above waits for the
  server before touching the UI (safe, slightly laggy). An optimistic
  update changes the UI immediately and rolls back on failure.
- **Loading and error state:** track them as in the fetching example
  above so the user isn't looking at a blank or stale screen.
- Put the base URL in an environment variable (`REACT_APP_API_URL` in
  CRA, `VITE_API_URL` in Vite), not hard-coded, so it can differ between
  development and deployment.
- The Angular book did the same job with Firebase (see
  [that README](../angular-typescripts-beginner/README.md#crud-with-firestore));
  here it's a plain REST API instead.

## Other built-in hooks (beyond the book)

- **`useRef`** — a mutable box (`ref.current`) that survives re-renders
  *without* triggering one. Used to grab a DOM element
  (`<input ref={inputRef} />`, then `inputRef.current.focus()`) or to
  hold a value like a timer id.
- **`useContext`** — reads a value provided by an ancestor's
  `<MyContext.Provider value={...}>`, so deeply nested components can
  share data (theme, logged-in user) without passing props through every
  level ("prop drilling").
- **`useReducer`** — like `useState`, but state changes go through a
  `reducer(state, action)` function. Better when the next state depends
  on several fields or there are many kinds of update; pairs well with
  `useContext` for app-wide state.
- **`useMemo` / `useCallback`** — cache a computed value / a function
  between renders so expensive work or child re-renders are skipped
  unless the dependencies change. Optimisations to reach for after
  measuring a problem, not by default.

## Custom hooks

A custom hook is just a function whose name starts with `use` and that
calls other hooks. It extracts reusable *stateful logic* (not UI) out of
components.

```jsx
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    fetch(url)
      .then((res) => res.json())
      .then((json) => { if (!ignore) setData(json); })
      .catch((err) => { if (!ignore) setError(err.message); })
      .finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };
  }, [url]);                                   // re-fetch when the url changes

  return { data, loading, error };
}

// any component: const { data, loading, error } = useFetch('/api/movies');
```

Each component that calls the hook gets its **own separate copy** of the
state; hooks share code, not data.

## Routing (beyond the book)

React itself has no router. [**React Router**](https://reactrouter.com/)
is the standard library: it swaps which component renders as the URL
changes, without a page reload.

```bash
npm install react-router-dom
```

```jsx
import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>                {/* Link, not <a>: no full page reload */}
        <Link to="/movies/42">A movie</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/movies/:id" element={<MovieDetail />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

function MovieDetail() {
  const { id } = useParams();                   // reads the :id URL segment
  ...
}
```

- `useNavigate()` navigates from code (e.g. after a form submit);
  `useParams()` reads URL parameters; `useSearchParams()` reads `?a=b`.
- Older tutorials use `<Switch>` and `component={...}` (React Router v5);
  v6+ uses `<Routes>` and `element={<X />}`.

## Styling (beyond the book)

- Plain CSS files imported into a component (`import './Movie.css'`) are
  **global** despite the import — class names can collide.
- **CSS Modules** (`Movie.module.css`, imported as `styles`, used as
  `className={styles.title}`) scope class names to the component.
- Libraries like **Bootstrap** / **React-Bootstrap** or Tailwind work too,
  as in the Angular book's `RatingComponent`.

## Angular vs React, for recall

Coming from [`angular-typescripts-beginner/`](../angular-typescripts-beginner/README.md):

| Concept | Angular | React |
| --- | --- | --- |
| Kind | full framework | UI library |
| Language | TypeScript (required) | JavaScript (TypeScript optional) |
| Template | separate HTML with `*ngIf`/`*ngFor` | JSX with `&&`/ternary/`.map()` |
| Data down | `@Input()` | props |
| Events up | `@Output()` `EventEmitter` | callback function passed as a prop |
| Local state | class properties | `useState` |
| Lifecycle / side effects | `ngOnInit`, `ngOnDestroy` | `useEffect` + cleanup |
| Shared logic | services + dependency injection | custom hooks, Context |
| Forms | template-driven / reactive forms | controlled inputs |
| Routing | `@angular/router` (built in) | React Router (separate package) |
