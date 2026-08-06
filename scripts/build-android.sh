#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../mobile"

if [ ! -d "android" ]; then
  echo "==> Adding Android platform"
  npx cap add android
fi

echo "==> Building Angular web assets"
npm run build

echo "==> Syncing Capacitor"
npx cap sync android

echo "==> Assembling debug APK with Gradle"
cd android
./gradlew assembleDebug

echo ""
echo "==> APK ready: mobile/android/app/build/outputs/apk/debug/app-debug.apk"
