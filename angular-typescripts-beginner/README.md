# angular-typescripts-beginner

Notes for working through *Beginning Angular with TypeScript* (Greg Lim).

Follows this repo's default convention: one subfolder per stage/chapter,
each self-contained. See the root [README.md](../README.md) for the
full list of stages across all books.

Stages so far:

- [`my-app/`](my-app/README.md) — first Angular CLI project: `ng new`
  through `ng serve --open`, a `ProductComponent` mock landing page,
  and a `RatingComponent` (Bootstrap) demoing property/class/style/
  event/two-way binding.

## What Angular actually is

Angular is a framework for building **single-page applications (SPAs)**:
instead of the server rendering a fresh HTML page for every navigation
(the model most of this repo's Flask/Django stages follow), the browser
loads one HTML shell up front, and Angular's JavaScript takes over from
there — handling navigation, re-rendering the DOM, and reacting to user
input entirely on the client.

The server is only involved for:

- the **initial page load** (serving that one HTML shell, plus the
  compiled JS/CSS bundles), and
- **data/business logic that genuinely has to happen server-side** —
  database reads/writes, auth, anything the client can't be trusted to
  do itself.

Once the page is loaded, navigating between views or updating what's on
screen doesn't require a new page fetch from the server at all — Angular
re-renders the relevant HTML in place from data already in the browser
(or fetched via an API call in the background), which is what makes SPAs
feel faster and more "app-like" than traditional server-rendered pages.

## TypeScript

Angular is written in, and expects app code to be written in,
[**TypeScript**](https://www.typescriptlang.org/) — a superset of
JavaScript that adds static types, checked at compile time before the
code is transpiled down to plain JavaScript for the browser to run.

## Architecture of an Angular app

- **Modules** — an app is split into separate modules, each grouping
  together components/services/directives that are closely related in
  functionality (e.g. a feature area of the app). Modules are the
  top-level unit of organization.
- **Components** — the basic building block of the UI. Each component
  pairs an HTML template with a component class holding the data and
  logic that controls what that template renders. Components nest
  inside one another, so a page is typically a tree of components.
- **Services** — a class with one well-defined job the app needs, but
  that isn't itself a piece of UI: logging, talking to a backend server
  to fetch/save data, validating user input, etc. Services are consumed
  by components rather than duplicating that logic inside them, which
  keeps components lightweight — a component's job is mainly to render
  its view (backed by application logic in a service) for a good user
  experience, not to own business logic itself.
- **Directives** — component templates are dynamic: when Angular renders
  one, it transforms the resulting DOM according to instructions given
  by directives. Directives are how you alter the appearance or behavior
  of DOM elements (e.g. conditionally showing an element, repeating an
  element per item in a list) without writing that DOM manipulation by
  hand.

## Setting up

### Node.js

[**Node.js**](https://nodejs.org/) is a JavaScript runtime built on
Chrome's V8 engine that lets JavaScript run outside a browser — on your
own machine, as a regular command-line program. Angular's tooling (the
dev server, the TypeScript-to-JavaScript build/bundle step, running
tests) is itself written in JavaScript, so it needs Node installed to
run at all — this is separate from, and in addition to, the repo-root
`package.json`/`http-server` setup already documented in the root
[README.md](../README.md#javascript-setup), which just serves already-
built static files rather than running any build tooling.

Installing Node also installs **npm** (Node Package Manager) alongside
it — the tool that downloads and manages JavaScript packages from the
[npm registry](https://www.npmjs.com/). npm is what we then use to
install everything else this book needs, starting with the Angular CLI
below.

To install Node on Windows, either:

- Download the current **LTS** installer from [nodejs.org](https://nodejs.org/)
  and run it (defaults are fine — it installs both `node` and `npm`), or
- Use **[nvm-windows](https://github.com/coreybutler/nvm-windows)** if it's
  already on your machine (as it was here) — it manages multiple Node
  versions side by side:
  ```bash
  nvm install 20.18.1   # or whatever the current LTS version is
  nvm use 20.18.1
  ```

Then verify the install in a fresh terminal:

```bash
node -v
npm -v
```

> This machine originally had Node v14.17.4 installed, which predates
> Node's active LTS line and is too old for recent Angular CLI versions
> (Angular 17+ requires Node 18.13+). It's now been upgraded to Node
> v20.18.1 LTS (npm 10.8.2) via nvm-windows.

> **Troubleshooting (nvm-windows specific):** right after switching Node
> versions, `npm -v` failed here with `Cannot find module '@npmcli/config'`.
> Recent npm releases bundle some of their own internals
> (`@npmcli/arborist`, `@npmcli/config`, and the various `libnpm*`
> packages) as symlinks into an internal `npm/workspaces/` folder, and
> creating symlinks on Windows needs a privilege nvm-windows's plain zip
> extraction doesn't have — so those links silently come out missing
> instead of erroring during install. The fix was recreating them as
> NTFS junctions (which *don't* need elevated privileges), pointing each
> missing `node_modules/<pkg>` at its real `workspaces/<pkg>` folder
> inside `%APPDATA%\nvm\v<version>\node_modules\npm\`, via PowerShell's
> `New-Item -ItemType Junction`. If a future `nvm install`/`nvm use`
> reproduces this error, that's the same fix.

### Angular CLI

The [**Angular CLI**](https://angular.dev/tools/cli) is a command-line
tool (itself an npm package) that scaffolds new Angular projects and
components, runs the local dev server, and builds the app for
production — it's how virtually all Angular development is actually
done, rather than wiring up the build tooling by hand.

Install it globally via npm so the `ng` command is available from any
folder:

```bash
npm install -g @angular/cli
```

Then verify it installed correctly:

```bash
ng version
```

> Installed here as Angular CLI v19.2.27, alongside Node v20.18.1 and
> npm 10.8.2.
