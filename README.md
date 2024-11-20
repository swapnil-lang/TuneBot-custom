# TuneBot 🎵

A powerful, yet easy-to-use Discord music bot built with `discord.py` and `yt-dlp`. The bot can stream audio from YouTube, manage music queues, handle multiple guilds, and much more.

## Features
- 🎶 Play music from YouTube via URL or search
- 📜 Queue management (add songs to queue, view current queue)
- 🔁 Loop songs
- 🔊 Adjust volume (0-200%)
- 🛑 Stop and clear the queue
- ⏭️ Skip current track 
- ⏭ Auto-disconnect when everyone leaves the voice channel
- 🛠 Simple and customizable help command

## Installation (Docker)
1. Clone repository
2. Copy the example docker-compose file `cp docker-compose.example docker-compose.yml`
3. Add your bot token into docker-compose.yml
4. `docker-compose up -d --build`
5. Yes, it's that easy!
