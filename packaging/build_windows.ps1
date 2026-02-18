#!/usr/bin/env pwsh
<#
# Build script for Windows
# Creates a single-file DictaPilot.exe using PyInstaller spec file
#

$ErrorActionPreference = "Stop"

Write-Host "=== DictaPilot Windows Build ===" -ForegroundColor Cyan

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.10+"
}

# Install PyInstaller if needed
Write-Host "Ensuring PyInstaller is installed..."
pip install pyinstaller --quiet

# Clean previous build
if (Test-Path "dist") {
    Write-Host "Cleaning previous build..."
    Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
}

# Clean build folder
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
}

# Build using spec file
Write-Host "Building DictaPilot.exe..."
pyinstaller packaging/DictaPilot.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Build Complete ===" -ForegroundColor Green
    Write-Host "Output: dist/DictaPilot.exe" -ForegroundColor Green
    Write-Host "`nTo create release zip:"
    Write-Host "  Compress-Archive -Path dist/DictaPilot.exe -DestinationPath dist/DictaPilot-windows-x64.zip" -ForegroundColor Yellow
} else {
    Write-Error "Build failed!"
}