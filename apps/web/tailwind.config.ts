import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0F172A",
        sand: "#F8FAFC",
        accent: "#F97316",
        accentDark: "#EA580C",
      },
      boxShadow: {
        soft: "0 20px 60px rgba(15, 23, 42, 0.15)",
      },
      fontFamily: {
        display: ["var(--font-space)", "system-ui", "sans-serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
