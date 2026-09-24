// Entry point and the only state holder (same convention as
// dataviz-python-js/d3-interactive-web/js/app.js): every other module only
// knows how to render itself from data it's handed, this file decides what
// the current filters are and when to re-render what.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { loadTerminals, loadWorldTopology, loadGroupStats, loadAdvisorModel, loadAppVerdict, capacityByRegion, topTerminalsByCapacity, terminalKpis } from "./data.js";
import { initMap, updateTerminals, resetZoom } from "./map.js";
import { drawRegionChart, drawTopTerminalsChart } from "./charts.js";
import { renderDetail } from "./detail.js";
import { initFilters, setSelectedRegion } from "./filters.js";
import { renderBuildTrail } from "./buildTrail.js";
import { initAdvisorUi } from "./advisorUi.js";

const state = {
  allTerminals: [],
  filters: { region: null, search: "" },
  selectedTerminalId: null,
};

async function init() {
  let allTerminals, worldTopology, groupStats, advisorModel, appVerdict;
  try {
    [allTerminals, worldTopology, groupStats, advisorModel, appVerdict] = await Promise.all([
      loadTerminals(),
      loadWorldTopology(),
      loadGroupStats(),
      loadAdvisorModel(),
      loadAppVerdict(),
    ]);
  } catch (error) {
    reportLoadError(error);
    return;
  }

  state.allTerminals = allTerminals;

  renderKpis(allTerminals, groupStats);
  initMap("#map", worldTopology);
  initFilters(handleFilterChange);
  d3.select("#reset-view").on("click", resetZoom);
  renderBuildTrail(advisorModel, appVerdict);
  initAdvisorUi(advisorModel);

  render();
}

function handleFilterChange(filters) {
  state.filters = filters;
  render();
}

function handleSelectRegion(region) {
  const nextRegion = state.filters.region === region ? null : region;
  setSelectedRegion(nextRegion);
  handleFilterChange({ ...state.filters, region: nextRegion });
}

function handleSelectTerminal(id) {
  state.selectedTerminalId = state.selectedTerminalId === id ? null : id;
  render();
}

function render() {
  const search = state.filters.search;
  const searchFiltered = search
    ? state.allTerminals.filter((terminal) => terminal.name.toLowerCase().includes(search) || terminal.country.toLowerCase().includes(search))
    : state.allTerminals;
  const visible = state.filters.region ? searchFiltered.filter((terminal) => terminal.region === state.filters.region) : searchFiltered;

  const selectedTerminal = state.allTerminals.find((terminal) => terminal.id === state.selectedTerminalId) ?? null;

  updateTerminals(visible, state.allTerminals, { onSelectTerminal: handleSelectTerminal, selectedId: state.selectedTerminalId });

  // The region chart intentionally uses searchFiltered, not visible - see
  // js/app.js's module doc comment above: all five region bars stay
  // present and clickable regardless of the region filter, only the
  // search box narrows what they total.
  drawRegionChart("#chart-region", capacityByRegion(searchFiltered), {
    onSelectRegion: handleSelectRegion,
    selectedRegion: state.filters.region,
  });

  drawTopTerminalsChart("#chart-top-terminals", topTerminalsByCapacity(visible, 15), {
    onSelectTerminal: handleSelectTerminal,
    selectedId: state.selectedTerminalId,
  });

  renderDetail(selectedTerminal);

  d3.select("#result-count").text(`Showing ${visible.length} of ${state.allTerminals.length} terminals`);
}

function renderKpis(allTerminals, groupStats) {
  const { countryCount, terminalCount } = terminalKpis(allTerminals);
  d3.select("#kpi-countries").text(countryCount);
  d3.select("#kpi-terminals").text(terminalCount);
  d3.select("#kpi-group-teu").text(
    typeof groupStats.groupTeuHandled === "number"
      ? `${(groupStats.groupTeuHandled / 1_000_000).toFixed(1)}M TEU (${groupStats.groupTeuHandledYear})`
      : "not published",
  );
}

function reportLoadError(error) {
  console.error(error);
  d3.select("#map").selectAll("*").remove();
  d3.select("#map")
    .append("p")
    .attr("class", "detail-placeholder")
    .text("Couldn't load this demo's data files. If you opened index.html directly (file://), start a static server instead: see this README's \"Run it\" section.");
}

init();
