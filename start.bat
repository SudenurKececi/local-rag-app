@echo off
chcp 65001 >nul
title RAG Asistani

echo.
echo  ================================================
echo    RAG Asistani - Baslatiliyor
echo  ================================================
echo.

REM --- 1. Model yukle ---
echo  [1/3] Foundry modeli yukleniyor (phi-3.5-mini)...
foundry model load phi-3.5-mini
if %errorlevel% neq 0 (
    echo  HATA: Foundry modeli yuklenemedi.
    echo  Foundry'nin yuklu ve calisiyor olmasi gerekiyor.
    pause
    exit /b 1
)
echo  Model yuklendi.
echo.

REM --- 2. Flask sunucusunu arka planda baslat ---
echo  [2/3] Web sunucusu baslatiliyor...
cd /d "%~dp0"
start "RAG Sunucusu" /B cmd /c "venv\Scripts\activate && python src\server.py"
echo  Sunucu baslatildi.
echo.

REM --- 3. Kisa bekleme, sonra tarayici ac ---
echo  [3/3] Tarayici aciliyor (3 saniye bekleniyor)...
timeout /t 3 /nobreak >nul
start http://localhost:5000

echo.
echo  ================================================
echo    RAG Asistani hazir!
echo    Tarayicinizda http://localhost:5000 acildi.
echo  ================================================
echo.
echo  Bu pencereyi KAPATIRSANIZ sunucu da durur.
echo  Kapatmak icin bir tusa basin...
pause >nul
