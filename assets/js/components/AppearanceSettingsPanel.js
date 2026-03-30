/**
 * Panel de Configuración de Apariencia
 * Interfaz completa para personalización visual con preview en vivo
 */

class AppearanceSettingsPanel {
    constructor() {
        this.settingsStore = null;
        this.themeStore = null;
        this.themeProvider = null;
        this.previewMode = false;
        this.previewSettings = null;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Inicializa el panel
     */
    async init() {
        if (this.isInitialized) return;
        
        // Esperar a que las dependencias estén disponibles
        if (typeof window !== 'undefined') {
            await this.waitForDependencies();
            
            // Initialize new theme store system
            if (window.themeStore) {
                this.themeStore = window.themeStore;
            }
            
            // Initialize legacy settings store
            if (window.useSettings) {
                this.settingsStore = window.useSettings();
            }
            
            // Initialize theme provider
            if (window.getThemeProvider) {
                this.themeProvider = window.getThemeProvider();
            }
            
            this.isInitialized = true;
        }
    }

    /**
     * Espera a que las dependencias estén cargadas
     */
    async waitForDependencies() {
        const maxWait = 5000; // 5 segundos máximo
        const startTime = Date.now();
        
        while ((!window.useSettings && !window.themeStore && !window.getThemeProvider) && 
               (Date.now() - startTime) < maxWait) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        if (!window.useSettings && !window.themeStore && !window.getThemeProvider) {
            console.error('No se pudieron cargar las dependencias del panel de configuración');
        }
    }

    /**
     * Renderiza el panel completo
     */
    render() {
        return `
            <div class="appearance-settings-panel">
                <div class="settings-header">
                    <h2>Apariencia</h2>
                    <p>Personaliza la visualización de la interfaz</p>
                </div>

                <!-- Preview en vivo -->
                <div class="preview-section">
                    <h3> Vista Previa </h3>
                    <div class="preview-container" id="themePreview">
                        ${this.renderPreview()}
                    </div>
                </div>

                <!-- Configuración de colores -->
                <div class="settings-section">
                    <h3>Colores</h3>
                    
                    <!-- Color de fondo -->
                    <div class="setting-item">
                        <label for="backgroundColor">Color de fondo</label>
                        <div class="color-input-group">
                            <input type="color" id="backgroundColor" value="#f5f5f5">
                            <div class="color-presets">
                                <button class="color-preset" data-color="#ffffff" title="Blanco puro">
                                    <div class="preset-color" style="background: #ffffff; border: 1px solid #ddd;"></div>
                                </button>
                                <button class="color-preset" data-color="#f5f5f5" title="Gris claro">
                                    <div class="preset-color" style="background: #f5f5f5;"></div>
                                </button>
                                <button class="color-preset" data-color="#1a1a1a" title="Oscuro">
                                    <div class="preset-color" style="background: #1a1a1a;"></div>
                                </button>
                            </div>
                        </div>
                        <button class="btn-white-pure" id="btnWhitePure">
                            Fondo blanco entero
                        </button>
                    </div>

                    <!-- Color de texto -->
                    <div class="setting-item">
                        <label for="textColor">Color de texto</label>
                        <select id="textColor">
                            <option value="auto">Automático (calcular contraste)</option>
                            <option value="#000000">Negro</option>
                            <option value="#ffffff">Blanco</option>
                        </select>
                    </div>

                    <!-- Color de acento -->
                    <div class="setting-item">
                        <label for="accentColor">Color de acento</label>
                        <div class="color-input-group">
                            <input type="color" id="accentColor" value="#3b82f6">
                            <div class="color-presets">
                                <button class="color-preset" data-color="#3b82f6" title="Azul">
                                    <div class="preset-color" style="background: #3b82f6;"></div>
                                </button>
                                <button class="color-preset" data-color="#10b981" title="Verde">
                                    <div class="preset-color" style="background: #10b981;"></div>
                                </button>
                                <button class="color-preset" data-color="#f59e0b" title="Ámbar">
                                    <div class="preset-color" style="background: #f59e0b;"></div>
                                </button>
                                <button class="color-preset" data-color="#ef4444" title="Rojo">
                                    <div class="preset-color" style="background: #ef4444;"></div>
                                </button>
                                <button class="color-preset" data-color="#8b5cf6" title="Púrpura">
                                    <div class="preset-color" style="background: #8b5cf6;"></div>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Configuración de tipografía -->
                <div class="settings-section">
                    <h3>Tipografía</h3>
                    
                    <!-- Tamaño de fuente -->
                    <div class="setting-item">
                        <label for="fontSize">Tamaño de fuente</label>
                        <select id="fontSize">
                            <option value="small">Pequeño</option>
                            <option value="normal" selected>Normal</option>
                            <option value="large">Grande</option>
                            <option value="x-large">Extra grande</option>
                        </select>
                    </div>

                    <!-- Familia de fuente -->
                    <div class="setting-item">
                        <label for="fontFamily">Tipo de fuente</label>
                        <select id="fontFamily">
                            <option value="system" selected>Sistema</option>
                            <option value="serif">Serif</option>
                            <option value="monospace">Monospace</option>
                        </select>
                    </div>
                </div>

                <!-- Configuración de interfaz -->
                <div class="settings-section">
                    <h3>Interfaz</h3>
                    
                    <!-- Bordes redondeados -->
                    <div class="setting-item">
                        <label for="borderRadius">Bordes redondeados</label>
                        <select id="borderRadius">
                            <option value="none">Ninguno</option>
                            <option value="small">Pequeño</option>
                            <option value="normal" selected>Normal</option>
                            <option value="large">Grande</option>
                        </select>
                    </div>

                    <!-- Densidad -->
                    <div class="setting-item">
                        <label for="density">Densidad de interfaz</label>
                        <select id="density">
                            <option value="compact">Compacto</option>
                            <option value="normal" selected>Normal</option>
                            <option value="comfortable">Espaciado</option>
                        </select>
                    </div>
                </div>

                <!-- Configuración de layout -->
                <div class="settings-section">
                    <h3>Layout</h3>
                    
                    <div class="setting-item">
                        <label class="toggle-label">
                            <input type="checkbox" id="sidebarCollapsed">
                            <span class="toggle-slider"></span>
                            Barra lateral colapsada por defecto
                        </label>
                    </div>

                    <div class="setting-item">
                        <label class="toggle-label">
                            <input type="checkbox" id="showBreadcrumbs" checked>
                            <span class="toggle-slider"></span>
                            Mostrar breadcrumbs
                        </label>
                    </div>

                    <div class="setting-item">
                        <label class="toggle-label">
                            <input type="checkbox" id="enableAnimations" checked>
                            <span class="toggle-slider"></span>
                            Activar animaciones
                        </label>
                    </div>

                    <div class="setting-item">
                        <label class="toggle-label">
                            <input type="checkbox" id="stickyHeader" checked>
                            <span class="toggle-slider"></span>
                            Cabecera fija
                        </label>
                    </div>
                </div>

                <!-- Acciones -->
                <div class="settings-actions">
                    <button class="btn btn-primary" id="saveSettings">
                        Guardar Cambios
                    </button>
                    <button class="btn btn-secondary" id="resetSettings">
                        Restaurar Valores por Defecto
                    </button>
                    <button class="btn btn-outline" id="exportSettings">
                        Exportar Configuración
                    </button>
                    <input type="file" id="importSettings" accept=".json" style="display: none;">
                    <button class="btn btn-outline" id="importBtn">
                        Importar Configuración
                    </button>
                </div>
            </div>

            <style>
                .appearance-settings-panel {
                    max-width: 100%;
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    border-radius: 0;
                    box-shadow: none;
                }

                .settings-header {
                    margin-bottom: 32px;
                    text-align: center;
                    padding: 24px;
                    background: rgba(59, 130, 246, 0.05);
                    border-radius: 12px;
                    border: 1px solid rgba(59, 130, 246, 0.2);
                }

                .settings-header h2 {
                    color: var(--text-primary, #f8fafc);
                    margin-bottom: 12px;
                    font-size: 26px;
                    font-weight: 700;
                    background: linear-gradient(135deg, var(--accent-color, #3b82f6), #8b5cf6);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }

                .settings-header p {
                    color: var(--text-secondary, #94a3b8);
                    font-size: 16px;
                    font-weight: 500;
                }

                .preview-section {
                    margin-bottom: 32px;
                    padding: 24px;
                    background: var(--bg-surface, #1a1f2e);
                    border-radius: 12px;
                    border: 1px solid var(--border-color, #2d3748);
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .preview-section h3 {
                    color: var(--text-primary, #f8fafc);
                    margin-bottom: 20px;
                    font-size: 18px;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .preview-section h3::before {
                    content: '👁️';
                    font-size: 20px;
                }

                .preview-container {
                    padding: 24px;
                    border-radius: 12px;
                    background: var(--bg-primary, #ffffff);
                    border: 2px dashed var(--border-color, #e1e5e9);
                    min-height: 150px;
                    position: relative;
                    overflow: hidden;
                }

                .preview-container::before {
                    content: 'Vista Previa';
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    font-size: 11px;
                    color: var(--text-muted, #666);
                    background: rgba(0, 0, 0, 0.05);
                    padding: 2px 6px;
                    border-radius: 4px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .settings-section {
                    margin-bottom: 32px;
                    padding: 24px;
                    background: var(--bg-surface, #1a1f2e);
                    border-radius: 12px;
                    border: 1px solid var(--border-color, #2d3748);
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    transition: all 0.3s ease;
                }

                .settings-section:hover {
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
                    border-color: rgba(59, 130, 246, 0.3);
                    transform: translateY(-2px);
                }

                .settings-section h3 {
                    color: var(--text-primary, #f8fafc);
                    margin-bottom: 24px;
                    font-size: 20px;
                    font-weight: 700;
                    border-bottom: 2px solid var(--accent-color, #3b82f6);
                    padding-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .setting-item {
                    margin-bottom: 24px;
                    padding: 20px;
                    background: rgba(255, 255, 255, 0.02);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    transition: all 0.2s ease;
                }

                .setting-item:hover {
                    background: rgba(255, 255, 255, 0.04);
                    border-color: rgba(59, 130, 246, 0.2);
                }

                .setting-item:last-child {
                    margin-bottom: 0;
                }

                .setting-item label {
                    display: block;
                    color: var(--text-primary, #f8fafc);
                    font-weight: 600;
                    margin-bottom: 12px;
                    font-size: 15px;
                }

                .color-input-group {
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    margin-bottom: 12px;
                    flex-wrap: wrap;
                }

                .color-input-group input[type="color"] {
                    width: 64px;
                    height: 48px;
                    border: 2px solid var(--border-color, #2d3748);
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    background: var(--bg-primary, #ffffff);
                }

                .color-input-group input[type="color"]:hover {
                    border-color: var(--accent-color, #3b82f6);
                    transform: scale(1.05);
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                }

                .color-presets {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                }

                .color-preset {
                    width: 36px;
                    height: 36px;
                    border: 2px solid transparent;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }

                .color-preset:hover {
                    border-color: var(--accent-color, #3b82f6);
                    transform: scale(1.1) rotate(5deg);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }

                .color-preset:active {
                    transform: scale(0.95);
                }

                .preset-color {
                    width: 100%;
                    height: 100%;
                    border-radius: 6px;
                }

                .btn-white-pure {
                    background: linear-gradient(135deg, #ffffff, #f8f9fa);
                    color: #333;
                    border: 1px solid #dee2e6;
                    padding: 12px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .btn-white-pure:hover {
                    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                    border-color: var(--accent-color, #3b82f6);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                }

                select {
                    width: 100%;
                    padding: 12px 16px;
                    border: 2px solid var(--border-color, #2d3748);
                    border-radius: 8px;
                    background: var(--bg-primary, #ffffff);
                    color: var(--text-primary, #333);
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    appearance: none;
                    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
                    background-repeat: no-repeat;
                    background-position: right 12px center;
                    background-size: 20px;
                    padding-right: 40px;
                }

                select:hover {
                    border-color: var(--accent-color, #3b82f6);
                }

                select:focus {
                    outline: none;
                    border-color: var(--accent-color, #3b82f6);
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                }

                .toggle-label {
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    font-weight: 500;
                    color: var(--text-primary, #f8fafc);
                    padding: 16px;
                    background: rgba(255, 255, 255, 0.02);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    transition: all 0.2s ease;
                }

                .toggle-label:hover {
                    background: rgba(255, 255, 255, 0.04);
                    border-color: rgba(59, 130, 246, 0.2);
                }

                .toggle-label input[type="checkbox"] {
                    display: none;
                }

                .toggle-slider {
                    width: 52px;
                    height: 28px;
                    background: #4a5568;
                    border-radius: 28px;
                    position: relative;
                    margin-right: 16px;
                    transition: all 0.3s ease;
                    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .toggle-slider::before {
                    content: '';
                    position: absolute;
                    width: 24px;
                    height: 24px;
                    background: white;
                    border-radius: 50%;
                    top: 2px;
                    left: 2px;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                }

                input[type="checkbox"]:checked + .toggle-slider {
                    background: linear-gradient(135deg, var(--accent-color, #3b82f6), #8b5cf6);
                    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
                }

                input[type="checkbox"]:checked + .toggle-slider::before {
                    transform: translateX(24px);
                    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
                }

                .settings-actions {
                    display: flex;
                    gap: 16px;
                    flex-wrap: wrap;
                    padding: 24px;
                    background: var(--bg-surface, #1a1f2e);
                    border-radius: 12px;
                    border: 1px solid var(--border-color, #2d3748);
                    margin-top: 32px;
                }

                .btn {
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .btn::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                    transition: left 0.5s;
                }

                .btn:hover::before {
                    left: 100%;
                }

                .btn-primary {
                    background: linear-gradient(135deg, var(--accent-color, #3b82f6), #8b5cf6);
                    color: white;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                }

                .btn-primary:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
                }

                .btn-secondary {
                    background: var(--bg-surface, #2d3748);
                    color: var(--text-primary, #f8fafc);
                    border: 2px solid var(--border-color, #4a5568);
                }

                .btn-secondary:hover {
                    background: var(--bg-elevated, #4a5568);
                    border-color: var(--accent-color, #3b82f6);
                    transform: translateY(-2px);
                }

                .btn-outline {
                    background: transparent;
                    color: var(--accent-color, #3b82f6);
                    border: 2px solid var(--accent-color, #3b82f6);
                }

                .btn-outline:hover {
                    background: var(--accent-color, #3b82f6);
                    color: white;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                }

                /* Responsive */
                @media (max-width: 768px) {
                    .settings-header,
                    .preview-section,
                    .settings-section,
                    .settings-actions {
                        padding: 16px;
                    }

                    .color-input-group {
                        flex-direction: column;
                        align-items: flex-start;
                    }

                    .settings-actions {
                        flex-direction: column;
                    }

                    .btn {
                        width: 100%;
                        padding: 14px 20px;
                    }

                    .setting-item {
                        padding: 16px;
                    }

                    .toggle-label {
                        padding: 12px;
                    }
                }
            </style>
        `;
    }

    /**
     * Renderiza el preview en vivo
     */
    renderPreview() {
        const settings = this.getCurrentPreviewSettings();
        
        return `
            <div class="preview-content" style="
                background: ${settings.theme.backgroundColor};
                color: ${this.computeTextColor(settings.theme.backgroundColor, settings.theme.textColor)};
                font-family: ${this.getFontFamily(settings.theme.fontFamily)};
                font-size: ${this.getFontSize(settings.theme.fontSize)};
                border-radius: ${this.getBorderRadius(settings.theme.borderRadius)};
                padding: ${this.getSpacing(settings.theme.density)};
            ">
                <h4 style="color: ${settings.theme.accentColor};">Título de Ejemplo</h4>
                <p>Este es un párrafo de ejemplo para mostrar cómo se verá el texto con la configuración seleccionada.</p>
                <button style="
                    background: ${settings.theme.accentColor};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: ${this.getBorderRadius(settings.theme.borderRadius)};
                    font-size: ${this.getFontSize(settings.theme.fontSize)};
                ">Botón de Ejemplo</button>
            </div>
        `;
    }

    /**
     * Obtiene las configuraciones actuales para el preview
     */
    getCurrentPreviewSettings() {
        if (this.previewMode && this.previewSettings) {
            return { theme: this.previewSettings };
        }
        
        // Try new theme store first, then fallback to legacy
        if (this.themeStore) {
            return { theme: this.themeStore.getCurrentTheme() };
        } else if (this.settingsStore) {
            return this.settingsStore.getSettings();
        }
        
        return { theme: this.getDefaultSettings().theme };
    }

    /**
     * Obtiene configuraciones por defecto
     */
    getDefaultSettings() {
        return {
            theme: {
                backgroundColor: '#f5f5f5',
                textColor: 'auto',
                accentColor: '#3b82f6',
                fontSize: 'normal',
                fontFamily: 'system',
                borderRadius: 'normal',
                density: 'normal'
            },
            layout: {
                sidebarCollapsed: false,
                showBreadcrumbs: true,
                enableAnimations: true,
                stickyHeader: true
            }
        };
    }

    /**
     * Calcula el color de texto para el preview
     */
    computeTextColor(backgroundColor, textColor) {
        if (textColor !== 'auto') {
            return textColor;
        }
        
        const luminance = this.calculateLuminance(backgroundColor);
        return luminance > 0.5 ? '#000000' : '#ffffff';
    }

    /**
     * Calcula la luminancia
     */
    calculateLuminance(hex) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return 0.5;
        
        const { r, g, b } = rgb;
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    }

    /**
     * Convierte hex a RGB
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    /**
     * Obtiene la familia de fuente
     */
    getFontFamily(fontFamily) {
        const families = {
            system: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            serif: 'Georgia, "Times New Roman", serif',
            monospace: '"Fira Code", "Courier New", monospace'
        };
        return families[fontFamily] || families.system;
    }

    /**
     * Obtiene el tamaño de fuente
     */
    getFontSize(fontSize) {
        const sizes = {
            small: '14px',
            normal: '16px',
            large: '18px',
            'x-large': '20px'
        };
        return sizes[fontSize] || '16px';
    }

    /**
     * Obtiene el radio de borde
     */
    getBorderRadius(borderRadius) {
        const radii = {
            none: '0px',
            small: '4px',
            normal: '8px',
            large: '12px'
        };
        return radii[borderRadius] || '8px';
    }

    /**
     * Obtiene el espaciado
     */
    getSpacing(density) {
        const densities = {
            compact: '8px',
            normal: '16px',
            comfortable: '24px'
        };
        return densities[density] || '16px';
    }

    /**
     * Inicializa los event listeners del panel
     */
    initEventListeners(container) {
        if (!container) return;

        // Color de fondo
        const bgColorInput = container.querySelector('#backgroundColor');
        const colorPresets = container.querySelectorAll('.color-preset');
        
        bgColorInput?.addEventListener('input', (e) => {
            this.updatePreview('theme.backgroundColor', e.target.value);
        });

        colorPresets.forEach(preset => {
            preset.addEventListener('click', () => {
                const color = preset.dataset.color;
                bgColorInput.value = color;
                this.updatePreview('theme.backgroundColor', color);
            });
        });

        // Botón de fondo blanco puro
        const btnWhitePure = container.querySelector('#btnWhitePure');
        btnWhitePure?.addEventListener('click', () => {
            bgColorInput.value = '#ffffff';
            this.updatePreview('theme.backgroundColor', '#ffffff');
            this.updatePreview('theme.textColor', '#000000');
            
            const textColorSelect = container.querySelector('#textColor');
            if (textColorSelect) {
                textColorSelect.value = '#000000';
            }
        });

        // Color de texto
        const textColorSelect = container.querySelector('#textColor');
        textColorSelect?.addEventListener('change', (e) => {
            this.updatePreview('theme.textColor', e.target.value);
        });

        // Color de acento
        const accentColorInput = container.querySelector('#accentColor');
        accentColorInput?.addEventListener('input', (e) => {
            this.updatePreview('theme.accentColor', e.target.value);
        });

        // Tipografía
        const fontSizeSelect = container.querySelector('#fontSize');
        fontSizeSelect?.addEventListener('change', (e) => {
            this.updatePreview('theme.fontSize', e.target.value);
        });

        const fontFamilySelect = container.querySelector('#fontFamily');
        fontFamilySelect?.addEventListener('change', (e) => {
            this.updatePreview('theme.fontFamily', e.target.value);
        });

        // Interfaz
        const borderRadiusSelect = container.querySelector('#borderRadius');
        borderRadiusSelect?.addEventListener('change', (e) => {
            this.updatePreview('theme.borderRadius', e.target.value);
        });

        const densitySelect = container.querySelector('#density');
        densitySelect?.addEventListener('change', (e) => {
            this.updatePreview('theme.density', e.target.value);
        });

        // Layout
        const sidebarCollapsed = container.querySelector('#sidebarCollapsed');
        sidebarCollapsed?.addEventListener('change', (e) => {
            this.updatePreview('layout.sidebarCollapsed', e.target.checked);
        });

        const showBreadcrumbs = container.querySelector('#showBreadcrumbs');
        showBreadcrumbs?.addEventListener('change', (e) => {
            this.updatePreview('layout.showBreadcrumbs', e.target.checked);
        });

        const enableAnimations = container.querySelector('#enableAnimations');
        enableAnimations?.addEventListener('change', (e) => {
            this.updatePreview('layout.enableAnimations', e.target.checked);
        });

        const stickyHeader = container.querySelector('#stickyHeader');
        stickyHeader?.addEventListener('change', (e) => {
            this.updatePreview('layout.stickyHeader', e.target.checked);
        });

        // Acciones
        const saveBtn = container.querySelector('#saveSettings');
        saveBtn?.addEventListener('click', () => this.saveSettings());

        const resetBtn = container.querySelector('#resetSettings');
        resetBtn?.addEventListener('click', () => this.resetSettings());

        const exportBtn = container.querySelector('#exportSettings');
        exportBtn?.addEventListener('click', () => this.exportSettings());

        const importBtn = container.querySelector('#importBtn');
        const importInput = container.querySelector('#importSettings');
        
        importBtn?.addEventListener('click', () => {
            importInput?.click();
        });

        importInput?.addEventListener('change', (e) => {
            this.importSettings(e.target.files[0]);
        });
    }

    /**
     * Actualiza el preview en vivo
     */
    updatePreview(path, value) {
        console.log('🔍 DEBUG: updatePreview llamado con:', { path, value });
        
        if (!this.previewMode) {
            this.enablePreviewMode();
        }

        // Convert path format for new theme store
        const themePath = path.replace('theme.', '');
        console.log('🔍 DEBUG: themePath convertido:', themePath);
        
        // Update preview settings - CLONAR para evitar referencia
        if (!this.previewSettings) {
            this.previewSettings = { ...this.getCurrentTheme() };
            console.log('🔍 DEBUG: previewSettings inicializado con clon:', this.previewSettings);
        }
        
        // Actualizar valor específico
        const oldValue = this.previewSettings[themePath];
        this.previewSettings[themePath] = value;
        console.log('🔍 DEBUG: Actualizado previewSettings:', {
            key: themePath,
            from: oldValue,
            to: value,
            newPreviewSettings: { ...this.previewSettings }
        });

        // Update preview visual
        const previewContainer = document.querySelector('#themePreview');
        if (previewContainer) {
            previewContainer.innerHTML = this.renderPreview();
        }

        // Apply real-time changes using new theme manager
        if (window.themeManager) {
            window.themeManager.applyPreviewTheme(this.previewSettings);
        } else if (this.themeProvider) {
            this.themeProvider.applyPreviewSettings({ theme: this.previewSettings });
        }
    }

    /**
     * Habilita el modo preview
     */
    enablePreviewMode() {
        console.log('🔍 DEBUG: Habilitando preview mode');
        this.previewMode = true;
        
        // CLONAR para evitar referencia al objeto original
        const currentTheme = this.getCurrentTheme();
        this.previewSettings = { ...currentTheme };
        console.log('🔍 DEBUG: previewSettings clonado:', this.previewSettings);
        
        if (this.themeProvider) {
            this.themeProvider.enablePreviewMode();
        }
    }

    /**
     * Deshabilita el modo preview
     */
    disablePreviewMode() {
        this.previewMode = false;
        this.previewSettings = null;
        
        if (this.themeProvider) {
            this.themeProvider.disablePreviewMode();
        }
    }

    /**
     * Guarda las configuraciones
     */
    saveSettings() {
        // Usar debugger si está disponible
        if (window.themeDebugger) {
            window.themeDebugger.log('🚀 Iniciando saveSettings()');
            const analysis = window.themeDebugger.analyzePanelState(this);
            window.themeDebugger.log('📊 Análisis completo', analysis);
        }
        
        console.log('🔍 DEBUG: Iniciando saveSettings()');
        console.log('🔍 DEBUG: previewMode:', this.previewMode);
        console.log('🔍 DEBUG: previewSettings:', this.previewSettings);
        
        // Obtener valores actuales del formulario
        const currentFormValues = this.getFormValues();
        console.log('🔍 DEBUG: Valores del formulario:', currentFormValues);
        
        // Verificar integridad de datos
        if (window.themeDebugger) {
            window.themeDebugger.checkDataIntegrity(currentFormValues, 'FormValues');
        }
        
        // Obtener valores originales
        const originalValues = this.getCurrentTheme();
        console.log('🔍 DEBUG: Valores originales:', originalValues);
        
        // Comparar valores
        const hasChanges = this.hasChanges(originalValues, currentFormValues);
        console.log('🔍 DEBUG: ¿Hay cambios?', hasChanges);
        
        if (!hasChanges) {
            this.showMessage('No hay cambios para guardar', 'warning');
            return;
        }

        // Use new theme manager if available
        if (window.themeManager) {
            window.themeManager.confirmPreview();
            // Opcional: sincronizar con servidor si el usuario está autenticado
            window.themeManager.syncWithServer();
        } else if (this.themeStore) {
            this.themeStore.updateTheme(this.previewSettings);
        } else if (this.settingsStore) {
            this.settingsStore.updateSettings({ theme: this.previewSettings });
        }
        
        this.disablePreviewMode();
        this.showMessage('Configuración guardada exitosamente', 'success');
        
        // Mostrar resumen del debugging
        if (window.themeDebugger) {
            window.themeDebugger.showSummary();
        }
    }

    /**
     * Restablece las configuraciones
     */
    resetSettings() {
        if (confirm('¿Estás seguro de que deseas restablecer todas las configuraciones a los valores por defecto?')) {
            // Use new theme manager if available
            if (window.themeManager) {
                window.themeManager.resetTheme();
            } else if (this.themeStore) {
                this.themeStore.resetTheme();
            } else if (this.settingsStore) {
                this.settingsStore.resetToDefaults();
            }
            
            this.disablePreviewMode();
            this.loadCurrentSettings();
            this.showMessage('Configuración restablecida', 'info');
        }
    }

    /**
     * Exporta las configuraciones
     */
    exportSettings() {
        let settings;
        
        // Use new theme store if available
        if (this.themeStore) {
            settings = this.themeStore.exportTheme();
        } else if (this.settingsStore) {
            settings = JSON.stringify(this.settingsStore.getSettings(), null, 2);
        } else {
            settings = JSON.stringify(this.getDefaultSettings(), null, 2);
        }
        
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(settings);
        
        const exportFileDefaultName = 'appearance-settings.json';
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        this.showMessage('Configuración exportada', 'success');
    }

    /**
     * Importa configuraciones
     */
    importSettings(file) {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const settings = JSON.parse(e.target.result);
                
                // Use new theme store if available
                if (this.themeStore) {
                    this.themeStore.importTheme(e.target.result);
                } else if (this.settingsStore) {
                    this.settingsStore.updateSettings(settings);
                }
                
                this.loadCurrentSettings();
                this.showMessage('Configuración importada exitosamente', 'success');
            } catch (error) {
                this.showMessage('Error al importar la configuración', 'error');
                console.error('Error importando settings:', error);
            }
        };
        reader.readAsText(file);
    }

    /**
     * Obtiene el tema actual
     */
    getCurrentTheme() {
        if (window.themeManager) {
            return window.themeManager.getCurrentTheme();
        } else if (this.themeStore) {
            return this.themeStore.getCurrentTheme();
        } else if (this.settingsStore) {
            return this.settingsStore.getSettings().theme;
        }
        return this.getDefaultSettings().theme;
    }

    /**
     * Carga las configuraciones actuales en los controles
     */
    loadCurrentSettings() {
        const theme = this.getCurrentTheme();
        
        // Actualizar controles del formulario
        setTimeout(() => {
            const container = document.querySelector('.appearance-settings-panel');
            if (!container) return;

            // Colores
            const bgColorInput = container.querySelector('#backgroundColor');
            if (bgColorInput) bgColorInput.value = theme.backgroundColor;

            const textColorSelect = container.querySelector('#textColor');
            if (textColorSelect) textColorSelect.value = theme.textColor || 'auto';

            const accentColorInput = container.querySelector('#accentColor');
            if (accentColorInput) accentColorInput.value = theme.accentColor;

            // Tipografía
            const fontSizeSelect = container.querySelector('#fontSize');
            if (fontSizeSelect) fontSizeSelect.value = theme.fontSize;

            const fontFamilySelect = container.querySelector('#fontFamily');
            if (fontFamilySelect) fontFamilySelect.value = theme.fontFamily || 'system';

            // Interfaz
            const borderRadiusSelect = container.querySelector('#borderRadius');
            if (borderRadiusSelect) borderRadiusSelect.value = theme.borderRadius || 'normal';

            const densitySelect = container.querySelector('#density');
            if (densitySelect) densitySelect.value = theme.density || 'normal';

            // Layout - use legacy settings if available
            const layout = this.settingsStore?.getSettings()?.layout || {};
            const sidebarCollapsed = container.querySelector('#sidebarCollapsed');
            if (sidebarCollapsed) sidebarCollapsed.checked = layout.sidebarCollapsed || false;

            const showBreadcrumbs = container.querySelector('#showBreadcrumbs');
            if (showBreadcrumbs) showBreadcrumbs.checked = layout.showBreadcrumbs !== false;

            const enableAnimations = container.querySelector('#enableAnimations');
            if (enableAnimations) enableAnimations.checked = layout.enableAnimations !== false;

            const stickyHeader = container.querySelector('#stickyHeader');
            if (stickyHeader) stickyHeader.checked = layout.stickyHeader !== false;

            // Actualizar preview
            const previewContainer = container.querySelector('#themePreview');
            if (previewContainer) {
                previewContainer.innerHTML = this.renderPreview();
            }
        }, 100);
    }

    /**
     * Obtiene los valores actuales del formulario
     */
    getFormValues() {
        const container = document.querySelector('.appearance-settings-panel');
        if (!container) return {};

        const values = {};
        
        // Colores
        const bgColorInput = container.querySelector('#backgroundColor');
        if (bgColorInput) values.backgroundColor = bgColorInput.value;

        const textColorSelect = container.querySelector('#textColor');
        if (textColorSelect) values.textColor = textColorSelect.value;

        const accentColorInput = container.querySelector('#accentColor');
        if (accentColorInput) values.accentColor = accentColorInput.value;

        // Tipografía
        const fontSizeSelect = container.querySelector('#fontSize');
        if (fontSizeSelect) values.fontSize = fontSizeSelect.value;

        const fontFamilySelect = container.querySelector('#fontFamily');
        if (fontFamilySelect) values.fontFamily = fontFamilySelect.value;

        // Interfaz
        const borderRadiusSelect = container.querySelector('#borderRadius');
        if (borderRadiusSelect) values.borderRadius = borderRadiusSelect.value;

        const densitySelect = container.querySelector('#density');
        if (densitySelect) values.density = densitySelect.value;

        console.log('🔍 DEBUG: Valores extraídos del DOM:', values);
        return values;
    }

    /**
     * Compara dos objetos de configuración para detectar cambios
     */
    hasChanges(original, current) {
        console.log('🔍 DEBUG: Comparando objetos');
        console.log('🔍 DEBUG: Original:', JSON.stringify(original, null, 2));
        console.log('🔍 DEBUG: Current:', JSON.stringify(current, null, 2));
        
        // Asegurar que ambos objetos existen
        if (!original || !current) {
            console.log('🔍 DEBUG: Uno de los objetos es null/undefined');
            return false;
        }
        
        // Obtener todas las claves de ambos objetos
        const allKeys = new Set([...Object.keys(original), ...Object.keys(current)]);
        
        let changesFound = false;
        const changes = {};
        
        for (const key of allKeys) {
            const originalValue = original[key];
            const currentValue = current[key];
            
            // Comparación profunda para strings y valores primitivos
            const isEqual = this.deepEqual(originalValue, currentValue);
            
            if (!isEqual) {
                changesFound = true;
                changes[key] = {
                    from: originalValue,
                    to: currentValue
                };
                console.log(`🔍 DEBUG: Cambio detectado en ${key}:`, changes[key]);
            }
        }
        
        console.log('🔍 DEBUG: Cambios encontrados:', changes);
        return changesFound;
    }

    /**
     * Comparación profunda entre dos valores
     */
    deepEqual(val1, val2) {
        // Manejo de null/undefined
        if (val1 === val2) return true;
        if (val1 == null || val2 == null) return false;
        
        // Comparación de tipos
        if (typeof val1 !== typeof val2) return false;
        
        // Comparación de objetos
        if (typeof val1 === 'object') {
            const keys1 = Object.keys(val1);
            const keys2 = Object.keys(val2);
            
            if (keys1.length !== keys2.length) return false;
            
            for (const key of keys1) {
                if (!keys2.includes(key)) return false;
                if (!this.deepEqual(val1[key], val2[key])) return false;
            }
            
            return true;
        }
        
        // Comparación de valores primitivos
        return val1 === val2;
    }
    showMessage(message, type = 'info') {
        // Crear elemento de mensaje
        const messageEl = document.createElement('div');
        messageEl.className = `settings-message settings-message-${type}`;
        messageEl.textContent = message;
        
        // Estilos
        Object.assign(messageEl.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '9999',
            opacity: '0',
            transform: 'translateY(-20px)',
            transition: 'all 0.3s ease'
        });

        // Color según tipo
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        messageEl.style.background = colors[type] || colors.info;

        document.body.appendChild(messageEl);

        // Animación de entrada
        setTimeout(() => {
            messageEl.style.opacity = '1';
            messageEl.style.transform = 'translateY(0)';
        }, 100);

        // Remover después de 3 segundos
        setTimeout(() => {
            messageEl.style.opacity = '0';
            messageEl.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                document.body.removeChild(messageEl);
            }, 300);
        }, 3000);
    }

    /**
     * Monta el panel en un contenedor
     */
    mount(container) {
        if (!container) return;

        container.innerHTML = this.render();
        this.initEventListeners(container);
        this.loadCurrentSettings();
    }
}

// Crear instancia global
let appearanceSettingsPanel = null;

/**
 * Función helper para obtener el panel de configuración
 */
function getAppearanceSettingsPanel() {
    if (!appearanceSettingsPanel) {
        appearanceSettingsPanel = new AppearanceSettingsPanel();
    }
    return appearanceSettingsPanel;
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AppearanceSettingsPanel, getAppearanceSettingsPanel };
} else {
    window.AppearanceSettingsPanel = AppearanceSettingsPanel;
    window.getAppearanceSettingsPanel = getAppearanceSettingsPanel;
    window.appearanceSettingsPanel = getAppearanceSettingsPanel();
}
