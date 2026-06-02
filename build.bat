@echo off
chcp 65001 >nul
setlocal

echo [1/3] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo Dependency installation failed.
  exit /b 1
)

echo [2/3] Building EXE...
pyinstaller --noconfirm --clean --onefile --windowed --name pdf2img --paths src main.py
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo [3/3] Done.
echo EXE path: dist\pdf2img.exe
pause
