import discord

from .utils.u_mongo import Mongo
from .utils.u_discord import DiscordUtils

from discord.ext import commands
from discord.ext.commands import has_permissions

class Warcraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def wr(self, ctx):
        """Warcraft Module

        Commands:
        -wr - Показывает это сообщение

        -wr create - Создать базу на этом сервере
        """

        if ctx.invoked_subcommand is None:
            msg = ctx.command.help
            em = discord.Embed(colour=ctx.message.author.colour)
            em.add_field(name="Command Helper", value=F"{msg}")
            await ctx.send(embed=em)
            return

    @wr.command(pass_context=True)
    async def create(self, ctx):
        """
        Создать базу
        -wr create
        """

        record = await Mongo.get_record('warcraft', 'id', ctx.message.author.id)

        if record is not None:
            await ctx.send("You already have a base")
            return
        
        upg = {
            "id": ctx.message.author.id,
            "gold": 0,
            "food": 0,
            "food_max": 20,
            "tree": 0,
            "heroes": [],
            "builds": [],
            "units": []
        }
    
        await Mongo.record_insert('warcraft', upg)
    
    @wr.command(pass_context=True)
    async def build(self, ctx):
        """
        Построить
        1. Юниты
        2. Здания
        """
        pass

    @wr.command(pass_context=True)
    async def buy(self, ctx):
        """
        Купить предмет для вашего героя
        """
        pass

    @wr.command(pass_context=True)
    @has_permissions(administrator=True)
    async def add(self, ctx, category):
        """
        Добавление зданий, юнитов, предметов [Administrator]
        """
        #Todo: Automatic system of create hero
        if category == "builds":
            msg = await ctx.send("Введите название здания")

            check = lambda message: message.author == ctx.author

            name_msg = await self.bot.wait_for('message', check=check) 
            hp_msg = await self.bot.wait_for('message', check=check)
            food_msg = await self.bot.wait_for('message', check=check)
            gold_msg = await self.bot.wait_for('message', check=check) 
            avaliable_msg = await self.bot.wait_for('message', check=check) 
            time_msg = await self.bot.wait_for('message', check=check)

            name = name_msg.content
            hp = hp_msg.content
            food = food_msg.content
            gold_price = gold_msg.content
            avaliable = avaliable_msg.content
            time_build = time_msg.content

            stats = {
                "name": name,
                "hp": hp,
                "food": food,
                "gold_price": gold_price,
                "avaliable": [],
                "upgrades": [],
                "time_build": time_build
            }
        elif category == "units":
            stats = {
                "name": name,
                "hp": hp,
                "food": food,
                "damage": damage,
                "armor": armor,
                "gold_price": gold_price,
                "tree_price": tree_price,
                "time_build": time_build
            }

        elif category == "heroes":
            stats = {
                "name": name,
                "hp": hp,
                "food": food,
                "damage": damage,
                "armor": armor,
                "gold_price": gold_price,
                "time_build": time_build
            }
        else:
            await ctx.send("Invalid category")
            return

    @wr.commands(pass_context=True)
    @has_permissions(administrator=True)
    async def add_upgrade(self, ctx, name, upgrade_type):
        """
        Добавить улучшение для здания. Типы улучшения:
        1. build - позволяет улучшить само здание
        2. passive - позволяет добавить пассивное улучшение.
        3. units - пассивное улучшение для юнитов
        """
        # Todo: Upgrade types
        #* 1. Build - build 
        #* 2. Passive skill Build - passive
        #* 3. Units skill upgrade - units

        # Todo: Upgrades in types
        #* 1. Builds
        #* 1.1 Add HP to build
        #* 1.2 Add Damage to build
        #* 1.3 ...

        #* 2. Passive
        #* 2.1 Add food priority + 10 + 30 + 50 + 100 + 110
        #* 2.2 Add tree priority + 10

        #* 3. Units
        #* 3.1 Add damagae to units
        #* 3.2 Add hp to units
        #* 3.3 Add armor to units

        if upgrade_type == "build":
            
            upg = {
                "name": name,
                "type": "build",
                "hp": hp,
                "damage": damage,
            }  
        elif upgrade_type == "passive":

            upg = {
                "name": name,
                "type": "passive",
                "food_max": food_max,
                "gold_price": gold_price,
                "tree_price": tree_price
            }
        elif upgrade_type == "units":

            upg = {
                "name": name,
                "type": "units"
            }
        else:
            await ctx.send("Invalid category")
            return
    
    @wr.command(pass_context=True)
    @has_permissions(administrator=True)
    async def edit(self, ctx):
        """
        Изменение зданий, юнитов, предметов [Administrator]
        """
        pass

    @wr.command(pass_context=True)
    @has_permissions(administrator=True)
    async def delete(self, ctx):
        """
        Удаление зданий, юнитов, предметов [Administrator]
        """

        pass


        

def setup(bot):
    bot.add_cog(Warcraft(bot))