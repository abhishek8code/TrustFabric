/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 40px rgba(59, 130, 246, 0.18)",
      },
      fontFamily: {
        display: ["Inter", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
};
