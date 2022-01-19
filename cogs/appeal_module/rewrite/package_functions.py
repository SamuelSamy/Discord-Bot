import copy
import urllib
import re
import discord
import time
import json

from discord_components import *



from cogs.appeal_module.rewrite.package_enums import AppealTypes, AppealStages, AppealStructure, Emotes
from cogs.appeal_module.rewrite.package_repository import DatabaseRepository


def get_appeal_json():
    with open('data/appeals.json') as appealsFile:
        appeals = json.load(appealsFile)
        appealsFile.close()
    return appeals


def save_appeal_json(data):
    with open("data/appeals.json", "w") as f:
        json.dump(data, f)


def convert_time(time):

        time_units = ['s', 'm', 'h', 'd']

        time_dict = {
            's' : 1,
            'm' : 60,
            'h' : 60 * 60,
            'd' : 60 * 60 * 24
        }

        time_unit = time[-1]

        if time_unit not in time_units:
            return -1

        try:
            actual_time = int(time[:-1])
        except:
            return -2
        
        return actual_time * time_dict[time_unit]
    
 
def get_profile(name):
    link = f"https://www.roblox.com/User.aspx?Username={name}"

    try:

        opener = urllib.request.build_opener()
        request = urllib.request.Request(link)
        redirect = opener.open(request)
        profile = redirect.geturl()
        return profile

    except:
        return None


def get_profile_link(roblox_id):
    return f"https://www.roblox.com/users/{roblox_id}/profile"
    

def get_roblox_id(link):
    id = re.search("\d+", link)
    return id.group(0)


def get_appeal_emote(answer):
    if answer == AppealTypes.accepted:
        return Emotes.accepted
    elif answer == AppealTypes.denied:
        return Emotes.denied
    elif answer == AppealTypes.warn:
        return Emotes.warned
    elif answer == AppealTypes.flagged:
        return Emotes.flagged

    return None


def get_logs(guild_id, id):

    guild_id = str(guild_id)

    ids = [id]
    all_time_ids = [id]
    logs = []
    logs_string = ""

    while len(ids) != 0:

        new_ids = []

        for id in ids:

            database = DatabaseRepository()
            data = database.select("select * from appeals where (user = ? or roblox = ?) and stage = ? and guild = ? and response != 0", (id, id, AppealStages.answered, guild_id))
            
            for appeal in data:
                
                if appeal[AppealStructure.ID] not in logs:
                    logs_string += f"{get_appeal_emote(appeal[AppealStructure.response])} {f'ID: {appeal[AppealStructure.ID]}'.ljust(10)} <t:{appeal[AppealStructure.response_time]}:R>\n"
                    logs.append(appeal[AppealStructure.ID])


                if appeal[AppealStructure.user] not in all_time_ids:
                    all_time_ids.append(appeal[AppealStructure.user])
                    new_ids.append(appeal[AppealStructure.user])

                if appeal[AppealStructure.roblox] not in all_time_ids:
                    all_time_ids.append(appeal[AppealStructure.roblox])
                    new_ids.append(appeal[AppealStructure.roblox])

        ids = copy.deepcopy(new_ids)

    if len(logs) != 0:
        return logs_string

    return "No logs found for this user!"


def generate_appeal(bot, guild, appeal_message, prev_appeal = True):

    appeal_id = appeal_message[AppealStructure.ID]

    sent_at = round(time.time())

    user_id = appeal_message[AppealStructure.user]
    user = bot.get_user(user_id)

    roblox_id = appeal_message[AppealStructure.roblox]
    roblox_link = get_profile_link(roblox_id)
    
    ban_reason = appeal_message[AppealStructure.ban_reason][:1024]
    unban_reason = appeal_message[AppealStructure.unban_reason][:1024]

    embed = discord.Embed(
        color = 0x0f8adb
    )

    embed.set_author(
        name = f"{user}",
        icon_url = user.avatar_url
    )

    embed.add_field(
        name = "Discord Profile",
        value = f"{user.mention}  -  {user_id}",
        inline = False
    )    

    embed.add_field(
        name = "Roblox Profile",
        value = f"{roblox_link}  -  {roblox_id}",
        inline = False
    )                   
            

    embed.add_field(
        name = "Why were you banned?",
        value = ban_reason,
        inline = False
    )

    embed.add_field(
        name = "Why do you think you should be unbanned?",
        value = unban_reason,
        inline = False
    )

    logs = ""
    _name = ""

    if prev_appeal:
        _name = "Previous Appeals"
        logs = get_logs(guild, user_id)
    else:
        _name = "Response"
        res = get_appeal_emote(appeal_message[AppealStructure.response])

        
        logs = f"{res} **ID: {appeal_message[AppealStructure.ID]}** at <t:{appeal_message[AppealStructure.response_time]}> (<t:{appeal_message[AppealStructure.response_time]}:R>)"


    if logs != "":
        embed.add_field(
            name = _name,
            value = logs,
            inline = False
        )

    embed.add_field(
        name = "Sent at",
        value = f"<t:{sent_at}> (<t:{sent_at}:R>)",
        inline = False
    )

    embed.set_footer(
        text = f"Appeal ID: {appeal_id}"
    )

    return embed

   
    


def get_appeal_cooldown(guild, discord_id, cooldown):
    guild = str(guild)
    database = DatabaseRepository()
    data = database.select("select * from appeals where guild = ? and user = ? and stage = ? order by response_time desc", (guild, discord_id, AppealStages.answered))
    
    if len(data) == 0:
        return 0
    else:
        appeal = data[0]

        _time = round(time.time()) - appeal[AppealStructure.response_time]

        if appeal[AppealStructure.response] == AppealTypes.warn:
            cooldown *= 2
            
        if _time < cooldown:
            return appeal[AppealStructure.response_time] + cooldown


def get_active_appeal(guild, discord_id):
    
    guild = str(guild)
    database = DatabaseRepository()
    data = database.select("select * from appeals where guild = ? and user = ? and stage != ? and response = 0", (guild, discord_id, AppealStages.answered))
    return None if len(data) == 0 else data[0]


def get_appeal_by_id(guild, appeal_id):
    guild = str(guild)
    database = DatabaseRepository()
    data = database.select("select * from appeals where guild = ? and ID = ?", (guild, appeal_id))
    return None if len(data) == 0 else data[0]


def get_appeal_id(string_id):
    id = re.search("\d+", string_id)
    return int(id.group(0))


def generate_log_embed(bot, appeal_message, admin):

    appeal_id = appeal_message[AppealStructure.ID]

    handled_at = round(time.time())

    user_id = appeal_message[AppealStructure.user]
    user = bot.get_user(user_id)

    roblox_id = appeal_message[AppealStructure.roblox]
    roblox_link = get_profile_link(roblox_id)

    response = "Accepted"
    _color = 0x0ee320
    emoji = Emotes.accepted

    if appeal_message[AppealStructure.response] == AppealTypes.denied:
        response = "Denied"
        _color = 0xe30e27
        emoji = Emotes.denied
    elif appeal_message[AppealStructure.response] == AppealTypes.warn:
        response = "Warn"   
        _color = 0xd6c315
        emoji = Emotes.warned
    elif appeal_message[AppealStructure.response] == AppealTypes.flagged:
        response = "Denied + Flag"
        _color = 0xe30e27
        emoji = Emotes.flagged

    embed = discord.Embed(
        color = _color
    )

    if user is not None:
        embed.set_author(
            name = f"{user}",
            icon_url = user.avatar_url
        )
    else:
        embed.set_author(
            name = "User left the server"
        )

    embed.add_field(
        name = "Discord Profile",
        value = f"{user.mention}  -  {user_id}",
        inline = False
    )    

    embed.add_field(
        name = "Roblox Profile",
        value = f"{roblox_link}  -  {roblox_id}",
        inline = False
    )                   
                
    embed.add_field(
        name = "Handled at",
        value = f"<t:{handled_at}>",
        inline = False
    )

    embed.add_field(
        name = "Response",
        value = f"{emoji} {response}",
        inline = False
    )

    embed.add_field(
        name = "Admin",
        value = f"<@{admin}>",
        inline = False
    )

    embed.set_footer(
        text = f"Appeal ID: {appeal_id}"
    )

    return embed


def cancel_appeal(guild, appeal_id):

    guild = str(guild)
    database = DatabaseRepository()
    rows_affected = database.delete("delete from appeals where guild = ? and id = ? and stage != ?", (guild, appeal_id, AppealStages.answered))

    return True if rows_affected != 0 else False


def get_discord_id_for_old_logs(message):
    reg = re.search("<@.*>", message)
    id = re.search("\d+", reg.group(0))
    return id.group(0)


def get_roblox_id_for_old_logs(message):
    reg = re.search(":\*\*.*/", message)
    id = re.search("\d+", reg.group(0))
    return id.group(0)





async def answer_appeal(bot, guild, appeal_id, answer, admin):
    
    appeal_message = get_appeal_by_id(guild, appeal_id)

    if appeal_message is None:
        return

    user_id = appeal_message[AppealStructure.user]
    user = bot.get_user(user_id)
    

    guild = str(guild)
    database = DatabaseRepository()
    database.general_statement(f"update appeals set {AppealStructure.response} = ?, {AppealStructure.response_time} = ? where {AppealStructure.ID} = ? and {AppealStructure.guild} = ?", (answer, round(time.time()), appeal_id, guild))

    set_sent_answered(guild, appeal_id)

    appeal_message = get_appeal_by_id(guild, appeal_id)

    appeals = get_appeal_json()

    logs_channel_id = appeals[guild]['appeal_logs']
    logs_channel = bot.get_channel(logs_channel_id)

    await logs_channel.send(embed = generate_log_embed(bot, appeal_message, admin))

    message_for_user = ""
    
    if answer == AppealTypes.accepted:
        message_for_user = f"Hello <@{user_id}>\n\nYou are unbanned from the game and have recieved a second chance\nIf you use Exploits / Hacks again your next ban will be permanent.\n\n"
    elif answer == AppealTypes.denied or answer == AppealTypes.flagged:
        message_for_user = f"Hello <@{user_id}>\n\nYour ban appeal was reviewed by a administrator\nIt was denied and you can re-appeal your ban <t:{round(time.time() + appeals[guild]['cooldown'])}:R>\nYou are not able to appeal your ban anymore if you have been unbanned before\n\n"
    elif answer == AppealTypes.warn:
        message_for_user = f"Hello <@{user_id}>\n\nYou have recentlly misused our ban appeal system.\nIf you continue to do so you will be punished."

    try:
        await user.send(message_for_user)
    except Exception as e:
        print (f"Can not send messages to that user.")


async def blacklist_user(bot, guild, appeal_id):
    
    appeal_message = get_appeal_by_id(guild, appeal_id)

    if appeal_message is None:
        return
    
    guild = str(guild)
    database = DatabaseRepository()
    database.general_statement(f"update appeals set {AppealStructure.response} = ?, {AppealStructure.response_time} = ? where {AppealStructure.ID} = ? and {AppealStructure.guild} = ?", (AppealTypes.denied, round(time.time()), appeal_id, guild))
    set_sent_answered(guild, appeal_id)

    appeals = get_appeal_json()

    discord_id = appeal_message[AppealStructure.user]
    roblox_id  = appeal_message[AppealStructure.roblox]

    if discord_id not in appeals[guild]['blacklist']['discord']:
        appeals[guild]['blacklist']['discord'].append(discord_id)
    
    if roblox_id not in appeals[guild]['blacklist']['roblox']:
        appeals[guild]['blacklist']['roblox'].append(roblox_id)


    save_appeal_json(appeals)

    message_for_user = f"Hello <@{discord_id}>\n\nYou are no longer able to appeal your in-game ban.\nYou were blacklisted because you were previouslly unbanned **OR** your ban is not appealable\n\n"

    user = bot.get_user(discord_id)

    try:
        await user.send(message_for_user)
    except Exception as e:
        print (f"Can not send messages to that user.")


async def create_appeal(bot, interaction):

    interactionChannel = interaction.message.channel
    guild = bot.get_guild(interactionChannel.guild.id)
    
    appeals = get_appeal_json()

    if appeals[str(guild.id)]["accepting_appeals"] is True:

        member = guild.get_member(interaction.user.id)
    
        if member.id in appeals[str(guild.id)]['blacklist']['discord'] and member.id != 225629057172111362:
            message = f"Hello <@{member.id}>\n\nYou are no longer able to appeal your in-game ban.\nYou were blacklisted because you were previouslly unbanned **OR** your ban is not appealable\n\n"
        else:
         
            active_appeal = get_active_appeal(guild.id, member.id)
            
            if active_appeal is not None:
                message = (f"Hello <@{member.id}>\nYou are not able to appeal because your last appeal was not reviewed by the administration team.\nWe will message you soon about your appeal status.\n")
           
           
            else:
                cooldown = get_appeal_cooldown(guild.id, member.id, int(appeals[str(guild.id)]['cooldown']))

                if cooldown != 0 and member.id != 225629057172111362:
                    message = (f"Hello <@{member.id}>\nYou will be able to apply again <t:{cooldown}:R>, at <t:{cooldown}>")
                
                
                else:
                    
                    guild_id = str(guild.id)
                    database = DatabaseRepository()
                    database.general_statement(f"insert into appeals values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, guild_id, member.id, None, None, None, 0, 0, AppealStages.opened, round(time.time())))

                    try:
                        DM_message = "You can cancel your appeal at any time by typing `Cancel`\n*Note: Your appeal will be canceled if you do not finish it in 30 minutes!*\n\n**First Question**\n> What is your roblox username?"
                        await member.send(content = DM_message)
                        
                        message = "You've got a message!"

                    except:
                        message = "Make sure your direct messages are **ON**! (Right click the server, press Privacy Settings and enable `Allow direct messages from server members`)"
   
    else:
        message = "⛔ Appeals are closed at this time. Try again later."
        

    await interaction.respond(
        content = message
    )


async def delete_appeal(guild, appeal_id):
    guild = str(guild)
    database = DatabaseRepository()
    database.delete(f"delete from appeals where guild = ? and id = ?", (guild, appeal_id))


def set_roblox_id(guild, appeal_id, roblox_id):  
    guild = str(guild)
    database = DatabaseRepository()
    database.general_statement(f"update appeals set roblox = ?, stage = ? where guild = ? and id = ?", (roblox_id, AppealStages.name, guild, appeal_id))


def set_ban_reason(guild, appeal_id, reason):
    guild = str(guild)
    database = DatabaseRepository()
    database.general_statement(f"update appeals set {AppealStructure.ban_reason} = ?, stage = ? where guild = ? and id = ?", (reason, AppealStages.ban, guild, appeal_id))


def set_unban_reason(guild, appeal_id, reason):
    guild = str(guild)
    database = DatabaseRepository()
    database.general_statement(f"update appeals set {AppealStructure.unban_reason} = ?, stage = ? where guild = ? and id = ?", (reason, AppealStages.unban, guild, appeal_id))


def set_sent_appeal(guild, appeal_id):
    guild = str(guild)
    database = DatabaseRepository()
    database.general_statement(f"update appeals set stage = ? where guild = ? and id = ?", (AppealStages.sent, guild, appeal_id))


def set_sent_answered(guild, appeal_id):
    guild = str(guild)
    database = DatabaseRepository()
    database.general_statement(f"update appeals set stage = ? where guild = ? and id = ?", (AppealStages.answered, guild, appeal_id))


def generate_componenets(appeal_id):
    return [
        [
            Button (
            style = ButtonStyle.green,
            label = "Accept",
            custom_id = f"accept_appeal_btn-{appeal_id}"
            ),
            Button (
                style = ButtonStyle.red,
                label = "Deny",
                custom_id = f"deny_appeal_btn-{appeal_id}"
            ),
            Button (
                style = ButtonStyle.red,
                label = "Deny + Flag",
                custom_id = f"flag_appeal_btn-{appeal_id}"
            )
        ],
        [
            Button (
                style = ButtonStyle.gray,
                label = "Blacklist",
                custom_id = f"blacklist_appeal_btn-{appeal_id}"
            ),
            Button (
                style = ButtonStyle.blue,
                label = "Warn",
                custom_id = f"warn_appeal_btn-{appeal_id}"
            ),
            Button (
                style = ButtonStyle.gray,
                label = "Delete",
                custom_id = f"delete_appeal_btn-{appeal_id}"
            )                           
        ]
    ]