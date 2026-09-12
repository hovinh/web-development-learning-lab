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

## Product component (mock landing page)

Added a `ProductComponent` that lists a handful of hardcoded mock
products on the landing page — the first real look at Angular's
template syntax (property binding, `*ngFor`, a pipe) beyond the CLI's
default boilerplate.

```bash
ng generate component product
```

This scaffolds `src/app/product/` (`product.component.ts`/`.html`/`.css`/
`.spec.ts`) and automatically adds `ProductComponent` to `AppModule`'s
`declarations` — no manual wiring needed, since the workspace's
`angular.json` already pins new components to `standalone: false` (set
by the `--standalone=false` flag back in `ng new`), so the CLI knows to
declare it in a module rather than generate a standalone component.

- **`product.model.ts`** — a `Product` TypeScript `interface` (`id`,
  `name`, `description`, `price`, `imageUrl`). This is the first payoff
  of TypeScript over plain JavaScript in this book: every mock product
  object is checked against this shape at compile time.
- **`product.component.ts`** — a hardcoded `products: Product[]` array
  of 4 mock products. Deliberately hardcoded rather than fetched from a
  server — this stage is about the component's template mechanics, not
  about talking to a backend yet. A later stage adding a
  `ProductService` (Angular's dependency-injection pattern, see the book
  folder's [README](../README.md#architecture-of-an-angular-app)) would
  swap this array for an HTTP call without the template needing to
  change, since the template only cares that it gets a `Product[]`.
- **`product.component.html`** — `*ngFor="let product of products"`
  repeats one `<article class="product-card">` per product; `[src]`/
  `[alt]` property-bind the image to each product's fields, and
  `{{ product.price | currency }}` uses Angular's built-in `currency`
  pipe to format the raw number (e.g. `89.99` → `$89.99`).
- **`product.component.css`** — a simple flex-wrap card grid, scoped to
  just this component (Angular's default view encapsulation means
  these styles don't leak out to the rest of the page).
- **`app.component.html`** — replaced the CLI's large default welcome
  page with a minimal header plus `<app-product></app-product>`, so the
  landing page now actually renders the mock product list.

Mock product images are loaded from
[placehold.co](https://placehold.co/) (a placeholder-image service) —
fine for mockup purposes, but not a real dependency to keep once the
book gets to actual product images/assets.

**Test files updated to match:** `ng generate component` doesn't touch
existing spec files, so `app.component.spec.ts` and
`product.component.spec.ts` needed two manual fixes to keep `ng test`
passing:
- `app.component.spec.ts`'s `TestBed` module now also declares
  `ProductComponent` (since `AppComponent`'s template references
  `<app-product>`) and its expected `h1` text was updated to match the
  new header (no more "Hello, my-app").
- Both spec files' `TestBed` modules now `imports: [CommonModule]` —
  `ProductComponent`'s template uses `*ngFor`/`currency`, which come
  from `CommonModule`. The real app gets this for free via
  `AppModule`'s `imports: [BrowserModule]` (which re-exports
  `CommonModule`), but each standalone `TestBed` test module needs it
  spelled out explicitly.

Verified with `ng test --watch=false --browsers=ChromeHeadless` — all 4
tests pass — and confirmed the running `ng serve` dev server hot-reloads
these changes with no compile errors.

## Rating component (Bootstrap + Angular's binding syntax)

Added a `RatingComponent` — 5 clickable stars, embedded in every product
card — as a deliberate, small-surface-area demo of Angular's core
template binding syntax: **property binding**, **class binding**,
**style binding**, **event binding**, and **two-way binding**, all in
one place.

```bash
npm install bootstrap bootstrap-icons
ng generate component rating
```

- **Bootstrap + Bootstrap Icons** are added as plain npm packages (no
  Angular-specific wrapper library needed for CSS/icons alone) and
  registered globally in `angular.json`'s `styles` array:
  ```json
  "styles": [
    "node_modules/bootstrap/dist/css/bootstrap.min.css",
    "node_modules/bootstrap-icons/font/bootstrap-icons.css",
    "src/styles.css"
  ]
  ```
  Bootstrap Icons supplies the `bi-star`/`bi-star-fill` icon classes used
  for empty/filled stars; Bootstrap itself supplies small utility
  classes (`d-flex`, `fs-3`, `me-1`, `ms-2`, `text-muted`) used in the
  template instead of hand-rolling that layout CSS.
  > **Gotcha:** editing `angular.json`'s `styles`/`scripts` array does
  > *not* hot-reload into an already-running `ng serve` — the dev
  > server has to be restarted (stop it and run `ng serve --open`
  > again) to pick up newly-added global stylesheets.

- **`product.model.ts`** — `Product` gained a `rating: number` field
  (how many of 5 stars are filled), and each mock product in
  `product.component.ts` was given a starting rating (`4`, `5`, `3`,
  `0`) so the four cards start out visibly different.

- **`rating.component.ts`** — the two-way-bindable piece:
  ```ts
  @Input() rating = 0;
  @Output() ratingChange = new EventEmitter<number>();
  ```
  This `<name>`/`<name>Change` naming pair is exactly what Angular
  looks for to support the "banana in a box" `[(rating)]` syntax on a
  *custom* component — the same mechanism `[(ngModel)]` uses on native
  form controls, just implemented by hand here instead of relying on
  `FormsModule`. `stars = [1, 2, 3, 4, 5]` is looped over with `*ngFor`;
  clicking a star calls `onStarClick(star)`, which sets `this.rating`
  and emits it via `ratingChange`.

- **`rating.component.html`** — one `<i>` per star, with four of the
  five binding types on the *same element*:
  ```html
  <i
    *ngFor="let star of stars"
    class="bi fs-3 me-1"
    [class.bi-star-fill]="star <= rating"
    [class.bi-star]="star > rating"
    [style.color]="star <= rating ? '#ffc107' : '#adb5bd'"
    [title]="star + (star === 1 ? ' star' : ' stars')"
    (click)="onStarClick(star)"
  ></i>
  ```
  - **Property binding** — `[title]` sets the native `title` DOM
    property (the hover tooltip) from an expression.
  - **Class binding** — `[class.bi-star-fill]`/`[class.bi-star]` toggle
    those two Bootstrap Icons classes on/off based on whether this
    star's position is at or below the current rating.
  - **Style binding** — `[style.color]` sets the icon's color directly
    (gold when filled, gray otherwise), no CSS class needed for that
    part.
  - **Event binding** — `(click)` calls `onStarClick(star)` whenever a
    star is clicked.

- **The fifth binding, two-way, happens where `RatingComponent` is
  *used*** — inside `product.component.html`:
  ```html
  <app-rating [(rating)]="product.rating"></app-rating>
  ```
  `RatingComponent` reads its starting value from `product.rating` and,
  on every click, writes the new value straight back onto that same
  `product` object — Angular desugars `[(rating)]="product.rating"`
  into `[rating]="product.rating" (ratingChange)="product.rating = $event"`.
  Each product card ends up with its own independent, live-updating
  rating.

All existing spec files (`app.component.spec.ts`,
`product.component.spec.ts`) needed `RatingComponent` added to their
`TestBed` declarations too, for the same "unknown element" reason as
`ProductComponent` before it; `rating.component.spec.ts` needed
`imports: [CommonModule]` for its own `*ngFor`. Verified with
`ng test --watch=false --browsers=ChromeHeadless` (5/5 passing) and by
restarting `ng serve --open` to confirm Bootstrap's styles/icons and
the click-to-rate behavior actually render in the browser.
