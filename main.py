import discord
import os

from cogs.utils.u_mongo import Mongo
from discord.ext import commands

async def get_prefix(bot, message):
    """
    Get prefix 
    """

    if not message.guild:
        return commands.when_mentioned_or("=")(bot, message)

    record = await Mongo.get_record('server_settings', 'id', message.guild.id)

    if message.guild.id != record['id']:
        return commands.when_mentioned_or("=")(bot, message)

    prefix = str(record['prefix'])
    return commands.when_mentioned_or(prefix)(bot, message)

bot = commands.Bot(command_prefix='=', description='Batrack v 1.5\n Standard prefix: "="')

extensions = ['cogs.standard',
              'cogs.admin',
              'cogs.shop',
              'cogs.owner',
              'cogs.event',
              'cogs.activity',
              'cogs.casino']


if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(str(os.getenv('TOKEN')))