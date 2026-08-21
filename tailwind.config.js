/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0B0F19',
          900: '#111726',
          800: '#1A2236',
          700: '#242E45',
        },
        brand: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          400: '#818CF8',
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA',
        },
        accent: {
          500: '#7C3AED',
          600: '#6D28D9',
        },
        neon: {
          cyan: '#22D3EE',
          violet: '#A855F7',
          magenta: '#F472B6',
          lime: '#84CC16',
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 2px 0 rgba(16, 24, 40, 0.05), 0 1px 3px 0 rgba(16, 24, 40, 0.06)',
        glowCyan: '0 0 0 1px rgba(34,211,238,0.25), 0 0 24px rgba(34,211,238,0.25)',
        glowViolet: '0 0 0 1px rgba(168,85,247,0.25), 0 0 24px rgba(168,85,247,0.25)',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: 1, transform: 'scale(1)' },
          '50%': { opacity: 0.6, transform: 'scale(1.15)' },
        },
        radarSpin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
      animation: {
        pulseGlow: 'pulseGlow 2s ease-in-out infinite',
        radarSpin: 'radarSpin 3s linear infinite',
        scanline: 'scanline 2.4s ease-in-out infinite',
        gradientShift: 'gradientShift 6s ease infinite',
      },
    },
  },
  plugins: [],
}
