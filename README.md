# TuneBot 🎵
A powerful Discord music bot with YouTube and Spotify support. Stream music from both platforms with simple commands.

## Features
- 🎵 Play from YouTube URLs or search terms
- 🎧 Spotify support (tracks, playlists, albums)
- 📑 Queue management
- 🔁 Loop mode
- ⏭️ Skip tracks
- 🔊 Volume control
- 🛑 Auto-disconnect when channel is empty

## Quick Start (Docker)
1. Clone the repository
2. Create `docker-compose.yml`:
```yaml
services:
  tunebot:
    build: .
    environment:
      - DISCORD_BOT_TOKEN=your_bot_token
      - DISCORD_PREFIX=!
      - SPOTIFY_CLIENT_ID=your_spotify_client_id
      - SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```
3. Add your credentials:
   - Get Discord token from [Discord Developer Portal](https://discord.com/developers/applications)
   - Get Spotify credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
4. Run: `docker-compose up -d`

## Commands
- `!play <query>` - Play from YouTube/Spotify
- `!skip` - Skip current track
- `!queue` - Show playlist
- `!loop` - Toggle loop mode
- `!volume <0-200>` - Adjust volume
- `!stop` - Stop and clear queue
- `!dc` - Disconnect bot

## Spotify Support
Just paste any Spotify link:
```
!play https://open.spotify.com/track/...   // Single track
!play https://open.spotify.com/album/...   // Full album
!play https://open.spotify.com/playlist/... // Playlist
```

## Notes
- Music is streamed via YouTube
- Stop playlist processing anytime with !stop
- Requires Discord bot with Message Content Intent enabled