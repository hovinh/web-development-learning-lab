'use strict';

// A small array of numbers to sum up.
const data = [1, 2, 3, 4, 5];

// Running total, accumulated across the loop.
let sum = 0;

// Classic for loop: walk every index and add its value to the total.
for (let i = 0; i < data.length; i++) {
  sum += data[i];
}

// Print the result to the browser's dev tools console.
console.log(sum);
