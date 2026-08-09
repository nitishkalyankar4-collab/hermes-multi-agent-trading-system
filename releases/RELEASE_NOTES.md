# Hermes Multi-Agent Trading System - v1.0.0 Mobile Release

## Mobile Release Summary

This release includes the standalone Android APK package and PWA mobile application bundle for the **Hermes Multi-Agent Trading System**.

- **App Name**: Hermes Trading System
- **Package Name**: `com.hermes.tradingsystem`
- **Version**: `1.0.0`
- **Release APK**: [`releases/hermes-v1.0.0.apk`](./hermes-v1.0.0.apk)

## Features Included

1. **Touch-Optimized Mobile Dashboard**:
   - Live streaming of Delta Exchange India market scanner data.
   - Confluence Index gauge meters and sub-agent score breakdowns (SMC, Order Flow, Quant, Risk, Macro).
   - Filter bar and search optimized for mobile screen sizes (360px+).

2. **Mobile App Architecture**:
   - Native Android WebView runtime container with internet and network state permissions.
   - Standalone Progressive Web App (PWA) manifest (`manifest.json`) and Service Worker (`sw.js`) for caching and offline execution.

3. **Backend Multi-Agent Engine Integration**:
   - REST API integration pointing to `http://localhost:8888` for live scan polling and force re-scanning.
   - Telegram Bot controls (`/begin`, `/stopapp`, `/analyse`, `/crosscheck`).

## Installation Instructions

1. **Android APK Installation**:
   - Download [`hermes-v1.0.0.apk`](./hermes-v1.0.0.apk) directly to your Android device.
   - Enable "Install from Unknown Sources" in your device settings if prompted.
   - Tap the `.apk` file to install and launch **Hermes Trading System**.

2. **PWA Mobile Browser Installation**:
   - Open `http://localhost:8888` on Chrome/Safari on mobile.
   - Tap "Add to Home Screen" to install the standalone Web App.
