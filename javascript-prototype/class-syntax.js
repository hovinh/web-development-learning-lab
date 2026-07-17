// --- The SAME Animal/Dog example, written with ES6 `class` syntax ---
//
// `class` is syntactic sugar: under the hood it still creates a constructor
// function with methods living on its `.prototype`, exactly like
// prototype.js. No new inheritance mechanism is introduced -- `extends`
// just automates the `Object.create(Parent.prototype)` wiring done by hand
// in prototype.js. The proof is at the bottom of runClassDemo().

class Animal {
  constructor(name) {
    this.name = name;
  }

  speak() {
    console.log(`${this.name} makes a sound.`);
  }
}

class Dog extends Animal {
  speak() {
    console.log(`${this.name} barks.`);
  }
}

export function runClassDemo() {
  console.log('--- class-syntax.js (ES6 class sugar) ---');

  const rex = new Dog('Rex');
  rex.speak(); // Rex barks.

  // typeof a class is 'function' -- classes ARE constructor functions.
  console.log('typeof Dog:', typeof Dog);

  // speak() ended up on Dog.prototype, same as when written by hand.
  console.log(
    "Dog.prototype has its own 'speak':",
    Object.prototype.hasOwnProperty.call(Dog.prototype, 'speak')
  );

  // `extends` wires up the exact same prototype chain as
  // `Dog.prototype = Object.create(Animal.prototype)` did in prototype.js.
  console.log(
    'Object.getPrototypeOf(Dog.prototype) === Animal.prototype:',
    Object.getPrototypeOf(Dog.prototype) === Animal.prototype
  );
}
