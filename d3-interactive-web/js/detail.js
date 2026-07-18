// Renders the mini-biography panel for whichever Pokemon is currently
// selected (from the list or from the height/weight scatter point).
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { artworkUrl } from "./api.js";
import { typeColor } from "./typeColors.js";

const detailPanel = d3.select("#detail-panel");

/**
 * @param {Object|null} pokemon - null clears the panel back to its
 *   placeholder (nothing selected yet).
 */
export function renderDetail(pokemon) {
  detailPanel.selectAll("*").remove();

  if (!pokemon) {
    detailPanel
      .append("p")
      .attr("class", "detail-placeholder")
      .text("Select a Pokemon from the list, or a point on the height vs. weight chart below, to see its mini-biography.");
    return;
  }

  // The full-resolution artwork comes from data-serve's own endpoint
  // (not the small sprite_url used in the list) - see api.js's
  // artworkUrl(). A plain <img> tag isn't subject to CORS the way a
  // fetch()/XHR read of the response body would be, so this works even
  // cross-origin without any extra setup.
  detailPanel
    .append("img")
    .attr("class", "detail-artwork")
    .attr("src", artworkUrl(pokemon))
    .attr("alt", `${pokemon.display_name} artwork`);

  detailPanel
    .append("h2")
    .attr("class", "detail-name")
    .text(`#${String(pokemon.national_number).padStart(3, "0")} ${pokemon.display_name}`);

  detailPanel.append("p").attr("class", "detail-species").text(pokemon.species);

  const typeBadges = detailPanel
    .append("div")
    .attr("class", "detail-types")
    .selectAll(".type-badge")
    .data(pokemon.types)
    .join((enter) => {
      const badge = enter.append("span").attr("class", "type-badge");
      badge.append("span").attr("class", "type-badge-dot");
      badge.append("span").attr("class", "type-badge-label");
      return badge;
    });

  typeBadges.select(".type-badge-dot").style("background-color", (type) => typeColor(type));
  typeBadges.select(".type-badge-label").text((type) => type);

  const factList = detailPanel.append("dl").attr("class", "detail-facts");
  addFact(factList, "Generation", pokemon.generation);
  addFact(factList, "Height", `${pokemon.height_m} m`);
  addFact(factList, "Weight", `${pokemon.weight_kg} kg`);
  addFact(factList, "Abilities", pokemon.abilities.join(", "));
  if (pokemon.hidden_ability) {
    addFact(factList, "Hidden ability", pokemon.hidden_ability);
  }
}

function addFact(factList, label, value) {
  factList.append("dt").text(label);
  // .text() (not .html()) - every value here comes from the API
  // response, so it's inserted as text, never parsed as markup.
  factList.append("dd").text(value);
}
