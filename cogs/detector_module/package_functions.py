import re
import json
import urllib.request
import discord

from ..__classes.settings import Settings


def save_json(blacklisted):
    with open("data/blacklist.json", "w") as f:
        json.dump(blacklisted, f)


def get_first_part(message):
        link = re.search("(?P<url>https?://[^\s]+)", message)
        return link[0]


def reassmble_link(parts):
    link = ""

    for i in range(2, len(parts)):
        link += parts[i] + "/"

    return link[:-1]


def is_blacklisted(message, blacklisted):

    for domain in blacklisted['scam_domains']:

        if domain in message:
            return True

    return False


# def is_mask(message_content, blacklisted):

#     urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', message_content)
#     masks = []

#     for mask in blacklisted['masks']:
#         masks.append(str(mask))

#     for link in urls:
#         link_parts = link.split('/')

#         if len(link_parts) > 2:
#             to_verrify = link_parts[2]
            
#             for mask in masks:
#                 distance = levenshtein_distance(to_verrify, mask)

#                 if distance < int(blacklisted['masks'][mask]['distance']) and blacklisted['masks'][mask]['exact_match']:
#                     return distance

#     return 0


# def levenshtein_distance(s, t):
#     # https://www.datacamp.com/community/tutorials/fuzzy-string-python?utm_source=adwords_ppc&utm_campaignid=14989519638&utm_adgroupid=127836677279&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=332602034364&utm_targetid=dsa-429603003980&utm_loc_interest_ms=&utm_loc_physical_ms=9040263&gclid=CjwKCAjwwsmLBhACEiwANq-tXHKieLemSgdCcH-veD1PhSOzUHK06Hp2e0PcefOtwX7-w_yh8FCHlRoCq4kQAvD_BwE
#     rows = len(s)+1
#     cols = len(t)+1
    
#     distance = []
    
#     for i in range(0, rows):

#         row = []

#         for j in range(0, cols):
#             row.append(0)

#         distance.append(row) 


#     for i in range(1, rows):
#         for k in range(1,cols):
#             distance[i][0] = i
#             distance[0][k] = k

#     for col in range(1, cols):
#         for row in range(1, rows):
#             if s[row-1] == t[col-1]:
#                 cost = 0 
#             else:
#                 cost = 1

#             distance[row][col] = min(
#                 distance[row-1][col] + 1,  
#                 distance[row][col-1] + 1,          
#                 distance[row-1][col-1] + cost
#             )    
    
#     return distance[row][col]


def is_possible_scam(message_content):
    
    urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', message_content)

    for url in urls:
        
        if "http" in url:

            try:
                opener = urllib.request.build_opener()
                request = urllib.request.Request(url)
                redirect = opener.open(request, timeout = 10).geturl()
                error = False
            except:
                error = True


            if not error:

                try:
                    response = urllib.request.urlopen(redirect, timeout = 10)
                    source = str(response.read()).lower()
                    open_error = False
                except:
                    open_error = True

                if not open_error:
                    triggers = [['discord', 'nitro', 'free', 'steam'], ['discord', 'nitro', 'gift-form', 'qrcode'], ['discord', 'nitro', 'free', 'new', 'year']]

                    for trigger_set in triggers:
                        if all(x in source for x in trigger_set):
                            return True

    return False



async def send_to_mod_logs(self, message, settings):

    server_invites = {
        "852143372353142785": "https://discord.gg/8KVh3qrKCA",
        "894160228239679490": "https://discord.gg/NqHbGEUVQ9",
        "876988765955039273": "https://discord.gg/VH8UJHYytx"
    }

    member = message.author
    guild = str(message.guild.id)
    
    try:
        await member.send(f"Hello {member.mention}\nYou were kicked from {message.guild} because your account was recentlly hacked.\n*Note: If this was a mistake you can join the server using the following link:* {server_invites[guild]}")
    except:
        pass

    mod_logs = self.bot.get_channel(settings[guild][Settings.mod_logs.value])

    embed = discord.Embed(color = 0xf04848)
    embed.set_author(name = f"[Kick] {member}", icon_url = member.avatar_url)
    embed.add_field(name = "User", value = member.mention)
    embed.add_field(name = "Moderator", value = self.bot.user.mention)
    embed.add_field(name = "Reason", value = "Compromised Account")

    await mod_logs.send(embed = embed)


async def send_link_to_logs(self, message):
    scam_links_logs = self.bot.get_channel(904824288996102195)
    await scam_links_logs.send(f"```\n{message}\n```")