// One shared tooltip element for the map and both companion charts, same
// pattern as d3-interactive-web/js/charts.js's getTooltip/showTooltip/
// hideTooltip - factored into its own module here since three render
// modules (map.js, charts.js) need it rather than just one file.
let tooltipEl = null;

function getTooltip() {
  if (!tooltipEl) {
    tooltipEl = document.getElementById("tooltip");
  }
  return tooltipEl;
}

/**
 * @param {PointerEvent} event
 * @param {string} text - always inserted via textContent, never innerHTML -
 *   terminal names/countries ultimately come from research data, so this
 *   is treated as untrusted content per the dataviz skill's interaction
 *   rules, same as d3-interactive-web's tooltip.
 */
export function showTooltip(event, text) {
  const tooltip = getTooltip();
  tooltip.textContent = text;
  tooltip.hidden = false;
  tooltip.style.left = `${event.clientX + 12}px`;
  tooltip.style.top = `${event.clientY + 12}px`;
}

export function hideTooltip() {
  getTooltip().hidden = true;
}
