// The load-bearing test (see README.md's "Tests" section): every one of
// the eight documented use cases in
// .claude/skills/web-stack-advisor/references/use-cases.md, encoded in
// data/advisor-model.json, must produce the stack that file documents when
// run through js/advisor.js's recommendStack(). This is what turns "the
// skill is useful" into a claim the repo checks, rather than 530 lines of
// Markdown a reader has to take on faith.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { recommendForUseCase, recommendStack, deriveNeedsFromIntake } from "../js/advisor.js";

const modelPath = fileURLToPath(new URL("../data/advisor-model.json", import.meta.url));
const model = JSON.parse(readFileSync(modelPath, "utf-8"));

// A quick lookup so each test below can find its use case by key rather
// than by array position (position would silently break if
// advisor-model.json is reordered).
function useCase(key) {
  const found = model.useCases.find((entry) => entry.key === key);
  assert.ok(found, `advisor-model.json has no use case with key "${key}"`);
  return found;
}

test("all eight documented use cases produce their documented stackId", () => {
  const expectedStackIdByDisplayStack = {
    "Static HTML + D3 (+ Tailwind)": "static-html-d3",
    "Streamlit first; D3 only for custom visuals": "streamlit",
    "Dash": "dash",
    "FastAPI, plus a Streamlit page if a UI is wanted": "fastapi",
    "Django": "django",
    "Django + Tailwind kit": "django",
    "React + shadcn/ui over an API": "react-api",
    "Python writes JSON, static D3 renders it": "static-html-d3",
    "Plain HTML/JS": "static-html-d3",
  };

  assert.equal(model.useCases.length, 9, "9 rows because 'multi-user product prototype' is split into its two documented outcomes (default UI vs app-like UI)");

  for (const uc of model.useCases) {
    const expectedStackId = expectedStackIdByDisplayStack[uc.displayStack];
    assert.ok(expectedStackId, `no expected stackId mapped for displayStack "${uc.displayStack}" (use case "${uc.key}")`);
    const result = recommendForUseCase(uc);
    assert.equal(result.stackId, expectedStackId, `use case "${uc.key}" (${uc.label}) expected stackId "${expectedStackId}", got "${result.stackId}"`);
  }
});

test("the two multi-user-prototype use cases share one functionality set and differ only by the appLikeUi flag", () => {
  const defaultUi = useCase("multi-user-prototype-django");
  const appLikeUi = useCase("multi-user-prototype-app-like");
  assert.deepEqual(defaultUi.needs, appLikeUi.needs, "same needs array in advisor-model.json");
  assert.equal(recommendForUseCase(defaultUi).stackId, "django");
  assert.equal(recommendForUseCase(appLikeUi).stackId, "react-api");
});

test("the 4+5 two-projects rule only pays for a split when the UI is app-like or another system needs the API", () => {
  const needs = new Set([2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
  assert.equal(recommendStack(needs, {}).stackId, "django", "no appLikeUi/externalConsumer -> collapse to one project");
  assert.equal(recommendStack(needs, { appLikeUi: true }).stackId, "react-api");
  assert.equal(recommendStack(needs, { externalConsumer: true }).stackId, "react-api", "another system needing the API is enough on its own, without an app-like UI");
});

test("escalation D-1: Streamlit/Dash to Django when accounts with different visibility are needed", () => {
  const needs = new Set([3, 6]); // a rung-2-looking functionality set on its own
  const withoutEscalation = recommendStack(needs, {});
  assert.equal(withoutEscalation.stackId, "streamlit");

  const withEscalation = recommendStack(needs, { needsAccountsWithDifferentVisibility: true });
  assert.equal(withEscalation.stackId, "django");
  assert.equal(withEscalation.reason, "escalation-d1-accounts-with-visibility");
});

test("escalation D-2: Flask/FastAPI to Django when re-implementing auth/ORM/admin", () => {
  const needs = new Set([4, 6]); // "demo a model"'s functionality set
  const withoutEscalation = recommendStack(needs, {});
  assert.equal(withoutEscalation.stackId, "fastapi");

  const withEscalation = recommendStack(needs, { reimplementingAuthOrmAdmin: true });
  assert.equal(withEscalation.stackId, "django");
  assert.equal(withEscalation.reason, "escalation-d2-reimplementing-django-features");
});

test("escalation D-3: Django to React+API when the UI needs to be app-like, even without ticking functionality 5", () => {
  const needs = new Set([7, 8, 9, 10]); // "labeling tool"'s functionality set - no 4 or 5 ticked
  const withoutEscalation = recommendStack(needs, {});
  assert.equal(withoutEscalation.stackId, "django");

  const withEscalation = recommendStack(needs, { appLikeUi: true });
  assert.equal(withEscalation.stackId, "react-api");
  assert.equal(withEscalation.reason, "escalation-d3-app-like-or-external-consumer");

  const withFrontendEngineer = recommendStack(needs, { frontendEngineerOwnsUi: true });
  assert.equal(withFrontendEngineer.stackId, "react-api", "a front-end engineer owning the UI is its own trigger, per use-cases.md");
});

test("the audience modifier changes the pick without changing the functionality set", () => {
  const needs = new Set([3, 6]);

  const forPeers = recommendStack(needs, { audience: "peers" });
  assert.equal(forPeers.stackId, "streamlit");

  const forBusinessReadonly = recommendStack(needs, { audience: "business-readonly" });
  assert.equal(forBusinessReadonly.stackId, "dash", "business-readonly's row lists 'Static D3 or Dash', never Streamlit");

  const forBusinessInteractive = recommendStack(needs, { audience: "business-interactive" });
  assert.equal(forBusinessInteractive.stackId, "django", "business-interactive escalates to Django even though the raw ticks alone read as rung 2");

  // The point of this test: all three calls above passed the exact same
  // `needs` Set object - only the audience option changed.
  assert.equal(needs.size, 2);
  assert.ok(needs.has(3) && needs.has(6));
});

test("deriveNeedsFromIntake: a solo peer-facing exploration tool needs only client interactivity and server compute", () => {
  const { needs } = deriveNeedsFromIntake({
    audience: "peers",
    users: "one",
    savesAnything: false,
    slowerThanFewSeconds: false,
    anotherSystemCallsIt: false,
  });
  assert.deepEqual([...needs].sort(), [1, 2, 3]);
});

test("deriveNeedsFromIntake: many users with different data ticks auth, authorization, and session", () => {
  const { needs, flags } = deriveNeedsFromIntake({
    audience: "business-interactive",
    users: "many-different-data",
    savesAnything: true,
    slowerThanFewSeconds: false,
    anotherSystemCallsIt: false,
  });
  for (const expected of [1, 2, 3, 6, 7, 8, 9, 10, 11]) {
    assert.ok(needs.has(expected), `expected functionality ${expected} to be ticked`);
  }
  assert.equal(flags.needsAccountsWithDifferentVisibility, true);
});
