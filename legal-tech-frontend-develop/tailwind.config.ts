import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  safelist: [
    'bg-cyan-100', 'bg-cyan-500',
    'bg-green-100', 'bg-green-500',
    'bg-red-100', 'bg-red-500',
    'bg-gray-200', 'bg-gray-300', 'bg-gray-400', 'bg-gray-500', 'bg-gray-600', 'bg-gray-700',
    'bg-[#DEECF8]', 'bg-[#BFE4A8]', 'bg-[#F7C6AE]', 'bg-[#D7D7D7]', 'bg-[#6E6E6E]', 'bg-[#A6A6A6]', 'bg-[#E6D8F8]',
    'bg-[#DEECF8]/80', 'bg-[#BFE4A8]/80', 'bg-[#F7C6AE]/80', 'bg-[#D7D7D7]/80', 'bg-[#6E6E6E]/80', 'bg-[#A6A6A6]/80', 'bg-[#E6D8F8]/80',
    'bg-[#DEECF8]/60', 'bg-[#BFE4A8]/60', 'bg-[#F7C6AE]/60', 'bg-[#D7D7D7]/60', 'bg-[#6E6E6E]/60', 'bg-[#A6A6A6]/60', 'bg-[#E6D8F8]/60'
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // Paleta minimalista y profesional
        'pure-white': '#FFFFFF',
        'light-gray': '#F5F5F5',
        'medium-gray': '#B0B0B0',
        'petroleum-blue': '#1C3D5A',
        'charcoal-gray': '#2B2B2B',
        'teal-green': '#2A9D8F',
        'soft-gold': '#C5A46D',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'serif': ['Merriweather', 'Georgia', 'serif'],
        'arial': ['Arial', 'sans-serif'],
      },
      fontSize: {
        // Jerarquía tipográfica profesional
        'h1': ['2.5rem', { lineHeight: '1.2', fontWeight: '700' }], // 40px
        'h2': ['1.75rem', { lineHeight: '1.3', fontWeight: '600' }], // 28px
        'h3': ['1.375rem', { lineHeight: '1.4', fontWeight: '600' }], // 22px
        'body': ['1.125rem', { lineHeight: '1.6', fontWeight: '400' }], // 18px
        'body-sm': ['1rem', { lineHeight: '1.5', fontWeight: '400' }], // 16px
        'small': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }], // 14px
        'button': ['1rem', { lineHeight: '1.5', fontWeight: '500' }], // 16px
      },
      lineHeight: {
        'relaxed': '1.6',
        'comfortable': '1.5',
      },
      letterSpacing: {
        'wide': '0.5px',
        'wider': '1px',
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
