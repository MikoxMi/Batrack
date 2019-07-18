import asyncio
import random

import discord

from .utils.u_mongo import Mongo
from .utils.u_discord import DiscordUtils

from discord.ext import commands


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def br(self, ctx, bet):
        """Кости, етить их мадрить
        
        -br <bet>"""

        emoji = await DiscordUtils.get_emoj(ctx)

        if not bet.isdigit():
            await ctx.send("Используйте только числа")
            return

        #Get money
        record = self.members.find_one({"user_id":ctx.message.author.id})
        record = await Mongo.get_record('members', 'id', ctx.message.author.id)
        money = int(record['money'])
        if money < int(bet):
            await self.bot.say('Недостаточно денег для игры')
            return
        
        count = money - int(bet)
        upg = {
            "money":count
        }
        await Mongo.update_record('members', record, upg)

        # Game
        ball = random.randint(0, 100)
        if ball >= 0 and ball <= 60:
            await self.bot.say(f"{ctx.message.author.mention}. Вы проиграли. Выпало число {ball}")
            return
        elif ball >= 60 and ball <= 89:
            networth = int(bet) * 2
            await self.bot.say(f"{ctx.message.author.mention}. Вы выйграли: {networth}{emoji}. Умножение: x2")
        elif ball >= 90 and ball <= 99:
            networth = int(bet) * 4
            await self.bot.say(f"{ctx.message.author.mention}. Вы выйграли: {networth}{emoji}. Умножение: x4")
        else:
            networth = int(bet) * 14
            await self.bot.say(f"{ctx.message.author.mention}. Вы выйграли: {networth}{emoji}. Умноежение: x14")

        count = money + networth
        upg = {
            "money":count
        }
        await Mongo.update_record('members', record, upg)

   


def setup(bot):
    bot.add_cog(Casino(bot))
