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
        primary: {
          50:  'rgb(var(--color-primary-50) / <alpha-value>)',
          100: 'rgb(var(--color-primary-100) / <alpha-value>)',
          200: 'rgb(var(--color-primary-200) / <alpha-value>)',
          300: 'rgb(var(--color-primary-300) / <alpha-value>)',
          400: 'rgb(var(--color-primary-400) / <alpha-value>)',
          500: 'rgb(var(--color-primary-500) / <alpha-value>)',
          600: 'rgb(var(--color-primary-600) / <alpha-value>)',
          700: 'rgb(var(--color-primary-700) / <alpha-value>)',
          800: 'rgb(var(--color-primary-800) / <alpha-value>)',
          900: 'rgb(var(--color-primary-900) / <alpha-value>)',
          950: 'rgb(var(--color-primary-950) / <alpha-value>)',
          DEFAULT: 'rgb(var(--color-primary-600) / <alpha-value>)',
        },
        violet: {
          50:  'rgb(var(--color-primary-50) / <alpha-value>)',
          100: 'rgb(var(--color-primary-100) / <alpha-value>)',
          200: 'rgb(var(--color-primary-200) / <alpha-value>)',
          300: 'rgb(var(--color-primary-300) / <alpha-value>)',
          400: 'rgb(var(--color-primary-400) / <alpha-value>)',
          500: 'rgb(var(--color-primary-500) / <alpha-value>)',
          600: 'rgb(var(--color-primary-600) / <alpha-value>)',
          700: 'rgb(var(--color-primary-700) / <alpha-value>)',
          800: 'rgb(var(--color-primary-800) / <alpha-value>)',
          900: 'rgb(var(--color-primary-900) / <alpha-value>)',
          950: 'rgb(var(--color-primary-950) / <alpha-value>)',
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
        glow:  "0 0 0 3px rgb(var(--color-primary-500) / 0.15)",
      },
    },
  },
  plugins: [],
}
