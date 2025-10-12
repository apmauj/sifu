/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Legacy colors (mantener compatibilidad temporal)
        'uruguay-blue': '#0038a8',
        'uruguay-yellow': '#ffd700',
        'uruguay-white': '#ffffff',
        
        // ⭐ NUEVO: Primary color con CSS variables (dinámico según tema)
        primary: {
          50: 'var(--color-primary-50, hsl(220, 100%, 97%))',
          100: 'var(--color-primary-100, hsl(220, 100%, 93%))',
          200: 'var(--color-primary-200, hsl(220, 100%, 86%))',
          300: 'var(--color-primary-300, hsl(220, 100%, 76%))',
          400: 'var(--color-primary-400, hsl(220, 100%, 66%))',
          500: 'var(--color-primary-500, hsl(220, 100%, 56%))',
          600: 'var(--color-primary-600, hsl(220, 100%, 46%))',
          700: 'var(--color-primary-700, hsl(220, 100%, 36%))',
          800: 'var(--color-primary-800, hsl(220, 95%, 26%))',
          900: 'var(--color-primary-900, hsl(220, 90%, 16%))',
          950: 'var(--color-primary-950, hsl(220, 85%, 10%))',
        },
        
        // ⭐ NUEVO: Neutral colors (ex-grays) con CSS variables
        // Estos cambian según el tema activo:
        // - Tema default: grays fríos (tinte azul)
        // - Tema warm: grays cálidos (tinte sepia)
        // - Tema cool: grays muy fríos (blue-gray)
        neutral: {
          50: 'var(--color-neutral-50, #f9fafb)',
          100: 'var(--color-neutral-100, #f3f4f6)',
          200: 'var(--color-neutral-200, #e5e7eb)',
          300: 'var(--color-neutral-300, #d1d5db)',
          400: 'var(--color-neutral-400, #9ca3af)',
          500: 'var(--color-neutral-500, #6b7280)',
          600: 'var(--color-neutral-600, #4b5563)',
          700: 'var(--color-neutral-700, #374151)',
          800: 'var(--color-neutral-800, #1f2937)',
          900: 'var(--color-neutral-900, #111827)',
          950: 'var(--color-neutral-950, #030712)',
        },
        
        // Secondary, accent, success, error mantienen valores fijos
        // (no cambian con el tema de color)
        secondary: {
          50: 'hsl(25, 88%, 97%)',    // #fef5f0
          100: 'hsl(25, 88%, 93%)',   // #fde8d9
          200: 'hsl(25, 88%, 85%)',   // #fbd2b3
          300: 'hsl(25, 88%, 75%)',   // #f8b580
          400: 'hsl(25, 88%, 65%)',   // #f5984d
          500: 'hsl(25, 88%, 55%)',   // #f27b1a
          600: 'hsl(25, 85%, 48%)',   // #e06609
          700: 'hsl(25, 82%, 40%)',   // #b85207
          800: 'hsl(25, 78%, 32%)',   // #8f4106
          900: 'hsl(25, 74%, 24%)',   // #663004
          950: 'hsl(25, 70%, 16%)',   // #441f03
        },
        accent: {
          50: 'hsl(190, 85%, 97%)',   // #f0fbfe
          100: 'hsl(190, 85%, 92%)',  // #d4f5fc
          200: 'hsl(190, 85%, 84%)',  // #a9ebf9
          300: 'hsl(190, 85%, 72%)',  // #6dd9f3
          400: 'hsl(190, 85%, 60%)',  // #31c7ed
          500: 'hsl(190, 85%, 48%)',  // #0db0db
          600: 'hsl(190, 82%, 40%)',  // #0a8fb3
          700: 'hsl(190, 78%, 32%)',  // #08708a
          800: 'hsl(190, 74%, 24%)',  // #065161
          900: 'hsl(190, 70%, 16%)',  // #04333d
          950: 'hsl(190, 66%, 10%)',  // #021e26
        },
        success: {
          50: 'hsl(145, 70%, 97%)',   // #f0fcf5
          100: 'hsl(145, 70%, 92%)',  // #d6f9e3
          200: 'hsl(145, 70%, 83%)',  // #aef3c7
          300: 'hsl(145, 70%, 70%)',  // #75e9a3
          400: 'hsl(145, 70%, 57%)',  // #3ddf7f
          500: 'hsl(145, 65%, 47%)',  // #1fc965
          600: 'hsl(145, 60%, 40%)',  // #19a852
          700: 'hsl(145, 55%, 32%)',  // #14843f
          800: 'hsl(145, 50%, 24%)',  // #0f602d
          900: 'hsl(145, 45%, 16%)',  // #0a3d1c
          950: 'hsl(145, 40%, 10%)',  // #062411
        },
        error: {
          50: 'hsl(355, 75%, 97%)',   // #fef0f1
          100: 'hsl(355, 75%, 93%)',  // #fcd9dc
          200: 'hsl(355, 75%, 85%)',  // #f9b3ba
          300: 'hsl(355, 75%, 73%)',  // #f5808b
          400: 'hsl(355, 75%, 61%)',  // #f14d5c
          500: 'hsl(355, 70%, 52%)',  // #e62838
          600: 'hsl(355, 68%, 45%)',  // #c91f2d
          700: 'hsl(355, 65%, 37%)',  // #a31924
          800: 'hsl(355, 62%, 29%)',  // #7d131b
          900: 'hsl(355, 58%, 21%)',  // #571012
          950: 'hsl(355, 54%, 13%)',  // #320a0b
        },
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
} 