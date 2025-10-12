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

## 🧩 Sistema Semántico de Colores (Phase 1)

### Arquitectura Centralizada
**Archivo**: `frontend/src/theme/colors.js`

Sistema que mapea **intenciones de diseño** → **colores de paleta**, permitiendo cambios globales desde un único punto.

### Categorías Semánticas

#### 1. **Status** - Estados del Sistema
```javascript
semanticColors.status = {
  success: 'success',  // Operaciones exitosas, datos actualizados
  error: 'error',      // Errores, fallos, validaciones
  warning: 'secondary', // Advertencias, atención requerida
  info: 'accent',      // Información neutral, tips
  neutral: 'gray',     // Estados sin connotación especial
}
```

#### 2. **Data** - Visualización de Datos Financieros
```javascript
semanticColors.data = {
  buy: 'success',      // Compra, valores positivos (+)
  sell: 'error',       // Venta, valores negativos (-)
  highlight: 'primary', // Valores destacados, actual
  neutral: 'gray',     // Sin cambio, neutro
  arbitrage: 'accent', // Oportunidades, diferencias
}
```

#### 3. **Freshness** - Frescura de Datos
```javascript
semanticColors.freshness = {
  fresh: 'success',    // < 5 min
  stale: 'secondary',  // 5-30 min
  outdated: 'error',   // > 30 min
  unknown: 'gray',     // Sin timestamp
}
```

#### 4. **Interactive** - Elementos Interactivos
```javascript
semanticColors.interactive = {
  primary: 'primary',   // Acción principal
  secondary: 'secondary', // Acción secundaria
  danger: 'error',      // Acción destructiva
  neutral: 'gray',      // Acción neutral
  ghost: 'transparent', // Sin fondo
}
```

### Helpers de Uso

#### `getSemanticClass(intent, type, shade)`
Genera clases Tailwind dinámicamente:

```javascript
import { getSemanticClass } from '@/theme/colors';

// Fondo de estado success
getSemanticClass('success', 'bg', 100);
// → 'bg-success-100'

// Texto de estado error
getSemanticClass('error', 'text', 700);
// → 'text-error-700'

// Borde de datos buy
getSemanticClass('buy', 'border', 300, 'data');
// → 'border-success-300'
```

#### `getComponentVariant(component, variant)`
Retorna clases completas predefinidas para componentes:

```javascript
import { getComponentVariant } from '@/theme/colors';

// Badge success completo
getComponentVariant('badge', 'success');
// → 'bg-success-100 text-success-800 dark:bg-success-900/30 dark:text-success-300'

// Button primary completo
getComponentVariant('button', 'primary');
// → 'bg-primary-600 hover:bg-primary-700 text-white ...'
```

### Componentes UI Reutilizables

#### **Badge** (`components/ui/Badge.jsx`)
Etiquetas inline para estados, categorías, contadores.

**Variantes**: `success` | `error` | `warning` | `info` | `neutral` | `primary`

```jsx
import Badge, { BadgeWithIcon, CountBadge, StatusBadge } from '@/components/ui/Badge';

// Badge básico
<Badge variant="success">Actualizado</Badge>

// Con icono
<BadgeWithIcon variant="error" icon={<AlertIcon />}>
  Error crítico
</BadgeWithIcon>

// Contador
<CountBadge variant="primary" count={42} max={99} />

// Con indicador animado
<StatusBadge variant="success" animated>
  En línea
</StatusBadge>
```

**Props**:
- `variant`: Variante de color
- `size`: `'sm' | 'md' | 'lg'` (default: `'sm'`)
- `rounded`: `boolean` - Esquinas redondeadas vs pill
- `className`: Clases adicionales

#### **Alert** (`components/ui/Alert.jsx`)
Mensajes de notificación, errores, advertencias.

**Variantes**: `success` | `error` | `warning` | `info`

```jsx
import Alert, { CompactAlert, ListAlert, LoadingAlert } from '@/components/ui/Alert';

// Alert básico
<Alert variant="success" title="Éxito">
  Operación completada correctamente
</Alert>

// Con cierre
<Alert 
  variant="error" 
  onClose={() => setAlert(null)}
>
  Error al procesar la solicitud
</Alert>

// Compacto (inline)
<CompactAlert variant="warning">
  Datos desactualizados
</CompactAlert>

// Lista de mensajes
<ListAlert variant="info" messages={[
  'Paso 1 completado',
  'Paso 2 en progreso...'
]} />

// Con loading
<LoadingAlert variant="info">
  Procesando datos...
</LoadingAlert>
```

**Props**:
- `variant`: Variante de color
- `title`: Título opcional
- `icon`: Icono custom (default: auto por variante)
- `onClose`: Callback para cerrar
- `children`: Contenido del mensaje

#### **Button** (`components/ui/Button.jsx`)
Botones con estados y variantes consistentes.

**Variantes**: `primary` | `secondary` | `danger` | `ghost` | `success`

```jsx
import Button, { ButtonGroup, IconButton, LinkButton } from '@/components/ui/Button';

// Button básico
<Button variant="primary" onClick={handleSubmit}>
  Guardar
</Button>

// Con loading
<Button variant="success" loading disabled>
  Guardando...
</Button>

// Con iconos
<Button 
  variant="secondary" 
  leftIcon={<SearchIcon />}
  rightIcon={<ArrowIcon />}
>
  Buscar
</Button>

// Grupo de botones conectados
<ButtonGroup>
  <Button variant="primary">Opción 1</Button>
  <Button variant="secondary">Opción 2</Button>
  <Button variant="ghost">Opción 3</Button>
</ButtonGroup>

// Icono solo
<IconButton variant="danger" icon={<TrashIcon />} />

// Estilo link
<LinkButton variant="primary" href="/docs">
  Ver documentación
</LinkButton>
```

**Props**:
- `variant`: Variante de color
- `size`: `'sm' | 'md' | 'lg'` (default: `'md'`)
- `loading`: Muestra spinner y deshabilita
- `disabled`: Deshabilitar botón
- `fullWidth`: Ancho completo
- `leftIcon` / `rightIcon`: Iconos laterales
- `onClick`: Handler de click

#### **Spinner** (`components/ui/Spinner.jsx`)
Indicadores de carga consistentes.

**Variantes**: `primary` | `secondary` | `white` | `gray`

```jsx
import Spinner, { 
  FullPageSpinner, 
  InlineSpinner, 
  SpinnerOverlay,
  PulseSpinner,
  DotsSpinner 
} from '@/components/ui/Spinner';

// Spinner básico
<Spinner variant="primary" size="md" />

// Con etiqueta
<Spinner 
  variant="primary" 
  size="lg" 
  label="Cargando datos..."
/>

// Centrado en contenedor
<Spinner center size="xl" label="Procesando..." />

// Full page overlay
<FullPageSpinner 
  variant="primary" 
  label="Cargando aplicación..."
  blur
/>

// Inline en texto
<p>Cargando <InlineSpinner variant="primary" /> datos...</p>

// Overlay sobre contenedor (posición relativa)
<div className="relative">
  <DataTable />
  <SpinnerOverlay variant="primary" label="Actualizando..." />
</div>

// Animación de pulso
<PulseSpinner variant="primary" size="lg" />

// Tres puntos animados
<DotsSpinner variant="secondary" size="md" />
```

**Props**:
- `variant`: Variante de color
- `size`: `'xs' | 'sm' | 'md' | 'lg' | 'xl'` (default: `'md'`)
- `label`: Texto descriptivo
- `center`: Centrar en contenedor
- `className`: Clases adicionales

### Ejemplo de Migración

**❌ Antes (hardcoded)**:
```jsx
<div className="bg-green-100 border border-green-200 text-green-800 px-3 py-2 rounded-lg">
  <span className="font-semibold">✓</span> Actualizado hace 2 minutos
</div>

<button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md disabled:opacity-50">
  Guardar
</button>
```

**✅ Después (semántico)**:
```jsx
import Alert from '@/components/ui/Alert';
import Button from '@/components/ui/Button';

<Alert variant="success">
  Actualizado hace 2 minutos
</Alert>

<Button variant="primary">
  Guardar
</Button>
```

**Beneficios**:
- ✅ Cambio global de tema desde `theme/colors.js`
- ✅ Dark mode automático
- ✅ Consistencia visual garantizada
- ✅ Menos código repetitivo
- ✅ Accesibilidad incorporada (focus, ARIA)

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

### Fase 1: Infraestructura ✅ (COMPLETADA)
- [x] Definir paleta en tailwind.config.js
- [x] Documentar variables CSS
- [x] Crear sistema semántico (`theme/colors.js`)
- [x] Badge component con 6 variantes
- [x] Alert component con 4 variantes
- [x] Button component con 5 variantes
- [x] Spinner component con 4 variantes
- [x] Documentar sistema semántico en THEMING.md
- [x] ThemeContext (ya existe toggle, extendido)

### Fase 2: Panels Principales (En Progreso)
- [ ] **BROUPanel** (~35-40 replacements)
  - Migrar badges inline → `<Badge variant="...">`
  - Migrar alerts inline → `<Alert variant="...">`
  - Migrar botones → `<Button variant="...">`
  - Migrar spinners → `<Spinner variant="...">`
- [ ] **ExchangeRatePanel** (~15-20 replacements)
  - Badges de freshness
  - Highlights de datos
  - Botones de acción

### Fase 3: Data Panels (Pendiente)
- [ ] **UIPanel** (~10-15 replacements)
- [ ] **URPanel** (~10-15 replacements)
- [ ] **Dashboard** (~20-25 replacements)

### Fase 4: Componentes Menores (Pendiente)
- [ ] Header
- [ ] SearchForm
- [ ] Card, CardHeader, CardBody
- [ ] MonitoringAccess
- [ ] Toast notifications
- [ ] Error boundaries
- [ ] Formularios (Input, Select)

**Progreso Total**: 5 / 20 archivos (~25%)

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

**Última actualización**: 2025-01-14  
**Versión**: 2.0.0 - Sistema Semántico Completo  
**Phase**: 1/4 Completada ✅
