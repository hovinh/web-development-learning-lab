# A pretty but standard UI for a prototype

Raw Tailwind gives utility classes, not a design. A "standard" look needs a
**component kit** on top. Tailwind is only styling, so it works with static HTML,
Django templates, React or Angular.

| Option | Good for | Cost |
|---|---|---|
| **Django templates + Tailwind + daisyUI** (or Flowbite) | A data-team prototype with a clean look. Buttons, cards, tables and navbars are class names. No React, no JS component build | Small. Recommended default |
| **React + Tailwind + shadcn/ui** | Best-looking, most customisable, matches what product teams use | Highest setup |
| **Dash + dash-bootstrap-components** | Tidy dashboards out of the box | Low |
| **Streamlit defaults** | Acceptable look with zero work | Little theming control |
| **Django admin** | Back-office screens (manage users, export labels) | Nearly none |

## Recommendation

For a data professional's product prototype: **Django templates + Tailwind + daisyUI**,
plus the Django admin for internal screens. Move to React + shadcn/ui only when the
UI needs app-like interaction.

## Build-step note

Tailwind normally needs Node to compile. Two ways around it:

- The **standalone CLI** (a single executable, no Node), or `pip install pytailwindcss`.
- The **browser build** via CDN for a quick prototype (needs internet; not for anything
  you keep).

daisyUI 5 is designed for Tailwind 4 and is configured in CSS (`@plugin "daisyui";`).
Getting it to work with the *standalone* CLI, without npm, was not verified; check the
daisyUI docs, or use the CDN build for a prototype. See `tools/tailwind.md`.
