/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0b0f14',
        panel: '#111820',
        panel2: '#17212b',
        line: '#273443',
        soft: '#93a4b8',
        text: '#e5edf7',
        accent: '#6aa6ff',
        green: '#49d17c',
        red: '#ff6b6b',
        yellow: '#f6c85f',
        cyan: '#58d7d3'
      },
      boxShadow: {
        panel: '0 18px 60px rgba(0, 0, 0, .28)'
      }
    },
  },
  plugins: [],
};
