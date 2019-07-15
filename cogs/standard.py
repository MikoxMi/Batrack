import random
import discord

from .utils.u_mongo import Mongo
from .utils.u_discord import DiscordUtils
from discord.ext import commands
from discord.ext.commands import has_permissions

class Standard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['$', 'bal'])
    async def money(self, ctx, *, nick=None):
        """
        Balance check
        -[money, $, bal] <nick> or None
        """

        emoji = await DiscordUtils.get_emoji(ctx)
        emoji_tree = await DiscordUtils.get_bot_emoji(self.bot, 'tree')
        emoji_food = await DiscordUtils.get_bot_emoji(self.bot, 'food')
        try:
            record, member = await DiscordUtils.get_user(self.bot, ctx, 0, nick)
        except TypeError:
            return

        money = record["money"]
        food = record["food"]
        food_max = record["food_max"]
        tree = record["tree"]
        obwak = record['summary_money']

        record_rank = await Mongo.get_record_sort('members', 'bank', -1)
        for i, doc in enumerate(record_rank):
            if doc['id'] == member.id:
                rank = i

        em = discord.Embed(colour=ctx.message.author.color, description=F"Ваш ранк: {rank}. Всего добыто: {obwak}{emoji}")
        em.set_author(name=f'Ресурсы пользователя: {member.name}', icon_url=member.avatar_url)
        em.add_field(name="Золото:", value=F"{money}{emoji}")
        em.add_field(name="Еда:", value=F"{food}/{food_max}{emoji_food}")
        em.add_field(name="Дерево:", value=F"{tree}{emoji_tree}")
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 14400, commands.BucketType.user)
    async def work(self, ctx):
        """Получение ежедневных денег
        -work"""

        emoji = await DiscordUtils.get_emoji(ctx)
        userID = ctx.message.author.id

        member = discord.utils.get(ctx.message.guild.members, id = userID)
        money_z = random.randint(50, 300)

        preds = ['сыграл в галактическое лотто и выиграл небольшую сумму в размере',
                'занял первое место на межгалактическом конкурсе красоты и получил приз в размере',
                'запустил стрим игры World of Tanks, получив пробитие, ему так или иначе задонатили в общей сумме',
                'устроился на подработку в местный зоопарк на Марсе, получает',
                'решил закупиться в местной пятёрочке на Венере, оказавшись её миллионным посетителем, он получает презент в размере',
                'принял участие в гонках на космошаттлах и выиграл главный приз в размере',
                'поменял плитку в ванной чиновнику провинции на Юпитере, тот оказался достаточно щедрым и заплатил ему',
                'просто разъезжал без дела по космическим просторам на своём спейс шаттле, при странном стечении обстоятельств он умудряется раздобыть',
                'устроился на подработку в местный Макдак на Сатурне и заработал',
                'отпахал смену на Астеройдной шахте и получил заслуженные',
                'устроился на Межгалактическую фрилансовую биржу и получил',
                'решил подработать в приюте для космических существ и получил',
                'помог перейти через звёздную дорогу пожилому киборгу и в качестве благодарности получает',
                'решил помочь бедной потерявшейся неко-космо-лоле добраться до своего дома и получил вознаграждение в виде поцелуя в щёчку и',
                'прилетел на Нептун и решается показать местным жителям несколько своих любимых аниме тайтлов, сначала ему вломили пиздюлей, а потом дали',
                'выпивая в окрестном баре в глубинке Цереры, продемонстрировал свои навыки в поглощении алкогольных напитков и так впечатлил местный контингент, что те решили вознаградить его в размере',
                'бродил по космическому пространству и наткнулся на жительницу Меркурия, нуждающуюся в починке своего космоавтомобиля. Решив ей помочь, он получает вознаграждение в виде',
                'исследует недра первой попавшейся Чёрной дыры и находит там',
                'исследуя просторы Вселенной, натыкается на заброшенный космический корабль. Там он находит сейф, где лежало',
                'отдыхая на Плутоне, решил сходить на местную аниме вписку. Приехав обратно домой и рассказав об этом своим друзьям, они скидываются ему на лечение в количестве']
        choice = random.choice(preds)
        em = discord.Embed(description=F"{ctx.message.author.mention} {choice} {money_z}{emoji}", colour=ctx.message.author.color)
        em.set_author(name=f'{member.name}', icon_url=member.avatar_url)

        record = await Mongo.get_record('members', 'id', userID)
        money = int(record["money"])
        summary = int(record["summary_money"])

        daily = money + money_z
        obwak = summary + money_z

        upg = {
            "summary_money": obwak,
            "money": daily
        }
        await Mongo.update_record('members', record, upg)
        await ctx.send(embed=em)


    async def dep(self, ctx, inp):
        """
        Deposit you money to bank
        -dep <money>
        """
        emoji = await DiscordUtils.get_emoji(ctx)

        userID = ctx.message.author.id
        record = await Mongo.get_record('members', 'id', userID)
        member = discord.utils.get(ctx.message.guild.members, id=userID)

        money = int(record["money"])
        bank = int(record["bank"])

        if inp == 'all':
            if money <= 0:
                await ctx.send(F"You don't have enough money")
                return

            wr_money = int(money) + int(bank)
            upg = {
                "bank":int(wr_money), 
                "money":0
                }
            
            await Mongo.update_record('members', record, upg)
            em = discord.Embed(description=(F"You deposit {money}{emoji} to the Soviet Bank"), 
                               colour=ctx.message.author.colour)
        else:
            if not inp.isdigit():
                await ctx.send("Use only numbers")
                return

            del_money = money - int(inp)
            if del_money < 0:
                await ctx.send(F"You don't have a money")
                return

            wr_money = bank + int(inp)

            upg = {
                "bank":wr_money, 
                "money":del_money
                }
            await Mongo.update_record('members', record, upg)

            em = discord.Embed(description=(F"You deposit {inp}{emoji} to the Soviet Bank"), 
                               colour=ctx.message.author.colour)

        em.set_author(name=f'{member.name}', icon_url=member.avatar_url)
        await ctx.send(embed=em)


    async def withed(self, ctx, dep):
        """
        Get money from bank
        -with <money>
        """

        emoji = await DiscordUtils.get_emoji(ctx)

        userID = ctx.message.author.id
        member = discord.utils.get(ctx.message.guild.members, id = userID)

        record = await Mongo.get_record('members', 'id', userID)
        money = int(record["money"])
        bank = int(record["bank"])
        if dep == 'all':
            if bank <= 0:
                await ctx.send(F"You don't have enough money")
                return

            wr_money = money + bank

            upg = {
                "bank":0, 
                "money":wr_money
            }

            await Mongo.update_record('members', record, upg)
            em = discord.Embed(description=(F"You get {bank}{emoji} from Soviet Bank"), 
                               colour=ctx.message.author.colour)
        else:
            if not dep.isdigit():
                await ctx.send("Use only numbers")
                return

            del_money = bank - int(dep)
            wr_money = money + int(dep)

            if del_money < 0:
                await ctx.send(F"You don't have enough money")
                return

            upg = {
                "bank":del_money, 
                "money":wr_money
                }

            await Mongo.update_record('members', record, upg)
            em = discord.Embed(description=(F"You get {dep}{emoji} from Soviet Bank"), 
                               colour=ctx.message.author.colour)

        em.set_author(name=f'{member.name}', icon_url=member.avatar_url)
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def rep(self, ctx, member:discord.Member):
        """
        Give reputation to member  
        -rep @Member
        """

        record = await Mongo.get_record('members', 'id', member.id)

        if record is None:
            await ctx.send("Member not found")
            ctx.command.reset_cooldown(ctx)
            return

        if member.id == ctx.message.author.id:
            await ctx.send("You don't give reputation to yourself")
            ctx.command.reset_cooldown(ctx)
            return

        rep = int(record['rep']) + 1

        upg = {
            "rep":rep
        }

        await Mongo.update_record('members', record, upg)

        e = discord.Embed(description = F"{ctx.message.author.mention} +rep {member.mention}", 
                          colour=ctx.message.author.colour)
        await ctx.send(embed=e)

    @commands.command(pass_context=True)
    async def give(self, ctx, member:discord.Member, money):
        """
        Give money to member
        -give <@member> <money>
        """

        emoji = await DiscordUtils.get_emoji(ctx)

        record = await Mongo.get_record('members', 'id', member.id)
        record_transfer = await Mongo.get_record('members', 'id', ctx.message.author.id)

        money_member = int(record_transfer['money'])

        if member.id == ctx.message.author.id:
            await ctx.send("You can't transfer money to yourself")
            return
	
        if money == "all":
            if money_member <= 0:
                await ctx.send("You don't have enough money")
                return

            networth = int(record['money']) + money_member

            upg_member = {
                "money":networth
            }
            upg_transfer = {
                "money":0
            }
            await Mongo.update_record('members', record, upg_member)
            await Mongo.update_record('members', record_transfer, upg_transfer)
        else:
            if not money.isdigit():
                await ctx.send("Use only numbers")
                return
           
            if money_member < int(money):
                await ctx.send("You don't have enough money")
                return

            networth = int(record['money']) + int(money)
            networth_transfer = money_member - int(money)

            updates = {
                "money":networth
            }
            updates_transfer = {
                "money":networth_transfer
            }
            await Mongo.update_record('members', record, updates)
            await Mongo.update_record('members', record_transfer, updates_transfer)

        em = discord.Embed(colour=ctx.message.author.colour, description=f'{ctx.message.author.mention} give {member.mention} - {money}{emoji}')
        em.set_author(name='Transaction system. Soviet Bank:')
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    async def profile(self, ctx, member=None):
        """
        Get profile member
        -profile <member>
        """
        #Todo: Custom profile
        try:
            record, member = await DiscordUtils.get_user(self.bot, ctx, 1, member)
        except TypeError:
            return TypeError
        em = discord.Embed(colour=member.colour)

        title = record["title"]
        name_field_1 = record["name_field_1"]
        name_field_2 = record["name_field_2"]
        field_1 = record["field_1"]
        field_2 = record["field_2"]
        description = record["description"]
        image = record["image"]
        em.add_field(name="Title", value=title, inline=False)

        #Todo: Check on key item names in fields
        check_name = [name_field_1, name_field_2]
        check_list = [field_1, field_2]
        check_keys = ['rep', 'summary_money']
        for i_keys, check in enumerate(check_list):
            if check in check_keys:
                print('true')
                record_member = await Mongo.get_record('members', 'id', member.id)
                value = record_member[check]
                em.add_field(name=check.capitalize(), value=value, inline=True)
            else:
                print(check_list[i_keys])
                em.add_field(name=f"{check_name[i_keys]}", value=check_list[i_keys], inline=True)

        record_inv = await Mongo.get_record('members', 'id', member.id)
        inventory = record_inv['inventory']

        if inventory:
            inv_str = ''
            for inv in inventory:
                inv_str += ''.join(inv) + '\n'
        else:
            inv_str = 'None'
        

        em.add_field(name='Inventory', value=inv_str, inline=True)
        em.add_field(name='Description', value=description, inline=False)
        em.set_thumbnail(url=member.avatar_url)
        if image != "None":
            em.set_image(url=image)
        else:
            pass
        
        await ctx.send(embed=em)


    @commands.command(pass_context=True)
    async def profile_edit(self, ctx):
        """
        Edit you profile
        -profile_edit <upg>
        """
        record = await Mongo.get_record('member_profile', 'id', ctx.message.author.id)

        title = record["title"]
        name_field_1 = record["name_field_1"]
        name_field_2 = record["name_field_2"]
        name_field_3 = record["name_field_3"]
        field_1 = record["field_1"]
        field_2 = record["field_2"]
        field_3 = record["field_3"]
        description = record["description"]
        image = record["image"]

        question_msg = """
        ```Py\nWhat do you want edit? Select a number\n
[1] Title
[2] Field 1
[3] Field 2
[4] Field 3
[6] Description
[7] Image
[8] Exit
```"""
        msg_quest = await ctx.send(question_msg)

        while True:
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if msg:
                id_msg = int(msg.content)
                if id_msg == 1:
                    #* Change Title
                    msg_helper = "Please enter you Title:"
                    helper = await ctx.send(msg_helper)
                    msg_title = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    title = msg_title.content

                    await msg_title.delete()
                    await msg_quest.delete()
                    await helper.delete()
                    await msg.delete()
                    
                    msg_quest = await ctx.send(question_msg)

                elif id_msg in (2,3,4):
                    #* Change Field
                    msg_tempalte = "You can use ready cell templates: `waifu`, `rep`, `summary_money`\nEnter you field content:"
                    msg_helper = "Please enter you Field name:"
                    helper = await ctx.send(msg_helper)

                    msg_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg_name:
                        template = await ctx.send(msg_tempalte)
                        msg_field = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                    if id_msg == 2:
                        name_field_1 = msg_name.content
                        field_1 = msg_field.content
                    elif id_msg == 3:
                        name_field_2 = msg_name.content
                        field_2 = msg_field.content
                    else:
                        name_field_3 = msg_name.content
                        field_3 = msg_field.content

                    await msg_name.delete()
                    await msg_field.delete()
                    await helper.delete()
                    await msg_quest.delete()
                    await template.delete()
                    await msg.delete()

                    msg_quest = await ctx.send(question_msg)

                elif id_msg == 6:
                    #* Change Description
                    msg_helper = "Please enter you Description:"
                    msg_help = await ctx.send(msg_helper)

                    msg_desc = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                    description = msg_desc.content

                    await msg_help.delete()
                    await msg_desc.delete()
                    await msg_quest.delete()
                    await msg.delete()

                    msg_quest = await ctx.send(question_msg)

                elif id_msg == 7:
                    #*Change Image
                    msg_helper = "Please enter you Image URL:"
                    helper = await ctx.send(msg_helper)

                    msg_img = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                    image = msg_img.content

                    await msg.delete()
                    await msg_img.delete()
                    await helper.delete()
                    await msg_quest.delete()

                    msg_quest = await ctx.send(question_msg)

                elif id_msg == 8:
                    #* Exit
                    await msg_quest.delete()
                    await msg.delete()
                    break
                else:
                    await ctx.send('Incorect Number')
                    await msg_quest.delete()
                    await msg.delete()
                    break
        upg = {
            "title": title,
            "name_field_1": name_field_1,
            "name_field_2": name_field_2,
            "name_field_3": name_field_3,
            "field_1": field_1,
            "field_2": field_2,
            "field_3": field_3,
            "description": description,
            "image": image
        }
        await Mongo.update_record('member_profile', record, upg)
        await ctx.send('Save successfully')


        

        

    @commands.command(pass_context=True)
    async def info(self, ctx):
        """
        Give information bot
        -info
        """
        em = discord.Embed(colour=int('0x36393f', 0))
        em.add_field(name="Creator:", value="**Object()**")
        em.add_field(name="Bot name:", value="**Batrack**")
        em.add_field(name="Version:", value="**Python v 3.6.2**")
        em.add_field(name="Category:", value="**Warcraft**")
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_image(url='https://steamuserimages-a.akamaihd.net/ugc/913545907614511543/B35B73E7B268D24301C435F86125178E73769E4C/')
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Standard(bot))