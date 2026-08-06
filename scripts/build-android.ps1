#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
$mobile = Join-Path $PSScriptRoot "..\mobile"
Push-Location $mobile

if (-not (Test-Path "android")) {
  Write-Host "==> Adding Android platform"
  npx cap add android
}

Write-Host "==> Building Angular web assets"
npm run build

Write-Host "==> Syncing Capacitor"
npx cap sync android

Write-Host "==> Assembling debug APK with Gradle"
Push-Location "android"
.\gradlew.bat assembleDebug
Pop-Location

Pop-Location
Write-Host "`n==> APK ready: mobile/android/app/build/outputs/apk/debug/app-debug.apk"
