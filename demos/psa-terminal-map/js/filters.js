// The region chip row and the search box above the map. The chips double
// as the map/charts' categorical color legend (dataviz skill: "a legend
// is always present for >= 2 series") so there is one component for both
// jobs instead of a chip row plus a separate legend repeating the same
// five swatches.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { REGION_ORDER } from "./data.js";
import { regionColor } from "./map.js";

const chipRow = d3.select("#region-chips");
const searchInput = d3.select("#terminal-search");
const resetButton = d3.select("#reset-filters");

/**
 * Renders the five region chips once (they are a fixed list, not derived
 * from the current data - see REGION_ORDER) and wires the search box and
 * reset button. Call once at startup.
 * @param {(filters: {region: string|null, search: string}) => void} onChange
 */
export function initFilters(onChange) {
  chipRow
    .selectAll(".region-chip")
    .data(REGION_ORDER)
    .join((enter) => {
      const chip = enter.append("button").attr("type", "button").attr("class", "region-chip");
      chip.append("span").attr("class", "region-chip-dot");
      chip.append("span").attr("class", "region-chip-label");
      return chip;
    })
    .style("--chip-color", (region) => regionColor(region))
    .each(function (region) {
      d3.select(this).select(".region-chip-dot").style("background-color", regionColor(region));
      d3.select(this).select(".region-chip-label").text(region);
    })
    .on("click", (event, region) => {
      const isAlreadySelected = d3.select(event.currentTarget).classed("is-selected");
      const nextRegion = isAlreadySelected ? null : region;
      // Update this row's own DOM state immediately, the same way
      // setSelectedRegion() does when a region filter is set some other
      // way (a region-bar click in charts.js) - without this, clicking a
      // chip directly would change the filter but never show as selected.
      setSelectedRegion(nextRegion);
      onChange({ region: nextRegion, search: readSearchValue() });
    });

  searchInput.on("input", () => onChange({ region: readSelectedRegion(), search: readSearchValue() }));

  resetButton.on("click", () => {
    searchInput.property("value", "");
    setSelectedRegion(null);
    onChange({ region: null, search: "" });
  });
}

function readSearchValue() {
  return searchInput.property("value").trim().toLowerCase();
}

function readSelectedRegion() {
  const selected = chipRow.select(".region-chip.is-selected");
  return selected.empty() ? null : selected.datum();
}

/**
 * Keeps the chip row's `.is-selected` state in sync with a region filter
 * that was set some other way (clicking a region bar in charts.js) - same
 * role as d3-interactive-web/js/filters.js's setFilterFormValues().
 * @param {string|null} region
 */
export function setSelectedRegion(region) {
  chipRow.selectAll(".region-chip").classed("is-selected", (chipRegion) => chipRegion === region);
}
