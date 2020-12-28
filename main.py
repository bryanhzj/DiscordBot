import discord
from discord.ext import commands, tasks
import os
from discord.voice_client import VoiceClient
# from replit import db
# from keep_alive import keep_alive
from random import choice
import youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

client = commands.Bot(command_prefix='?')

# @commands.command(pass_context=True)
# async def play(self, ctx, *, url):
#     print(url)
#     server = ctx.message.guild
#     voice_channel = server.voice_client

#     async with ctx.typing():
#         player = await YTDLSource.from_url(url, loop=self.bot.loop)
#         ctx.voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
#     await ctx.send('Now playing: {}'.format(player.title))

status = ['Jamming out to music!', 'Eating!', 'Sleeping!']

@client.event
async def on_ready():
  change_status.start()
  print('We have logged in  as {0.user}'.format(client))

@tasks.loop(seconds=20)
async def change_status():
  await client.change_presence(activity=discord.Game(choice(status)))

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
  await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)}ms')

@client.event
async def new_joiner(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}! Check out our commands `?help`')

@client.command(name='play', help='This command plays music')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))

@client.command(name='stop', help='This command stops any song that is playing')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()
    
# @client.event
# async def on_message(message):
#   if message.author == client.user:
#     return

#   # if message.content.startswith('?ping'):
#   #   ping(ctx)

#   if message.content.startswith('$hello'):
#     await message.channel.send('Hello!')

#   # else:
#   #   await message.channel.send("nice!", tts=True)
#   await client.process_commands(message)






# keep_alive()
# client.run(os.getenv('TOKEN'))
client.run('NzkyOTQ4MzQwMTk4MzQyNjg3.X-lIsA.fXkXoIOqggQFLJPvZNpEQYrZAFQ')