import discord
import logging 
import os
import asyncio
from discord.ext import commands
from utils.db_checker import Checker
from utils.config import Settings 


logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG if you want more details
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("discord.log", encoding="utf-8", mode="w"), 
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger("discord")  #


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='//', intents=intents)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')    
            

async def main():
  
    await Checker.check_db( Settings.db)
    await Checker.check_table()
    await load()
    await bot.start(Settings.token, reconnect=True)

    Settings.connection().close()
    
if __name__ == "__main__":
     asyncio.run(main())
     
