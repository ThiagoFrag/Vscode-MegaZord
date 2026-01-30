@echo off
chcp 65001 >nul
title LEVIATHAN VS - The Abyss Awaits
color 0B

echo.
echo    ██╗     ███████╗██╗   ██╗██╗ █████╗ ████████╗██╗  ██╗ █████╗ ███╗   ██╗
echo    ██║     ██╔════╝██║   ██║██║██╔══██╗╚══██╔══╝██║  ██║██╔══██╗████╗  ██║
echo    ██║     █████╗  ██║   ██║██║███████║   ██║   ███████║███████║██╔██╗ ██║
echo    ██║     ██╔══╝  ╚██╗ ██╔╝██║██╔══██║   ██║   ██╔══██║██╔══██║██║╚██╗██║
echo    ███████╗███████╗ ╚████╔╝ ██║██║  ██║   ██║   ██║  ██║██║  ██║██║ ╚████║
echo    ╚══════╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
echo.
echo                     [ VS Code Environment for the Deep ]
echo.
echo    ═══════════════════════════════════════════════════════════════════════
echo.
echo    [1] SUBMERGE  - Encode (sanitize code)
echo    [2] SURFACE   - Restore (decode code)
echo    [3] SCAN      - Preview changes
echo    [4] HUNT      - Statistics
echo    [5] ECHO      - History
echo    [6] DEPTHS    - Interactive mode
echo    [7] VALIDATE  - Check configuration
echo    [8] EMERGE    - Exit
echo.
echo    ═══════════════════════════════════════════════════════════════════════
echo.

set /p choice="    Enter the depths [1-8]: "

if "%choice%"=="1" goto encode
if "%choice%"=="2" goto decode
if "%choice%"=="3" goto preview
if "%choice%"=="4" goto stats
if "%choice%"=="5" goto history
if "%choice%"=="6" goto interactive
if "%choice%"=="7" goto validate
if "%choice%"=="8" goto exit
goto menu

:encode
echo.
echo    [LEVIATHAN] Submerging code into the abyss...
python core\translator.py encode
pause
goto menu

:decode
echo.
echo    [LEVIATHAN] Surfacing with original terms...
python core\translator.py restore
pause
goto menu

:preview
echo.
echo    [LEVIATHAN] Scanning the waters...
python core\translator.py preview
pause
goto menu

:stats
echo.
echo    [LEVIATHAN] Depth report...
python core\translator.py stats
pause
goto menu

:history
echo.
echo    [LEVIATHAN] Echo from the deep...
python core\translator.py history
pause
goto menu

:interactive
echo.
echo    [LEVIATHAN] Entering the abyss...
python core\translator.py interactive
pause
goto menu

:validate
echo.
echo    [LEVIATHAN] Validating lair configuration...
python core\translator.py validate
pause
goto menu

:menu
cls
goto start

:exit
echo.
echo    [LEVIATHAN] Returning to the surface...
timeout /t 2 >nul
exit

:start
cls
goto menu
