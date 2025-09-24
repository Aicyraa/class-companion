import pytz
import discord
import asyncpg
from datetime import datetime, time
from discord.ext import tasks, commands
from utils.sql_func_reminder import Reminder_Query as rq

class Reminder(commands.Cog):

    ph_time = pytz.timezone('Asia/Manila')

    def __init__ (self, bot):
        self.bot = bot
        self.time_checker.add_exception_type(asyncpg.PostgresConnectionError)
        self.time_checker.start() # for starting the loop
        self.stopper = False

    def cog_unload(self): # for cancelling the loop, must
        self.time_checker.cancel()

    @tasks.loop(minutes=1)
    async def time_checker(self):
        time, _ = datetime.now(self.ph_time).strftime("%I:%M %p").split(' ')
        hours, minutes = time.split(':')
        today = datetime.now(Reminder.ph_time).strftime("%A")


        if int(hours) + 12 == 13 and int(minutes) < 60 and not self.stopper :
            self.stopper = True 

            from utils.sql_func_reminder import Reminder_Query as rq
            result = rq.midnight_remind()

            for user_id, event in result.items():

                user = self.bot.get_user(user_id)
                if user is None:  # not in cache
                    try:
                        user = await self.bot.fetch_user(user_id)  # API call
                    except Exception as e:
                        print(f"Could not fetch user {user_id}: {e}")
                        continue

                embed = discord.Embed(title=f'Hello, {user}', description=f'Here is your schedules for {today}!', colour=discord.Colour.brand_red())
                
                print(f'{type(user_id)} ==> {event}')
                if event:
                    for schedule in event:
                        embed.add_field(name=f'{schedule[1]}', value=f'{schedule[0]}', inline=False)
        
                await user.send(embed=embed)

        if not int(hours) + 12 == 13:
            self.stopper = False

    @time_checker.before_loop
    async def before_remind(self):
        print('Waiting for class companion to start...')
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminder(bot))