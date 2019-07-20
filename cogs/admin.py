import discord

from .utils.u_mongo import Mongo
from discord.ext import commands
from discord.ext.commands import has_permissions

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def set_prefix(self, ctx, *, prefix='='):
        """
        Sets the prefix for the server
        -set_prefix <=, -, !>
        """

        record = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)
        upg = {
            "prefix": prefix
        }
        await Mongo.update_record('server_settings', record, upg)
        await ctx.send(f"Prefix is now: {prefix}")

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def set_descriptor(self, ctx, descriptor='en'):
        """
        Set descriptor for translate other languages 
        -set_descriptor <en, ru>
        """
        
        record = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)

        upg = {
            "translator": descriptor
        }
        await Mongo.update_record('server_settings', record, upg)
        await ctx.send(f"Descriptor is now: {descriptor}")

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def set_emoji(self, ctx, emoji):
        """
        Set emoji for money server
        -set_emoji <discord.Emoji>
        """

        server_id = ctx.message.guild.id
        record = await Mongo.get_record('server_settings', 'id', server_id)

        upg_emoji = {
            "emoji_name":emoji
        }
        await Mongo.update_record('server_settings', record, upg_emoji)

        await ctx.send(f"Money Emoji is now: {emoji}")

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def add_art_channel(self, ctx, *, channel):
        """
        Добавить арт-канал на этот сервер
        =add_art_channel <channel_name>
        """
        record = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)
        channels = record['channel_art']
        if channels:
            channels.append(channel)
        else:
            channels = []
            channels.append(channel)
        upg = {
            "channel_art": channels
        }
        await Mongo.update_record('server_settings', record, upg)
        

    @commands.command(pass_context=True)
    async def test(self, ctx, channel_id, msg):
        channel = discord.utils.get(self.bot.get_all_channels(), guild__name=ctx.guild.name, name=channel_id)
        msg = await channel.fetch_message(int(msg))

    @commands.command(pass_context=True, aliases=['arr'])
    @has_permissions(administrator=True)
    async def add_role_reaction(self, ctx, channel_name, message, reaction, *, role):
        """
        Добавить реакцию к сообщению и роль которая будет выдаваться
        =arr <message_id> <emoji> <ROLE_NAME>
        """

        record = await Mongo.get_record('reactions', 'msg_id', str(message))

        check_role = discord.utils.get(ctx.guild.roles, name=role)
        if check_role is None:
            await ctx.send("Роль не существует")
            return

        channel = discord.utils.get(self.bot.get_all_channels(), guild__name=ctx.guild.name, name=channel_name)
        msg = await channel.fetch_message(int(message))

        if record is None:
            upg = {
                "msg_id": message,
                "reactions": [reaction],
                "roles": [role],
                "more_roles": False
            }
            await Mongo.record_insert('reactions', upg)
        else:
            if reaction in record['reactions']:
                await ctx.send("Эта реакция уже существует")
                return

            react = record['reactions']
            react.append(reaction)

            roles = record['roles']
            roles.append(role)

            upg = {
                "reactions": react,
                "roles": roles
            }
            await Mongo.update_record('reactions', record, upg)
        
        await msg.add_reaction(reaction)
    
    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def reaction_roles(self, ctx, message, check):
        """
        Правило для выдачи ролей
        True - Позволяет брать несколько ролей| False - Заменяет роль на другую
        =reaction_roles <message_id> <True|False>
        """

        record = await Mongo.get_record('reactions', 'msg_id', message)

        if record is None:
            await ctx.send("Сообщение не найдено")
            return
        
        upg = {
            "more_roles": bool(check)
        }
        await Mongo.update_record('reactions', record, upg)

        await ctx.send(f'Успешно изменено на {check}')

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def reaction_clear(self, ctx, channel, message):
        """
        Убрать все реакции из сообщения
        =reaction_clear <channel_name> <msg_id>
        """

        record = await Mongo.get_record('reactions', 'msg_id', message)

        if record is None:
            await ctx.send("Сообщение не найдено")
            return

        channel = discord.utils.get(self.bot.get_all_channels(), guild__name=ctx.guild.name, name=channel)
        msg = await channel.fetch_message(int(message))

        await msg.clear_reactions()
        
        await Mongo.delete_record('reactions', 'msg_id', message)

    @commands.command(passc_context=True)
    @has_permissions(administrator=True)
    async def add_work(self, ctx, *, work):
        """
        Добавить работу
        -add_work <text>
        """
        record = await Mongo.get_record('server_settings', 'id', ctx.guild.id)
        works = record['preds_work']
        works.append(work)
        upg = {
            "preds_work": works
        }
        await Mongo.update_record('server_settings', record, upg)
        await ctx.send("Готово.")


def setup(bot):
    bot.add_cog(Admin(bot))