// Act 1's main visual: a world map with PSA terminals as proportional
// circles. Land geometry comes from the vendored data/world-110m.json
// (see this README's attribution note); topojson-client converts its
// arcs into a GeoJSON feature the same way any topojson consumer would.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import * as topojson from "https://cdn.jsdelivr.net/npm/topojson-client@3/+esm";
import { showTooltip, hideTooltip } from "./tooltip.js";
import { REGION_ORDER } from "./data.js";

// One color role per PSA region, in REGION_ORDER's fixed order - the
// dataviz skill's "assign categorical hues in fixed order, never cycled"
// rule, and the same --series-1..6 custom properties
// dataviz-python-js/d3-interactive-web/css/style.css uses, so this app's
// map and that stage's charts read as one system if seen side by side.
const REGION_COLOR_VARS = ["--series-1", "--series-2", "--series-3", "--series-4", "--series-5"];

/** @param {string} region */
export function regionColor(region) {
  const index = REGION_ORDER.indexOf(region);
  return index === -1 ? "var(--text-muted)" : `var(${REGION_COLOR_VARS[index]})`;
}

const WIDTH = 960;
const HEIGHT = 520;
const MIN_RADIUS = 5; // dataviz skill's interaction rule: hit targets/marks should read clearly even at the smallest data value
const MAX_RADIUS = 28;
const UNKNOWN_CAPACITY_RADIUS = 4; // a small, visually distinct fallback for terminals with no published designed capacity to scale by

let svgRoot = null;
let zoomGroup = null;
let zoomBehavior = null;
let projection = null;
let pathGenerator = null;
let radiusScale = null;
let landInitialized = false;

/**
 * Draws the base map once: projection fit to the vendored land topology,
 * land path, and the zoom/pan behavior. Call once at startup; call
 * updateTerminals() on every subsequent filter/selection change - keeping
 * the two separate means panning/zooming state survives a filter change
 * instead of resetting on every re-render.
 * @param {string} containerSelector
 * @param {Object} worldTopology - data/world-110m.json, already parsed
 */
export function initMap(containerSelector, worldTopology) {
  const container = d3.select(containerSelector);
  container.selectAll("*").remove();

  svgRoot = container
    .append("svg")
    .attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`)
    .attr("role", "img")
    .attr("aria-label", "World map of PSA International's deepsea container terminals, sized by designed capacity");

  const landFeature = topojson.feature(worldTopology, worldTopology.objects.land);

  // geoNaturalEarth1 (per PLAN.md) rather than the more common
  // geoMercator - it does not blow up polar land area the way Mercator
  // does, which matters here since PSA's network runs from Scandinavia to
  // Southeast Asia and a Mercator projection would visually overstate the
  // higher-latitude terminals' surrounding landmass.
  projection = d3.geoNaturalEarth1().fitSize([WIDTH, HEIGHT], landFeature);
  pathGenerator = d3.geoPath(projection);

  zoomGroup = svgRoot.append("g").attr("class", "map-zoom-group");

  zoomGroup.append("path").attr("class", "map-land").attr("d", pathGenerator(landFeature));

  zoomGroup.append("g").attr("class", "map-terminals");

  zoomBehavior = d3
    .zoom()
    .scaleExtent([1, 8])
    .translateExtent([
      [0, 0],
      [WIDTH, HEIGHT],
    ])
    .on("zoom", (event) => {
      zoomGroup.attr("transform", event.transform);
      // Keep marks a constant screen size while zoomed in, rather than
      // scaling up with the map - a proportional-capacity circle should
      // stay comparable across terminals regardless of zoom level.
      zoomGroup.selectAll(".mark-circle,.mark-circle-unknown-capacity").attr("stroke-width", 1 / event.transform.k);
    });

  svgRoot.call(zoomBehavior);

  landInitialized = true;
}

/** Resets pan/zoom back to the initial view - wired to the "Reset view" button in index.html. */
export function resetZoom() {
  if (!svgRoot || !zoomBehavior) return;
  svgRoot.transition().duration(400).call(zoomBehavior.transform, d3.zoomIdentity);
}

/**
 * Re-draws the terminal circles from whichever list is currently visible
 * (already filtered by region/search - see js/app.js). Land and zoom
 * state are untouched, so filtering never resets the view.
 * @param {Array<Object>} visibleTerminals
 * @param {Array<Object>} allTerminals - for the radius scale's domain, so a
 *   terminal's circle size never changes just because a filter shrank the
 *   visible set
 * @param {Object} handlers
 * @param {(id: string) => void} handlers.onSelectTerminal
 * @param {string|null} handlers.selectedId
 */
export function updateTerminals(visibleTerminals, allTerminals, { onSelectTerminal, selectedId } = {}) {
  if (!landInitialized) {
    throw new Error("initMap() must be called before updateTerminals()");
  }

  const maxCapacity = d3.max(allTerminals, (terminal) => terminal.designedCapacityTeu ?? 0) || 1;
  radiusScale = d3.scaleSqrt().domain([0, maxCapacity]).range([MIN_RADIUS, MAX_RADIUS]);

  const terminalsGroup = zoomGroup.select(".map-terminals");

  const known = visibleTerminals.filter((terminal) => typeof terminal.designedCapacityTeu === "number");
  const unknown = visibleTerminals.filter((terminal) => typeof terminal.designedCapacityTeu !== "number");

  // Draw unknown-capacity terminals first (small, fixed radius) so a
  // known-capacity circle drawn afterward never gets hidden underneath a
  // larger neighbor's unknown-radius dot - order here is z-order, not data order.
  terminalsGroup
    .selectAll(".mark-circle-unknown-capacity")
    .data(unknown, (terminal) => terminal.id)
    .join("circle")
    .attr("class", (terminal) => `mark-circle-unknown-capacity${terminal.id === selectedId ? " is-selected" : ""}`)
    .attr("transform", (terminal) => `translate(${projectPoint(terminal.coordinates)})`)
    .attr("r", UNKNOWN_CAPACITY_RADIUS)
    .style("fill", (terminal) => regionColor(terminal.region))
    .style("cursor", onSelectTerminal ? "pointer" : "default")
    .on("pointermove", (event, terminal) => showTooltip(event, tooltipText(terminal)))
    .on("pointerleave", hideTooltip)
    .on("click", onSelectTerminal ? (event, terminal) => onSelectTerminal(terminal.id) : null);

  terminalsGroup
    .selectAll(".mark-circle")
    .data(known, (terminal) => terminal.id)
    .join("circle")
    .attr("class", (terminal) => `mark-circle${terminal.id === selectedId ? " is-selected" : ""}`)
    .attr("transform", (terminal) => `translate(${projectPoint(terminal.coordinates)})`)
    .attr("r", (terminal) => radiusScale(terminal.designedCapacityTeu))
    .style("fill", (terminal) => regionColor(terminal.region))
    .style("fill-opacity", 0.8)
    .style("cursor", onSelectTerminal ? "pointer" : "default")
    .on("pointermove", (event, terminal) => showTooltip(event, tooltipText(terminal)))
    .on("pointerleave", hideTooltip)
    .on("click", onSelectTerminal ? (event, terminal) => onSelectTerminal(terminal.id) : null);
}

function projectPoint(coordinates) {
  const projected = projection(coordinates);
  // A terminal whose coordinates fall outside the projection's valid
  // range (shouldn't happen post-dataShape.test.js, but a bad edit could
  // still slip past it) returns null from d3's projection - park it off
  // the visible canvas rather than letting translate() emit "NaN,NaN"
  // and silently breaking every mark after it in the DOM.
  return projected ?? [-9999, -9999];
}

function tooltipText(terminal) {
  const capacity = typeof terminal.designedCapacityTeu === "number" ? `${terminal.designedCapacityTeu.toLocaleString()} TEU/yr designed capacity` : "designed capacity not published";
  return `${terminal.name} (${terminal.country}): ${capacity}`;
}
