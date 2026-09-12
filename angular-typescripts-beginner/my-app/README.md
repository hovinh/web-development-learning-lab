# my-app

First Angular project for *Beginning Angular with TypeScript* (Greg
Lim) — created with the Angular CLI to confirm the toolchain (Node,
npm, `ng`) actually works end-to-end, and to see the default project
Angular CLI scaffolds.

## How it was created

```bash
cd angular-typescripts-beginner
ng new my-app --routing=false --style=css --standalone=false --ssr=false --skip-git
```

Flag choices, and why:

- `--standalone=false` — Angular CLI v19 defaults new projects to
  **standalone components** (no `NgModule`s at all), its current
  recommended approach. This book (like most beginner Angular material)
  teaches the classic `NgModule`-based architecture instead — the
  "Modules" concept described in the [book folder's
  README](../README.md#architecture-of-an-angular-app) — so this flag
  keeps the generated project in that shape (an `AppModule` that
  declares/bootstraps `AppComponent`), matching what the book actually
  walks through.
- `--routing=false` and `--ssr=false` — this first project has no
  navigation between views yet and doesn't need server-side rendering;
  both can be added later (e.g. via `ng generate module app-routing`)
  once the book gets to routing.
- `--style=css` — plain CSS stylesheets per component, no
  Sass/Less preprocessor needed for this stage.
- `--skip-git` — this workspace lives inside the
  `web-development-learning-lab` monorepo, which already has its own
  git repo at the root; `ng new` would otherwise initialize a *second*,
  nested git repo inside `my-app/`, which we don't want.

`ng new` also prompts interactively for these same choices if you don't
pass them as flags — passing them explicitly here just made the command
non-interactive (needed since Claude Code ran it) and left a record of
exactly what was chosen and why.

## Running it

```bash
cd angular-typescripts-beginner/my-app
ng serve --open
```

- `ng serve` starts Angular's local dev server (on top of webpack/esbuild)
  with live-reload: it rebuilds and refreshes the browser automatically
  whenever a source file changes.
- `--open` (`-o`) launches the app in your default browser once the
  first build finishes, instead of you having to open the URL by hand.
- The server listens on **http://localhost:4200/** by default. Stop it
  with Ctrl+C.

First build output looked like this:

```
Application bundle generation complete. [4.951 seconds]
Watch mode enabled. Watching for file changes...
  ➜  Local:   http://localhost:4200/
```

`npm start` (from `package.json`'s `scripts.start`) runs the same
`ng serve` command without `--open`, if you'd rather open the browser
yourself.

## What got generated

- `src/app/app.module.ts` — the root `NgModule`: declares
  `AppComponent` and bootstraps it to start the app. This is the file
  that would grow to `imports: [...]` further modules/components as the
  app grows (e.g. `AppRoutingModule` once routing is added).
- `src/app/app.component.ts`/`.html`/`.css` — the root component. Its
  template is what actually renders at `/` — the CLI's generated
  `app.component.html` is a large default "Hello, my-app" welcome page,
  meant to be replaced with the book's own content as it goes.
- `src/main.ts` — the entry point: bootstraps `AppModule` in the
  browser.
- `angular.json` — the workspace's build/serve configuration (what
  `ng build`/`ng serve` actually reads to know how to compile this
  project).
- `package.json` — lists Angular's own packages (`@angular/core`,
  `@angular/router`, etc.) as dependencies. Note `@angular/router` is
  present even with `--routing=false` — the CLI always includes it as a
  baseline dependency, it's just not wired up into `app.module.ts` yet.
