import discord
import os

from .utils.u_mongo import Mongo
from .utils.u_discord import DiscordUtils

from discord.ext import commands
from discord.ext.commands import has_permissions

class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def em(self, ctx):
        """Описание саб-команд em
        
        -em new [Создание личного embed]
        -em author [text] [Установка названия ивента][128 symbols]
        -em descrip [description] [Установка описания ивента][2048 symbols]
        -em f [1-4] ["Название категории"] ["Описание категории"] [Максимум 4 категории][2048 symbols]
        -em set_img [url] [Вставка картинки, нужен url]
        -em footer [text] [Вставка футера]
        -em send [#channel] [Отправка сообщения с @here]
        -em clear [Очистить embed]
        -em view [Предпросмотр вашего embed]"""

        if ctx.invoked_subcommand is None:
            msg = ctx.command.help
            em = discord.Embed(colour=ctx.message.author.colour)
            em.add_field(name="Command Helper", value=F"{msg}")
            await ctx.send(embed=em)

    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def new(self, ctx):
        """Создание личного embed
        
        -em new"""
        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)
        if record is None:
            upg = {
                "embed_owner": author_id,
                "author": "",
                "description": "",
                "field_1": "",
                "name_1": "",
                "field_2": "",
                "name_2": "",
                "field_3": "",
                "name_3": "",
                "field_4": "",
                "name_4": "",
                "set_image": "",
                "footer": ""
            }
            await Mongo.record_insert('embed', upg)
            await ctx.send("Создание вашего личного embed успешно.:white_check_mark:")
        else:
            await ctx.send("У вас уже есть свои личный embed\nВы можете использовать 'em clear', для его очистки.")

    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def author(self, ctx, *, text):
        """Установка заголовка эмбеда
        
        -em author "text" """
        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)
        if len(text) > 128:
            await ctx.send("Слишком много символов. Максимальное количество: 128")
        else:
            upg = {
                "author":text
            }
            await Mongo.update_record('embed', record, upg)
            await ctx.send("Установка заголовка успешна")
        
    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def descrip(self, ctx, *, text):
        """Установка описания ивента
        
        -em descrip "text" """

        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)
        if record is None:
            await ctx.send("Для начала нужно создать свой личный embed\n 'em new'")
            pass
        if len(text) > 2048:
            await ctx.send("Слишком много символов. Максимальное количество: 2048")
        else:
            upg = {
                "description":text
            }
            await Mongo.update_record('embed', record, upg)

            await ctx.send("Description введен успешно.")

    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def set_img(self, ctx, *, url):
        """Установка главного изображения
        
        -em set_img "url" """

        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)

        if record is None:
            await ctx.send("Для начала нужно создать свой личный embed\n '-em new'")
            pass
        else:
            upg = {
                "set_image":url
            }
            await Mongo.update_record('embed', record, upg)
            await ctx.send("Установка изображения успешно!")


    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def f(self, ctx, field:int, header, text):
        """Установка f
        
        -em f (1-4) "header" "text" """

        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)

        if record is None:
            await ctx.send("Для начала нужно создать свой личный embed\n '-em new'")
            pass

        #Check_fields
        if field == 1:
            upg = {
                "field_1":header,
                "name_1":text
            }
            await Mongo.update_record('embed', record, upg)
            await ctx.send("Установка первого field успешно")
        elif field == 2:
            upg = {
                "field_2":header,
                "name_2":text
            }
            await Mongo.update_record('embed', record, upg)
            await ctx.send("Установка второго field успешно")
        elif field == 3:
            upg = {
                "field_3":header,
                "name_3":text
                }
            await Mongo.update_record('embed', record, upg)
            await ctx.send("Установка третьего field успешно")
        elif field == 4:
            upg = {
                "field_4":header,
                "name_4":text
            }
            await Mongo.update_record('embed', record, upg)
            await ctx.send("Установка четвертого field успешно")
        else:
            await ctx.send("Более fields недоступны")


    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def view(self, ctx):
        """Просмотр предварительного сообщения

        -em view"""

        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)

        if record is None:
            await ctx.send("Для начала нужно создать свой личный embed\n '-em new'")
            pass
        
        #check in record
        if record['description'] != "":
            e = discord.Embed(colour=int('0x36393f', 0), description=record['description'])
        else:
            e = discord.Embed(colour=int('0x36393f', 0))
        if record['author'] != "":
            e.set_author(name=record['author'])
        if record['field_1'] != "":
            e.add_field(name=record['field_1'], value=F"{record['name_1']}")
        if record['field_2'] != "":
            e.add_field(name=record['field_2'], value=F"{record['name_2']}")
        if record['field_3'] != "":
            e.add_field(name=record['field_3'], value=F"{record['name_3']}")
        if record['field_4'] != "":
            e.add_field(name=record['field_4'], value=F"{record['name_4']}")
        if record['set_image'] != "":
            e.set_image(url=record['set_image'])
        if record['footer'] != "":
            e.set_footer(text=record['footer'], icon_url=ctx.message.server.icon_url)

        await ctx.send(embed=e)
    
    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def clear(self, ctx):
        """Очистить ваш embed"""

        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)

        if record is None:
            await ctx.send("Для начала нужно создать свой личный embed\n '-em new'")
            pass
        
        upg = {
            "embed_owner":ctx.message.author.id,
            "author":"",
            "description":"",
            "field_1":"",
            "name_1":"",
            "field_2":"",
            "name_2":"",
            "field_3":"",
            "name_3":"",
            "field_4":"",
            "name_4":"",
            "set_image":"",
            "footer":""
        }
        await Mongo.update_record('embed', record, upg)
        await ctx.send("Очистка вашего embed успешна")

    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def footer(self, ctx, *, text):
        """Установка текста в footer
        
        -em footer <text>"""

        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)

        if record is None:
            await ctx.send("Для начала нужно создать свой личный embed\n '-em new'")
            pass
        else:
            upg = {
                "footer":text
            }
            await Mongo.update_record('embed', record, upg)
            await ctx.send("Установка футера успешно!")
    
    @em.group(pass_context=True)
    @has_permissions(manage_roles=True)
    async def send(self, ctx, channel):
        """Отправка сообщения в определенный канал. DANGER пингует @here
        
        -em send <channel_name>"""

        author_id = ctx.message.author.id
        record = await Mongo.get_record('embed', 'embed_owner', author_id)

        if record is None:
            await ctx.send("Для начала нужно создать свой личный embed\n '-em new'")
            pass
        
        if record['description'] != "":
            e = discord.Embed(colour=int('0x36393f', 0), description=record['description'])
        else:
            e = discord.Embed(colour=ctx.message.author.colour)
        if record['author'] != "":
            e.set_author(name=record['author'])
        if record['field_1'] != "":
            e.add_field(name=record['field_1'], value=F"{record['name_1']}")
        if record['field_2'] != "":
            e.add_field(name=record['field_2'], value=F"{record['name_2']}")
        if record['field_3'] != "":
            e.add_field(name=record['field_3'], value=F"{record['name_3']}")
        if record['field_4'] != "":
            e.add_field(name=record['field_4'], value=F"{record['name_4']}")
        if record['set_image'] != "":
            e.set_image(url=record['set_image'])
        if record['footer'] != "":
            e.set_footer(text=record['footer'], icon_url=ctx.message.server.icon_url)
        
        ch = discord.utils.get(self.bot.get_all_channels(), guild__name=ctx.guild.name, name=channel)
        await ch.send("@here")
        await ch.send(embed=e)
        
        
def setup(bot):
    bot.add_cog(Activity(bot))