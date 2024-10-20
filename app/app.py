import discord
import os
import yt_dlp
import asyncio
from discord.ext import commands
from collections import deque
from async_timeout import timeout

def format_duration(duration):
    """Formats duration in seconds to H:MM:SS or M:SS."""
    if duration is None:
        return "Unknown"
    hours, remainder = divmod(int(duration), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.message_content = True
        super().__init__(command_prefix=os.environ['DISCORD_PREFIX'], intents=intents)
        
        self.music_queues = {}
        
    async def setup_hook(self):
        """Initialize bot settings on startup."""
        await self.add_cog(Music(self)) 

    async def on_ready(self):
        """Event called when the bot is ready."""
        print(f"Logged in as {self.user}")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=f"{os.environ['DISCORD_PREFIX']}help for commands"
        ))

    async def on_voice_state_update(self, member, before, after):
        """Auto-disconnect when everyone leaves the voice channel."""
        if member.guild.voice_client:
            voice_channel = member.guild.voice_client.channel

            if len(voice_channel.members) == 1 and voice_channel.members[0] == member.guild.voice_client.user:
                await asyncio.sleep(5)
                if len(voice_channel.members) == 1:
                    await member.guild.voice_client.disconnect()

class MusicQueue:
    """Handles the music queue for a guild."""
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.loop = False
        self.volume = 1.0

class YTDLSource(discord.PCMVolumeTransformer):
    """Enhanced YouTube downloader with error handling and metadata."""
    ytdl_format_options = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
        }],
    }
    
    ffmpeg_options = {
        'options': '-vn -loglevel warning'
    }
    
    ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

    def __init__(self, source, *, data, volume=1.0):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('webpage_url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader')

    @classmethod
    async def create_source(cls, search: str, *, loop=None, download=False):
        """Creates a source from a YouTube URL or search term."""
        loop = loop or asyncio.get_event_loop()
        
        try:
            async with timeout(10):
                data = await loop.run_in_executor(
                    None,
                    lambda: cls.ytdl.extract_info(search, download=download)
                )
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")

        if 'entries' in data:
            # Take the first item from a playlist or search result
            data = data['entries'][0]

        if download:
            source = cls.ytdl.prepare_filename(data)
        else:
            source = data['url']

        return cls(
            discord.FFmpegPCMAudio(source, **cls.ffmpeg_options),
            data=data
        )

class Music(commands.Cog):
    """Music commands cog."""
    def __init__(self, bot):
        self.bot = bot
        
    async def get_queue(self, ctx) -> MusicQueue:
        """Gets or creates a music queue for the guild."""
        if ctx.guild.id not in self.bot.music_queues:
            self.bot.music_queues[ctx.guild.id] = MusicQueue()
        return self.bot.music_queues[ctx.guild.id]

    @commands.command(name='play', aliases=['p'], help='Plays a song from YouTube URL or search term')
    async def play(self, ctx, *, query):
        """Play a song or add it to the queue."""
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")

        queue = await self.get_queue(ctx)
        
        try:
            if not ctx.voice_client:
                await ctx.author.voice.channel.connect()
            elif ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
                
            async with ctx.typing():
                source = await YTDLSource.create_source(query, loop=self.bot.loop)
                
                if ctx.voice_client.is_playing():
                    queue.queue.append(source)
                    duration_str = format_duration(source.duration)
                    embed = discord.Embed(
                        title="Added to Queue",
                        description=f"🎵 **{source.title}**\nBy: {source.uploader}\nDuration: {duration_str}",
                        color=discord.Color.green()
                    )
                    if source.thumbnail:
                        embed.set_thumbnail(url=source.thumbnail)
                    await ctx.send(embed=embed)
                else:
                    await self.play_song(ctx, source)
                    
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    async def play_song(self, ctx, source):
        """Plays a song and handles the queue."""
        queue = await self.get_queue(ctx)
        queue.current = source
        
        ctx.voice_client.play(
            source,
            after=lambda e: self.bot.loop.create_task(
                self.play_next(ctx) if not e else ctx.send(f"Error: {e}")
            )
        )
        
        duration_str = format_duration(source.duration)
        embed = discord.Embed(
            title="Now Playing",
            description=f"🎵 **{source.title}**\nBy: {source.uploader}\nDuration: {duration_str}",
            color=discord.Color.blue()
        )
        if source.thumbnail:
            embed.set_thumbnail(url=source.thumbnail)
        await ctx.send(embed=embed)

    async def play_next(self, ctx):
        """Plays the next song in the queue."""
        queue = await self.get_queue(ctx)
        
        if queue.loop and queue.current:
            queue.queue.appendleft(queue.current)
            
        if queue.queue:
            next_song = queue.queue.popleft()
            await self.play_song(ctx, next_song)

    @commands.command(name='queue', help='Shows the current queue')
    async def show_queue(self, ctx):
        """Displays the current queue."""
        queue = await self.get_queue(ctx)
        
        if not queue.current and not queue.queue:
            return await ctx.send("The queue is empty!")
            
        embed = discord.Embed(
            title="Music Queue",
            color=discord.Color.blue()
        )
        
        if queue.current:
            duration_str = format_duration(queue.current.duration)
            embed.add_field(
                name="Now Playing",
                value=f"🎵 {queue.current.title} ({duration_str})",
                inline=False
            )
            
        if queue.queue:
            queue_list = "\n".join(
                f"{i+1}. {song.title} ({format_duration(song.duration)})"
                for i, song in enumerate(queue.queue)
            )
            embed.add_field(
                name="Up Next",
                value=queue_list,
                inline=False
            )
            
        await ctx.send(embed=embed)

    @commands.command(name='loop', help='Toggles loop mode')
    async def toggle_loop(self, ctx):
        """Toggles loop mode for the current queue."""
        queue = await self.get_queue(ctx)
        queue.loop = not queue.loop
        await ctx.send(f"Loop mode: {'enabled' if queue.loop else 'disabled'}")

    @commands.command(name='volume', help='Sets the volume (0-200)')
    async def volume(self, ctx, volume: int):
        """Adjusts the player volume."""
        if not 0 <= volume <= 200:
            return await ctx.send("Volume must be between 0 and 200!")
            
        if ctx.voice_client and ctx.voice_client.source:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f"Volume set to {volume}%")
        else:
            await ctx.send("Not playing any audio to adjust volume.")

    @commands.command(name='clear', help='Clears the queue')
    async def clear(self, ctx):
        """Clears the music queue."""
        queue = await self.get_queue(ctx)
        queue.queue.clear()
        await ctx.send("Queue cleared!")

    @commands.command(name='stop', help='Stops playing and clears the queue')
    async def stop(self, ctx):
        """Stops playing and clears the queue."""
        queue = await self.get_queue(ctx)
        queue.queue.clear()
        if ctx.voice_client:
            ctx.voice_client.stop()
        await ctx.send("Stopped playing and cleared the queue.")

    @commands.command(name='disconnect', aliases=['dc'], help='Disconnects the bot')
    async def disconnect(self, ctx):
        """Disconnects the bot from voice."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from voice channel.")

def setup(bot):
    """Sets up the Music cog."""
    bot.add_cog(Music(bot))

if __name__ == "__main__":
    bot = MusicBot()
    bot.run(os.environ['DISCORD_BOT_TOKEN'])
