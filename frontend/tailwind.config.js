/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          light: "#4da6ff",
          DEFAULT: "#0080ff",
          dark: "#0066cc",
        },
        secondary: {
          light: "#f8fafc",
          DEFAULT: "#f1f5f9",
          dark: "#e2e8f0",
        },
      },
    },
  },
  plugins: [],
};
