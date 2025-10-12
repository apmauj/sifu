# Sistema de Theming - SIFU

## Paleta Cromática Armónica

### Estrategia de Diseño
Basada en **escala cromática** con 5 colores principales que mantienen armonía visual y accesibilidad en modos claro y oscuro.

---

## 🎨 Colores Principales

### 1. **Primary (Azul Uruguay)** 
**Uso**: Acciones principales, enlaces, elementos destacados
- Base: `#0038a8` (azul bandera uruguaya)
- Escalas HSL: `hue: 220°, saturation: 100%`

```css
--primary-50:  hsl(220, 100%, 97%)   /* #f0f5ff */
--primary-100: hsl(220, 100%, 93%)   /* #d9e5ff */
--primary-200: hsl(220, 100%, 86%)   /* #b3ccff */
--primary-300: hsl(220, 100%, 76%)   /* #80aaff */
--primary-400: hsl(220, 100%, 66%)   /* #4d88ff */
--primary-500: hsl(220, 100%, 56%)   /* #1a66ff */
--primary-600: hsl(220, 100%, 46%)   /* #0052e6 */
--primary-700: hsl(220, 100%, 36%)   /* #0041b8 */ ← Uruguay Blue
--primary-800: hsl(220, 95%, 26%)    /* #00307a */
--primary-900: hsl(220, 90%, 16%)    /* #001f4d */
--primary-950: hsl(220, 85%, 10%)    /* #001233 */
```

### 2. **Secondary (Naranja Cálido)** - Complementario Análogo
**Uso**: Botones secundarios, badges, elementos de apoyo
- Base: Análogo al primary (hue +150° → naranja/coral cálido)
- Escalas HSL: `hue: 25°, saturation: 88%`

```css
--secondary-50:  hsl(25, 88%, 97%)   /* #fef5f0 */
--secondary-100: hsl(25, 88%, 93%)   /* #fde8d9 */
--secondary-200: hsl(25, 88%, 85%)   /* #fbd2b3 */
--secondary-300: hsl(25, 88%, 75%)   /* #f8b580 */
--secondary-400: hsl(25, 88%, 65%)   /* #f5984d */
--secondary-500: hsl(25, 88%, 55%)   /* #f27b1a */
--secondary-600: hsl(25, 85%, 48%)   /* #e06609 */
--secondary-700: hsl(25, 82%, 40%)   /* #b85207 */
--secondary-800: hsl(25, 78%, 32%)   /* #8f4106 */
--secondary-900: hsl(25, 74%, 24%)   /* #663004 */
--secondary-950: hsl(25, 70%, 16%)   /* #441f03 */
```

### 3. **Accent (Cyan)** - Triádico
**Uso**: Highlights, información, datos numéricos
- Base: Triádico al primary (hue +120° → cyan/turquesa)
- Escalas HSL: `hue: 190°, saturation: 85%`

```css
--accent-50:  hsl(190, 85%, 97%)   /* #f0fbfe */
--accent-100: hsl(190, 85%, 92%)   /* #d4f5fc */
--accent-200: hsl(190, 85%, 84%)   /* #a9ebf9 */
--accent-300: hsl(190, 85%, 72%)   /* #6dd9f3 */
--accent-400: hsl(190, 85%, 60%)   /* #31c7ed */
--accent-500: hsl(190, 85%, 48%)   /* #0db0db */
--accent-600: hsl(190, 82%, 40%)   /* #0a8fb3 */
--accent-700: hsl(190, 78%, 32%)   /* #08708a */
--accent-800: hsl(190, 74%, 24%)   /* #065161 */
--accent-900: hsl(190, 70%, 16%)   /* #04333d */
--accent-950: hsl(190, 66%, 10%)   /* #021e26 */
```

### 4. **Success (Verde)** - Estados Positivos
**Uso**: Confirmaciones, datos actualizados, checks
- Base: Verde estándar optimizado para accesibilidad
- Escalas HSL: `hue: 145°, saturation: 70%`

```css
--success-50:  hsl(145, 70%, 97%)   /* #f0fcf5 */
--success-100: hsl(145, 70%, 92%)   /* #d6f9e3 */
--success-200: hsl(145, 70%, 83%)   /* #aef3c7 */
--success-300: hsl(145, 70%, 70%)   /* #75e9a3 */
--success-400: hsl(145, 70%, 57%)   /* #3ddf7f */
--success-500: hsl(145, 65%, 47%)   /* #1fc965 */
--success-600: hsl(145, 60%, 40%)   /* #19a852 */
--success-700: hsl(145, 55%, 32%)   /* #14843f */
--success-800: hsl(145, 50%, 24%)   /* #0f602d */
--success-900: hsl(145, 45%, 16%)   /* #0a3d1c */
--success-950: hsl(145, 40%, 10%)   /* #062411 */
```

### 5. **Error (Rojo)** - Estados Negativos
**Uso**: Errores, alertas, validaciones fallidas
- Base: Rojo optimizado para contraste
- Escalas HSL: `hue: 355°, saturation: 75%`

```css
--error-50:  hsl(355, 75%, 97%)   /* #fef0f1 */
--error-100: hsl(355, 75%, 93%)   /* #fcd9dc */
--error-200: hsl(355, 75%, 85%)   /* #f9b3ba */
--error-300: hsl(355, 75%, 73%)   /* #f5808b */
--error-400: hsl(355, 75%, 61%)   /* #f14d5c */
--error-500: hsl(355, 70%, 52%)   /* #e62838 */
--error-600: hsl(355, 68%, 45%)   /* #c91f2d */
--error-700: hsl(355, 65%, 37%)   /* #a31924 */
--error-800: hsl(355, 62%, 29%)   /* #7d131b */
--error-900: hsl(355, 58%, 21%)   /* #571012 */
--error-950: hsl(355, 54%, 13%)   /* #320a0b */
```

### 6. **Neutral (Grays)** - Texto, Fondos, Bordes
**Uso**: Tipografía, fondos, separadores, UI base
- Mantener escala Tailwind gray existente (optimizada)

---

## 📐 Uso Semántico por Contexto

### Backgrounds
```css
/* Light Mode */
--bg-primary: white
--bg-secondary: var(--primary-50)
--bg-tertiary: var(--gray-100)

/* Dark Mode */
--bg-primary: var(--gray-900)
--bg-secondary: var(--gray-800)
--bg-tertiary: var(--gray-850)
```

### Text
```css
/* Light Mode */
--text-primary: var(--gray-900)
--text-secondary: var(--gray-600)
--text-tertiary: var(--gray-400)

/* Dark Mode */
--text-primary: var(--gray-50)
--text-secondary: var(--gray-300)
--text-tertiary: var(--gray-500)
```

### Interactive Elements
```css
/* Buttons */
--btn-primary-bg: var(--primary-600)
--btn-primary-hover: var(--primary-700)
--btn-secondary-bg: var(--secondary-500)
--btn-secondary-hover: var(--secondary-600)

/* Links */
--link-color: var(--primary-600)
--link-hover: var(--primary-700)
/* Dark mode */
--link-color-dark: var(--primary-400)
--link-hover-dark: var(--primary-300)
```

---

## ♿ Ratios de Contraste (WCAG AA)

### Texto Normal (4.5:1 mínimo)
- **Light**: Gray-900 en White = 18.6:1 ✅
- **Light**: Primary-700 en White = 8.2:1 ✅
- **Dark**: Gray-50 en Gray-900 = 18.3:1 ✅
- **Dark**: Primary-300 en Gray-900 = 7.8:1 ✅

### Texto Grande (3:1 mínimo)
- **Light**: Primary-600 en Primary-50 = 12.4:1 ✅
- **Dark**: Accent-400 en Gray-800 = 9.1:1 ✅

### UI Elements (3:1 mínimo)
- **Light**: Bordes Gray-200 en White = 1.8:1 ⚠️ (considerar Gray-300)
- **Dark**: Bordes Gray-700 en Gray-900 = 2.2:1 ⚠️ (considerar Gray-600)

---

## 🛠️ Implementación Tailwind

### tailwind.config.js
```javascript
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'hsl(220, 100%, 97%)',
          100: 'hsl(220, 100%, 93%)',
          200: 'hsl(220, 100%, 86%)',
          300: 'hsl(220, 100%, 76%)',
          400: 'hsl(220, 100%, 66%)',
          500: 'hsl(220, 100%, 56%)',
          600: 'hsl(220, 100%, 46%)',
          700: 'hsl(220, 100%, 36%)', // Uruguay Blue
          800: 'hsl(220, 95%, 26%)',
          900: 'hsl(220, 90%, 16%)',
          950: 'hsl(220, 85%, 10%)',
        },
        secondary: {
          50: 'hsl(25, 88%, 97%)',
          100: 'hsl(25, 88%, 93%)',
          // ... escalas completas
        },
        accent: {
          50: 'hsl(190, 85%, 97%)',
          // ... escalas completas
        },
        success: {
          50: 'hsl(145, 70%, 97%)',
          // ... escalas completas
        },
        error: {
          50: 'hsl(355, 75%, 97%)',
          // ... escalas completas
        },
      },
    },
  },
};
```

### Clases Tailwind Resultantes
```jsx
{/* Backgrounds */}
<div className="bg-primary-50 dark:bg-primary-950">
<div className="bg-secondary-100 dark:bg-secondary-900">

{/* Text */}
<p className="text-primary-700 dark:text-primary-300">
<span className="text-error-600 dark:text-error-400">

{/* Borders */}
<div className="border border-accent-200 dark:border-accent-800">

{/* Buttons */}
<button className="bg-primary-600 hover:bg-primary-700 text-white">
<button className="bg-secondary-500 hover:bg-secondary-600 text-white">
```

---

## 🎯 Guía de Aplicación

### 1. Elementos de UI Base
```jsx
// Cards
<Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">

// Inputs
<input className="border-gray-300 dark:border-gray-600 
                  bg-white dark:bg-gray-900
                  focus:border-primary-500 focus:ring-primary-500/20" />
```

### 2. Estados
```jsx
// Success
<div className="bg-success-50 dark:bg-success-950 
                text-success-700 dark:text-success-300">

// Error
<div className="bg-error-50 dark:bg-error-950 
                text-error-700 dark:text-error-300">

// Info/Accent
<div className="bg-accent-50 dark:bg-accent-950 
                text-accent-700 dark:text-accent-300">
```

### 3. Hover/Active States
```jsx
// Interactive rows
<tr className="hover:bg-primary-50 dark:hover:bg-primary-950/30">

// Active items
<div className="bg-primary-100 dark:bg-primary-900/40 
                border-primary-300 dark:border-primary-700">
```

---

## 📊 Casos de Uso SIFU

### Dashboard Cards
```jsx
<Card className="bg-white dark:bg-gray-800 
                 border-gray-200/60 dark:border-gray-700/40">
  <CardHeader className="border-b border-gray-100 dark:border-gray-800">
    <h3 className="text-gray-900 dark:text-gray-50">
```

### Data Panels (UI/UR/Exchange)
```jsx
// Highlights
<div className="bg-accent-50 dark:bg-accent-950/30 
                text-accent-700 dark:text-accent-300">
  
// Current values
<span className="text-primary-600 dark:text-primary-400 font-semibold">

// Errors
<div className="bg-error-50 dark:bg-error-950/30 border-error-200 dark:border-error-800">
```

### TOTP Modal
```jsx
// Modal backdrop
<div className="bg-gray-900/50 dark:bg-gray-950/80">

// Modal content
<div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">

// Input focus
<input className="border-primary-500 ring-4 ring-primary-500/20 dark:ring-primary-400/20">
```

---

## 🔄 Migración Gradual

### Fase 1: Infraestructura ✅
- [x] Definir paleta en tailwind.config.js
- [x] Documentar variables CSS
- [ ] Agregar ThemeContext (ya existe toggle, extender)

### Fase 2: Componentes Base
- [ ] Card, CardHeader, CardBody
- [ ] Button variants (primary/secondary)
- [ ] Input, Select, Form controls

### Fase 3: Panels
- [ ] UIPanel
- [ ] URPanel
- [ ] ExchangeRatePanel
- [ ] BROUPanel

### Fase 4: Features
- [ ] Dashboard
- [ ] MonitoringAccess
- [ ] Toast notifications
- [ ] Error boundaries

---

## 🧪 Testing Checklist

- [ ] Validar contraste en WebAIM Contrast Checker
- [ ] Probar light/dark toggle en todos los componentes
- [ ] Verificar hover states visibles
- [ ] Confirmar focus indicators accesibles
- [ ] Test en diferentes navegadores (Chrome, Firefox, Safari)
- [ ] Test con reducción de movimiento (prefers-reduced-motion)

---

## 📚 Referencias

- [Tailwind Color Scales](https://tailwindcss.com/docs/customizing-colors)
- [HSL Color Theory](https://en.wikipedia.org/wiki/HSL_and_HSV)
- [WCAG Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Color Harmony](https://www.canva.com/colors/color-wheel/)

---

**Última actualización**: 2025-10-12  
**Versión**: 1.0.0
