// Renders the detail card for whichever terminal is currently selected -
// clicked on the map or on the top-15 chart. Same placeholder/clear
// pattern as dataviz-python-js/d3-interactive-web/js/detail.js's
// renderDetail().
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { regionColor } from "./map.js";

const detailPanel = d3.select("#detail-panel");

/** Renders "value" or a muted "not published" placeholder for a null field - the dataShape test guarantees every field is a number or null, never a placeholder string, so this is the one place that turns null into display text. */
function factValue(value, formatter = (v) => v) {
  return value === null || value === undefined ? "not published" : formatter(value);
}

/**
 * @param {Object|null} terminal - null clears the panel back to its placeholder
 */
export function renderDetail(terminal) {
  detailPanel.selectAll("*").remove();

  if (!terminal) {
    detailPanel.append("p").attr("class", "detail-placeholder").text("Select a terminal on the map, or a bar on the top-15 chart, to see its detail card.");
    return;
  }

  const regionBadge = detailPanel.append("div").attr("class", "detail-region-badge");
  regionBadge.append("span").attr("class", "region-badge-dot").style("background-color", regionColor(terminal.region));
  regionBadge.append("span").attr("class", "region-badge-label").text(terminal.region);

  detailPanel.append("h2").attr("class", "detail-name").text(terminal.name);
  detailPanel.append("p").attr("class", "detail-country").text(terminal.country);

  const factList = detailPanel.append("dl").attr("class", "detail-facts");
  addFact(factList, "Berths", factValue(terminal.berths));
  addFact(factList, "Quay length", factValue(terminal.quayLengthM, (v) => `${v.toLocaleString()} m`));
  addFact(factList, "Depth alongside", factValue(terminal.depthM, (v) => `${v} m`));
  addFact(factList, "Terminal area", factValue(terminal.terminalAreaHa, (v) => `${v.toLocaleString()} ha`));
  addFact(factList, "Quay cranes", factValue(terminal.quayCranes));
  addFact(factList, "Designed capacity", factValue(terminal.designedCapacityTeu, (v) => `${v.toLocaleString()} TEU/yr`));

  detailPanel
    .append("p")
    .attr("class", "detail-approx-note")
    .text(terminal.coordinatesApproximate ? "Map position is an approximate port location, not surveyed coordinates." : "");

  const sourcesList = detailPanel.append("div").attr("class", "detail-sources");
  sourcesList.append("span").attr("class", "detail-sources-label").text(terminal.sources.length > 1 ? "Sources: " : "Source: ");
  terminal.sources.forEach((url, index) => {
    if (index > 0) sourcesList.append("span").text(", ");
    sourcesList.append("a").attr("href", url).attr("target", "_blank").attr("rel", "noopener noreferrer").text(`[${index + 1}]`);
  });
  sourcesList.append("span").attr("class", "detail-retrieved").text(` — retrieved ${terminal.retrievedDate}`);
}

function addFact(factList, label, value) {
  factList.append("dt").text(label);
  // .text(), not .html() - every value here ultimately comes from
  // research data, so it is inserted as text, never parsed as markup.
  factList.append("dd").text(value);
}
