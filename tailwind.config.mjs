import typography from '@tailwindcss/typography';

export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Navy istituzionale - Autorevolezza e credibilità
        navy: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#1e3a5f', // Primary
          900: '#102a43',
        },
        // Ambra siciliana - Identità, calore
        amber: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706', // Accent
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        // Verde salvia - Trasparenza, positività
        sage: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#059669', // Success
          900: '#047857',
        },
        // Grigi caldi
        warm: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Manrope', 'system-ui', 'sans-serif'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: '#292524',
            a: {
              color: '#1e3a5f',
              fontWeight: '600',
              textDecoration: 'underline',
              textDecorationColor: '#d97706',
              textUnderlineOffset: '3px',
              '&:hover': {
                color: '#d97706',
              },
            },
            h1: {
              fontFamily: 'Fraunces, Georgia, serif',
              fontWeight: '700',
            },
            h2: {
              fontFamily: 'Fraunces, Georgia, serif',
              fontWeight: '700',
            },
            h3: {
              fontFamily: 'Fraunces, Georgia, serif',
              fontWeight: '600',
            },
          },
        },
      },
      backgroundImage: {
        'grid-pattern': "url(\"data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h60v60H0z' fill='none'/%3E%3Cpath d='M0 0h1v60H0zM60 0v1H0V0z' fill='%23e7e5e4' fill-opacity='0.4'/%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [typography],
};
