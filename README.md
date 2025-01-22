<div align="center">

# 🔄 App Store & Play Market Update Tracker

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-iOS%20%7C%20Android-lightgrey)](https://github.com/yourusername/app-update-tracker)

</div>

> Track app updates from both App Store and Google Play Store with Telegram notifications.

## 📱 Screenshots

<details>
<summary>Click to expand</summary>

### iOS Notification

![image](https://github.com/user-attachments/assets/0b7bfcc9-ad97-44fe-ac47-1c1af798535e)

### Android Notification

![image](https://github.com/user-attachments/assets/5ebacf27-a873-4133-87c0-b7deceec4bd4)

</details>

## ✨ Features

- 🔄 Real-time update tracking
- 📱 Support for both iOS and Android apps
- 🚀 Version comparison (old -> new)
- 📅 Release date tracking
- 📝 Changelog updates
- ⚡ Fast and lightweight

## 🛠 Installation

1. Clone the repository

```bash
git clone https://github.com/bohd4nx/update-tracker.git
```

2. Install required packages

```bash
pip install -r requirements.txt
```

## 🚀 Usage

### For iOS apps:

Run the App Store tracker:

```bash
python AppStore.py
```

### For Android apps:

Run the Play Store tracker:

```bash
python PlayStore.py
```

## 📝 How to Track Your App

### iOS App

1. Find your app in App Store
2. Get the app ID from URL (numbers after 'id')
3. Update `API_URL` and `DOWNLOAD_URL` with your app ID

### Android App

1. Find your app in Play Store
2. Copy package name from URL (after 'id=')
3. Update `PACKAGE_NAME` and `DOWNLOAD_URL` with your package name

## 🤖 Telegram Setup

1. Create new bot through [@BotFather](https://t.me/BotFather)
2. Copy the bot token
3. Create a channel
4. Add bot as admin to channel
5. Get channel ID (forward message to @getmyid_bot)
6. Update `TOKEN` and `CHAT_ID` in config

## ⚡ Quick Start Example

### Track Telegram app:

```python
# For iOS
API_URL = "https://itunes.apple.com/lookup?id=686449807"
DOWNLOAD_URL = "https://apps.apple.com/app/telegram-messenger/id686449807"

# For Android
PACKAGE_NAME = "org.telegram.messenger"
DOWNLOAD_URL = "https://play.google.com/store/apps/details?id=org.telegram.messenger"
```

## 🔧 Advanced Configuration

- Change check interval: modify `INTERVAL` (in minutes)
- Customize message format: edit `make_message()` method
- Change date format: update `strftime()` parameters

## 📄 License

This project is MIT licensed.