/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        // AI Infrastructure & Research Observability Theme
        canvas: '#0B0F14',
        surface: {
          DEFAULT: '#141E2A',
          secondary: '#101722',
          elevated: '#192536',
          inset: '#0D141D',
        },
        border: {
          DEFAULT: '#263548',
          subtle: '#1E2A39',
          focus: '#3B82F6',
        },
        text: {
          primary: '#F1F5F9',
          secondary: '#A0AEC0',
          muted: '#718096',
        },
        brand: {
          blue: '#3B82F6',
          hover: '#2563EB',
        },
        tier: {
          small: '#34D399',   // Green
          medium: '#F59E0B',  // Amber
          large: '#818CF8',   // Indigo
        },
        mode: {
          real: '#34D399',
          demo: '#3B82F6',
          estimated: '#F59E0B',
          error: '#EF4444',
        }
      },
      animation: {
        'fadeIn': 'fadeIn 0.2s ease-out',
        'slideUp': 'slideUp 0.25s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      }
    },
  },
  plugins: [],
}
