// Pure aggregation helpers - a plain array of Pokemon objects in, a
// Map/array summary out, no D3 and no DOM. These mirror
// ../../data-analysis/charts.py's count_by_type()/count_by_generation()/
// top_abilities(): the same "how many Pokemon per X" questions, just
// recomputed here from the live API response instead of baked into a
// saved PNG. Deliberately kept free of any import (no D3, no CDN URL)
// so tests/chartData.test.js can run under plain `node --test` without
// a browser or a network-resolved import - see charts.js for the D3
// rendering half that consumes these.

/**
 * How many Pokemon have each type. A dual-typed Pokemon (e.g.
 * Bulbasaur: Grass, Poison) counts toward both types, so the counts
 * don't sum to pokemonList.length - same behavior as the Python version.
 * @param {Array<Object>} pokemonList
 * @returns {Map<string, number>}
 */
export function countByType(pokemonList) {
  const counts = new Map();
  for (const entry of pokemonList) {
    for (const type of entry.types) {
      counts.set(type, (counts.get(type) ?? 0) + 1);
    }
  }
  return counts;
}

/**
 * How many Pokemon belong to each generation.
 * @param {Array<Object>} pokemonList
 * @returns {Map<number, number>}
 */
export function countByGeneration(pokemonList) {
  const counts = new Map();
  for (const entry of pokemonList) {
    counts.set(entry.generation, (counts.get(entry.generation) ?? 0) + 1);
  }
  return counts;
}

/**
 * The `topN` most common abilities across pokemonList, most common
 * first. Like countByType(), a Pokemon with two abilities counts
 * toward both.
 * @param {Array<Object>} pokemonList
 * @param {number} [topN]
 * @returns {Array<[string, number]>}
 */
export function topAbilities(pokemonList, topN = 15) {
  const counts = new Map();
  for (const entry of pokemonList) {
    for (const ability of entry.abilities) {
      counts.set(ability, (counts.get(ability) ?? 0) + 1);
    }
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, topN);
}
