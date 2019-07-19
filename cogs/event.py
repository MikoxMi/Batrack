import discord

from googletrans import Translator
from cogs.utils.u_mongo import Mongo
from discord.ext import commands

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Instructions after authorization
        """
        print("=============================")
        print("Authorization successful!")
        print("To the following servers:")
        for s in self.bot.guilds:
            print(f'- {s.name} {s.id}')

        # Get all members to check
        for s in self.bot.guilds:
            for member in s.members:
                userID = int(member.id)
                check = await Mongo.get_record('members', 'id', userID)
                server_record = await Mongo.get_record('server_settings', 'id', s.id)
                member_profile = await Mongo.get_record('member_profile', 'id', userID)

                if check is None:
                    inv = []

                    upg_member = {
                        "id": userID,
                        "member_name": f"{member}",
                        "money": 0,
                        "tree": 0,
                        "food": 0,
                        "food_max": 0,
                        "rep": 0,
                        "summary_money": 0,
                        "inventory": inv,
                    }
                    await Mongo.record_insert('members', upg_member)
                if member_profile is None:
                    upg_profile = {
                        "id": userID,
                        "member_name": f"{member}",
                        "title": "None",
                        "name_field_1": "None",
                        "name_field_2": "None",
                        "field_1": "None",
                        "field_2": "None",
                        "description": "None",
                        "image": "None"
                    }
                    await Mongo.record_insert('member_profile', upg_profile)
                if server_record is None:
                    upg_server = {
                        "id": int(s.id),
                        "prefix":"=",
                        "emoji_name": "None",
                        "translator": 'en'
                    }
                    await Mongo.record_insert('server_settings', upg_server)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        React on add emoji on message
        """
        emoji = payload.emoji
        guild_id = payload.guild_id
        msg_id = payload.message_id
        user_id = payload.user_id
        if user_id == 596671342514798597:
            return

        record = await Mongo.get_record('reactions', 'msg_id', str(msg_id))

        if record is None:
            return

        rec_reactions = record["reactions"]
        rec_roles = record["roles"]
        more_roles = record["more_roles"]

        guild = discord.utils.get(self.bot.guilds, id=guild_id)
        member = discord.utils.get(guild.members, id=user_id)

        for i, reaction in enumerate(rec_reactions):
            if str(emoji) == reaction:
                role = discord.utils.get(guild.roles, name=rec_roles[i])
            else:
                pass

        await member.add_roles(role)

        if more_roles is not True:
            for role_check in member.roles:
                for role_record in rec_roles:
                    if str(role_check) == str(role_record) and role.name != str(role_check):
                        await member.remove_roles(role_check)
                    else:
                        pass
        else:
            pass

        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """
        Remove role from member if role is exists
        """
        emoji = payload.emoji
        guild_id = payload.guild_id
        msg_id = payload.message_id
        user_id = payload.user_id

        if user_id == 596671342514798597:
            return

        record = await Mongo.get_record('reactions', 'msg_id', str(msg_id))
        if record is None:
            return
        
        rec_reactions = record["reactions"]
        rec_roles = record["roles"]

        for i, reaction in enumerate(rec_reactions):
            if str(emoji) == reaction:
                _id = i
            else:
                pass

        guild = discord.utils.get(self.bot.guilds, id=guild_id)
        role = discord.utils.get(guild.roles, name=rec_roles[_id])
        member = discord.utils.get(guild.members, id=user_id)
        await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        React bot on all member message
        """

        #*Check if bot
        if message.author.bot:
            return
        
        userID = message.author.id
        member_record = await Mongo.get_record('members', 'id', userID)
        server_record = await Mongo.get_record('server_settings', 'id', message.guild.id)

        member = discord.utils.get(message.guild.members, id=userID)

        document = member_record["member_name"]
        if document != member:
            upg_name = {
                "member_name": f"{member}"
            }
            await Mongo.update_record('members', member_record, upg_name)
        else:
            pass

        #* Add money on member message
        if len(message.content) > 10:
            if ":" in message.content or "<@" in message.content:
                pass
            else:
                money_message = int(member_record['money']) + 3
                obwak = int(member_record['summary_money']) + 3
                upg_money = {
                    "money": money_message,
                    "summary_money": obwak
                }
                await Mongo.update_record('members', member_record, upg_money)

        channel_art = server_record["channel_art"]
        if str(message.channel) in channel_art:
            reactions = ['👍', '👎']
            for react in reactions:
                await message.add_reaction(react)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Event for member join 
        """

        member_record = await Mongo.get_record('members', 'id', member.id)
        member_profile = await Mongo.get_record('member_profile', 'id', member.id)
            
        inv = []

        if member_record is None:
            upg_member = {
                "id": member.id,
                "member_name": "%s" % (member),
                "money": 0,
                "tree": 0,
                "food": 0,
                "food_max": 20,
                "bank": 0,
                "rep": 0,
                "summary_money": 0,
                "inventory": inv,
            }
            await Mongo.record_insert('members', upg_member)

        if member_profile is None:
            upg_profile = {
                "id": int(member.id),
                "member_name": f"{member}",
                "title": "None",
                "name_field_1": "None",
                "name_field_2": "None",
                "field_1": "None",
                "field_2": "None",
                "description": "None",
                "image": "None"
            }
            await Mongo.record_insert('member_profile', upg_profile)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Delete record User
        """
        await Mongo.delete_record('members', 'id', member.id)
        await Mongo.delete_record('members', 'id', member.id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Реакция на ошибки в командах или Cooldown"""
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("\N{WARNING SIGN} Вы не можете использовать эту команду в Bot.Direct")

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("\N{WARNING SIGN} Эта команда на данный момент отключена!")

        elif isinstance(error, commands.CommandOnCooldown):
            h = error.retry_after // 3600
            m = (error.retry_after // 60) % 60
            s = error.retry_after % 60
            em = discord.Embed(description=f"{ctx.message.author.mention} Введите эту команду через {toFixed(h)} hours {toFixed(m)} minutes {toFixed(s)} sec", 
                               colour=ctx.message.author.colour)
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            em = discord.Embed(colour=ctx.message.author.colour)
            em.add_field(name="Command Helper", value=F"{ctx.command.help}")
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Events(bot))