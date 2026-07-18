// Renders the scrollable grid of small Pokemon cards - a D3 data-join
// keyed by name, so re-rendering after a filter change only touches the
// cards that actually entered/exited rather than rebuilding the whole
// list from scratch every time.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

const listContainer = d3.select("#pokemon-list");

/**
 * @param {Array<Object>} pokemonList - the currently filtered list
 * @param {string|null} selectedName
 * @param {(name: string) => void} onSelect
 */
export function renderPokemonList(pokemonList, selectedName, onSelect) {
  const cards = listContainer
    .selectAll(".pokemon-card")
    .data(pokemonList, (pokemon) => pokemon.name)
    .join((enter) => {
      const card = enter.append("button").attr("type", "button").attr("class", "pokemon-card");
      card.append("img").attr("class", "pokemon-card-sprite").attr("loading", "lazy");
      card.append("span").attr("class", "pokemon-card-name");
      return card;
    });

  cards
    .classed("is-selected", (pokemon) => pokemon.name === selectedName)
    .on("click", (event, pokemon) => onSelect(pokemon.name));

  cards.select(".pokemon-card-sprite").attr("src", (pokemon) => pokemon.sprite_url).attr("alt", (pokemon) => pokemon.display_name);
  cards.select(".pokemon-card-name").text((pokemon) => pokemon.display_name);
}
