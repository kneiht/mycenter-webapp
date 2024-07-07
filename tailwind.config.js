/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}","./static/js/**/*.{html,js}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'theme': {
          '50': '#f0f8ff',
          '100': '#e1f1fd',
          '200': '#bbe3fc',
          '300': '#80cdf9',
          '400': '#3cb4f4',
          '500': '#1299e5',
          '600': '#067cc6',
          '700': '#06619e',
          '800': '#0a5382',
          '900': '#0e456c',
          '950': '#092c48',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    // ...
  ],
}



