// The two filter <select> controls (type, generation) plus the reset
// button. Populates their options from whatever's actually in the
// dataset (rather than a hardcoded list) and wires their change events
// to a callback app.js supplies - this module doesn't know or care
// what happens when a filter changes, only that something should be
// told.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

const typeSelect = d3.select("#type-filter");
const generationSelect = d3.select("#generation-filter");
const resetButton = d3.select("#reset-filters");

/**
 * Populates the filter dropdowns from the dataset and wires their
 * events. Call once, after the initial unfiltered fetch.
 * @param {Array<Object>} allPokemon - the full, unfiltered dataset
 * @param {(filters: {type: string, generation: string}) => void} onChange
 */
export function initFilters(allPokemon, onChange) {
  const types = [...new Set(allPokemon.flatMap((pokemon) => pokemon.types))].sort();
  const generations = [...new Set(allPokemon.map((pokemon) => pokemon.generation))].sort((a, b) => a - b);

  typeSelect
    .selectAll("option.dynamic-option")
    .data(types)
    .join("option")
    .attr("class", "dynamic-option")
    .attr("value", (type) => type)
    .text((type) => type);

  generationSelect
    .selectAll("option.dynamic-option")
    .data(generations)
    .join("option")
    .attr("class", "dynamic-option")
    .attr("value", (generation) => generation)
    .text((generation) => `Generation ${generation}`);

  const emitChange = () => onChange(readFilterValues());

  typeSelect.on("change", emitChange);
  generationSelect.on("change", emitChange);
  resetButton.on("click", () => {
    setFilterFormValues({ type: "", generation: "" });
    emitChange();
  });
}

/**
 * Reads the two <select> elements' current values.
 * @returns {{type: string, generation: string}}
 */
export function readFilterValues() {
  return {
    type: typeSelect.property("value"),
    generation: generationSelect.property("value"),
  };
}

/**
 * Programmatically sets the <select> elements - used when a chart bar
 * is clicked (charts.js's onSelectType/onSelectGeneration), so the
 * dropdown UI stays in sync with a filter that was set by clicking a
 * bar rather than choosing from the dropdown itself.
 * @param {{type?: string, generation?: string|number}} filters
 */
export function setFilterFormValues({ type, generation }) {
  typeSelect.property("value", type ?? "");
  generationSelect.property("value", generation === undefined || generation === null ? "" : String(generation));
}
