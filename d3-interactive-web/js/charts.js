// D3 rendering for the four dataset charts. Split from chartData.js on
// purpose (same split data-analysis/charts.py uses between its
// count_*/top_abilities functions and its plot_* functions): this file
// takes a summary and draws it, chartData.js holds the "how do you
// summarize this data" logic. Nothing here is unit-tested (an SVG's
// geometry isn't a meaningful assertion) - opening index.html and
// looking at the charts is the real check, same as this repo's other
// stages treat a demo/main script as the check for wiring rather than
// for logic.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { countByType, countByGeneration, topAbilities } from "./chartData.js";
import { typeColor } from "./typeColors.js";

// Mark spec constants (dataviz skill's "marks-and-anatomy"): bars are
// capped at 24px thick even when a band has more room to give, and
// round only at the data-end, 4px.
const BAR_MAX_THICKNESS = 24;
const BAR_RADIUS = 4;

// The dataviz skill's validated categorical order (see style.css's
// --series-1..6), used for the generation chart's 6 bars. Generation N
// always gets slot N - 1, regardless of what's filtered elsewhere, so
// a generation's color never shifts underneath a reader (skill rule:
// "color follows the entity, never its rank").
const GENERATION_COLORS = [
  "var(--series-1)",
  "var(--series-2)",
  "var(--series-3)",
  "var(--series-4)",
  "var(--series-5)",
  "var(--series-6)",
];

let tooltipEl = null;

function getTooltip() {
  if (!tooltipEl) {
    tooltipEl = document.getElementById("tooltip");
  }
  return tooltipEl;
}

function showTooltip(event, text) {
  const tooltip = getTooltip();
  // textContent, not innerHTML - tooltip text is built from Pokemon/type
  // names that ultimately come from the API response, so it's treated
  // as untrusted data per the dataviz skill's interaction rules.
  tooltip.textContent = text;
  tooltip.hidden = false;
  tooltip.style.left = `${event.clientX + 12}px`;
  tooltip.style.top = `${event.clientY + 12}px`;
}

function hideTooltip() {
  getTooltip().hidden = true;
}

/**
 * An SVG rounded-rect path where each corner's radius is given
 * independently (0 for a plain square corner) - used so a bar rounds
 * only at its data-end and stays square at the baseline, in either
 * orientation, instead of needing a separate helper per orientation.
 */
function roundedRectPath(x, y, width, height, corners = {}) {
  const w = Math.max(width, 0);
  const h = Math.max(height, 0);
  // Clamp every radius to half the smaller side - a bar for a small
  // value can be narrower than 2x the mark spec's 4px radius (e.g. a
  // rarely-shared ability in the top-15 chart), and an unclamped radius
  // there would draw a self-intersecting arc instead of a small pill.
  const maxRadius = Math.min(w, h) / 2;
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

/**
 * A sorted, descending horizontal bar chart for one series of [label,
 * value] pairs - the shared shape behind the type and abilities charts
 * (both are "how many Pokemon have X", just for a different X).
 *
 * Ordering note vs. data-analysis/charts.py's plot_horizontal_bar():
 * the Python version sorts ascending because matplotlib's barh() draws
 * bottom-to-top, so ascending order puts the largest bar visually on
 * top. SVG's y-axis runs the other way (down the page), so this sorts
 * descending directly - same "largest bar at the top" result, without
 * relying on that matplotlib-specific quirk.
 *
 * `colorFor(label)` is optional - the type chart passes typeColors.js's
 * `typeColor` so each bar gets its type's canonical color; the
 * abilities chart passes nothing and falls back to style.css's flat
 * `--series-1` (no identity to color abilities by, see drawAllCharts()).
 */
function drawHorizontalBarChart(containerSelector, entries, { onBarClick, selectedLabel, colorFor } = {}) {
  const sorted = [...entries].sort((a, b) => b[1] - a[1]);
  const labels = sorted.map(([label]) => label);

  const margin = { top: 4, right: 44, bottom: 4, left: 108 };
  const width = 520;
  const rowHeight = 28;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = labels.length * rowHeight;
  const height = innerHeight + margin.top + margin.bottom;

  const container = d3.select(containerSelector);
  container.selectAll("*").remove(); // full redraw every call - see drawAllCharts()

  const svg = container
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("role", "img")
    .attr("aria-label", `Bar chart, ${labels.length} categories, largest at the top`);

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const y = d3.scaleBand().domain(labels).range([0, innerHeight]).padding(0.25);
  const x = d3
    .scaleLinear()
    .domain([0, d3.max(sorted, ([, value]) => value)])
    .nice()
    .range([0, innerWidth]);

  g.append("g")
    .attr("class", "gridlines")
    .call(d3.axisTop(x).tickSize(-innerHeight).tickFormat(""))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  const barThickness = Math.min(y.bandwidth(), BAR_MAX_THICKNESS);
  const barOffset = (y.bandwidth() - barThickness) / 2;

  g.selectAll(".mark-bar")
    .data(sorted, ([label]) => label)
    .join("path")
    .attr("class", ([label]) => `mark-bar${label === selectedLabel ? " is-selected" : ""}`)
    .attr("d", ([label, value]) =>
      roundedRectPath(0, y(label) + barOffset, x(value), barThickness, {
        topRight: BAR_RADIUS,
        bottomRight: BAR_RADIUS,
      }),
    )
    .style("fill", colorFor ? ([label]) => colorFor(label) : null)
    .style("cursor", onBarClick ? "pointer" : "default")
    .on("pointermove", (event, [label, value]) => showTooltip(event, `${label}: ${value}`))
    .on("pointerleave", hideTooltip)
    .on("click", onBarClick ? (event, [label]) => onBarClick(label) : null);

  g.append("g")
    .attr("class", "axis axis-category")
    .call(d3.axisLeft(y).tickSize(0))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  // Value label at each bar's tip (marks-and-anatomy: "bars -> value at
  // the tip"). One series, all 15-18 bars labeled - see that reference's
  // note on why that's readable here despite the general "label
  // sparingly" rule for busier, multi-series charts.
  g.selectAll(".bar-value-label")
    .data(sorted, ([label]) => label)
    .join("text")
    .attr("class", "bar-value-label")
    .attr("x", ([, value]) => x(value) + 6)
    .attr("y", ([label]) => y(label) + barOffset + barThickness / 2)
    .attr("dy", "0.32em")
    .text(([, value]) => value);
}

/** A column chart of Pokemon count per generation, kept in generation
 * order (1-6) rather than sorted by count - generation has a real,
 * meaningful order that sorting by size would destroy. */
function drawGenerationBarChart(containerSelector, pokemonList, { onSelectGeneration, selectedGeneration } = {}) {
  const counts = countByGeneration(pokemonList);
  const generations = [...counts.keys()].sort((a, b) => a - b);

  const margin = { top: 20, right: 12, bottom: 30, left: 40 };
  const width = 480;
  const height = 320;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const container = d3.select(containerSelector);
  container.selectAll("*").remove();

  const svg = container
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("role", "img")
    .attr("aria-label", "Column chart of Pokemon per generation, generations 1 through 6");

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand().domain(generations).range([0, innerWidth]).padding(0.3);
  const y = d3
    .scaleLinear()
    .domain([0, d3.max(generations, (generation) => counts.get(generation))])
    .nice()
    .range([innerHeight, 0]);

  g.append("g")
    .attr("class", "gridlines")
    .call(d3.axisLeft(y).tickSize(-innerWidth).tickFormat(""))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  const barThickness = Math.min(x.bandwidth(), BAR_MAX_THICKNESS);
  const barOffset = (x.bandwidth() - barThickness) / 2;

  g.selectAll(".mark-bar")
    .data(generations, (generation) => generation)
    .join("path")
    .attr("class", (generation) => `mark-bar${generation === selectedGeneration ? " is-selected" : ""}`)
    .attr("d", (generation) => {
      const value = counts.get(generation);
      return roundedRectPath(x(generation) + barOffset, y(value), barThickness, innerHeight - y(value), {
        topLeft: BAR_RADIUS,
        topRight: BAR_RADIUS,
      });
    })
    .style("fill", (generation) => GENERATION_COLORS[(generation - 1) % GENERATION_COLORS.length])
    .style("cursor", onSelectGeneration ? "pointer" : "default")
    .on("pointermove", (event, generation) => showTooltip(event, `Generation ${generation}: ${counts.get(generation)}`))
    .on("pointerleave", hideTooltip)
    .on("click", onSelectGeneration ? (event, generation) => onSelectGeneration(generation) : null);

  g.append("g")
    .attr("class", "axis axis-category")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(
      d3
        .axisBottom(x)
        .tickSize(0)
        .tickFormat((generation) => `Gen ${generation}`),
    )
    .call((axisGroup) => axisGroup.select(".domain").remove());

  // Value label on each column's cap (marks-and-anatomy: "columns ->
  // value on the cap").
  g.selectAll(".bar-value-label")
    .data(generations, (generation) => generation)
    .join("text")
    .attr("class", "bar-value-label")
    .attr("text-anchor", "middle")
    .attr("x", (generation) => x(generation) + barOffset + barThickness / 2)
    .attr("y", (generation) => y(counts.get(generation)) - 6)
    .text((generation) => counts.get(generation));
}

/** A scatter of every Pokemon's height against its weight, both axes
 * log-scaled (height spans 0.1-14.5m, weight 0.1-950kg in this dataset -
 * a linear scale would crush nearly everything into one corner). Not
 * colored by type: 18 types is well past the ~8-hue ceiling a reader
 * can keep pairwise distinct (see data-analysis/README.md's "Chart
 * design notes" for the same call made there), so this stays a single
 * hue and lets height/weight be the whole story. */
function drawScatterChart(containerSelector, pokemonList, { onSelectPokemon, selectedName } = {}) {
  const margin = { top: 12, right: 12, bottom: 42, left: 52 };
  const width = 480;
  const height = 420;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const container = d3.select(containerSelector);
  container.selectAll("*").remove();

  const svg = container
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("role", "img")
    .attr("aria-label", "Scatter plot of height versus weight, log scale on both axes");

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLog()
    .domain(d3.extent(pokemonList, (pokemon) => pokemon.height_m))
    .nice()
    .range([0, innerWidth]);
  const y = d3
    .scaleLog()
    .domain(d3.extent(pokemonList, (pokemon) => pokemon.weight_kg))
    .nice()
    .range([innerHeight, 0]);

  g.append("g")
    .attr("class", "gridlines")
    .call(d3.axisLeft(y).ticks(5, "~s").tickSize(-innerWidth).tickFormat(""))
    .call((axisGroup) => axisGroup.select(".domain").remove());

  g.append("g")
    .attr("class", "axis axis-value")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x).ticks(5, "~s"));

  g.append("g").attr("class", "axis axis-value").call(d3.axisLeft(y).ticks(5, "~s"));

  g.append("text")
    .attr("class", "axis-title")
    .attr("text-anchor", "middle")
    .attr("x", innerWidth / 2)
    .attr("y", innerHeight + 36)
    .text("Height (m)");

  g.append("text")
    .attr("class", "axis-title")
    .attr("text-anchor", "middle")
    .attr("transform", `translate(${-38},${innerHeight / 2}) rotate(-90)`)
    .text("Weight (kg)");

  const points = g
    .selectAll(".scatter-point-group")
    .data(pokemonList, (pokemon) => pokemon.name)
    .join("g")
    .attr("class", (pokemon) => `scatter-point-group${pokemon.name === selectedName ? " is-selected" : ""}`)
    .attr("transform", (pokemon) => `translate(${x(pokemon.height_m)},${y(pokemon.weight_kg)})`)
    .style("cursor", onSelectPokemon ? "pointer" : "default");

  // The visible mark: a small dot filled by the Pokemon's primary type
  // color (typeColors.js), with a surface-color ring (via CSS stroke,
  // see style.css's .scatter-point) so overlapping points stay
  // legible - dataviz skill's mark spec. Colored by primary type only
  // (types[0]) rather than trying to split dual-typed Pokemon across
  // two hues - a single mark can only carry one fill.
  points
    .append("circle")
    .attr("class", "scatter-point")
    .attr("r", 4)
    .style("fill", (pokemon) => typeColor(pokemon.types[0]));

  // An invisible, larger hit target layered on top - a literal 4px dot
  // is too small to reliably point at or tap, so hover/click listeners
  // live on this circle instead (dataviz skill's interaction rule: hit
  // targets should be bigger than the mark, >=24px across).
  points
    .append("circle")
    .attr("class", "scatter-hit-target")
    .attr("r", 12)
    .on("pointermove", (event, pokemon) =>
      showTooltip(event, `${pokemon.display_name} (${pokemon.types.join("/")}): ${pokemon.height_m} m, ${pokemon.weight_kg} kg`),
    )
    .on("pointerleave", hideTooltip)
    .on("click", onSelectPokemon ? (event, pokemon) => onSelectPokemon(pokemon.name) : null);
}

/**
 * Draws all four charts from the full (unfiltered) Pokemon list - see
 * index.html's "charts-note" for why they intentionally ignore the
 * type/generation filter above them. Called again on every filter or
 * selection change so the "selected" highlight stays in sync; a full
 * redraw is cheap enough at this dataset's size (~721 records, 4
 * small charts) that there's no real benefit to a more surgical update.
 * @param {Array<Object>} pokemonList - always the unfiltered dataset
 * @param {Object} [handlers]
 * @param {(type: string) => void} [handlers.onSelectType]
 * @param {(generation: number) => void} [handlers.onSelectGeneration]
 * @param {(name: string) => void} [handlers.onSelectPokemon]
 * @param {string} [handlers.selectedType]
 * @param {number} [handlers.selectedGeneration]
 * @param {string} [handlers.selectedName]
 */
export function drawAllCharts(
  pokemonList,
  { onSelectType, onSelectGeneration, onSelectPokemon, selectedType, selectedGeneration, selectedName } = {},
) {
  drawHorizontalBarChart("#chart-type", [...countByType(pokemonList).entries()], {
    onBarClick: onSelectType,
    selectedLabel: selectedType,
    colorFor: typeColor,
  });

  drawGenerationBarChart("#chart-generation", pokemonList, {
    onSelectGeneration,
    selectedGeneration,
  });

  // Abilities aren't a filterable dimension on data-serve's API, so
  // this chart is display-only - no onBarClick.
  drawHorizontalBarChart("#chart-abilities", topAbilities(pokemonList, 15));

  drawScatterChart("#chart-scatter", pokemonList, { onSelectPokemon, selectedName });
}
