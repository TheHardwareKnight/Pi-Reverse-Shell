@echo off
color 0A
echo.
echo  ============================================================
echo    Pi Reverse Shell ^| Windows PC Information
echo  ============================================================
echo.
echo  ---- SYSTEM ------------------------------------------------
echo.
echo    Hostname   : %COMPUTERNAME%
echo    Username   : %USERNAME%
echo    User Domain: %USERDOMAIN%
echo.
for /f "tokens=2 delims==" %%A in ('wmic os get Caption /value 2^>nul') do echo    OS         : %%A
for /f "tokens=2 delims==" %%A in ('wmic os get Version /value 2^>nul') do echo    OS Version : %%A
for /f "tokens=2 delims==" %%A in ('wmic os get OSArchitecture /value 2^>nul') do echo    Arch       : %%A
echo.
echo  ---- NETWORK -----------------------------------------------
echo.
ipconfig | findstr /i "adapter\|IPv4\|IPv6\|Gateway\|subnet"
echo.
echo  ---- PYTHON ------------------------------------------------
echo.
python --version >nul 2>&1
if %errorlevel%==0 (
    for /f %%V in ('python --version 2^>^&1') do echo    %%V
    for /f %%P in ('where python 2^>nul') do echo    Path: %%P
) else (
    echo    Python not found in PATH.
    echo    Download from: https://www.python.org/downloads/
)
echo.
echo  ---- STARTUP PATHS (Task Scheduler / Run key) --------------
echo.
echo    Startup folder : %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
echo    Task Scheduler : Run "taskschd.msc" to open Task Scheduler
echo.
echo  ============================================================
echo.
pause
