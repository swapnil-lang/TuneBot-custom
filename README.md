# TuneBot

A Discord music bot with advanced playback controls and Spotify integration.

## Quick Start (Docker)
1. Clone the repository
    - `git clone xxx`
2. Copy the example docker compose file
    - `cp docker-compose.example.yml docker-compose.yml`
3. Add your credentials to the environment variables:
    - Get Discord token from [Discord Developer Portal](https://discord.com/developers/applications)
    - Get Spotify credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
4. Run the bot
   - `docker-compose up -d`

## Features

### Music Controls
- `play` or `p` - Play a song from YouTube or Spotify
- `queue` or `q` - Show current queue
- `skip` or `s` - Skip current song
- `stop` - Stop playback and clear queue
- `pause`, `resume` - Control playback
- `nowplaying` or `np` - Show current song info
- `playnum <number>` or `ptn` - Play specific song from queue
- `shuffle` or `sh` - Shuffle the queue

### Queue Management
- `clear` - Clear the queue
- `remove <number>` or `rm` - Remove specific song from queue
- `remove @user` or `rm @user` - Remove all songs by a user
- `move <from> <to>` or `mv` - Move song in queue
- `loop` - Toggle queue loop

### System Commands
- `disconnect` or `d` - Leave voice channel
- `ping` - Check bot latency
- `help` - Show help message

### Spotify Integration
- Support for Spotify tracks and playlists
- Automatic YouTube search for Spotify tracks
- Queue management for playlists

## Technical Details
- Uses discord.py for Discord integration
- yt-dlp for YouTube downloads
- FFmpeg for audio processing
- Async/await for non-blocking operations
- SponsorBlock integration for skipping non-music segments