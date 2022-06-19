/** @type {import('tailwindcss').Config} */
module.exports = {
  tailwindcss: {},
  autoprefixer: {},
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
}
