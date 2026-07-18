// Entry point: fetches data-serve's data once, then wires the filters,
// pokemon list, detail panel, and charts together. Each of those lives
// in its own module and only knows how to render itself from data it's
// handed - this file is the only one that holds app state and decides
// when to re-render what.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { fetchPokemon } from "./api.js";
import { drawAllCharts } from "./charts.js";
import { initFilters, setFilterFormValues } from "./filters.js";
import { renderPokemonList } from "./pokemonList.js";
import { renderDetail } from "./detail.js";
import { renderTypeLegend } from "./typeLegend.js";

const resultCount = d3.select("#result-count");

const state = {
  allPokemon: [], // unfiltered - source for every chart and for the filter dropdowns' option lists
  visiblePokemon: [], // whatever the current type/generation filter shows in the list
  filters: { type: "", generation: "" },
  selectedName: null,
};

async function init() {
  try {
    state.allPokemon = await fetchPokemon({ limit: 1000 });
  } catch (error) {
    reportLoadError(error);
    return;
  }

  state.visiblePokemon = state.allPokemon;
  initFilters(state.allPokemon, handleFilterChange);
  renderTypeLegend("#type-legend"); // static (the 18 fixed type colors), rendered once rather than on every re-render
  render();
}

async function handleFilterChange(filters) {
  state.filters = filters;
  try {
    state.visiblePokemon = await fetchPokemon({
      type: filters.type,
      generation: filters.generation,
      limit: 1000,
    });
  } catch (error) {
    reportLoadError(error);
    return;
  }
  render();
}

/**
 * Clicking a chart bar is a second way to drive the same filters the
 * dropdowns control (see index.html's "charts-note"). Clicking the
 * already-selected bar again clears that filter, same as Reset would.
 */
function handleChartFilterClick(partialFilters) {
  const nextFilters = { ...state.filters, ...partialFilters };
  for (const key of Object.keys(partialFilters)) {
    if (String(state.filters[key] ?? "") === String(partialFilters[key])) {
      nextFilters[key] = "";
    }
  }
  setFilterFormValues(nextFilters);
  handleFilterChange(nextFilters);
}

function handleSelectPokemon(name) {
  state.selectedName = name;
  render();
}

function render() {
  const selectedPokemon = state.allPokemon.find((pokemon) => pokemon.name === state.selectedName) ?? null;

  renderPokemonList(state.visiblePokemon, state.selectedName, handleSelectPokemon);
  renderDetail(selectedPokemon);

  resultCount.text(`Showing ${state.visiblePokemon.length} of ${state.allPokemon.length} Pokemon`);

  drawAllCharts(state.allPokemon, {
    onSelectType: (type) => handleChartFilterClick({ type }),
    onSelectGeneration: (generation) => handleChartFilterClick({ generation: String(generation) }),
    onSelectPokemon: handleSelectPokemon,
    selectedType: state.filters.type || undefined,
    selectedGeneration: state.filters.generation ? Number(state.filters.generation) : undefined,
    selectedName: state.selectedName,
  });
}

function reportLoadError(error) {
  console.error(error);
  const list = d3.select("#pokemon-list");
  list.selectAll("*").remove();
  list
    .append("p")
    .attr("class", "detail-placeholder")
    .text(
      "Couldn't reach data-serve's API at http://localhost:5000. Start it first: " +
        "`python data-serve/app.py` (see data-serve/README.md), then reload this page.",
    );
}

init();
