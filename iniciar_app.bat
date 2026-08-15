@echo off
setlocal enabledelayedexpansion
title Lista de Presenca - Festa de Sabado
cd /d "%~dp0"

echo ============================================
echo   Lista de Presenca - Festa de Sabado
echo ============================================
echo.

REM ------------------------------------------------------------
REM 1. Verificar se Python esta instalado
REM ------------------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao foi encontrado no PATH.
    echo Instale o Python em https://www.python.org/downloads/
    echo e marque a opcao "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM 2. Garantir que as bibliotecas necessarias estao instaladas
REM ------------------------------------------------------------
echo Verificando dependencias (streamlit, pandas, openpyxl, qrcode, opencv)...
python -m pip show streamlit >nul 2>nul
if errorlevel 1 (
    echo Instalando dependencias, aguarde...
    python -m pip install --quiet "streamlit>=1.32" pandas openpyxl qrcode[pil] pillow opencv-python-headless numpy
) else (
    python -m pip show pandas >nul 2>nul
    if errorlevel 1 python -m pip install --quiet pandas
    python -m pip show openpyxl >nul 2>nul
    if errorlevel 1 python -m pip install --quiet openpyxl
    python -m pip show qrcode >nul 2>nul
    if errorlevel 1 python -m pip install --quiet qrcode[pil] pillow
    python -m pip show opencv-python-headless >nul 2>nul
    if errorlevel 1 python -m pip install --quiet opencv-python-headless numpy
)

REM ------------------------------------------------------------
REM 3. Definir a senha do anfitriao (se ainda nao configurada)
REM ------------------------------------------------------------
if "%ADMIN_PASSWORD%"=="" (
    set ADMIN_PASSWORD=festa123
    echo [AVISO] Usando senha padrao "festa123" para o painel do anfitriao.
    echo Para trocar, defina a variavel ADMIN_PASSWORD antes de rodar este arquivo.
)

REM ------------------------------------------------------------
REM 4. Verificar porta livre automaticamente usando PowerShell
REM ------------------------------------------------------------
echo Procurando porta livre...
for /f "tokens=*" %%a in ('powershell -Command "$l = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0); $l.Start(); $p = $l.LocalEndpoint.Port; $l.Stop(); $p"') do set PORTA=%%a

if not defined PORTA (
    echo [ERRO] Nao foi possivel encontrar uma porta livre.
    set PORTA=8501
)

echo.
echo Iniciando o servidor deste projeto na porta %PORTA%...
echo (isso pode levar alguns segundos na primeira vez)
echo.

REM ------------------------------------------------------------
REM 5. Iniciar o Streamlit em segundo plano, SEM abrir navegador sozinho
REM ------------------------------------------------------------
start "Lista de Presenca - Servidor" /min python -m streamlit run app.py --server.headless true --server.port %PORTA% --browser.serverAddress localhost


REM ------------------------------------------------------------
REM 6. Esperar o servidor deste projeto responder antes de abrir o navegador
REM    (evita abrir a pagina cedo demais e cair em erro/pagina errada)
REM ------------------------------------------------------------
set TENTATIVAS=0
:esperar_servidor
set /a TENTATIVAS+=1
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:!PORTA!' -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
    if !TENTATIVAS! GEQ 30 (
        echo.
        echo [ERRO] O servidor nao respondeu a tempo na porta !PORTA!.
        echo Verifique a janela minimizada "Lista de Presenca - Servidor" para ver mensagens de erro.
        pause
        exit /b 1
    )
    timeout /t 1 /nobreak >nul
    goto esperar_servidor
)

echo Servidor no ar! Abrindo http://localhost:!PORTA!
start "" "http://localhost:!PORTA!"

echo.
echo Este app esta rodando na janela minimizada "Lista de Presenca - Servidor".
echo Para encerrar, feche aquela janela (ou esta e digite S quando perguntado).
echo.
pause
