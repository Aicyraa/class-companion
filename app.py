import discord
import logging
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

handler = logging.FileHandler( filename='./txt/discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='//', intents=intents)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

#@bot.command()
# async def viewSchedule():
#     pass
#
#@bot.command()
# async def updateSchedule():
#     pass
#
# @bot.command()
# async def setActivity():
#     pass


async def load():
    for filename in os.listdir('./cogs/*'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs{filename[:-3]}')    
            
async def main():
        await load()
        await bot.run(token, log_handler=handler, log_level=logging.DEBUG )
        

asyncio.run(main())
