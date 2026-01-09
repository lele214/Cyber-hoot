/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js"
  ],
  safelist: [
    {
      pattern: /(bg|text|border)-(cyber)-(bg|text|border|accent|error|success)(-light|-lighter|-bright|-muted|-dark|-bg|-border)?/,
    },
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#667eea',
          dark: '#764ba2',
        },
        cyber: {
          bg: '#0f1f0f',
          'bg-light': '#1a2a1a',
          'bg-lighter': '#1a3a1a',
          border: '#2a4a2a',
          'border-light': '#3a5a3a',
          'border-lighter': '#4a6a4a',
          text: '#a8c4a0',
          'text-light': '#b8d8b0',
          'text-lighter': '#c8e8c0',
          'text-bright': '#d8f8d0',
          'text-muted': '#8a9a8a',
          'text-dark': '#6a8a6a',
          accent: '#5a7a5a',
          'accent-light': '#6a8a6a',
          error: '#ff9999',
          'error-bg': 'rgba(180, 50, 50, 0.2)',
          'error-border': 'rgba(180, 50, 50, 0.5)',
          success: '#c8f8c0',
          'success-bg': 'rgba(100, 180, 100, 0.2)',
          'success-border': 'rgba(100, 180, 100, 0.5)',
        }
      },
      fontFamily: {
        'mono': ['Share Tech Mono', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 10px rgba(100, 180, 100, 0.5), 0 0 20px rgba(100, 180, 100, 0.3)',
        'glow-sm': '0 0 15px rgba(100, 180, 100, 0.3)',
        'glow-md': '0 0 20px rgba(100, 180, 100, 0.3)',
        'glow-lg': '0 0 25px rgba(100, 180, 100, 0.15)',
        'glow-xl': '0 0 30px rgba(100, 180, 100, 0.4)',
      },
    },
  },
  plugins: [],
}
