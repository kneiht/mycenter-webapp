/** @type {import('tailwindcss').Config} */

module.exports = {
  content: ["../templates/**/*.{html,js}"],
  darkMode: 'class',
  plugins: [require("@tailwindcss/forms"),require('tailwind-scrollbar'),],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', 'sans-serif'], // Roboto with a sans-serif fallback
      },
      colors: {
        'theme': {
            '50': '#ecfdff',
            '100': '#d0f6fd',
            '200': '#a7edfa',
            '300': '#6addf6',
            '400': '#26c3ea',
            '500': '#0aa6d0',
            '600': '#0c85ae',
            '700': '#116a8d',
            '800': '#175773',
            '900': '#184861',
            '950': '#092e43',
            '1000': '#020f17',
        },
        // You can add more custom colors here
      },
      height: {
        '1px': '1px',
      },

    },
    screens: {
      'sm': '640px',
      'lg': '1024px',
      'xl': '1280px',
      // => @media (min-width: 1280px) { ... }
      '2xl': '1536px',
      // => @media (min-width: 1536px) { ... }
    }
  },
}


