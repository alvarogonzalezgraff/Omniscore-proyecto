# Panel de Configuración de Apariencia - Documentación Completa

## 📋 Resumen de Implementación

Se ha implementado un sistema completo de personalización visual con panel de configuración, persistencia y aplicación en tiempo real.

## 📁 Archivos Creados

### Core del Sistema
```
assets/js/
├── stores/settings.js                    # Store de configuración con persistencia
├── components/ThemeProvider.js           # Provider de temas con CSS variables
└── components/AppearanceSettingsPanel.js # Panel UI completo con preview
```

## 🎨 Variables CSS Generadas

### Colores Principales
```css
:root {
  /* Colores base */
  --bg-primary: #f5f5f5;              /* Fondo principal */
  --bg-surface: #fafafa;               /* Fondo de superficies */
  --bg-elevated: #ffffff;              /* Fondo elevado */
  --bg-overlay: rgba(0,0,0,0.8);      /* Overlay para modales */
  
  /* Texto */
  --text-primary: #000000;              /* Texto principal */
  --text-secondary: #666666;           /* Texto secundario */
  --text-muted: #999999;               /* Texto silenciado */
  --text-inverse: #ffffff;             /* Texto inverso */
  
  /* Acento */
  --accent-color: #3b82f6;             /* Color primario de acento */
}
```

### Tipografía
```css
:root {
  /* Familias */
  --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  
  /* Tamaños */
  --font-size-base: 16px;             /* Tamaño base */
  --font-size-sm: 14px;               /* Pequeño */
  --font-size-lg: 18px;               /* Grande */
  --font-size-xl: 20px;               /* Extra grande */
}
```

### Espaciado y Layout
```css
:root {
  /* Espaciado */
  --spacing-xs: 0.25rem;              /* 4px */
  --spacing-sm: 0.5rem;               /* 8px */
  --spacing-base: 1rem;               /* 16px */
  --spacing-md: 0.75rem;              /* 12px */
  --spacing-lg: 1.5rem;               /* 24px */
  --spacing-xl: 2rem;                 /* 32px */
  
  /* Bordes */
  --border-radius-base: 8px;           /* Radio base */
  --border-radius-sm: 4px;             /* Radio pequeño */
  --border-radius-lg: 12px;            /* Radio grande */
}
```

### Sombras y Transiciones
```css
:root {
  /* Sombras (ajustadas según tema) */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  /* Transiciones */
  --transition-base: all 0.2s ease-in-out;
  --transition-fast: all 0.2s ease-in-out;
  --transition-slow: all 0.4s ease-in-out;
}
```

## 🚀 Integración en Templates

### 1. Incluir Scripts en Template Base

```html
<!-- En tu template base (antes de closing </body>) -->
<script src="/assets/js/stores/settings.js"></script>
<script src="/assets/js/components/ThemeProvider.js"></script>
<script src="/assets/js/components/AppearanceSettingsPanel.js"></script>
```

### 2. Crear Página de Configuración

```html
<!-- templates/configuracion.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuración - BetWin</title>
</head>
<body>
    <!-- Tu header existente -->
    <header>...</header>
    
    <!-- Contenido principal -->
    <main class="main-content">
        <div class="container">
            <h1>Configuración</h1>
            
            <!-- Panel de apariencia -->
            <div id="appearanceSettingsContainer"></div>
        </div>
    </main>
    
    <!-- Tu footer existente -->
    <footer>...</footer>
    
    <script>
        // Inicializar panel de configuración
        document.addEventListener('DOMContentLoaded', function() {
            const panel = getAppearanceSettingsPanel();
            const container = document.getElementById('appearanceSettingsContainer');
            
            if (container) {
                panel.mount(container);
            }
        });
    </script>
</body>
</html>
```

### 3. Actualizar Componentes Existentes

#### Ejemplo: Botón con Variables CSS
```css
.btn-primary {
    background: var(--accent-color, #3b82f6);
    color: white;
    border: none;
    padding: var(--spacing-sm, 8px) var(--spacing-base, 16px);
    border-radius: var(--border-radius-base, 8px);
    font-family: var(--font-family-base, sans-serif);
    font-size: var(--font-size-base, 16px);
    transition: var(--transition-base, all 0.2s ease);
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
}

.btn-primary:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: var(--shadow-base, 0 1px 3px rgba(0,0,0,0.1));
}
```

#### Ejemplo: Card con Variables CSS
```css
.card {
    background: var(--bg-surface, #ffffff);
    border: 1px solid var(--border-color, #e1e5e9);
    border-radius: var(--border-radius-base, 8px);
    padding: var(--spacing-base, 16px);
    box-shadow: var(--shadow-base, 0 1px 3px rgba(0,0,0,0.1));
    transition: var(--transition-base, all 0.2s ease);
}

.card:hover {
    box-shadow: var(--shadow-md, 0 4px 6px rgba(0,0,0,0.1));
    border-color: var(--accent-color, #3b82f6);
}
```

#### Ejemplo: Texto con Variables CSS
```css
.heading {
    color: var(--text-primary, #333);
    font-family: var(--font-family-base, sans-serif);
    font-size: var(--font-size-xl, 20px);
    margin-bottom: var(--spacing-md, 12px);
}

.body-text {
    color: var(--text-secondary, #666);
    font-family: var(--font-family-base, sans-serif);
    font-size: var(--font-size-base, 16px);
    line-height: 1.6;
}
```

## 🎛️ Configuraciones Disponibles

### Tema (theme)
```javascript
{
  backgroundColor: '#ffffff' | '#f5f5f5' | '#1a1a1a' | string,
  textColor: 'auto' | '#000000' | '#ffffff',
  accentColor: '#3b82f6' | string,
  fontSize: 'small' | 'normal' | 'large' | 'x-large',
  fontFamily: 'system' | 'serif' | 'monospace',
  borderRadius: 'none' | 'small' | 'normal' | 'large',
  density: 'compact' | 'normal' | 'comfortable'
}
```

### Layout (layout)
```javascript
{
  sidebarCollapsed: boolean,
  showBreadcrumbs: boolean,
  enableAnimations: boolean,
  stickyHeader: boolean
}
```

## 🔧 Uso Programático

### Acceder al Store
```javascript
// Obtener store
const settings = useSettings();

// Obtener configuración actual
const currentSettings = settings.getSettings();

// Obtener valor específico
const bgColor = settings.getSetting('theme.backgroundColor');

// Actualizar valor
settings.updateSetting('theme.fontSize', 'large');

// Suscribirse a cambios
const unsubscribe = settings.subscribe((newSettings) => {
    console.log('Configuración actualizada:', newSettings);
});

// Cancelar suscripción
unsubscribe();
```

### Controlar ThemeProvider
```javascript
// Obtener provider
const themeProvider = getThemeProvider();

// Obtener variables CSS actuales
const cssVars = themeProvider.getCurrentCSSVariables();

// Exportar/importar configuración
const exported = themeProvider.exportSettings();
themeProvider.importSettings(newSettings);

// Resetear a valores por defecto
themeProvider.resetToDefaults();
```

## 🎨 Clases CSS Aplicadas

### Clases de Tema
```css
.theme-light      /* Fondos claros */
.theme-dark       /* Fondos oscuros */
.theme-custom     /* Fondos personalizados */
```

### Clases de Tipografía
```css
.font-small      /* 14px */
.font-normal     /* 16px */
.font-large      /* 18px */
.font-x-large    /* 20px */
```

### Clases de Densidad
```css
.density-compact     /* 0.5rem spacing */
.density-normal      /* 1rem spacing */
.density-comfortable /* 1.5rem spacing */
```

### Clases de Bordes
```css
.border-none     /* 0px radius */
.border-small    /* 4px radius */
.border-normal   /* 8px radius */
.border-large    /* 12px radius */
```

### Clases de Layout
```css
.sidebar-collapsed    /* Sidebar colapsado */
.hide-breadcrumbs    /* Ocultar breadcrumbs */
.sticky-header       /* Header fijo */
.no-animations      /* Desactivar animaciones */
.high-contrast      /* Alto contraste */
```

## ♿ Accesibilidad

### WCAG Compliance
- **Contraste automático**: Calcula luminancia del fondo para asegurar WCAG AA (4.5:1)
- **Reduced motion**: Respeta `prefers-reduced-motion`
- **Alto contraste**: Aplica clase `high-contrast` si el contraste es insuficiente

### Eventos de Accesibilidad
```javascript
// Escuchar cambios de tema
window.addEventListener('themechange', (event) => {
    const { settings } = event.detail;
    console.log('Tema actualizado:', settings);
});
```

## 🔄 Persistencia

### localStorage
```javascript
// Clave: 'app_settings'
{
  "theme": {
    "backgroundColor": "#f5f5f5",
    "textColor": "auto",
    "accentColor": "#3b82f6",
    ...
  },
  "layout": {
    "sidebarCollapsed": false,
    ...
  }
}
```

### Import/Export
- **Export**: Descarga archivo JSON con configuración completa
- **Import**: Carga configuración desde archivo JSON
- **Reset**: Restablece a valores por defecto

## 🎯 Características Especiales

### Fondo Blanco Entero
```javascript
// Activa automáticamente:
// - backgroundColor: '#ffffff'
// - textColor: '#000000'
// - Sin sombras (look flat)
// - Sin patrones de fondo
```

### Preview en Vivo
- **Actualización real**: Los cambios se aplican instantáneamente
- **Modo preview**: No se guarda hasta confirmar
- **Cancelación**: Puede revertir cambios con un clic

### Detección de Sistema
- **Tema oscuro/claro**: Detecta `prefers-color-scheme`
- **Reduced motion**: Detecta `prefers-reduced-motion`
- **Valores por defecto**: Se ajustan según preferencias del sistema

## 📱 Responsive Design

El panel de configuración es completamente responsive:
- **Desktop**: Layout en columnas
- **Tablet**: Layout adaptativo
- **Mobile**: Layout en una sola columna

## 🚨 Notas Importantes

1. **No modificar componentes existentes**: Solo añadir CSS variables
2. **Compatibilidad**: Funciona con navegadores modernos (CSS variables)
3. **Performance**: Las actualizaciones son optimizadas y no causan reflows
4. **Seguridad**: Las configuraciones se validan antes de aplicar
5. **Fallback**: Valores por defecto si las variables no están definidas

## 🧪 Testing

### Verificar Funcionamiento
```javascript
// En consola del navegador
const settings = useSettings();
console.log('Configuración actual:', settings.getSettings());

// Verificar variables CSS
const root = document.documentElement;
console.log('CSS Variables:', getComputedStyle(root));
```

### Test de Contraste
```javascript
// Verificar WCAG compliance
const isCompliant = settings.checkWCAGContrast();
console.log('WCAG AA compliant:', isCompliant);
```

---

Este sistema proporciona personalización completa sin afectar la estructura existente de tu aplicación.
