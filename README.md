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
- `play` (`p`) - Play music or add to queue
- `playnext` (`pn`) - Add song to play next
- `pause` - Pause playback
- `resume` - Resume playback
- `skip` (`s`) - Skip to next song
- `nowplaying` (`np`) - Show current song info

### Queue Controls
- `queue` (`q`) - View current queue
- `shuffle` (`sh`) - Randomize queue
- `clear` (`c`) - Empty the queue
- `playnum` - Play specific song number from the queue
- `repeat` (`r`) - Toggle queue loop
- `remove` (`rm`) - Remove specific song from queue, or all songs play a user

### System Controls
- `disconnect` (`dc`) - Leave channel
- `help` (`h`) - Show help message

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