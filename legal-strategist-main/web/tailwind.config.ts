import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      fontFamily: {
        arial: ['Arial', 'sans-serif'],
      },
      animation: {
        shake: "shake 0.5s ease-in-out",
      },
      keyframes: {
        shake: {
          "0%": {
            transform: "translateX(0)",
          },
          "25%": {
            transform: "translateX(-2px)",
          },
          "50%": {
            transform: "translateX(2px)",
          },
          "75%": {
            transform: "translateX(-2px)",
          },
          "100%": {
            transform: "translateX(0)",
          }
        }
      },
    },
  },
  plugins: [],
};
export default config;
