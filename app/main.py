import os
import discord
import asyncio
from discord.ext import commands
from models.spotify_client import SpotifyClient

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

class MusicBot(commands.Bot):
    def __init__(self):
        prefix = os.getenv('DISCORD_PREFIX', '/')
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            help_command=None
        )
        
        self.music_queues = {}
        self.spotify_client = SpotifyClient()
        self._initialized = False
        self._shutdown_event = asyncio.Event()
        self.current_np_view = None
    
    async def setup_hook(self):
        """Initialize cogs and configurations."""
        if self._initialized:
            return
            
        print("\n✅ Bot Initialization")
        
        try:
            # Load music cog
            from cogs.music import Music
            await self.add_cog(Music(self))
            print("✅ Commands")

            # Register help command
            @self.command(name='help', aliases=['h'])
            async def help_command(ctx):
                embed = discord.Embed(
                    title="🎵 TuneBot Commands",
                    description=f"Use `{ctx.prefix}command` or its alias",
                    color=discord.Color.blue()
                )

                music_controls = (
                    f"`play` (`p`) - Play music or add to queue\n"
                    f"`playnext` (`pn`) - Add song to play next\n"
                    f"`pause` - Pause playback\n"
                    f"`resume` - Resume playback\n"
                    f"`skip` (`s`) - Skip to next song\n"
                    f"`nowplaying` (`np`) - Show current song info\n"
                    f"`fastforward` (`ff`) - Skip ahead in current song (default 15 seconds)\n"
                )
                embed.add_field(name="Music Controls", value=music_controls, inline=False)

                queue_controls = (
                    f"`queue` (`q`) - View current queue\n"
                    f"`shuffle` (`sh`) - Randomize queue\n"
                    f"`clear` (`c`) - Empty the queue\n"
                    f"`playnum <number>` - Play specific song number\n"
                    f"`repeat` (`r`) - Toggle queue loop"
                    f"`remove` (`rm`)` - Remove specific song from queue, or all songs play a user"
                )
                embed.add_field(name="Queue Controls", value=queue_controls, inline=False)

                system_controls = (
                    f"`disconnect` (`dc`) - Leave channel\n",
                    f"`help` (`h`) - Show help message"
                )
                embed.add_field(name="System Controls", value=system_controls, inline=False)

                examples = (
                    f"`{ctx.prefix}p never gonna give you up` - Search & play\n"
                    f"`{ctx.prefix}p https://youtu.be/...` - Play URL\n"
                    f"`{ctx.prefix}ff 45` - Jump to 45 seconds\n"
                    f"`{ctx.prefix}playnum 3` - Play queue item #3"
                    f"`{ctx.prefix}rm 3` - Remove queue item #3"
                    f"`{ctx.prefix}rm @user` - Remove all queue items by user"
                )
                embed.add_field(name="Examples", value=examples, inline=False)

                await ctx.send(embed=embed)

            if self.spotify_client.check_connection():
                print("✅ Spotify")
            else:
                print("❌ Spotify")

            print("✅ Ready")
            self._initialized = True

        except Exception as e:
            print("❌ Failed to load commands")
            raise e
    
    async def on_ready(self):
        """Called when the bot is ready."""
        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name=f"music | {self.command_prefix}help"
        )
        await self.change_presence(activity=activity)

    async def close(self):
        """Clean shutdown."""
        for guild in self.guilds:
            if guild.voice_client:
                await guild.voice_client.disconnect()

        if self.current_np_view:
            self.current_np_view.stop()

        self.music_queues.clear()

        await super().close()

async def main():
    """Main async function to run the bot."""
    bot = MusicBot()
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        raise ValueError("No Discord token found in environment variables!")
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass