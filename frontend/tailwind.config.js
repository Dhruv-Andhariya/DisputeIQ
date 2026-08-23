/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        dark: {
          base: '#070b14',
          card: '#0e1626',
          border: '#1b2a47',
          hover: '#152238',
          accent: '#1e3a8a',
        },
        brand: {
          50: '#eef6ff',
          100: '#e0effe',
          400: '#38bdf8',
          500: '#0284c7',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#0f172a',
        }
      },
      boxShadow: {
        'glow-blue': '0 0 25px -5px rgba(37, 99, 235, 0.25)',
        'glow-rose': '0 0 25px -5px rgba(244, 63, 94, 0.25)',
        'glow-emerald': '0 0 25px -5px rgba(16, 185, 129, 0.25)',
        'glow-amber': '0 0 25px -5px rgba(245, 158, 11, 0.25)',
      }
    },
  },
  plugins: [],
}
