/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // White-dominant palette — violet as sole accent
        surface: {
          DEFAULT: "#ffffff",
          subtle:  "#fafafa",
          raised:  "#f5f5f5",
        },
        border: {
          DEFAULT: "#ebebeb",
          strong:  "#d4d4d4",
        },
        ink: {
          DEFAULT: "#111111",
          muted:   "#737373",
          faint:   "#a3a3a3",
        },
        violet: {
          50:  "#f5f3ff",
          100: "#ede9fe",
          200: "#ddd6fe",
          300: "#c4b5fd",
          400: "#a78bfa",
          500: "#8b5cf6",
          600: "#7c3aed",
          700: "#6d28d9",
          800: "#5b21b6",
          900: "#3b0764",
        },
        // semantic status colours (muted, white-friendly)
        ok:   { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" },
        warn: { bg: "#fffbeb", text: "#b45309", border: "#fde68a" },
        err:  { bg: "#fff1f2", text: "#be123c", border: "#fecdd3" },
        info: { bg: "#f0f9ff", text: "#0369a1", border: "#bae6fd" },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        card:  "0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.04)",
        pop:   "0 4px 16px 0 rgb(0 0 0 / 0.08), 0 1px 4px -1px rgb(0 0 0 / 0.06)",
        glow:  "0 0 0 3px rgb(139 92 246 / 0.15)",
      },
    },
  },
  plugins: [],
}
