/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        teal: {
          50:  '#E8F2F2',
          100: '#D0E8E8',
          600: '#1A6B6B',
          700: '#145858',
          800: '#0F4444',
        },
        amber: {
          50:  '#FEF3C7',
          400: '#F59E0B',
          600: '#D97706',
        },
      },
      fontFamily: {
        serif: ['"DM Serif Display"', 'serif'],
        sans:  ['"DM Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
