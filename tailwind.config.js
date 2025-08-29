/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4F46E5', // indigo-600
          dark: '#4338CA', // indigo-700
        },
        secondary: '#1F2937', // gray-900
        text: '#374151', // gray-700
        background: '#F9FAFB', // gray-50
        border: '#D1D5DB', // gray-300
        success: '#16A34A', // green-600
        danger: '#DC2626', // red-600
        warning: '#F59E0B', // yellow-500
        info: '#3B82F6', // blue-500
      },
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}