// Loads this app's static JSON/TopoJSON files and derives the aggregates
// the two companion charts need. Split from map.js/charts.js the same way
// d3-interactive-web splits chartData.js from charts.js: this file answers
// "what does the data say", the render modules answer "how do you draw
// that" - see js/map.js and js/charts.js.

/**
 * @returns {Promise<Array<Object>>} the researched terminal records - see
 *   data/terminals.json and this README's "Data provenance" section.
 */
export async function loadTerminals() {
  const response = await fetch("data/terminals.json");
  if (!response.ok) {
    throw new Error(`Failed to load data/terminals.json: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

/** @returns {Promise<Object>} the vendored world-atlas 110m land TopoJSON - see this README's attribution note. */
export async function loadWorldTopology() {
  const response = await fetch("data/world-110m.json");
  if (!response.ok) {
    throw new Error(`Failed to load data/world-110m.json: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

/** @returns {Promise<Object>} PSA's group-wide throughput KPI - see data/group-stats.json. */
export async function loadGroupStats() {
  const response = await fetch("data/group-stats.json");
  if (!response.ok) {
    throw new Error(`Failed to load data/group-stats.json: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

/** @returns {Promise<Object>} the web-stack-advisor skill's rules as data - see data/advisor-model.json. */
export async function loadAdvisorModel() {
  const response = await fetch("data/advisor-model.json");
  if (!response.ok) {
    throw new Error(`Failed to load data/advisor-model.json: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

/** @returns {Promise<Object>} this app's own 12-row functionality verdict - see data/this-app-verdict.json. */
export async function loadAppVerdict() {
  const response = await fetch("data/this-app-verdict.json");
  if (!response.ok) {
    throw new Error(`Failed to load data/this-app-verdict.json: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

/**
 * PSA's five documented regions, in a fixed display order - the dataviz
 * skill's "assign categorical hues in fixed order, never cycled" rule
 * means this order (not a sort-by-count order that would shuffle whenever
 * the filtered set changes) is also what drives each region's color slot
 * - see js/map.js's REGION_COLORS, which is keyed off this same array.
 */
export const REGION_ORDER = ["Southeast Asia", "Northeast Asia", "Middle East, South Asia, Africa, Türkiye", "Europe", "Americas"];

/**
 * Terminal count and summed *designed capacity* per region (only summing
 * terminals where designedCapacityTeu is known - a region with more nulls
 * will show a lower bar even if its real capacity is comparable, which the
 * chart's caption calls out explicitly rather than leaving it implicit).
 * @param {Array<Object>} terminals
 * @returns {Array<{region: string, count: number, capacityTeu: number, knownCapacityCount: number}>} in REGION_ORDER, regions with zero terminals omitted
 */
export function capacityByRegion(terminals) {
  const byRegion = new Map(REGION_ORDER.map((region) => [region, { region, count: 0, capacityTeu: 0, knownCapacityCount: 0 }]));

  for (const terminal of terminals) {
    const bucket = byRegion.get(terminal.region);
    if (!bucket) continue; // dataShape.test.js already guarantees every region is one of REGION_ORDER, but stay defensive here rather than throw mid-render
    bucket.count += 1;
    if (typeof terminal.designedCapacityTeu === "number") {
      bucket.capacityTeu += terminal.designedCapacityTeu;
      bucket.knownCapacityCount += 1;
    }
  }

  return [...byRegion.values()].filter((bucket) => bucket.count > 0);
}

/**
 * The top-N terminals by designed capacity, largest first. Terminals with
 * an unknown (null) capacity are excluded - they cannot be ranked, not
 * ranked last as if their capacity were zero.
 * @param {Array<Object>} terminals
 * @param {number} [topN]
 * @returns {Array<Object>}
 */
export function topTerminalsByCapacity(terminals, topN = 15) {
  return terminals
    .filter((terminal) => typeof terminal.designedCapacityTeu === "number")
    .sort((a, b) => b.designedCapacityTeu - a.designedCapacityTeu)
    .slice(0, topN);
}

/**
 * The KPI row's per-terminal-derived figures (countries and terminal
 * count) - the third KPI, group-wide TEU handled, is a distinct researched
 * statistic from data/group-stats.json, not derived from this array, so it
 * is intentionally not computed here (see this README's "Data provenance").
 * @param {Array<Object>} terminals
 * @returns {{countryCount: number, terminalCount: number}}
 */
export function terminalKpis(terminals) {
  return {
    countryCount: new Set(terminals.map((terminal) => terminal.country)).size,
    terminalCount: terminals.length,
  };
}
