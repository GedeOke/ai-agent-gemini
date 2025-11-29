/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",
        "primary-dark": "#1d4ed8",
      },
      boxShadow: {
        soft: "0 10px 40px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
};
