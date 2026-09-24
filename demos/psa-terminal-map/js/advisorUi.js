// Act 3: the live advisor. Two input paths into the same output renderer:
// the eight documented use cases as a one-click shortcut row, or the five
// SKILL.md intake questions for a free-form case. Both paths end at
// js/advisor.js's recommendStack() - this file only turns its return value
// into DOM, plus the 12-functionality "lights" and the flagged-gaps list.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { recommendForUseCase, recommendStack, deriveNeedsFromIntake, buildGaps } from "./advisor.js";

const REASON_TEXT = {
  "rule-c-base-pick": "Picked directly from the ticked functionalities (Rule C) - no escalation or audience override applied.",
  "escalation-d1-accounts-with-visibility": "Escalated: accounts with different data visibility, saved records, or a back-office screen push this from Streamlit/Dash to Django.",
  "escalation-d2-reimplementing-django-features": "Escalated: re-implementing auth, an ORM layer and an admin by hand pushes this from Flask/FastAPI to Django.",
  "escalation-d3-app-like-or-external-consumer": "Escalated: an app-like UI, an external consumer of the API, or a front-end engineer owning the UI justifies the two-project cost of React (or Angular) + API.",
  "audience-business-interactive": "Audience override: business users who will interact with accounts push the pick to Django even though the raw functionality ticks alone read lighter.",
  "audience-business-readonly": "Audience override: a read-only business audience moves a Streamlit pick to Dash - the audience table never lists Streamlit for that row.",
};

let advisorModel = null;

/**
 * @param {Object} model - data/advisor-model.json, already parsed
 */
export function initAdvisorUi(model) {
  advisorModel = model;
  renderFunctionalityLights(new Set()); // start with nothing lit

  renderUseCaseShortcuts();
  wireIntakeForm();
}

function renderUseCaseShortcuts() {
  d3.select("#use-case-shortcuts")
    .selectAll("button")
    .data(advisorModel.useCases)
    .join("button")
    .attr("type", "button")
    .attr("class", "use-case-shortcut")
    .text((useCase) => useCase.label)
    .on("click", (event, useCase) => {
      d3.selectAll(".use-case-shortcut").classed("is-selected", false);
      d3.select(event.currentTarget).classed("is-selected", true);
      const result = recommendForUseCase(useCase);
      renderResult({
        needs: new Set(useCase.needs),
        result,
        sourceLabel: `Shortcut: "${useCase.label}"`,
        gaps: buildGaps(new Set(useCase.needs)),
      });
    });
}

function wireIntakeForm() {
  const form = d3.select("#intake-form");
  form.on("submit", (event) => {
    event.preventDefault();
    d3.selectAll(".use-case-shortcut").classed("is-selected", false);

    const formEl = form.node();
    const answers = {
      audience: formEl.audience.value,
      users: formEl.users.value,
      savesAnything: formEl.savesAnything.checked,
      slowerThanFewSeconds: formEl.slowerThanFewSeconds.checked,
      anotherSystemCallsIt: formEl.anotherSystemCallsIt.checked,
      appLikeUi: formEl.appLikeUi.checked,
    };

    const { needs, flags } = deriveNeedsFromIntake(answers);
    const result = recommendStack(needs, flags);
    renderResult({ needs, result, sourceLabel: "Your answers", gaps: buildGaps(needs) });
  });

  // The "app-like UI" question is only meaningful once "another system
  // calls it" is answered yes (see advisor.js's deriveNeedsFromIntake) -
  // disabled rather than hidden, so the form's shape doesn't jump around
  // as someone fills it in.
  const anotherSystemCheckbox = form.select('[name="anotherSystemCallsIt"]');
  const appLikeUiCheckbox = form.select('[name="appLikeUi"]');
  anotherSystemCheckbox.on("change", function () {
    const enabled = this.checked;
    appLikeUiCheckbox.property("disabled", !enabled);
    if (!enabled) appLikeUiCheckbox.property("checked", false);
  });
}

function renderFunctionalityLights(needs) {
  d3.select("#functionality-lights")
    .selectAll(".functionality-light")
    .data(advisorModel.functionalities)
    .join((enter) => {
      const light = enter.append("div").attr("class", "functionality-light");
      light.append("span").attr("class", "functionality-light-number");
      light.append("span").attr("class", "functionality-light-name");
      return light;
    })
    .classed("is-lit", (f) => needs.has(f.number))
    .each(function (f) {
      d3.select(this).select(".functionality-light-number").text(f.number);
      d3.select(this).select(".functionality-light-name").text(f.name);
    });
}

/**
 * @param {{needs: Set<number>, result: {rung: number, stackId: string, label: string, reason: string}, sourceLabel: string, gaps: string[]}} params
 */
function renderResult({ needs, result, sourceLabel, gaps }) {
  renderFunctionalityLights(needs);

  const resultPanel = d3.select("#advisor-result");
  resultPanel.classed("is-empty", false);

  d3.select("#advisor-result-source").text(sourceLabel);
  d3.select("#advisor-result-rung").text(`Rung ${result.rung}`);
  d3.select("#advisor-result-stack").text(result.label);
  d3.select("#advisor-result-reason").text(REASON_TEXT[result.reason] ?? result.reason);

  const toolStatusEntry = advisorModel.toolStatus.find((entry) => result.label.toLowerCase().includes(entry.tool.split(" ")[0].toLowerCase()));
  d3.select("#advisor-result-tool-status").text(
    toolStatusEntry
      ? toolStatusEntry.status === "run"
        ? `${toolStatusEntry.tool}: verified by running (${toolStatusEntry.note}).`
        : `${toolStatusEntry.tool}: ${toolStatusEntry.note}.`
      : "",
  );

  const gapsList = d3.select("#advisor-result-gaps");
  gapsList.selectAll("li").data(gaps).join("li").text((gap) => gap);
  d3.select("#advisor-result-gaps-heading").style("display", gaps.length > 0 ? null : "none");
}
