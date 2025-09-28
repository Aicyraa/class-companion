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
        self.remind_schedule.add_exception_type(asyncpg.PostgresConnectionError)
        self.remind_schedule.start() # for starting the reminder
        self.remind_activites.start()
        self.check_expiration_date.start() # for starting the func for checking the expiratin date
        self.stopper = False

    def cog_unload(self): # for cancelling the loop, must
        self.remind_schedule.cancel()
        self.remind_activites.cancel()
        self.check_expiration_date.cancel()


    @tasks.loop(minutes=1) # loops for sending and reminding students their schedule
    async def remind_schedule(self):
        today = datetime.now(self.ph_time).strftime("%A")
        time, _ = datetime.now(self.ph_time).strftime("%I:%M %p").split(' ')
        hours, minutes = time.split(':')

        if int(hours) == 12 and int(minutes) < 60 and not self.stopper :
            self.stopper = True 

            result = rq.schedule_remind()
            for user_id, event in result.items():
                user = self.bot.get_user(user_id)
                if user is None:  # not in cache
                    try:
                        user = await self.bot.fetch_user(user_id)  # API call
                    except Exception as e:
                        print(f"Could not fetch user {user_id}: {e}")
                        continue
                
                embed = discord.Embed(title=f'Hello, {user}', description=f"Here is your schedule for {today}!" if len(event) < 2 else f"Here is your schedules for {today}!", colour=discord.Colour.brand_red())       
                if event:
                    for schedule in event:
                        embed.add_field(name=f'{schedule[1]}', value=f'{schedule[0]}', inline=False)
        
                await user.send(embed=embed)

        if not int(hours) == 12:
            self.stopper = False

    @tasks.loop(minutes=1)
    async def remind_activites(self):
        
        print('1')
        for guild_id, events in rq.activity_remind().items():

            print(type(guild_id))
            guild = await self.bot.fetch_guild(guild_id)
            channels = await guild.fetch_channels()
            channel = discord.utils.get(channels, name="《🔔》event-schedule")
            
            for event in events:
    
                embed = discord.Embed(title=f'🔔《Reminder》🔔 !!', description=f'Activity: {event}', color=discord.Colour.dark_gold())
                embed.add_field(name=f'**{event}**',value=None, inline=False)
                embed.set_image(url='https://cdn.dribbble.com/userupload/23917499/file/original-f0fec54e6c9d49c25c75e1b443f03b0b.gif')
                await channel.send(embed=embed)

            # await channel.send(f'@everyone, these are your activies for today! ')


    @tasks.loop(minutes=1)
    async def check_expiration_date(self):
        rq.check_date()

    @remind_schedule.before_loop
    @check_expiration_date.before_loop
    async def before_remind(self):
        print('Waiting for class companion to start...')
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminder(bot))