# 🎮 Let's Play Discord Server Manager

A custom Discord bot to manage your Minecraft server — designed for the Let's Play Discord community.

---

## 🛠 Features

- 🟢 Start your Minecraft server with a command  
- 💬 View online players directly from Discord  
- 📊 Check server TPS and status  
- 📥 Share modpack download link  
- 📡 Monitor activity and auto-shutdown if idle  
- 🛡️ Secure player login and registration support (via Minecraft mod)

---

## ⚙️ Setup Guide

1. Clone this repo  
2. Create a `.env` file in the root directory  
3. Fill it with the following keys:

```env
# Used for hashing passwords securely
PASSWORD_PEPPER=your_secret_pepper

# Your Discord bot token
DISCORD_API_KEY=your_discord_bot_api_key

# RCON password set in server.properties
RCON_PASSWORD=your_rcon_password

# Full path to the server startup script
# Example for Windows:
SERVER_PATH="C:\\Path\\To\\Your\\Server\\run.bat"
# Example for Linux:
# SERVER_PATH="/home/youruser/mcserver/start.sh"

# Custom server info
SERVER_NAME=LPS Minecraft Server
SERVER_DOMAIN=play.lpsmc.net
SERVER_VERSION=1.21.1
MOD_LOADER=Fabric

# Modpack download link (optional but recommended)
MODPACK_URL=https://your.upload.link/mods.rar
