@echo off
echo Iniciando Lista de Presenca...

echo Verificando Python...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python nao encontrado. Instale o Python para continuar.
    pause
    exit /b
)

echo Instalando dependencias...
pip install streamlit pandas >nul 2>&1

set PORT=8501
:SEARCHPORT
netstat -o -n -a | findstr ":%PORT% " | findstr "LISTENING" > NUL
if %ERRORLEVEL% EQU 0 (
  set /a PORT+=1
  goto SEARCHPORT
)

echo Porta livre encontrada: %PORT%
echo Iniciando Streamlit na porta %PORT%...
start http://localhost:%PORT%
streamlit run app.py --server.port %PORT% --server.headless true
