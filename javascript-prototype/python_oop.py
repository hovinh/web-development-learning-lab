"""The same Animal/Dog example, written with Python's class-based OOP.

This is the comparison point for prototype.js and class-syntax.js in this
folder. Where a JS object looks up a method by walking a live, per-object
[[Prototype]] chain, a Python instance has a fixed reference to its `type`
(the class object). Attribute lookup checks the instance's own __dict__
first, then walks the class's Method Resolution Order (MRO) -- a tuple
computed once, when the class hierarchy is defined, via C3 linearization.
"""

from __future__ import annotations


class Animal:
    """Base class. Its methods live as attributes of the class object
    itself (Animal.speak), not on each instance."""

    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> None:
        print(f"{self.name} makes a sound.")


class Dog(Animal):
    """Subclass: overriding speak() here means Dog's own copy is found
    before Animal's when Python walks Dog.__mro__."""

    def speak(self) -> None:
        print(f"{self.name} barks.")


def run_class_demo() -> None:
    print("--- python_oop.py (class-based inheritance) ---")

    generic_animal = Animal("Some creature")
    rex = Dog("Rex")

    generic_animal.speak()  # Some creature makes a sound.
    rex.speak()  # Rex barks. (Dog.speak overrides Animal.speak)

    # Interesting parallel with JS: attribute lookup in Python is ALSO
    # resolved at call time, not baked in when the instance was created.
    # So attaching a method to Animal after rex already exists still works
    # for rex, the same way it did for JS's prototype chain in
    # prototype.js. Dynamic lookup isn't unique to JS.
    def describe(self: Animal) -> None:
        print(f"{self.name} is an animal.")

    Animal.describe = describe  # type: ignore[attr-defined]
    rex.describe()  # Rex is an animal. (found via Dog -> Animal in the MRO)

    # The real structural difference from JS shows up here: the MRO is a
    # fixed tuple resolved once from the class statement's inheritance list
    # (`class Dog(Animal)`), and it natively supports MULTIPLE inheritance
    # via C3 linearization. A JS object only ever has ONE [[Prototype]]
    # link -- there is no built-in equivalent, only workarounds like mixins.
    print("Dog.__mro__:", [cls.__name__ for cls in Dog.__mro__])


if __name__ == "__main__":
    run_class_demo()
