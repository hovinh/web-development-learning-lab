// A small color-key row: one swatch + label per Pokemon type. Rendered
// once, near the type chart and scatter, so every colored mark those
// two charts draw from typeColors.js has a dependable, always-visible
// place to look up "which type is this hue" - the legend the dataviz
// skill requires whenever color carries identity, rather than asking
// the reader to hold an 18-entry mapping in their head.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { TYPE_COLORS } from "./typeColors.js";

/**
 * @param {string} containerSelector
 */
export function renderTypeLegend(containerSelector) {
  const container = d3.select(containerSelector);
  container.selectAll("*").remove();

  const items = container
    .selectAll(".type-legend-item")
    .data(Object.entries(TYPE_COLORS))
    .join("span")
    .attr("class", "type-legend-item");

  items
    .append("span")
    .attr("class", "type-legend-swatch")
    .style("background-color", ([, color]) => color);

  items.append("span").attr("class", "type-legend-label").text(([type]) => type);
}
