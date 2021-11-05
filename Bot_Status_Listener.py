import asyncio
import discord
import json

from discord.ext import tasks, commands

bot = commands.Bot(intents = discord.Intents.all(), command_prefix = "=")


with open('data/config.json') as file:
    config = json.load(file)
    file.close()


@bot.event
async def on_ready():
    
    check_bots.start()

    print ("Bot is ready")


@tasks.loop(seconds = 60)
async def check_bots():
    
    guild = bot.get_guild(896413113044316162)

    bura = guild.get_member(900101389416546314)
    af   = guild.get_member(867480262777765918)

    if str(bura.status) == "offline":
        await send_alert(bura)

    if str(af.status) == "offline":
        await send_alert(af)


async def send_alert(client):
    
    channel = bot.get_channel(905919522349928458)

    await channel.send(f"``` ```\n<@225629057172111362>\n<@{client.id}> just went offline\n``` ```")


bot.run(config['listener_token'])    

