/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Verde principal (comunidad, naturaleza, identidad)
        primary: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a', // default
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        // Marron (tierra, comunidad campesina, calidez)
        secondary: {
          50:  '#faf7f2',
          100: '#f0e9d9',
          200: '#e0d2b3',
          300: '#cdb78a',
          400: '#b89768',
          500: '#a17e4f',
          600: '#8b6f47', // default
          700: '#6e5839',
          800: '#523f29',
          900: '#382a1c',
          950: '#1d150e',
        },
        // Dorado (acentos premium, CTAs importantes, admin)
        accent: {
          50:  '#fdf9e7',
          100: '#faf0c1',
          200: '#f5e08a',
          300: '#eecb53',
          400: '#e2b52a',
          500: '#c89d22',
          600: '#b8972a', // default
          700: '#94771f',
          800: '#70591a',
          900: '#4d3d11',
        },
        // Estados
        success: '#16a34a',
        warning: '#b8972a',
        danger:  '#b91c1c',
        info:    '#15803d',
        // Colores semánticos de texto
        mute:  '#6b7280',
        soft:  '#9ca3af',
      },
      fontFamily: {
        sans:  ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['"Playfair Display"', 'Georgia', 'serif'],
      },
      borderRadius: {
        'sm':  '0.25rem',
        DEFAULT: '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
      },
      boxShadow: {
        'card': '0 8px 32px rgba(10, 61, 31, 0.12), 0 2px 8px rgba(10, 61, 31, 0.06)',
        'card-hover': '0 12px 40px rgba(10, 61, 31, 0.18), 0 4px 12px rgba(10, 61, 31, 0.10)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)',     opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
