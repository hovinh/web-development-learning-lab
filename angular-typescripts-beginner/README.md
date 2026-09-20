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

## Working with components

A component is a TypeScript class decorated with `@Component`, which
tells Angular how to wire the class to its template:

```ts
@Component({
  selector: 'app-product',            // the custom HTML tag: <app-product>
  templateUrl: './product.component.html',
  styleUrls: ['./product.component.css'],
  standalone: false,                  // declared in an NgModule instead
})
export class ProductComponent { ... }
```

- **Generate, don't hand-write:** `ng generate component <name>` (short:
  `ng g c <name>`) creates the `.ts`/`.html`/`.css`/`.spec.ts` files and
  adds the class to the `declarations` of the nearest `NgModule`. A
  component that isn't declared in some module (or, in standalone
  mode, imported by the component using it) produces an "unknown
  element" error.
- **Interpolation:** `{{ expression }}` renders a class property (or any
  simple expression) into the template as text.
- **Binding syntax cheat sheet** (see [`my-app/`](my-app/README.md) for
  all of these working together):

  | Syntax | Direction | Use |
  | --- | --- | --- |
  | `{{ x }}` | class → view | text interpolation |
  | `[prop]="x"` | class → view | property binding (`[src]`, `[title]`, `[disabled]`) |
  | `[class.name]="cond"` / `[style.color]="x"` | class → view | toggle a class / set one style |
  | `(event)="handler()"` | view → class | event binding (`(click)`, `(input)`) |
  | `[(ngModel)]="x"` | both | two-way binding ("banana in a box") |

- **Passing data between components:** a child receives data from its
  parent through an `@Input()` property, and tells the parent something
  happened through an `@Output()` `EventEmitter`. The parent binds them
  as `[input]="value"` and `(output)="handler($event)"`.
- **Styles are scoped:** by default (view encapsulation), a component's
  CSS only applies to that component's own template. Global styles go in
  `src/styles.css` or the `styles` array in `angular.json`.

## Conditional rendering

Structural directives add or remove elements from the DOM based on a
condition. They're prefixed with `*`, which is shorthand for wrapping
the element in an `<ng-template>`.

```html
<!-- *ngIf: element exists only while the condition is true -->
<p *ngIf="products.length === 0">No products yet.</p>

<!-- else branch points at a named template -->
<ul *ngIf="products.length > 0; else empty">...</ul>
<ng-template #empty><p>Nothing here.</p></ng-template>

<!-- *ngFor: repeat per item; trackBy avoids re-creating DOM on updates -->
<li *ngFor="let p of products; let i = index; trackBy: trackById">
  {{ i + 1 }}. {{ p.name }}
</li>

<!-- ngSwitch: pick one of several -->
<div [ngSwitch]="status">
  <span *ngSwitchCase="'ok'">All good</span>
  <span *ngSwitchCase="'error'">Failed</span>
  <span *ngSwitchDefault>Unknown</span>
</div>
```

- `*ngIf` **removes** the element from the DOM when false. To just hide
  it while keeping it in the DOM, use `[hidden]="cond"` or
  `[style.display]`.
- Only **one** structural directive per element. To combine `*ngIf` and
  `*ngFor`, wrap with `<ng-container>` — a grouping element that
  renders nothing itself.
- `[ngClass]` and `[ngStyle]` are attribute directives for toggling
  several classes/styles from one object expression.
- Angular 17+ also has built-in control flow (`@if`, `@for`, `@switch`)
  as a newer replacement for these directives. This book uses the
  `*ng...` forms, which are still fully supported.

## Pipes

A pipe transforms a value **for display only** in the template, leaving
the underlying data untouched: `{{ value | pipeName:arg1:arg2 }}`.
Pipes chain left to right.

- Built-in: `date` (`{{ d | date:'shortDate' }}`), `currency`,
  `number` (`'1.2-2'` = min 1 integer digit, 2 to 2 decimals),
  `percent`, `uppercase`/`lowercase`/`titlecase`, `slice`, `json`
  (handy for debugging), and `async` (see Observables below).
- **Custom pipe:** `ng generate pipe <name>` creates a class with
  `@Pipe({ name: 'summary' })` implementing
  `transform(value, ...args)`, which must be declared in a module like
  a component.
  ```ts
  @Pipe({ name: 'summary', standalone: false })
  export class SummaryPipe implements PipeTransform {
    transform(text: string, max = 50): string {
      return text.length > max ? text.slice(0, max) + '…' : text;
    }
  }
  ```
  ```html
  {{ product.description | summary:30 }}
  ```
- Pipes are *pure* by default: Angular re-runs them only when the input
  value's **reference** changes. Mutating an array or object in place
  won't re-trigger one; replace it with a new one instead.

## Content projection with `ng-content`

`<ng-content>` is a slot in a component's template where the parent's
own markup, written between the component's tags, gets inserted. It's
what lets you build reusable wrapper components (cards, panels, modals)
whose inner content varies per use.

```html
<!-- panel.component.html -->
<div class="panel">
  <h3 class="panel-title"><ng-content select="[panel-title]"></ng-content></h3>
  <div class="panel-body"><ng-content></ng-content></div>   <!-- default slot -->
</div>

<!-- used by a parent -->
<app-panel>
  <span panel-title>Shipping</span>
  <p>Arrives in 3 days.</p>            <!-- goes to the default slot -->
</app-panel>
```

- `select` takes a CSS selector (an attribute, tag name, or class) to
  route matching content to that slot. Unmatched content goes to the
  plain `<ng-content>`.
- The projected content belongs to the **parent**: it's bound against
  the parent's class and styled by the parent's CSS, not the panel's.

## Template-driven forms

The form's structure lives in the **template**; Angular infers the form
model from directives. Needs `FormsModule` in the module's `imports`.

```html
<form #f="ngForm" (ngSubmit)="save(f.value)">
  <input name="email" [(ngModel)]="user.email"
         required email #email="ngModel">
  <div *ngIf="email.invalid && email.touched">A valid email is required.</div>

  <button type="submit" [disabled]="f.invalid">Save</button>
</form>
```

- `ngModel` registers a control with the enclosing `ngForm`; the input
  **must have a `name`** attribute or Angular throws.
- `#f="ngForm"` / `#email="ngModel"` are template reference variables
  giving access to the form/control state.
- Validation uses plain HTML attributes (`required`, `minlength`,
  `pattern`, `email`).
- Each control tracks state as properties and CSS classes: `valid`/
  `invalid`, `touched`/`untouched`, `dirty`/`pristine` (e.g.
  `ng-invalid`, `ng-touched`), which you can style or bind to.
- Good for small, simple forms; validation logic scattered across the
  template gets hard to test or reuse as forms grow.

## Model-driven (reactive) forms

The form's structure is defined **in the component class** as explicit
objects, and the template just binds to them. Needs
`ReactiveFormsModule` in `imports` (not `FormsModule`).

```ts
form = this.fb.group({
  email: ['', [Validators.required, Validators.email]],
  address: this.fb.group({ city: [''], zip: ['', Validators.pattern(/^\d{5}$/)] }),
  tags: this.fb.array([]),                 // dynamic list of controls
});
constructor(private fb: FormBuilder) {}
```

```html
<form [formGroup]="form" (ngSubmit)="save()">
  <input formControlName="email">
  <div formGroupName="address"><input formControlName="city"></div>
  <div *ngIf="form.get('email')?.errors?.['required']">Required.</div>
  <button [disabled]="form.invalid">Save</button>
</form>
```

- Building blocks: `FormControl` (one value), `FormGroup` (named set of
  controls), `FormArray` (list). `FormBuilder` is shorthand for
  creating them.
- **Custom validators** are plain functions
  `(control: AbstractControl) => ValidationErrors | null`, added to the
  validators array, and are easy to unit test on their own.
- The form exposes `valueChanges` and `statusChanges` Observables, so
  you can react to input as it changes (e.g. debounced live search).
- `setValue()`/`patchValue()`/`reset()` update it programmatically.
- Preferred for larger forms, dynamic fields, and cross-field
  validation.

## Observables

An **Observable** (from the RxJS library that Angular builds on) is a
stream of values delivered over time. Nothing happens until something
`subscribe`s to it. Unlike a `Promise`, it can emit many values and can
be cancelled by unsubscribing.

```ts
this.http.get<Product[]>('/api/products').subscribe({
  next: (products) => (this.products = products),
  error: (err) => (this.error = err.message),
  complete: () => (this.loading = false),
});
```

- **Where they show up:** `HttpClient` calls (needs `HttpClientModule`
  in `imports`), router params, form `valueChanges`, and
  `EventEmitter`.
- **Operators** transform a stream via `.pipe(...)`: `map`, `filter`,
  `debounceTime`, `distinctUntilChanged`, `switchMap` (cancel the
  previous inner request when a new value arrives), `catchError`.
- **`async` pipe:** `*ngFor="let p of products$ | async"` subscribes in
  the template and unsubscribes automatically on destroy — no manual
  `subscribe`, no leak. By convention, Observable variable names end in
  `$`.
- **Unsubscribe** from long-lived streams (`ngOnDestroy`, `takeUntil`,
  or the `async` pipe). `HttpClient` requests complete on their own, so
  they need no cleanup.
- A **service** is the usual home for the `HttpClient` call: it returns
  the Observable and components subscribe.

## Routing

The router swaps which component is shown in the page as the URL
changes, without a full page reload — this is what makes several
"pages" possible in a single-page app. `my-app` was generated with
`--routing=false`; to add it, run
`ng generate module app-routing --flat --module=app`.

```ts
const routes: Routes = [
  { path: '', component: ProductComponent },
  { path: 'products/:id', component: ProductDetailComponent },
  { path: 'admin', component: AdminComponent, canActivate: [authGuard] },
  { path: '**', component: NotFoundComponent },   // wildcard: keep last
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
```

```html
<nav>
  <a routerLink="/" routerLinkActive="active">Home</a>
  <a [routerLink]="['/products', product.id]">Details</a>
</nav>
<router-outlet></router-outlet>   <!-- the matched component renders here -->
```

- Routes are matched **top to bottom, first match wins**, so specific
  paths go before the `**` wildcard.
- `RouterModule.forRoot()` is used once, in the root; feature modules
  use `forChild()`.
- Use `routerLink` rather than `href` — a plain `href` triggers a full
  page reload and throws away app state.
- **Reading route parameters:** inject `ActivatedRoute`; `paramMap` is an
  Observable (so it updates if only the param changes), while
  `snapshot.paramMap` is a one-time read.
- **Navigating from code:** inject `Router` and call
  `this.router.navigate(['/products', id])`.
- **Guards** (`canActivate`, `canDeactivate`) run before entering or
  leaving a route and can block navigation, e.g. for login checks or
  unsaved form changes.
- **Lazy loading:** `loadChildren: () => import('./admin/admin.module')
  .then(m => m.AdminModule)` downloads a feature module's code only
  when its route is first visited.

## Structuring large apps with modules

One giant `AppModule` declaring every component stops scaling quickly.
The fix is to split the app into **feature modules**, each owning one
area of functionality, plus a couple of special-purpose ones.

```bash
ng generate module products --routing     # creates ProductsModule + ProductsRoutingModule
ng generate component products/product-list
```

Typical module roles:

| Module | Contains | Imported by |
| --- | --- | --- |
| **Root** (`AppModule`) | `AppComponent`, bootstraps the app, `RouterModule.forRoot()` | — |
| **Feature** (`ProductsModule`, `AdminModule`) | components/pipes/routes for one area | root (eagerly) or router (lazily) |
| **Shared** (`SharedModule`) | reusable dumb pieces: buttons, pipes, directives, plus re-exports of `CommonModule`/`FormsModule` | every feature module that needs them |
| **Core** (`CoreModule`) | app-wide singletons: navbar, auth service, interceptors | root only, once |

Key rules of the `NgModule` metadata:

- `declarations` — components/pipes/directives **owned** by this module.
  Each one may be declared in exactly one module.
- `imports` — other modules whose *exported* things this module's
  templates need. A module doesn't inherit its parent's imports: if
  `ProductsModule`'s templates use `*ngIf`, it imports `CommonModule`
  itself (only the root gets it via `BrowserModule`).
- `exports` — what a module makes available to modules that import it.
  This is how `SharedModule` shares things.
- `providers` — services registered for the module's injector. Prefer
  `@Injectable({ providedIn: 'root' })` on the service instead, which
  gives one app-wide singleton and lets unused services be tree-shaken.

Routing and lazy loading tie in here: each feature module has its own
routes registered with `RouterModule.forChild(routes)`, and the root
routes load it on demand:

```ts
// app-routing.module.ts
{ path: 'products', loadChildren: () => import('./products/products.module')
    .then(m => m.ProductsModule) },

// products-routing.module.ts  (paths are relative to /products)
const routes: Routes = [
  { path: '', component: ProductListComponent },
  { path: ':id', component: ProductDetailComponent },
];
```

A lazily loaded module is fetched as a separate bundle the first time
its route is visited, which keeps the initial download small. Don't
also import a lazy module in `AppModule`, or it gets bundled eagerly and
the laziness is lost.

Common folder layout: `src/app/{core,shared,products,admin}/`, each
feature folder holding its own module, routing module, components and
services.

> Modern Angular's standalone components (`standalone: true`) remove
> the need for most of this module plumbing. This book teaches the
> `NgModule` way, which is still what many existing codebases use.

## Firebase: setup

[**Firebase**](https://firebase.google.com/) is Google's backend-as-a-
service: hosted database (Firestore), authentication, file storage and
hosting, all reachable straight from the browser with no server of your
own to write. It slots into the "server is only for data and
auth" idea from the SPA overview above.

1. In the [Firebase console](https://console.firebase.google.com/),
   create a project, then add a **Web app** to it. The console shows a
   `firebaseConfig` object (`apiKey`, `authDomain`, `projectId`, ...).
2. Install the Angular bindings, [AngularFire](https://github.com/angular/angularfire):
   ```bash
   ng add @angular/fire
   ```
   (or `npm install firebase @angular/fire`).
3. Put the config in `src/environments/environment.ts` (generate the
   file with `ng generate environments` if the project doesn't have it
   yet):
   ```ts
   export const environment = {
     production: false,
     firebase: { apiKey: '...', authDomain: '...', projectId: '...', appId: '...' },
   };
   ```
4. Register Firebase in `AppModule`'s `providers` (AngularFire's
   modular API):
   ```ts
   providers: [
     provideFirebaseApp(() => initializeApp(environment.firebase)),
     provideFirestore(() => getFirestore()),
     provideAuth(() => getAuth()),
   ],
   ```
   Older tutorials, including possibly this book, use the *compat* API
   instead: `AngularFireModule.initializeApp(environment.firebase)`,
   `AngularFirestoreModule` and `AngularFireAuthModule` from
   `@angular/fire/compat/...`. It still works, and the concepts below
   are the same; only the call syntax differs.

> The Firebase web `apiKey` is **not a secret** — it just identifies the
> project and is visible to anyone using the app. What actually
> protects your data is the **security rules** covered below, not
> hiding the config.

## CRUD with Firestore

**Cloud Firestore** is a NoSQL document database. Data is organised as
**collections** of **documents** (JSON-like objects, each with an id),
and a document can contain further sub-collections. There are no joins
or fixed schema; you shape documents around how the app reads them.

CRUD wrapped in a service (components shouldn't talk to Firebase
directly):

```ts
@Injectable({ providedIn: 'root' })
export class ProductService {
  private productsRef = collection(this.firestore, 'products');

  constructor(private firestore: Firestore) {}

  // READ (live): emits again every time the collection changes.
  // idField copies the document id into each object's `id` property.
  getProducts(): Observable<Product[]> {
    return collectionData(this.productsRef, { idField: 'id' }) as Observable<Product[]>;
  }

  // READ (one)
  getProduct(id: string): Observable<Product> {
    return docData(doc(this.firestore, `products/${id}`), { idField: 'id' }) as Observable<Product>;
  }

  // CREATE: Firestore generates the document id. Returns a Promise.
  addProduct(product: Omit<Product, 'id'>) {
    return addDoc(this.productsRef, product);
  }

  // UPDATE: updateDoc changes only the listed fields; setDoc replaces the doc.
  updateProduct(id: string, changes: Partial<Product>) {
    return updateDoc(doc(this.firestore, `products/${id}`), changes);
  }

  // DELETE
  deleteProduct(id: string) {
    return deleteDoc(doc(this.firestore, `products/${id}`));
  }
}
```

```html
<li *ngFor="let p of products$ | async">
  {{ p.name }}
  <button (click)="service.deleteProduct(p.id)">Delete</button>
</li>
```

- **Reads are Observables** (so the `async` pipe and RxJS operators
  from the Observables section apply). Because they're live listeners, a
  change made by anyone appears without refetching, and the UI updates
  by itself after your own writes too.
- **Writes return Promises**: `.then(...)`/`await` for success, `.catch`
  for errors such as permission denied.
- **Queries** are built with `query(ref, where('price', '<', 50),
  orderBy('name'), limit(10))` and passed to `collectionData`.
  Combining a range filter with a different `orderBy` field needs a
  composite index; Firestore's error message includes a link that
  creates it.
- Firestore doesn't accept `undefined` field values; omit the field or
  use `null`.

## Authentication in Firebase

Firebase Authentication handles sign-up, sign-in, sessions and tokens,
so you never store passwords yourself. Enable the sign-in methods you
want in the console under **Authentication → Sign-in method** (e.g.
Email/Password, Google).

```ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  // Emits the current User, or null when signed out. Fires on load
  // too, once Firebase has restored any saved session.
  user$ = user(this.auth);

  constructor(private auth: Auth, private router: Router) {}

  register(email: string, password: string) {
    return createUserWithEmailAndPassword(this.auth, email, password);
  }

  login(email: string, password: string) {
    return signInWithEmailAndPassword(this.auth, email, password);
  }

  loginWithGoogle() {
    return signInWithPopup(this.auth, new GoogleAuthProvider());
  }

  async logout() {
    await signOut(this.auth);
    this.router.navigate(['/login']);
  }
}
```

- Every call returns a Promise. Failures carry a `code` such as
  `auth/wrong-password`, `auth/email-already-in-use` or
  `auth/weak-password`, to map to friendly messages.
- Firebase persists the session in the browser (IndexedDB) and restores
  it on reload, so `user$` is the single source of truth for "who is
  logged in". Use it in templates:
  ```html
  <a *ngIf="(auth.user$ | async) === null" routerLink="/login">Log in</a>
  <button *ngIf="auth.user$ | async as user" (click)="auth.logout()">
    Log out {{ user.email }}
  </button>
  ```
- **Route guard:** protect pages by checking `user$` before activating
  the route:
  ```ts
  export const authGuard: CanActivateFn = () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    return auth.user$.pipe(
      take(1),                                   // read once, then complete
      map(user => user ? true : router.createUrlTree(['/login'])),
    );
  };
  ```
  Used as `{ path: 'admin', component: AdminComponent, canActivate: [authGuard] }`.
  A guard only controls what the *UI* shows; real protection is in the
  security rules.
- The login/register forms are ordinary template-driven or reactive
  forms (see above) calling these methods.

## Implementing for multiple users

By default a Firestore collection is shared: every user sees every
document. To make each user's data private, tie documents to the
signed-in user's **uid** (the unique id in `user.uid`) and enforce it
on the server.

**1. Store the owner on each document**

```ts
addProduct(product: Omit<Product, 'id' | 'ownerId'>) {
  const uid = this.auth.currentUser?.uid;
  if (!uid) throw new Error('Must be signed in');
  return addDoc(this.productsRef, { ...product, ownerId: uid });
}
```

**2. Query only the current user's documents**

```ts
getMyProducts(): Observable<Product[]> {
  return user(this.auth).pipe(                  // emits on every login/logout
    switchMap(user => user
      ? collectionData(query(this.productsRef, where('ownerId', '==', user.uid)),
                       { idField: 'id' })
      : of([])),                                // signed out: no data
  ) as Observable<Product[]>;
}
```

`switchMap` re-runs the query whenever the user logs in or out and
cancels the previous listener. An alternative layout is per-user
sub-collections: `users/{uid}/products`, where the path itself scopes
the data.

**3. Enforce it with Firestore security rules** (Firebase console →
Firestore → Rules, or `firestore.rules`):

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /products/{productId} {
      // Anyone signed in can read; only the owner can change their doc.
      allow read: if request.auth != null;
      allow create: if request.auth != null
                    && request.resource.data.ownerId == request.auth.uid;
      allow update, delete: if request.auth != null
                            && resource.data.ownerId == request.auth.uid;
    }
  }
}
```

- **Rules are what actually secure the data.** Anyone can open dev
  tools and call Firestore directly, so filtering in the Angular query
  or hiding a button is only a convenience. To make documents private,
  tighten `read` to `resource.data.ownerId == request.auth.uid` and make
  the query filter on `ownerId` (a query the rules can't prove is
  restricted is rejected outright).
- Never leave a database in "test mode" (`allow read, write: if true`)
  beyond early experimenting; it expires after 30 days by default anyway.
- For per-user profile data (display name, preferences), a common
  pattern is a `users/{uid}` document created right after registration.
- Roles (e.g. admin) can be stored in that user document or as **custom
  claims**, and checked in both the route guard and the rules.
