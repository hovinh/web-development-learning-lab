// A thin wrapper around data-serve's REST API (see
// ../../data-serve/README.md for the full endpoint reference). Kept as
// its own module so every other file talks to "the API" through these
// two functions rather than building fetch() calls/URLs itself.

// data-serve defaults to this address when run with `python
// data-serve/app.py` and no PORT override (see that stage's README).
// Hardcoded rather than made configurable: this is a learning stage
// meant to be run locally alongside the API it demonstrates, not a
// deployable client.
export const API_BASE = "http://localhost:5000";

/**
 * Fetch a page of Pokemon, optionally filtered by type/generation.
 * Mirrors data-serve's `GET /api/pokemon` query params exactly - see
 * app.py's `list_pokemon()` route.
 * @param {Object} [options]
 * @param {string} [options.type] - e.g. "fire" (case-insensitive server-side)
 * @param {number|string} [options.generation] - 1-6
 * @param {number} [options.limit] - defaults to 1000, well above this
 *   dataset's ~721 Pokemon, so an unfiltered call returns everything in
 *   one request instead of needing pagination.
 * @param {number} [options.offset]
 * @returns {Promise<Array<Object>>}
 */
export async function fetchPokemon({ type, generation, limit = 1000, offset = 0 } = {}) {
  const url = new URL("/api/pokemon", API_BASE);
  if (type) url.searchParams.set("type", type);
  if (generation !== undefined && generation !== null && generation !== "") {
    url.searchParams.set("generation", generation);
  }
  url.searchParams.set("limit", limit);
  url.searchParams.set("offset", offset);

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`GET ${url} failed with status ${response.status}`);
  }
  return response.json();
}

/**
 * The full image URL for one Pokemon's artwork - `artwork_url` on every
 * record is API-relative ("/api/pokemon/pikachu/artwork"), so it needs
 * API_BASE prefixed before it can be used as an <img> src from this
 * page's own origin.
 * @param {Object} pokemon
 * @returns {string}
 */
export function artworkUrl(pokemon) {
  return `${API_BASE}${pokemon.artwork_url}`;
}
