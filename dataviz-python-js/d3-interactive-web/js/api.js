// A thin wrapper around data-serve's REST API (see
// ../../data-serve/README.md for the full endpoint reference). Kept as
// its own module so every other file talks to "the API" through these
// two functions rather than building fetch() calls/URLs itself.

// This page runs in two places (see ../../deploy/README.md):
// - locally, alongside `python data-serve/app.py`, which defaults to
//   this address with no PORT override (see that stage's README);
// - deployed to GitHub Pages, where there's no localhost API to talk
//   to, so it must call the API's public Render URL instead.
// Picking between them by hostname (rather than a build step) keeps
// this a plain static file with no bundler/templating - the same
// js/api.js file is served in both places unmodified.
const LOCAL_API_BASE = "http://localhost:5000";

// Filled in once, after deploy/render.yaml's service is created for
// the first time - see deploy/README.md's "First-time setup" section.
// Render assigns this URL from the service's `name:` in render.yaml
// (https://<name>.onrender.com), so it only needs setting once, not
// on every deploy.
const DEPLOYED_API_BASE = "https://pokedex-learning-lab-api.onrender.com";

const isLocalHost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
export const API_BASE = isLocalHost ? LOCAL_API_BASE : DEPLOYED_API_BASE;

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
