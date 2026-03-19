@echo off
echo ========================================
echo BetWin - Servidor de Desarrollo
echo ========================================
echo.
echo Opciones disponibles:
echo.
echo 1. Desarrollo con recarga automática (las sesiones se cierran al cambiar código)
echo 2. Desarrollo sin recarga (las sesiones se mantienen activas)
echo 3. Producción (sin recarga, optimizado)
echo.
set /p option="Selecciona una opción (1-3): "

if "%option%"=="1" (
    echo.
    echo Iniciando servidor con recarga automática...
    echo ⚠️  Las sesiones se cerrarán al modificar el backend
    python run_dev.py --port 8001
) else if "%option%"=="2" (
    echo.
    echo Iniciando servidor sin recarga automática...
    echo ✅ Las sesiones se mantendrán activas
    python run_dev.py --no-reload --port 8001
) else if "%option%"=="3" (
    echo.
    echo Iniciando servidor en modo producción...
    python run_dev.py --no-reload --port 8001
) else (
    echo Opción no válida
)

pause
