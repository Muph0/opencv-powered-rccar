@echo off

python main.py

echo.
echo.
echo Error %errorlevel%
if not "%errorlevel%" == "0" pause