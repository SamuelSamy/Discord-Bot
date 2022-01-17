from discord.ext import commands

from cogs.appeal_module.rewrite.package_enums import AppealTypes
from cogs.appeal_module.rewrite.package_functions import *


class AppealListeners(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener("on_ready")
    async def appeal_button_listener(self):
        
        while True:

            interaction = await self.bot.wait_for(
                'interaction'
            )

            id = interaction.custom_id
            guild = str(interaction.guild.id)


        
            if id == "appeal_button":
                await create_appeal(self.bot, interaction)
            elif id.startswith("accept_appeal_btn-"):
                await answer_appeal(self.bot, guild, get_appeal_id(id),  AppealTypes.accepted, interaction.author.id)
            elif id.startswith("deny_appeal_btn-"):
                await answer_appeal(self.bot, guild, get_appeal_id(id), AppealTypes.denied, interaction.author.id)
            elif id.startswith("delete_appeal_btn-"):
                await delete_appeal(guild, get_appeal_id(id))
            elif id.startswith("warn_appeal_btn-"):
                await answer_appeal(self.bot, guild, get_appeal_id(id), AppealTypes.warn, interaction.author.id)
            elif id.startswith("flag_appeal_btn-"):
                await answer_appeal(self.bot, guild, get_appeal_id(id), AppealTypes.flagged, interaction.author.id)
            elif id.startswith("blacklist_appeal_btn-"):
                await blacklist_user(self.bot, guild, get_appeal_id(id))

            if id not in ['appeal_button']:
                await interaction.message.delete()

         


    @commands.Cog.listener("on_ready")
    async def dm_listener(self):
        
        guilds = {
            875089864998133780: "894160228239679490", # MAIN
            900101389416546314: "876988765955039273", # BURA
            867480262777765918: "852143372353142785" # AF
        }

        while True:

            message = await self.bot.wait_for(
                'message',
                check = lambda message: isinstance(message.channel, discord.DMChannel)
            )

            author =  message.author
            guild = guilds[self.bot.user.id]
            appeals = get_appeal_json()

            if not author.bot:
            
                if appeals[guild]["accepting_appeals"] == True:

                    id = author.id

                    steps = {
                        AppealStages.name: "",
                        AppealStages.ban: "**Second Question**\n> Why were you banned?",
                        AppealStages.unban: "**Third Question**\n> Why do you think you should be unbanned?",
                        AppealStages.sent: "**Your appeal has been sent!**\nYou will be messaged by me (the bot) when your appeal is handled!"
                    }

                    message_lower = message.content.lower().strip()

                    appeal_message = get_active_appeal(guild, id)

                    if appeal_message is not None:

                        if message_lower == "cancel":
                            cancel_appeal(guild, appeal_message[AppealStructure.ID])
                            await author.send("Your appeal has been canceled!")

                        else:
                            last_step = appeal_message[AppealStructure.stage]

                            if last_step == AppealStages.opened:
                                
                                bot_message = await author.send("<a:loading:901197462935580692> Searching profile...\n> Please wait")

                                profile = get_profile(message.content)
                                roblox_id = get_roblox_id(profile)

                                if profile is None:
                                    await bot_message.edit("Player not found. Please try again")
                                else:
                                    set_roblox_id(guild, appeal_message[AppealStructure.ID], roblox_id)
                                    await bot_message.edit(steps[AppealStages.ban])


                            elif last_step == AppealStages.name:
                                
                                if len(message.content) == 0:
                                    await author.send("**The message can not be empty!**")
                                elif len(message.content) > 800:
                                    await author.send("**The message is too long.\nThe maximum amount of characters is** `800`**!**")
                                else:
                                    set_ban_reason(guild, appeal_message[AppealStructure.ID], message.content)
                                    await author.send(steps[AppealStages.unban])


                            elif last_step == AppealStages.ban:
                                
                                if len(message.content) == 0:
                                    await author.send("**The message can not be empty!**")
                                elif len(message.content) > 800:
                                    await author.send("**The message is too long.\nThe maximum amount of characters is** `800`**!**")
                                else:
                                    set_unban_reason(guild, appeal_message[AppealStructure.ID], message.content)

                                    appeal_message = get_appeal_by_id(guild, appeal_message[AppealStructure.ID])

                                    # SEND APPEAL

                                    appeal_channel_id = appeals[guild]['appeal_channel']
                                    appeal_channel = self.bot.get_channel(appeal_channel_id)

                                    comps = generate_componenets(appeal_message[AppealStructure.ID])       

                                    try:

                                        await appeal_channel.send(
                                            embed = generate_appeal(self.bot, guild, appeal_message),
                                            components = comps
                                        )
                                        set_sent_appeal(guild, appeal_message[AppealStructure.ID])
                                        await author.send(steps[AppealStages.sent])

                                    except Exception as e:
                                        print(f"Sending Appeal Error:\n{e}\n")
                                        cancel_appeal(guild, appeal_message)
                                        await author.send("There was an error while sending the appeal.\nIf you see this message contact <@225629057172111362> (greater#2407).")

    
def setup(bot):
    bot.add_cog(AppealListeners(bot))