// The tested core of Act 3 (the live advisor) and Act 2 (the build trail).
// This module encodes the web-stack-advisor skill's rules as data-driven
// logic - see .claude/skills/web-stack-advisor/references/functionalities.md
// ("How to use the table", called Rule C below) and
// .claude/skills/web-stack-advisor/references/use-cases.md ("When to
// escalate a rung" and "Audience adjusts the pick", called Rule D and the
// audience modifier below). Nothing here touches the DOM - advisorUi.js and
// buildTrail.js are the only files that render what this module returns,
// which is what makes tests/advisor.test.js possible: it can assert against
// this module directly, with no browser involved.

/**
 * The five-rung ladder (SKILL.md's "The lightest-first ladder"), each rung
 * carrying a stable `stackId` so the scoring functions below can return a
 * short, comparable key instead of a prose string. Two rungs (2) share the
 * same rung number but a different stackId - Streamlit and Dash are both
 * "rung 2", picked apart by the `layoutControl` signal (see
 * `pickBaseStack`).
 */
export const RUNGS = {
  staticD3: { rung: 1, stackId: "static-html-d3", label: "Static HTML + D3 (+ Tailwind)" },
  streamlit: { rung: 2, stackId: "streamlit", label: "Streamlit" },
  dash: { rung: 2, stackId: "dash", label: "Dash" },
  fastapi: { rung: 3, stackId: "fastapi", label: "FastAPI (or Flask)" },
  django: { rung: 4, stackId: "django", label: "Django (+ Tailwind kit)" },
  reactApi: { rung: 5, stackId: "react-api", label: "React (or Angular) + Tailwind over an API" },
};

/**
 * Rule C (functionalities.md, "How to use the table"), the tick-only base
 * pick - no escalation flags or audience considered yet:
 *   1. Ticks at 7-11 onward (persistence, forms, auth, authorization,
 *      session) are a reason to move toward Django - even one such tick is
 *      enough, since Django ships all of them together rather than one at a
 *      time. (12, background/long jobs, is deliberately excluded: Django
 *      6.0's own tasks API ships no worker, per background-jobs.md, so
 *      ticking 12 alone does not argue for Django - it is surfaced as a
 *      gap/caution instead, see buildGaps() below.)
 *   2. Functionality 4 alone (providing an API), with none of the above,
 *      is "demo a model" - FastAPI.
 *   3. Functionality 3 + 6 together (client interactivity + server-side
 *      compute), with nothing heavier, is "explore/dashboard" - Streamlit
 *      by default, Dash when the caller flags a need for more layout/
 *      callback control (SKILL.md's quick-pick row: "Streamlit (Dash if you
 *      need layout control)").
 *   4. Otherwise, presentation/styling/interactivity only - static HTML + D3.
 * @param {Set<number>} needs - ticked functionality numbers, 1-12
 * @param {{layoutControl?: boolean}} [options]
 */
function pickBaseStack(needs, { layoutControl = false } = {}) {
  const has = (n) => needs.has(n);

  const highTicks = [7, 8, 9, 10, 11].filter(has);
  if (highTicks.length > 0) return RUNGS.django;

  if (has(4)) return RUNGS.fastapi;

  if (has(3) && has(6)) return layoutControl ? RUNGS.dash : RUNGS.streamlit;

  return RUNGS.staticD3;
}

/**
 * The full recommendation: Rule C's base pick, then Rule D's three named
 * escalations (use-cases.md, "When to escalate a rung"), then the audience
 * modifier (use-cases.md, "Audience adjusts the pick") applied last. Every
 * escalation and the audience modifier can change the *pick* without ever
 * changing the *functionality set* the caller passed in - `needs` is read,
 * never mutated.
 *
 * @param {Set<number>} needs - ticked functionality numbers, 1-12
 * @param {Object} [options]
 * @param {boolean} [options.layoutControl] - Rule C tie-break for rung 2
 * @param {boolean} [options.appLikeUi] - the UI needs instant, app-like interaction
 * @param {boolean} [options.externalConsumer] - another system also needs the API
 * @param {boolean} [options.frontendEngineerOwnsUi] - a front-end engineer will own the UI
 * @param {boolean} [options.needsAccountsWithDifferentVisibility] - escalation D-1 trigger
 * @param {boolean} [options.reimplementingAuthOrmAdmin] - escalation D-2 trigger
 * @param {"peers"|"business-readonly"|"business-interactive"} [options.audience]
 * @returns {{rung: number, stackId: string, label: string, reason: string}}
 */
export function recommendStack(needs, options = {}) {
  const {
    layoutControl = false,
    appLikeUi = false,
    externalConsumer = false,
    frontendEngineerOwnsUi = false,
    needsAccountsWithDifferentVisibility = false,
    reimplementingAuthOrmAdmin = false,
    audience = "peers",
  } = options;

  // Escalation D-1: "Streamlit/Dash to Django: you need accounts with
  // different data visibility, saved records, or a back-office screen."
  // Checked first because this can be true even when the raw ticks alone
  // would read as a rung-2 case (e.g. the caller only ticked 3 and 6 but
  // knows, from experience, that per-user visibility is coming).
  if (needsAccountsWithDifferentVisibility) {
    return { ...RUNGS.django, reason: "escalation-d1-accounts-with-visibility" };
  }

  let pick = pickBaseStack(needs, { layoutControl });
  let reason = "rule-c-base-pick";

  // Escalation D-2: "Flask/FastAPI to Django: you are re-implementing
  // auth, an ORM layer and an admin."
  if (pick.stackId === "fastapi" && reimplementingAuthOrmAdmin) {
    pick = RUNGS.django;
    reason = "escalation-d2-reimplementing-django-features";
  }

  // Rule C step 3 (ticks at 4 and 5 together mean two projects) and
  // escalation D-3 ("Django to React + API: the UI needs instant, app-like
  // interaction, or other systems also need the API, or a front-end
  // engineer will own the UI") are the same move - only pay for a second
  // project when one of those is genuinely true.
  const wantsAppLikeSplit = appLikeUi || externalConsumer || frontendEngineerOwnsUi;
  const tickedBothApiSides = needs.has(4) && needs.has(5);
  if (wantsAppLikeSplit && (tickedBothApiSides || pick.stackId === "django")) {
    pick = RUNGS.reactApi;
    reason = "escalation-d3-app-like-or-external-consumer";
  }

  // Audience modifier (use-cases.md's "Audience adjusts the pick" table),
  // applied last and never touching `needs` itself:
  // - business users who will interact with accounts push the pick up to
  //   Django even if the raw ticks alone read lighter (same reasoning as
  //   D-1, from a different signal - the audience answer rather than a
  //   direct "accounts" flag).
  // - business users who are read-only, when the base pick was Streamlit,
  //   move to Dash - the audience table's read-only row lists "Static D3 or
  //   Dash", never Streamlit, since business users judge by polish.
  if (audience === "business-interactive" && pick.rung < 4) {
    pick = RUNGS.django;
    reason = "audience-business-interactive";
  } else if (audience === "business-readonly" && pick.stackId === "streamlit") {
    pick = RUNGS.dash;
    reason = "audience-business-readonly";
  }

  return { ...pick, reason };
}

/**
 * Convenience wrapper for the Act 3 "shortcut row of the eight documented
 * use cases": looks up a use case's `needs`/flags from advisor-model.json
 * and runs them through recommendStack(), rather than the caller having to
 * re-derive the ticks. `useCase` is one element of advisor-model.json's
 * `useCases` array.
 * @param {Object} useCase
 * @returns {{rung: number, stackId: string, label: string, reason: string}}
 */
export function recommendForUseCase(useCase) {
  const needs = new Set(useCase.needs);
  return recommendStack(needs, useCase.flags ?? {});
}

/**
 * Turns the five SKILL.md intake answers into a functionality tick set, for
 * Act 3's free-form path (as opposed to the eight-use-case shortcut). This
 * is judgment, not a lookup table - SKILL.md's own procedure calls step 2
 * "decompose", not "look up" - so treat this as a reasonable default
 * mapping rather than the load-bearing logic (that's recommendStack()
 * above, which tests/advisor.test.js checks against all eight documented
 * use cases).
 *
 * @param {Object} answers
 * @param {"peers"|"business-readonly"|"business-interactive"} answers.audience
 * @param {"one"|"many-same-data"|"many-different-data"} answers.users
 * @param {boolean} answers.savesAnything
 * @param {boolean} answers.slowerThanFewSeconds
 * @param {boolean} answers.anotherSystemCallsIt
 * @param {boolean} [answers.appLikeUi] - only meaningful when anotherSystemCallsIt is true
 * @returns {{needs: Set<number>, flags: Object}}
 */
export function deriveNeedsFromIntake(answers) {
  const { audience, users, savesAnything, slowerThanFewSeconds, anotherSystemCallsIt, appLikeUi = false } = answers;

  // 1 (presentation) and 2 (styling) are baseline for anything with a page
  // at all; 3 (client interactivity) is baseline for anything that is not
  // pure download-a-file static content, which every use case this advisor
  // covers assumes.
  const needs = new Set([1, 2, 3]);

  const manyWithVisibility = users === "many-different-data";
  if (manyWithVisibility) {
    // Different users seeing different data needs authentication (9),
    // authorization (10), and something to remember who is who between
    // requests (11, session/state).
    needs.add(9).add(10).add(11);
  } else if (users === "many-same-data") {
    // Many users sharing one view still needs *a* server rendering it -
    // captured below via functionality 6, not auth/authz.
  }

  if (savesAnything) {
    // Saving implies both a place to put it (7, persistence) and, in
    // practice, a way to create/edit/delete those records (8, forms/CRUD) -
    // the intake only asks "does it save anything", so this mapping folds
    // both ticks into one "yes".
    needs.add(7).add(8);
  }

  if (slowerThanFewSeconds) {
    needs.add(12); // background and long jobs
  }

  if (anotherSystemCallsIt) {
    needs.add(4); // API: providing
    if (appLikeUi) {
      // Only tick "API: consuming" (5) when this app's own UI is what
      // calls the API - a use case where *only* another system calls it
      // (5's absence) stays a single FastAPI project with no front end of
      // its own, per Rule C step 3's "only accept [two projects] if the UI
      // is app-like or another system needs the API".
      needs.add(5);
    }
  }

  // Functionality 6 (server-side compute) is ticked whenever anything
  // beyond pure static content is needed - any tick already added above
  // beyond the {1,2,3} baseline implies a server is doing work.
  const hasServerSideNeed = [4, 7, 8, 9, 10, 11, 12].some((n) => needs.has(n));
  if (hasServerSideNeed) needs.add(6);

  return {
    needs,
    flags: {
      appLikeUi,
      externalConsumer: anotherSystemCallsIt && !appLikeUi,
      needsAccountsWithDifferentVisibility: manyWithVisibility,
      audience,
    },
  };
}

/**
 * Act 2's build-trail gaps list and Act 3's "flagged gaps" output share
 * this: things the scoring functions above deliberately do NOT account
 * for, because they are cross-cutting rather than rung-driving (SKILL.md's
 * Cautions section, and functionalities.md's "Not covered" list).
 * @param {Set<number>} needs
 * @returns {string[]} human-readable gap/caution strings
 */
export function buildGaps(needs) {
  const gaps = [];
  if (needs.has(12)) {
    gaps.push(
      "Functionality 12 (background/long jobs) is ticked but never changes the rung by itself - see " +
        "references/background-jobs.md. On Windows, RQ has no native support (needs WSL) and Celery has " +
        "dropped Windows support; Huey with SQLite storage is the verified local default.",
    );
  }
  if (needs.has(9) || needs.has(10)) {
    gaps.push(
      "Authorization must be enforced on the server, never just by hiding a button in the client - " +
        "SKILL.md's first Caution.",
    );
  }
  return gaps;
}
