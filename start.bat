@echo off
title TicketMaster Pro
echo ============================================
echo   TICKET MASTER PRO - Sistema de Boletos
echo ============================================
echo.

REM Verificar que Docker este corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta corriendo.
    echo         Abre Docker Desktop y vuelve a intentar.
    echo.
    pause
    exit /b 1
)

echo [1/2] Iniciando base de datos MySQL...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] No se pudo iniciar la base de datos.
    echo         Asegurate de que el archivo docker-compose.yml este en esta carpeta.
    echo.
    pause
    exit /b 1
)

echo [*] Esperando que MySQL este listo...
timeout /t 12 /nobreak >nul

echo [2/2] Iniciando TicketMaster Pro...
if not exist "TicketMasterPro.exe" (
    echo [ERROR] No se encontro TicketMasterPro.exe en esta carpeta.
    pause
    exit /b 1
)

start "" "TicketMasterPro.exe"
