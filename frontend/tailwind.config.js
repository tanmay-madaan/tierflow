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
        canvas: '#0B0F14',
        panel: '#121923',
        'panel-subtle': '#161F2C',
        'panel-inset': '#0E141C',
        'panel-raised': '#1A2431',
        'border-subtle': '#1F2937',
        'border-default': '#293545',
        'border-active': '#3B82F6',
        tierflow: {
          bg: '#0B0F14',
          panel: '#121923',
          raised: '#1A2431',
          accent: '#3B82F6',
          text: '#F1F5F9',
          muted: '#94A3B8',
          success: '#34D399',
          border: '#293545',
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
