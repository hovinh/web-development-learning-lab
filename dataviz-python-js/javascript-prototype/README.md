# javascript-prototype

JavaScript's **prototypal inheritance**, and how it differs from Python's
**class-based** OOP model. Same `Animal` / `Dog` example implemented three
ways, so the mechanism can be compared directly rather than described in the
abstract.

## Files

- `prototype.js` — the example built by hand with constructor functions and
  `.prototype`, the classic (pre-ES6) way to wire up a prototype chain. This
  is where the mechanism is most visible.
- `class-syntax.js` — the *same* example written with ES6 `class`/`extends`,
  plus a few checks proving it compiles down to the exact same prototype
  chain as `prototype.js`. `class` is sugar, not a new mechanism.
- `index.js` — entry point; runs both JS demos.
- `python_oop.py` — the same example in Python, for contrast.

## The core idea

**JavaScript objects don't have a fixed "class" baked into them.** Every
object carries an internal link — its `[[Prototype]]` — to one other
object. When you access a property that isn't found on the object itself,
JS walks that link (and the next, and the next) until it finds the
property or runs off the end of the chain (`null`). This is the
**prototype chain**, and the lookup happens *at access time*, live, every
time — not once at creation.

`Animal.prototype.speak = ...` puts `speak` on one shared object that every
`Animal` instance delegates to. There's no copy of `speak` per instance,
and — as `prototype.js` demonstrates — adding a method to `Animal.prototype`
*after* instances already exist still makes it available to them, because
the chain is walked fresh on every call.

`class Dog extends Animal` (`class-syntax.js`) does not change any of
this. It's syntax sugar: `extends` is doing the same
`Dog.prototype = Object.create(Animal.prototype)` wiring that `prototype.js`
does explicitly. `typeof Dog === 'function'` proves a "class" is still just
a constructor function underneath.

**Python objects, by contrast, have a fixed `type`** — the class object —
assigned at creation and never reassigned. Attribute lookup checks the
instance's own `__dict__` first, then walks the class's **Method
Resolution Order (MRO)**: a tuple computed *once*, when the class hierarchy
is declared (`class Dog(Animal)`), using C3 linearization.

Interestingly, Python's lookup is *also* dynamic at call time in the same
way JS's is — `python_oop.py` shows that attaching a method to `Animal`
after `rex` already exists still works for `rex`, mirroring the JS
behavior. The "JS is dynamic, Python is static" framing is too simple; the
real structural differences are elsewhere:

| | JavaScript (prototype) | Python (class) |
|---|---|---|
| What an object is linked to | One other **object** (`[[Prototype]]`) | One **class**, via `type(obj)` |
| Where methods live | On a `.prototype` object, shared by delegation | As attributes of the class object |
| Chain shape | A single linked list of objects, reshapeable at runtime (`Object.setPrototypeOf`) | A precomputed tuple (`__mro__`), fixed once the class is defined |
| Multiple inheritance | Not built in — only one `[[Prototype]]` link per object; mixins are the workaround | First-class, via C3 linearization ordering all ancestor classes |
| `class` keyword | Sugar over constructor functions + `.prototype` (no new mechanism) | The actual mechanism — not sugar over anything more primitive |
| Instantiation | `new Fn()`: allocate an object, link its `[[Prototype]]` to `Fn.prototype`, run `Fn` with `this` bound to it | `Cls(...)`: `type.__call__` invokes `Cls.__new__` then `Cls.__init__` |

## Running the code

JavaScript (from this folder):

```bash
node index.js
```

Python (from the repo root, with `.venv` active):

```bash
python javascript-prototype/python_oop.py
```
