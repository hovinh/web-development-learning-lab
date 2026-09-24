import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
//
// @tailwindcss/vite (not the standalone Tailwind CLI demos/labeling-django
// uses) is Tailwind 4's official Vite integration - it scans this
// project's source files at build/dev time and only ships the utility
// classes actually used, unlike demos/labeling-django's CDN browser
// build. See ../README.md's "Styling" section for that contrast.
export default defineConfig({
  plugins: [react(), tailwindcss()],
})
