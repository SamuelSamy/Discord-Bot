import discord
import json
import os
import datetime, time

from discord.ext import commands
from discord.ext.commands.core import has_permissions


def load_packages(files, bot):

    for file in files:
        if file.endswith(".py"):
            file = file.replace("/", ".")
            bot.load_extension(file[2:-3])


def unload_packages(files, bot):

    for file in files:
        if file.endswith(".py"):
            file = file.replace("/", ".")
            bot.unload_extension(file[2:-3])


def init_files(path_root, files):

    current_files = os.listdir(path_root)

    for file_path_name in current_files:

        if os.path.isdir(f"{path_root}/{file_path_name}") and file_path_name not in ["__pycache__", "__classes"]:
            init_files(f"{path_root}/{file_path_name}", files)
        elif file_path_name.endswith('.py') and not file_path_name.startswith('package'):
            files.append(f"{path_root}/{file_path_name}")


def get_json_file(path):

    with open(path) as file:
        json_f = json.load(file)
        file.close()

    return json_f


prefixes = get_json_file('data/prefixes.json')
config = get_json_file('data/config.json')

files = []
init_files('./cogs', files)

bot = commands.Bot(intents = discord.Intents.all(), command_prefix = prefixes['852143372353142785'])

load_packages(files, bot)


@bot.command()
@has_permissions(administrator = True)
async def restart(ctx):

    if ctx.author.id == 225629057172111362:
        try:
            unload_packages(files, bot)
            load_packages(files, bot)
            await ctx.send("Modules restarted!")
        except Exception as e:
            await ctx.send("Error while restarting")
            print (f"Error While Restarting:\n{e}\n")


@bot.event
async def on_ready():
    global startTime
    startTime = round(time.time())


@bot.command()
@has_permissions(administrator = True)
async def uptime(ctx):
    uptime = str(datetime.timedelta(seconds = int(round(time.time() - startTime))))
    await ctx.send(f"Uptime: {uptime}")


class NewHelpName(commands.MinimalHelpCommand):
    
    def get_pages(self):
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            return emby


class NewHelpName(commands.MinimalHelpCommand):
    
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)


bot.help_command = NewHelpName()

bot.run(config['anime_fighters_token'])    

