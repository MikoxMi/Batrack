import re
import asyncio
import discord
import random

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
        

    @commands.command(pass_context=True, aliases=['arr'])
    @has_permissions(administrator=True)
    async def add_role_reaction(self, ctx, channel_name, message, reaction, *, role):
        """
        Добавить реакцию к сообщению и роль которая будет выдаваться
        =arr <message_id> <emoji> <ROLE_NAME>
        """

        record = await Mongo.get_record('reactions', 'msg_id', str(message))

        guild = discord.utils.get(self.bot.guilds, id=593163382421585921)

        check_role = discord.utils.get(guild.roles, name=role)
        if check_role is None:
            await ctx.send("Роль не существует")
            return

        channel = discord.utils.get(self.bot.get_all_channels(), guild__name=guild.name, name=channel_name)
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

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def edit_embed(self, ctx, channel_id, msg_id, *, msg):
        """
        Изменение отправленного ембеда
        =edit_embed <channel_id> <msg_id> <msg> 
        """

        channel = discord.utils.get(self.bot.get_all_channels(), guild__name=ctx.guild.name, name=channel_id)
        get_msg = await channel.fetch_message(int(msg_id))

        e = discord.Embed(colour=int('0x36393f', 0), description=msg)
        msg = await get_msg.edit(embed=e)


    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def lottery(self, ctx, item, time):
        """
        Создать лотерею
        =lottery <item_name> <>
        Example: =lottery <Бутерброд> <30h, 30m, 30s>
        """
        time_str = int(re.findall('\\d+', time)[0])
        if "h" in time:
            t = time_str * 60 * 24
            
        elif "m" in time:
            t = time_str * 60
        else:
            t = time_str
        
        s_time = f'{time}'
        em = discord.Embed(colour=int('0x36393f', 0))
        em.set_author(name=f'🎉 Розыгрыш: {item}')

        msg = await ctx.send(embed=em)
        await msg.add_reaction('🎉')
        await asyncio.sleep(t)

        reaction = discord.Reaction(message=msg, data=ctx, emoji='🎉')
        users = await reaction.users().flatten()
        winner = random.choice(users)
        print(users)
        print(winner)
        await msg.edit(embed=em)


    @commands.command(pass_context=True)
    @has_permissions(view_audit_log=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """Заварнить человека
        -warn @member <reason>"""

        if reason is None:
            reason = 'None'
        else:
            reason = reason

        author = ctx.message.author
        record = await Mongo.get_record('members', 'id', member.id)
        record_server = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)

        mute_role = record_server['mute_role']
        if mute_role == "None":
            await ctx.send("Mute_role не добавлена")
            return

        warns = int(record['warns']) + 1
        if warns != 3:
            desc = f"{author.mention} заварнил {member.mention}\nПричина:**{reason}**\n Количество варнов:{warns}"
            em = discord.Embed(colour=int('0x36393f', 0), description=desc)
            em.set_image(url='https://i.imgur.com/xiJT07q.gif')
            await ctx.send(embed=em)
            await member.send(embed=em)
            check_warns = False
        else:
            warns = 3
            desc = f"{ctx.message.author.mention} заварнил {member.mention}\nПричина:**{reason}**\nКоличество варнов: {warns}\nВыдан мут на 15 минут"

            role = discord.utils.get(author.guild.roles, id=mute_role)
            await member.add_roles(role)
            e = discord.Embed(colour=int('0x36393f', 0), description=desc)
            e.set_image(url='https://i.imgur.com/xiJT07q.gif')
            await ctx.send(embed=e)

            muted = record_server['muted']
            person = {
                "id": member.id,
            }
            muted.append(person)
            upg = {
                "muted": muted
            }
            await Mongo.update_record('server_settings', record_server, upg)

            await asyncio.sleep(900)
            await member.remove_roles(role)
            await member.send(f"С вас прошел мут, можете дальше наслаждаться вечерними буднями на Space Desu.")

            muted = record_server['muted']
            for i, mute in enumerate(muted):
                if mute["id"] == member.id:
                    muted.pop(i)
                else:
                    pass
            upg = {
                "muted": muted
            }
            await Mongo.update_record('server_settings', record_server, upg)

            check_warns = True

        #* If warns == 3 then reset warns
        if check_warns:
            updates = {
                "warns": 0
            }
        else:
            updates = {
                "warns": warns
            }
        await Mongo.update_record('members', record, updates)

    @commands.command(pass_context=True)
    @has_permissions(view_audit_log=True)
    async def unwarn(self, ctx, member:discord.Member):
        """Снять варны с участника сервера
        
        -unmute @member"""

        desc = f"{ctx.message.author.mention} обнулил варны у пользователя {member.mention}"
        record = await Mongo.get_record('members', 'id', member.id)
        upg = {
            "warns":0
        }
        await Mongo.update_record('members', record, upg)
        em = discord.Embed(colour=ctx.message.author.colour, description=desc)
        await ctx.send(embed=em)

    @commands.command(pass_context=True, aliases=['m'])
    @has_permissions(view_audit_log=True)
    async def mute(self, ctx, member: discord.Member, duration="15m", *, reason=None):
        """Замутить человека
        -mute <@member> <hour-0> <minute=15> <second=0> <reason>"""


        if reason is None:
            reason = 'None'
        
        record_server = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)
        
        mute_role = record_server['mute_role']
        if mute_role == "None":
            await ctx.send("Mute Role не добавлена")
            return

        role = discord.utils.get(ctx.message.guild.roles, id=mute_role)
        await member.add_roles(role)

        count = 0
        dur_count = re.findall('\\d+', duration)[0]
        if not dur_count.isdigit():
            await ctx.send("Используйте только числа")
            return

        if "h" in duration:
            count += int(dur_count) * 3600
        elif "m" in duration:
            count += int(dur_count) * 60
        elif "s" != 0:
            count += int(dur_count)

        hour = count // 3600
        minute = (count // 60) % 60
        second = count % 60

        desc = f"Пользователю {member.mention} был выдан мут на: {hour}h:{minute}m:{second}s\nАдминистратором:{ctx.message.author.mention}\nПричина:{reason}"

        em = discord.Embed(colour=ctx.message.author.colour, description=desc)
        em.set_image(url="https://i.imgur.com/xTMHjQd.jpg")
        em.set_author(name="Admin system:")
        await ctx.send(embed=em)

        muted = record_server['muted']
        person = {
            "id": member.id,
        }
        muted.append(person)
        upg = {
            "muted": muted
        }
        await Mongo.update_record('server_settings', record_server, upg)


        await asyncio.sleep(count)

        await member.remove_roles(role)
        await member.send(f"С вас прошел мут, можете дальше наслаждаться вечерними буднями на Space Desu.")

        muted = record_server['muted']
        for i, mute in enumerate(muted):
            if mute["id"] == member.id:
                muted.pop(i)
            else:
                pass
        upg = {
            "muted": muted
        }
        await Mongo.update_record('server_settings', record_server, upg)

    @commands.command(pass_context=True)
    @has_permissions(view_audit_log=True)
    async def unmute(self, ctx, member: discord.Member):
        """Снять с пользователя мут
        
        -unmute @member"""
        
        record_server = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)

        mute_role = record_server['mute_role']      
        if mute_role == "None":
            await ctx.send("Mute Role не добавлена")
            return

        role = discord.utils.get(ctx.message.guild.roles, id=mute_role)
        await member.remove_roles(role)
        await ctx.send(f"Mute с пользователя {member.mention} был снят")
        
    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def add_mute_role(self, ctx, id):
        """Создание роли для мута
        -add_mute_role <id_role>"""

        record = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)

        role = discord.utils.get(ctx.message.guild.roles, id=record['mute_role'])

        if role is None:
            await ctx.send('Неизвестная роль')
            return

        upg = {
            "mute_role": int(id)
        }

        await Mongo.update_record('server_settings', record, upg)


    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def delete_mute_role(self, ctx):
        """Удаление мут-роли

        -delete_mute_role
        """
        

        record = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)

        update = {
            "mute_role": "None"
        }

        await Mongo.update_record('server_settings', record, update)
        await ctx.send(f"Успешное удаление Mute Role")




def setup(bot):
    bot.add_cog(Admin(bot))