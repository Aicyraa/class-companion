import discord
# import logging 
import os
import asyncio
import mysql.connector as sql
from discord.ext import commands
from utils.db_checker import Checker
from utils.settings import Settings 

# handler = logging.FileHandler( filename='./discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='//', intents=intents)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')    
            

async def main():
  
    cnx = sql.connect(**Settings.config) # 
    cursor = cnx.cursor() # 

    await Checker.check_db(cursor, Settings.db)
    await Checker.check_table(cursor, Settings.tb_schedule)
    await load()
    await bot.start(Settings.token, reconnect=True)
    
if __name__ == "__main__":
     asyncio.run(main())
     
