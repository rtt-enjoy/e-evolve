@echo off
setlocal

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"

if not exist "%FRONTEND%\package.json" (
  echo Could not find frontend\package.json.
  exit /b 1
)

where pnpm >nul 2>nul
if errorlevel 1 (
  echo pnpm is required to run the local dashboard.
  echo Install it with: npm install -g pnpm
  exit /b 1
)

cd /d "%FRONTEND%" || exit /b 1

if not exist "node_modules" (
  echo Installing frontend dependencies...
  call pnpm install
  if errorlevel 1 exit /b %errorlevel%
)

echo.
echo Starting E-Evolve local dashboard...
echo Local-only dashboard tools are enabled in dev mode.
echo Open the URL printed by Vite, usually http://127.0.0.1:5173/
echo.

call pnpm run dev
