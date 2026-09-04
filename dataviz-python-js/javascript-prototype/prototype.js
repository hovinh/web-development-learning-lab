// --- Demonstrating JavaScript's PROTOTYPE-based inheritance ---
//
// In JS, an object doesn't have a fixed "class" blueprint baked into it.
// Every object carries an internal link (its [[Prototype]]) to another
// object. When you read a property that isn't found on the object itself,
// JS walks up that link -- and then the next one, and so on -- until it
// finds the property or runs out of chain. This is the PROTOTYPE CHAIN.
//
// Constructor functions + the `.prototype` property are the classic
// (pre-ES6) way to set that link up. This file uses that style deliberately
// so the mechanism is visible; class-syntax.js shows the same thing written
// with the newer `class` keyword.

// A constructor function: called with `new`, it creates a fresh object,
// sets that object's [[Prototype]] to Animal.prototype, and runs this
// function body with `this` bound to the new object.
function Animal(name) {
  this.name = name;
}

// Methods belong on Animal.prototype, not inside the constructor body.
// Every object created via `new Animal(...)` shares this exact same
// function object through its prototype link -- it is not copied per
// instance the way it would be if defined as `this.speak = ...` above.
Animal.prototype.speak = function () {
  console.log(`${this.name} makes a sound.`);
};

// Dog "inherits" from Animal by making Dog.prototype's own [[Prototype]]
// point at Animal.prototype. That builds the chain:
//   rex -> Dog.prototype -> Animal.prototype -> Object.prototype -> null
function Dog(name) {
  // Borrow Animal's constructor logic, running it with this Dog instance
  // as `this` -- the closest JS gets to calling a Python super().__init__().
  Animal.call(this, name);
}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

// A method found earlier in the chain shadows one found later. This is
// JS's version of overriding.
Dog.prototype.speak = function () {
  console.log(`${this.name} barks.`);
};

export function runPrototypeDemo() {
  console.log('--- prototype.js (constructor functions) ---');

  const genericAnimal = new Animal('Some creature');
  const rex = new Dog('Rex');

  genericAnimal.speak(); // Some creature makes a sound.
  rex.speak(); // Rex barks. (Dog.prototype.speak shadows Animal's)

  // Proof the chain is live, not a snapshot: adding a method to
  // Animal.prototype AFTER both objects already exist still makes it
  // reachable from rex, because lookup happens at CALL time, walking
  // whatever the chain looks like right now -- not at creation time.
  Animal.prototype.describe = function () {
    console.log(`${this.name} is an animal.`);
  };
  rex.describe(); // Rex is an animal. (found via the prototype chain)

  // The chain can be inspected directly:
  console.log(
    'Object.getPrototypeOf(rex) === Dog.prototype:',
    Object.getPrototypeOf(rex) === Dog.prototype
  );
  console.log(
    'Object.getPrototypeOf(Dog.prototype) === Animal.prototype:',
    Object.getPrototypeOf(Dog.prototype) === Animal.prototype
  );
}
