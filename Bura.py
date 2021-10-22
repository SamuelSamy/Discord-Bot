import discord
import json
import os

from discord.ext import commands


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
        elif file_path_name.endswith('.py'):
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

bot = commands.Bot(intents = discord.Intents.all(), command_prefix = prefixes['876988765955039273'])

load_packages(files, bot)


@bot.command()
async def restart(ctx):

    if ctx.author.id == 225629057172111362:
        try:
            unload_packages(files, bot)
            load_packages(files, bot)
            await ctx.send("Modules restarted!")
        except:
            await ctx.send("Error while restarting")


bot.run(config['bura_token'])    

