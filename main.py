import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
import requests

# FFmpeg options for audio playback
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# Create a bot instance with specified command prefix and intents
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command("help")  # Remove the default help command


def search(query):
    # Use YoutubeDL library to search for videos or extract info from the provided query
    with YoutubeDL({"format": "bestaudio", "noplaylist": "True"}) as ydl:
        try:
            requests.get(query)  # Check if the query is a direct URL
        except:
            info = ydl.extract_info(f"ytsearch:{query}", download="False")["entries"][0]  # Search for videos based on the query
        else:
            info = ydl.extract_info(query, download="False")  # Extract video info from the provided URL
    return info, info['formats'][0]['url']  # Return the video info and the audio source URL


@bot.event
async def on_ready():
    # Event handler for when the bot is ready and connected to the server
    print("Tıngırdatmaya hazır!")


@bot.command(name="join", aliases=["Katıl", "katıl", "gir"])
async def join(ctx):
    # Command to make the bot join the voice channel of the user who issued the command
    member_vc = ctx.author.voice
    if member_vc and member_vc.channel:
        await member_vc.channel.connect()
    else:
        await ctx.send("Bir hata oldu, bir ses kanalında olduğundan emin ol.")


@bot.command(name="leave", aliases=["Leave", "çık", "ayrıl"])
async def leave(ctx):
    # Command to make the bot leave the voice channel
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Sohbetin de sıkıcıydı zaten 🤭")
    else:
        await ctx.send("Zaten bir sesli sohbet kanalında değilim.")


@bot.command(name="play", aliases=["Play", "oynat", "p"])
async def play(ctx, *, query):
    # Command to play a video/audio in the voice channel
    member_vc = ctx.author.voice
    if member_vc and member_vc.channel:
        if ctx.voice_client:
            # If the bot is already in a voice channel, play the requested audio
            client_voice = ctx.voice_client
            video, source = search(query)
            await ctx.send(f"{video['title']} çalıyor.")
            client_voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTIONS))
            client_voice.is_playing()
        else:
            # If the bot is not in a voice channel, join the user's channel and play the requested audio
            await member_vc.channel.connect()
            client_voice = ctx.voice_client
            video, source = search(query)
            await ctx.send(f"{video['title']} çalıyor.")
            client_voice.play(FFmpegPCMAudio(source))
            client_voice.is_playing()


@bot.command(aliases=["dur", "kapat"], pass_content=True)
async def stop(ctx):
    # Command to stop the audio playback
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


bot.run("-Your discord developer token here-")
