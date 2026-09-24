// Checks data/terminals.json's shape, not its exact values - the values
// come from real research (see README.md's "Data provenance"), so this
// file cannot assert "PSA Antwerp has 8 berths"; it can only assert that
// every record follows the schema the rest of the app (js/data.js,
// js/map.js, js/detail.js) relies on, so a bad research edit fails fast
// here instead of silently drawing a NaN circle on the map.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const terminalsPath = fileURLToPath(new URL("../data/terminals.json", import.meta.url));
const terminals = JSON.parse(readFileSync(terminalsPath, "utf-8"));

const VALID_REGIONS = new Set(["Southeast Asia", "Northeast Asia", "Middle East, South Asia, Africa, Türkiye", "Europe", "Americas"]);

const REQUIRED_KEYS = [
  "id",
  "name",
  "country",
  "region",
  "coordinates",
  "coordinatesApproximate",
  "berths",
  "quayLengthM",
  "depthM",
  "terminalAreaHa",
  "quayCranes",
  "designedCapacityTeu",
  "sources",
  "retrievedDate",
];

test("terminals.json is a non-empty array", () => {
  assert.ok(Array.isArray(terminals), "top-level JSON must be a bare array, not wrapped in an object");
  assert.ok(terminals.length > 0, "expected at least one terminal");
});

test("every terminal has every required key", () => {
  for (const terminal of terminals) {
    for (const key of REQUIRED_KEYS) {
      assert.ok(Object.prototype.hasOwnProperty.call(terminal, key), `terminal "${terminal.id ?? "?"}" is missing key "${key}"`);
    }
  }
});

test("every terminal id is unique and kebab-case", () => {
  const ids = terminals.map((terminal) => terminal.id);
  assert.equal(new Set(ids).size, ids.length, "duplicate id found");
  for (const id of ids) {
    assert.match(id, /^[a-z0-9]+(-[a-z0-9]+)*$/, `id "${id}" is not kebab-case`);
  }
});

test("every terminal has a region from PSA's five documented regions", () => {
  for (const terminal of terminals) {
    assert.ok(VALID_REGIONS.has(terminal.region), `terminal "${terminal.id}" has an unrecognized region "${terminal.region}"`);
  }
});

test("every terminal has a non-empty sources array of http(s) URLs", () => {
  for (const terminal of terminals) {
    assert.ok(Array.isArray(terminal.sources) && terminal.sources.length > 0, `terminal "${terminal.id}" has an empty sources array`);
    for (const url of terminal.sources) {
      assert.match(url, /^https?:\/\//, `terminal "${terminal.id}" has a non-URL source "${url}"`);
    }
  }
});

test("every terminal's coordinates are [longitude, latitude] within range", () => {
  for (const terminal of terminals) {
    const [lon, lat] = terminal.coordinates;
    assert.ok(Array.isArray(terminal.coordinates) && terminal.coordinates.length === 2, `terminal "${terminal.id}" coordinates must be a [lon, lat] pair`);
    assert.ok(lon >= -180 && lon <= 180, `terminal "${terminal.id}" longitude ${lon} out of range - check it isn't swapped with latitude`);
    assert.ok(lat >= -90 && lat <= 90, `terminal "${terminal.id}" latitude ${lat} out of range - check it isn't swapped with longitude`);
    assert.equal(terminal.coordinatesApproximate, true, `terminal "${terminal.id}" should mark coordinatesApproximate: true - these position a dot, not survey data`);
  }
});

test("designedCapacityTeu is either a positive number or explicitly null, never a string or zero", () => {
  for (const terminal of terminals) {
    const value = terminal.designedCapacityTeu;
    if (value === null) continue;
    assert.equal(typeof value, "number", `terminal "${terminal.id}" designedCapacityTeu must be a number or null, got ${typeof value}`);
    assert.ok(value > 0, `terminal "${terminal.id}" designedCapacityTeu must be positive when known`);
  }
});

test("every numeric field PSA does not publish is explicitly null, never a placeholder string", () => {
  const numericFields = ["berths", "quayLengthM", "depthM", "terminalAreaHa", "quayCranes", "designedCapacityTeu"];
  for (const terminal of terminals) {
    for (const field of numericFields) {
      const value = terminal[field];
      assert.ok(value === null || typeof value === "number", `terminal "${terminal.id}" field "${field}" must be a number or null, got ${JSON.stringify(value)}`);
      if (typeof value === "number") {
        assert.ok(value > 0, `terminal "${terminal.id}" field "${field}" must be positive when known`);
      }
    }
  }
});

test("retrievedDate is an ISO date string", () => {
  for (const terminal of terminals) {
    assert.match(terminal.retrievedDate, /^\d{4}-\d{2}-\d{2}$/, `terminal "${terminal.id}" retrievedDate "${terminal.retrievedDate}" is not an ISO date`);
  }
});
