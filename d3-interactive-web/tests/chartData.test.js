// A minimal hand-rolled test runner instead of node:test or Jest: this
// repo's installed Node (v14) predates node:test (added in Node 18),
// and this stage has no npm dependencies to add Jest as one of - see
// the "Testing" section of this stage's README for the full reasoning.
// Run with: node d3-interactive-web/tests/chartData.test.js
import assert from "assert";
import { countByType, countByGeneration, topAbilities } from "../js/chartData.js";

const strict = assert.strict;
let failureCount = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`ok - ${name}`);
  } catch (error) {
    failureCount += 1;
    console.error(`FAIL - ${name}`);
    console.error(error);
  }
}

// A small synthetic dataset (not the real API response) - fast, and
// independent of whether data-serve is running, same reasoning as
// data-analysis/tests/test_charts.py's synthetic fixture.
const SAMPLE = [
  { name: "bulbasaur", generation: 1, types: ["Grass", "Poison"], abilities: ["Overgrow", "Chlorophyll"] },
  { name: "charmander", generation: 1, types: ["Fire"], abilities: ["Blaze", "Solar Power"] },
  { name: "squirtle", generation: 1, types: ["Water"], abilities: ["Torrent"] },
  { name: "pikachu", generation: 1, types: ["Electric"], abilities: ["Static", "Lightning Rod"] },
  { name: "chikorita", generation: 2, types: ["Grass"], abilities: ["Overgrow"] },
];

test("countByType counts a dual-typed Pokemon toward both types", () => {
  const counts = countByType(SAMPLE);
  strict.equal(counts.get("Grass"), 2);
  strict.equal(counts.get("Poison"), 1);
  strict.equal(counts.get("Fire"), 1);
  strict.equal(counts.has("Ice"), false);
});

test("countByGeneration counts Pokemon per generation", () => {
  const counts = countByGeneration(SAMPLE);
  strict.equal(counts.get(1), 4);
  strict.equal(counts.get(2), 1);
});

test("topAbilities returns the most common abilities first, capped at topN", () => {
  const top = topAbilities(SAMPLE, 2);
  strict.equal(top.length, 2);
  strict.equal(top[0][0], "Overgrow");
  strict.equal(top[0][1], 2);
});

test("topAbilities counts a multi-ability Pokemon toward every one of its abilities", () => {
  const counts = new Map(topAbilities(SAMPLE, 10));
  strict.equal(counts.get("Chlorophyll"), 1);
  strict.equal(counts.get("Static"), 1);
  strict.equal(counts.get("Lightning Rod"), 1);
});

if (failureCount > 0) {
  console.error(`\n${failureCount} test(s) failed.`);
  process.exit(1);
} else {
  console.log("\nAll tests passed.");
}
