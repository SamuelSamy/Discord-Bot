import discord
import json
import os

from discord.ext import commands


def init_bot(bot_prefix):
    bot = commands.Bot(intents = discord.Intents.all(), command_prefix = bot_prefix)
    return bot


def run_bot(bot, config, token):
    print (bot)
    print (config)
    print (token)
    bot.run(config[token])    
    print("run")


def load_packages(files, bot):

    for file in files:
        if file.endswith(".py"):
            file = file.replace("/", ".")
            bot.load_extension(file[2:-3])


def init_files(path_root, files):

    current_files = os.listdir(path_root)

    for file_path_name in current_files:

        if os.path.isdir(f"{path_root}/{file_path_name}") and file_path_name != "__pycache__":
            init_files(f"{path_root}/{file_path_name}", files)
        elif file_path_name.endswith('.py'):
            files.append(f"{path_root}/{file_path_name}")


def get_json_file(path):

    with open(path) as file:
        json_f = json.load(file)
        file.close()

    return json_f


def main():

    files = []
    prefixes = get_json_file('data/prefixes.json')
    config = get_json_file('data/config.json')

    init_files('./cogs', files)

    bot = init_bot(prefixes['894160228239679490'])
    

    load_packages(files, bot)

    run_bot(bot, config, 'main_token')



main()

