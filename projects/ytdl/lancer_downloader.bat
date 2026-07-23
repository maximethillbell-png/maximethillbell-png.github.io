@echo off
title Video Downloader - Démarrage...
echo.
echo  ╔══════════════════════════════════════╗
echo  ║      🎬  Video Downloader            ║
echo  ║      Démarrage en cours...           ║
echo  ╚══════════════════════════════════════╝
echo.

:: Vérifie que Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ❌  Python n'est pas installé ou pas dans le PATH.
    echo  ➡  Télécharge Python sur https://python.org
    pause
    exit /b 1
)

:: Installe yt-dlp si absent
python -c "import yt_dlp" >nul 2>&1
if %errorlevel% neq 0 (
    echo  📦  Installation de yt-dlp...
    python -m pip install yt-dlp -q
)

:: Lance l'app (sans console)
echo  ✅  Lancement de l'application...
start "" pythonw "%~dp0downloader.py"
exit
