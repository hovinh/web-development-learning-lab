// Canonical Pokemon type colors - the same fixed mapping used across
// Pokedex apps/games (Fire is orange-red, Water is blue, Grass is
// green, ...), not an invented categorical palette. Used to color the
// type bar chart, the height/weight scatter, and the mini-biography's
// type badges.
//
// This deliberately overrides the dataviz skill's ~8-hue categorical
// safety ceiling (18 types, not 8): that ceiling exists because a
// reader has to *learn* an arbitrary series-to-color mapping, and past
// ~8 hues no one can hold the mapping in their head. Type colors are
// the opposite case - a fixed, widely memorized domain convention (the
// games themselves teach it) rather than something invented for this
// chart.
//
// Run through the skill's validate_palette.py, these 18 colors
// actually FAIL two of its checks (lightness band and chroma floor -
// Normal/Ice/Steel in particular read as too light or too close to
// gray to trust as a sole identity channel). That's an expected,
// accepted cost of a fixed brand palette nobody is free to re-order or
// re-step - which is exactly why the mitigation here isn't "pick
// better colors" but the skill's other hard rule, "never color alone":
// every mark colored from this map is always paired with its type name
// as text too (an axis tick, a tooltip, or the legend rendered by
// renderTypeLegend()), so no reading here actually depends on
// distinguishing hues that don't clear the floor. See "Fixed" status
// colors in the dataviz skill's palette.md for the same
// never-themed-but-fixed reasoning applied to a different fixed domain
// vocabulary.
export const TYPE_COLORS = {
  Normal: "#A8A878",
  Fire: "#F08030",
  Water: "#6890F0",
  Electric: "#F8D030",
  Grass: "#78C850",
  Ice: "#98D8D8",
  Fighting: "#C03028",
  Poison: "#A040A0",
  Ground: "#E0C068",
  Flying: "#A890F0",
  Psychic: "#F85888",
  Bug: "#A8B820",
  Rock: "#B8A038",
  Ghost: "#705898",
  Dragon: "#7038F8",
  Dark: "#705848",
  Steel: "#B8B8D0",
  Fairy: "#EE99AC",
};

/**
 * @param {string} type
 * @returns {string} the type's fixed color, or the chart accent blue
 *   for any type not in the table (defensive only - every type in this
 *   dataset is one of the 18 keys above).
 */
export function typeColor(type) {
  return TYPE_COLORS[type] ?? "var(--series-1)";
}
