import discord
import logging 
import os
import asyncio
from threading import Thread
from discord.ext import commands
from utils.sql_func_checker import Checker
from utils.config import Settings 

logging.basicConfig(
    level=logging.ERROR,  # Change to DEBUG if you want more details
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("discord.log", encoding="utf-8", mode="w"), 
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger("discord")   

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='//', intents=intents)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')    
            
async def main():
    
    await Checker.check_db(Settings.db) # for checking the database
    await Checker.check_table() # for checking the table
    await load() # loading cogs
    await bot.start(Settings.token, reconnect=True)

    Settings.connection().close()
    
if __name__ == "__main__":
    asyncio.run(main())
     
