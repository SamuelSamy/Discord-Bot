from discord.ext import commands


class MemberUpdateModule(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        try:
            ContentCreatorID = 853258101385068555
            ApprovedCC = 868456826855915531
            
            user = f"{after.mention} / {after.id}"

            if len(before.roles) < len(after.roles):

                new_role = next(role for role in after.roles if role not in before.roles)

                if new_role.id == ContentCreatorID:
                    greater = self.bot.get_user(225629057172111362)
                    await greater.send(f"{user} - recieved content creator!")

                elif new_role.id == ApprovedCC:

                    greater = self.get_user(225629057172111362)
                    await greater.send(f"{user} - recieved approved content creator!")
            elif len(before.roles) > len(after.roles):

                old_role = next(role for role in before.roles if role not in after.roles)

                if old_role.id == ContentCreatorID:
                    greater = self.bot.get_user(225629057172111362)
                    await greater.send(f"{user} - removed from content creator!")

                elif old_role.id == ApprovedCC:
                    greater = self.get_user(225629057172111362)
                    await greater.send(f"{user} - removed from approved content creator!")
        except Exception as e:
            print (f"CC Listener Error:\n{e}\n")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        
        try:

            reportLogsChannelID = 54697531119501343

            if ctx.channel_id == reportLogsChannelID:
                if ctx.emoji.name == "✅":

                    channel = self.bot.get_channel(reportLogsChannelID)
                    messageID = ctx.message_id

                    messageObject = await channel.fetch_message(messageID)
                    message = messageObject.content
                    user = self.bot.get_user(messageObject.mentions[0].id)

                    newMessage = "Hello {}\n\nYour report has been reviewed by the Anime Fighters Administration Team!\n\nReport content:\n{}".format(user.mention, message)
                    await user.send(newMessage)
        except Exception as e:
            print (f"Raw Reaction Add Error:\n{e}\n")
            

def setup(bot):
    bot.add_cog(MemberUpdateModule(bot))