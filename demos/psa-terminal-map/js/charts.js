// The two companion charts: capacity by region, and the top-15 terminal
// ranking - both cross-filtered with the map (see js/app.js). Follows the
// same horizontal-bar-chart shape as
// dataviz-python-js/d3-interactive-web/js/charts.js's
// drawHorizontalBarChart(), reimplemented here rather than imported since
// this is a separate stage with its own package.json and no shared
// dependency between stages (see docs/javascript.md).
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { regionColor } from "./map.js";
import { showTooltip, hideTooltip } from "./tooltip.js";

const BAR_MAX_THICKNESS = 24; // dataviz skill's mark spec: thin marks even when a band has more room
const BAR_RADIUS = 4; // rounded only at the data-end, per the mark spec

/** An SVG rounded-rect path with independently-radiused corners (0 = square) - see marks-and-anatomy.md's "round only the data-end, square at the baseline". */
function roundedRectPath(x, y, width, height, corners = {}) {
  const w = Math.max(width, 0);
  const h = Math.max(height, 0);
  const maxRadius = Math.min(w, h) / 2; // clamp so a tiny bar never draws a self-intersecting arc
  const topLeft = Math.min(corners.topLeft ?? 0, maxRadius);
  const topRight = Math.min(corners.topRight ?? 0, maxRadius);
  const bottomRight = Math.min(corners.bottomRight ?? 0, maxRadius);
  const bottomLeft = Math.min(corners.bottomLeft ?? 0, maxRadius);
  return `M${x + topLeft},${y}
    H${x + w - topRight}
    A${topRight},${topRight} 0 0 1 ${x + w},${y + topRight}
    V${y + h - bottomRight}
    A${bottomRight},${bottomRight} 0 0 1 ${x + w - bottomRight},${y + h}
    H${x + bottomLeft}
    A${bottomLeft},${bottomLeft} 0 0 1 ${x},${y + h - bottomLeft}
    V${y + topLeft}
    A${topLeft},${topLeft} 0 0 1 ${x + topLeft},${y}
    Z`;
}

function formatTeu(value) {
  return `${(value / 1_000_000).toFixed(1)}M TEU/yr`;
}

/**
 * Horizontal bar chart of designed capacity per region, kept in
 * REGION_ORDER (not sorted by size) - region has a real geographic
 * identity, same reasoning as d3-interactive-web's generation chart
 * keeping generation order rather than sorting by count, and it also
 * means a region's bar position never jumps around as filters change.
 * @param {string} containerSelector
 * @param {Array<{region: string, count: number, capacityTeu: number, knownCapacityCount: number}>} buckets
 * @param {{onSelectRegion?: (region: string) => void, selectedRegion?: string|null}} [handlers]
 */
export function drawRegionChart(containerSelector, buckets, { onSelectRegion, selectedRegion } = {}) {
  const margin = { top: 4, right: 56, bottom: 4, left: 168 };
  const width = 480;
  const rowHeight = 32;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = buckets.length * rowHeight;
  const height = innerHeight + margin.top + margin.bottom;

  const container = d3.select(containerSelector);
  container.selectAll("*").remove();

  const svg = container
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("role", "img")
    .attr("aria-label", "Bar chart of designed container capacity by PSA region");

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const y = d3
    .scaleBand()
    .domain(buckets.map((bucket) => bucket.region))
    .range([0, innerHeight])
    .padding(0.28);
  const x = d3
    .scaleLinear()
    .domain([0, d3.max(buckets, (bucket) => bucket.capacityTeu) || 1])
    .nice()
    .range([0, innerWidth]);

  g.append("g")
    .attr("class", "gridlines")
    .call(d3.axisTop(x).tickSize(-innerHeight).tickFormat(""))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  const barThickness = Math.min(y.bandwidth(), BAR_MAX_THICKNESS);
  const barOffset = (y.bandwidth() - barThickness) / 2;

  g.selectAll(".mark-bar")
    .data(buckets, (bucket) => bucket.region)
    .join("path")
    .attr("class", (bucket) => `mark-bar${bucket.region === selectedRegion ? " is-selected" : ""}`)
    .attr("d", (bucket) =>
      roundedRectPath(0, y(bucket.region) + barOffset, x(bucket.capacityTeu), barThickness, {
        topRight: BAR_RADIUS,
        bottomRight: BAR_RADIUS,
      }),
    )
    .style("fill", (bucket) => regionColor(bucket.region))
    .style("cursor", onSelectRegion ? "pointer" : "default")
    .on("pointermove", (event, bucket) =>
      showTooltip(
        event,
        `${bucket.region}: ${formatTeu(bucket.capacityTeu)} across ${bucket.knownCapacityCount} of ${bucket.count} terminal${bucket.count === 1 ? "" : "s"} with published capacity`,
      ),
    )
    .on("pointerleave", hideTooltip)
    .on("click", onSelectRegion ? (event, bucket) => onSelectRegion(bucket.region) : null);

  g.append("g")
    .attr("class", "axis axis-category")
    .call(d3.axisLeft(y).tickSize(0))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  g.selectAll(".bar-value-label")
    .data(buckets, (bucket) => bucket.region)
    .join("text")
    .attr("class", "bar-value-label")
    .attr("x", (bucket) => x(bucket.capacityTeu) + 6)
    .attr("y", (bucket) => y(bucket.region) + barOffset + barThickness / 2)
    .attr("dy", "0.32em")
    .text((bucket) => formatTeu(bucket.capacityTeu));
}

/**
 * Horizontal bar chart of the top-N terminals by designed capacity,
 * largest at the top (see data.js's topTerminalsByCapacity, already
 * sorted descending and pre-filtered to terminals with a known capacity).
 * @param {string} containerSelector
 * @param {Array<Object>} topTerminals
 * @param {{onSelectTerminal?: (id: string) => void, selectedId?: string|null}} [handlers]
 */
export function drawTopTerminalsChart(containerSelector, topTerminals, { onSelectTerminal, selectedId } = {}) {
  const margin = { top: 4, right: 56, bottom: 4, left: 176 };
  const width = 480;
  const rowHeight = 24;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = topTerminals.length * rowHeight;
  const height = Math.max(innerHeight, 1) + margin.top + margin.bottom;

  const container = d3.select(containerSelector);
  container.selectAll("*").remove();

  if (topTerminals.length === 0) {
    container.append("p").attr("class", "chart-empty-note").text("No terminals with a published designed capacity in the current filter.");
    return;
  }

  const svg = container
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("role", "img")
    .attr("aria-label", `Bar chart of the top ${topTerminals.length} PSA terminals by designed capacity`);

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const y = d3
    .scaleBand()
    .domain(topTerminals.map((terminal) => terminal.id))
    .range([0, innerHeight])
    .padding(0.22);
  const x = d3
    .scaleLinear()
    .domain([0, d3.max(topTerminals, (terminal) => terminal.designedCapacityTeu)])
    .nice()
    .range([0, innerWidth]);

  g.append("g")
    .attr("class", "gridlines")
    .call(d3.axisTop(x).tickSize(-innerHeight).tickFormat(""))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  const barThickness = Math.min(y.bandwidth(), BAR_MAX_THICKNESS);
  const barOffset = (y.bandwidth() - barThickness) / 2;

  g.selectAll(".mark-bar")
    .data(topTerminals, (terminal) => terminal.id)
    .join("path")
    .attr("class", (terminal) => `mark-bar${terminal.id === selectedId ? " is-selected" : ""}`)
    .attr("d", (terminal) =>
      roundedRectPath(0, y(terminal.id) + barOffset, x(terminal.designedCapacityTeu), barThickness, {
        topRight: BAR_RADIUS,
        bottomRight: BAR_RADIUS,
      }),
    )
    .style("fill", (terminal) => regionColor(terminal.region))
    .style("cursor", onSelectTerminal ? "pointer" : "default")
    .on("pointermove", (event, terminal) => showTooltip(event, `${terminal.name} (${terminal.country}): ${formatTeu(terminal.designedCapacityTeu)}`))
    .on("pointerleave", hideTooltip)
    .on("click", onSelectTerminal ? (event, terminal) => onSelectTerminal(terminal.id) : null);

  g.append("g")
    .attr("class", "axis axis-category")
    .call(d3.axisLeft(y).tickSize(0).tickFormat((id) => topTerminals.find((terminal) => terminal.id === id)?.name ?? id))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  g.selectAll(".bar-value-label")
    .data(topTerminals, (terminal) => terminal.id)
    .join("text")
    .attr("class", "bar-value-label")
    .attr("x", (terminal) => x(terminal.designedCapacityTeu) + 6)
    .attr("y", (terminal) => y(terminal.id) + barOffset + barThickness / 2)
    .attr("dy", "0.32em")
    .text((terminal) => formatTeu(terminal.designedCapacityTeu));
}
