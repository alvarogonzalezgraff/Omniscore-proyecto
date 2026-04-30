/**
 * Herramienta de Debugging para el Sistema de Temas
 * Ayuda a diagnosticar problemas de detección de cambios
 */

class ThemeDebugger {
    constructor() {
        this.enabled = true;
        this.logs = [];
    }

    /**
     * Activa/desactiva el debugging
     */
    setEnabled(enabled) {
        this.enabled = enabled;
    }

    /**
     * Log con timestamp
     */
    log(message, data = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            message,
            data: data ? JSON.parse(JSON.stringify(data)) : null
        };
        
        this.logs.push(logEntry);
        
        console.log(`🎨 [${timestamp}] ${message}`, data || '');
    }

    /**
     * Compara dos objetos con detalle
     */
    compareObjects(obj1, obj2, label = 'Objects') {
        this.log(`🔍 Comparando ${label}`, { obj1, obj2 });
        
        if (obj1 === obj2) {
            this.log(`✅ ${label}: Son la misma referencia`);
            return { equal: true, reason: 'same_reference' };
        }
        
        if (!obj1 || !obj2) {
            this.log(`❌ ${label}: Uno es null/undefined`);
            return { equal: false, reason: 'null_undefined' };
        }
        
        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);
        
        if (keys1.length !== keys2.length) {
            this.log(`❌ ${label}: Diferente número de claves`, { keys1, keys2 });
            return { equal: false, reason: 'different_keys', keys1, keys2 };
        }
        
        const differences = {};
        let hasDifferences = false;
        
        for (const key of keys1) {
            const val1 = obj1[key];
            const val2 = obj2[key];
            
            if (val1 !== val2) {
                differences[key] = { from: val1, to: val2 };
                hasDifferences = true;
                this.log(`🔄 ${label}: Diferencia en "${key}"`, { from: val1, to: val2 });
            }
        }
        
        if (hasDifferences) {
            this.log(`❌ ${label}: Se encontraron diferencias`, differences);
            return { equal: false, reason: 'value_differences', differences };
        } else {
            this.log(`✅ ${label}: Iguales por valores`);
            return { equal: true, reason: 'same_values' };
        }
    }

    /**
     * Analiza el estado completo del panel
     */
    analyzePanelState(panel) {
        this.log('🔬 Analizando estado del panel');
        
        const analysis = {
            previewMode: panel.previewMode,
            previewSettings: panel.previewSettings,
            currentTheme: panel.getCurrentTheme(),
            formValues: panel.getFormValues ? panel.getFormValues() : 'N/A'
        };
        
        this.log('📊 Estado del panel', analysis);
        
        // Comparaciones
        const comparisons = {
            previewVsCurrent: this.compareObjects(
                panel.previewSettings, 
                panel.getCurrentTheme(), 
                'Preview vs Current'
            ),
            formVsPreview: panel.getFormValues ? this.compareObjects(
                panel.getFormValues(), 
                panel.previewSettings, 
                'Form vs Preview'
            ) : 'N/A',
            formVsCurrent: panel.getFormValues ? this.compareObjects(
                panel.getFormValues(), 
                panel.getCurrentTheme(), 
                'Form vs Current'
            ) : 'N/A'
        };
        
        return { analysis, comparisons };
    }

    /**
     * Verifica la integridad de los datos
     */
    checkDataIntegrity(obj, name = 'Object') {
        this.log(`🔍 Verificando integridad de ${name}`);
        
        const issues = [];
        
        if (!obj) {
            issues.push(`${name} es null/undefined`);
            return { valid: false, issues };
        }
        
        if (typeof obj !== 'object') {
            issues.push(`${name} no es un objeto: ${typeof obj}`);
            return { valid: false, issues };
        }
        
        // Verificar valores undefined
        for (const [key, value] of Object.entries(obj)) {
            if (value === undefined) {
                issues.push(`${name}.${key} es undefined`);
            }
        }
        
        // Verificar tipos de datos esperados
        const expectedTypes = {
            backgroundColor: 'string',
            textColor: 'string',
            accentColor: 'string',
            fontSize: 'string',
            fontFamily: 'string',
            borderRadius: 'string',
            density: 'string'
        };
        
        for (const [key, expectedType] of Object.entries(expectedTypes)) {
            if (obj[key] !== undefined && typeof obj[key] !== expectedType) {
                issues.push(`${name}.${key} debería ser ${expectedType}, es ${typeof obj[key]}`);
            }
        }
        
        const valid = issues.length === 0;
        this.log(`${valid ? '✅' : '❌'} Integridad de ${name}`, { valid, issues });
        
        return { valid, issues };
    }

    /**
     * Exporta todos los logs
     */
    exportLogs() {
        return JSON.stringify(this.logs, null, 2);
    }

    /**
     * Limpia los logs
     */
    clearLogs() {
        this.logs = [];
        this.log('🧹 Logs limpiados');
    }

    /**
     * Muestra resumen de problemas
     */
    showSummary() {
        const errors = this.logs.filter(log => log.message.includes('❌'));
        const warnings = this.logs.filter(log => log.message.includes('⚠️'));
        const successes = this.logs.filter(log => log.message.includes('✅'));
        
        console.log('📋 Resumen del Debugging:');
        console.log(`❌ Errores: ${errors.length}`);
        console.log(`⚠️ Advertencias: ${warnings.length}`);
        console.log(`✅ Éxitos: ${successes.length}`);
        
        if (errors.length > 0) {
            console.log('🔥 Errores encontrados:');
            errors.forEach(log => console.log(`  - ${log.message}`, log.data));
        }
        
        return { errors: errors.length, warnings: warnings.length, successes: successes.length };
    }
}

// Crear instancia global
const themeDebugger = new ThemeDebugger();

// Exportar
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeDebugger, themeDebugger };
} else {
    window.ThemeDebugger = ThemeDebugger;
    window.themeDebugger = themeDebugger;
}
