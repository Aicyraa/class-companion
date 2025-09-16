import discord
import logging
import os
import asyncio
import mysql.connector as sql
from mysql.connector import errorcode
from discord.ext import commands
from dotenv import load_dotenv
from utils.sql import Sql

# handler = logging.FileHandler( filename='./discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='//', intents=intents)
load_dotenv()

token = os.getenv('TOKEN')
db = 'Discord_Bot'
    
config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')    
            

async def main():
  
    cnx = sql.connect(**config)
    cursor = cnx.cursor()

    await Sql.check_db(cursor, db)
    await load()
    await bot.start(token, reconnect=True)
    
if __name__ == "__main__":
     asyncio.run(main())
     
