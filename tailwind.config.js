/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Montserrat', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      colors: {
        'primary': {
          50: '#e6f5ff',
          100: '#cce9ff',
          200: '#99d2ff',
          300: '#66bcff',
          400: '#33a5ff',
          500: '#0088ff',
          600: '#006dcc',
          700: '#005299',
          800: '#003666',
          900: '#001b33',
        },
        'secondary': {
          50: '#fff7e6',
          100: '#ffefc9',
          200: '#ffe093',
          300: '#ffd05d',
          400: '#ffc126',
          500: '#f0b000',
          600: '#cc9600',
          700: '#997100',
          800: '#664b00',
          900: '#332600',
        },
        'accent': {
          50: '#f5e6ff',
          100: '#e8ccff',
          200: '#d199ff',
          300: '#ba66ff',
          400: '#a333ff',
          500: '#9000ff',
          600: '#7300cc',
          700: '#560099',
          800: '#390066',
          900: '#1c0033',
        },
        'success': {
          500: '#10B981',
          600: '#059669',
        },
        'danger': {
          500: '#EF4444',
          600: '#DC2626',
        },
        'warning': {
          500: '#F59E0B',
          600: '#D97706',
        },
        'info': {
          500: '#3B82F6',
          600: '#2563EB',
        },
      },
      boxShadow: {
        'elevation-1': '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
        'elevation-2': '0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23)',
        'elevation-3': '0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23)',
        'elevation-4': '0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22)',
        'elevation-5': '0 19px 38px rgba(0, 0, 0, 0.30), 0 15px 12px rgba(0, 0, 0, 0.22)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    function({ addUtilities }) {
      const newUtilities = {
        '.gradient-primary': {
          background: 'linear-gradient(135deg, var(--tw-gradient-stops))',
          '--tw-gradient-from': '#0088ff',
          '--tw-gradient-to': '#006dcc',
          '--tw-gradient-stops': 'var(--tw-gradient-from), var(--tw-gradient-to)',
        },
        '.gradient-secondary': {
          background: 'linear-gradient(135deg, var(--tw-gradient-stops))',
          '--tw-gradient-from': '#ffc126',
          '--tw-gradient-to': '#cc9600',
          '--tw-gradient-stops': 'var(--tw-gradient-from), var(--tw-gradient-to)',
        },
        '.gradient-accent': {
          background: 'linear-gradient(135deg, var(--tw-gradient-stops))',
          '--tw-gradient-from': '#a333ff',
          '--tw-gradient-to': '#7300cc',
          '--tw-gradient-stops': 'var(--tw-gradient-from), var(--tw-gradient-to)',
        },
        '.hover-lift': {
          transition: 'transform 0.3s ease-in-out',
        },
        '.hover-lift:hover': {
          transform: 'translateY(-5px)',
        },
        '.line-clamp-1': {
          overflow: 'hidden',
          display: '-webkit-box',
          '-webkit-box-orient': 'vertical',
          '-webkit-line-clamp': '1',
        },
        '.line-clamp-2': {
          overflow: 'hidden',
          display: '-webkit-box',
          '-webkit-box-orient': 'vertical',
          '-webkit-line-clamp': '2',
        },
        '.line-clamp-3': {
          overflow: 'hidden',
          display: '-webkit-box',
          '-webkit-box-orient': 'vertical',
          '-webkit-line-clamp': '3',
        },
      };
      
      addUtilities(newUtilities, ['responsive', 'hover']);
    },
  ],
} 