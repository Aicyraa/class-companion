import pytz
import discord
import asyncpg
from datetime import datetime, time
from discord.ext import tasks, commands
from utils.sql_func_reminder import Reminder_Query as query

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

        counter = 1        
        hours, minutes, today = datetime.now(self.ph_time).strftime("%I %M %A").split(' ') # for fetching the current time hours, minutes day

        if int(hours) == 11 and int(minutes) < 60 and not self.stopper :
           
            self.stopper = True 
            result = query.schedule_remind()
            
            for user_id, event in result.items():
            
                user = await self.bot.fetch_user(user_id)  # API call
                embed = discord.Embed(title=f'📌 Hello, {user}❗', description=f"Here is your schedule for **`{today}`**  🗺️." if len(event) < 2 else f"Here is your schedules for **`{today}`**  🗺️.", colour=discord.Colour.brand_red())       
               
                if event:
                    for schedule in event:
                        print(f'Type, {type(schedule[0])},  {type(schedule[1])}, ==> {schedule} ')
                        embed.add_field(name=f'**`Schedule {counter}`** ⏰', value=f'> Time:   **{schedule[1][1:]}**\n> Schedule:   **{schedule[0]}** ' if schedule[1].startswith('0') else f'> Time:   **{schedule[1]}**\n> Schedule:   **{schedule[0]}** ', inline=False)
                        counter += 1
                    counter = 1
                await user.send(embed=embed)

        if not int(hours) == 11:
            self.stopper = False

    @tasks.loop(minutes=1)
    async def remind_activites(self):
        
        for guild_id, events in query.activity_remind().items():
            
            guild = await self.bot.fetch_guild(guild_id)
            channels = await guild.fetch_channels()
            channel = discord.utils.get(channels, name="《🔔》event-schedule")
            
            for event in events:
                
                text, time = event
                expiry_date = str(time).split(' ')[:-1][0]

                embed = discord.Embed(title=f'🔔 **Reminder** 🔔 ', description=f'Activity: `{text.upper()}` \nDeadline: **{expiry_date}**', color=discord.Colour.dark_gold())
                embed.set_image(url='https://cdn.dribbble.com/userupload/23917499/file/original-f0fec54e6c9d49c25c75e1b443f03b0b.gif')
                await channel.send(embed=embed, delete_after=100)

            await channel.send(f' @everyone, these are your activies for today!', delete_after=100)

    @tasks.loop(minutes=1)
    async def check_expiration_date(self):
        query.check_date()

    @remind_schedule.before_loop
    @remind_activites.before_loop
    async def before_remind(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminder(bot))