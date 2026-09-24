// Act 2: "Why this stack" - renders entirely from data/advisor-model.json
// and data/this-app-verdict.json, never hardcoded in HTML, so the build
// trail is visibly data-driven rather than a paragraph someone wrote once
// and forgot to update.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { buildGaps } from "./advisor.js";

// Each higher rung's proof-of-work: the demo in this repo that already
// occupies it, tying the four demos into one story (PLAN.md: "demos 1/2/3
// become the proof for rungs 4, 5 and functionality 12" - functionality
// 12's proof, demos/long-jobs/, surfaces in the gaps list below instead of
// here, since it isn't a rung). Rung 3 (FastAPI alone) has no link: this
// repo's only FastAPI code is demos/labeling-fastapi-react/api/, which is
// half of the rung-5 demo rather than a rung-3-only one, so claiming it
// here would overstate what's actually isolated.
const RUNG_DEMO_LINKS = {
  2: null, // Streamlit/Dash are documentation-only in this repo (see advisor-model.json's toolStatus)
  3: null,
  4: { label: "demos/labeling-django/", href: "../labeling-django/README.md" },
  5: { label: "demos/labeling-fastapi-react/", href: "../labeling-fastapi-react/README.md" },
};

const RUNG_ESCALATION_HINT = {
  1: "What would push this app up a rung: reviewers needing accounts to curate/comment on terminals (-> rung 4, Django) - see escalation D-1 below.",
  2: null,
  3: null,
  4: null,
  5: null,
};

/**
 * @param {Object} advisorModel - data/advisor-model.json, already parsed
 * @param {Object} appVerdict - data/this-app-verdict.json, already parsed
 */
export function renderBuildTrail(advisorModel, appVerdict) {
  renderFunctionalityTable(advisorModel, appVerdict);
  renderLadder(advisorModel, appVerdict);
  renderEscalations(advisorModel);
  renderGaps(appVerdict);
}

function renderFunctionalityTable(advisorModel, appVerdict) {
  const verdictByNumber = new Map(appVerdict.rows.map((row) => [row.number, row]));

  const rows = d3
    .select("#functionality-table-body")
    .selectAll("tr")
    .data(advisorModel.functionalities)
    .join("tr");

  rows.append("td").attr("class", "functionality-number").text((f) => f.number);
  rows.append("td").attr("class", "functionality-name").text((f) => f.name);
  rows
    .append("td")
    .attr("class", (f) => `functionality-needed ${verdictByNumber.get(f.number).needed ? "is-needed" : "is-not-needed"}`)
    .text((f) => (verdictByNumber.get(f.number).needed ? "✓" : "✗"));
  rows.append("td").attr("class", "functionality-tool").text((f) => verdictByNumber.get(f.number).tool);
  rows.append("td").attr("class", "functionality-why").text((f) => verdictByNumber.get(f.number).why);
}

function renderLadder(advisorModel, appVerdict) {
  const rungItems = d3
    .select("#ladder")
    .selectAll(".ladder-rung")
    .data(advisorModel.rungs)
    .join((enter) => {
      const item = enter.append("li").attr("class", "ladder-rung");
      item.append("span").attr("class", "ladder-rung-number");
      item.append("span").attr("class", "ladder-rung-name");
      item.append("p").attr("class", "ladder-rung-description");
      item.append("p").attr("class", "ladder-rung-hint");
      item.append("p").attr("class", "ladder-rung-demo-link");
      return item;
    });

  rungItems.classed("is-lit", (rung) => rung.rung === appVerdict.rung);
  rungItems.select(".ladder-rung-number").text((rung) => `Rung ${rung.rung}`);
  rungItems.select(".ladder-rung-name").text((rung) => rung.name);
  rungItems.select(".ladder-rung-description").text((rung) => rung.description);
  rungItems.select(".ladder-rung-hint").text((rung) => RUNG_ESCALATION_HINT[rung.rung] ?? "");

  rungItems.select(".ladder-rung-demo-link").each(function (rung) {
    const cell = d3.select(this);
    cell.selectAll("*").remove();
    const link = RUNG_DEMO_LINKS[rung.rung];
    if (!link) {
      if (rung.rung === appVerdict.rung) {
        cell.text("This app.");
      } else if (rung.rung === 2) {
        cell.text("Streamlit/Dash are documentation-only in this repo - no demo to link yet.");
      } else {
        cell.text("No demo in this repo isolates this rung on its own.");
      }
      return;
    }
    cell.text("Proof-of-work: ");
    cell.append("a").attr("href", link.href).text(link.label);
  });
}

function renderEscalations(advisorModel) {
  d3.select("#escalations-list")
    .selectAll("li")
    .data(advisorModel.escalations)
    .join("li")
    .html((escalation) => `<strong>${escalation.from} &rarr; ${escalation.to}:</strong> ${escapeHtml(escalation.trigger)}`);
  // .html() here only ever interpolates advisor-model.json's own
  // maintainer-authored strings (never terminal-research data or visitor
  // input), and escapeHtml() below still escapes them - belt and braces
  // rather than relying on "this file is trusted" alone.
}

function renderGaps(appVerdict) {
  const needsFromVerdict = new Set(appVerdict.rows.filter((row) => row.needed).map((row) => row.number));
  const gaps = buildGaps(needsFromVerdict).concat(appVerdict.escalationTriggers ?? []);

  d3.select("#build-trail-gaps")
    .selectAll("li")
    .data(gaps)
    .join("li")
    .text((gap) => gap);
}

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
