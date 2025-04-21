/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#A4D65A',  // Light green
          DEFAULT: '#8CC63F',  // Green from reference image
          dark: '#72A62E',  // Dark green
        },
        background: '#2B2D42',  // Dark blue-gray for background exactly matching reference
        surface: '#3D405B',  // Slightly lighter for cards exactly matching reference
        warning: '#FFC107',  // Amber exactly matching reference
        danger: '#EF4444',  // Red exactly matching reference
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  safelist: [
    'text-warning',
    'text-green-500',
    'bg-primary',
    'bg-surface',
    'bg-warning',
    'bg-green-900/20',
    'bg-red-900/20',
    'text-green-400',
    'text-red-400',
  ],
  plugins: [],
}; 