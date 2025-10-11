import pytz
import discord
import asyncpg
from datetime import datetime
from discord.ext import tasks, commands
from utils.sql_func_reminder import Reminder_Query as query

class Reminder(commands.Cog):

    ph_time = pytz.timezone('Asia/Manila')

    def __init__ (self, bot):
        self.bot = bot
        self.remind_schedule.add_exception_type(asyncpg.PostgresConnectionError)
        self.remind_schedule.start() # for starting the loop
        self.remind_activites.start() 
        self.check_expiration_date.start() 
        self.schedule_stopper = False
        self.activity_stopper = False

    def cog_unload(self): # for cancelling the loop, must
        self.remind_schedule.cancel()
        self.remind_activites.cancel()
        self.check_expiration_date.cancel()

    @tasks.loop(minutes=1) # loops for sending and reminding students their schedule
    async def remind_schedule(self):
        
        counter = 1        
        _, __, today = datetime.now(self.ph_time).strftime("%H %M %A").split(' ') # for fetching the current time hours, minutes day
        hours, minutes = int(_), int(__)
    
        if hours in [0, 6, 12] and minutes < 59 and not self.schedule_stopper :
            self.schedule_stopper = True 
            result = query.schedule_remind()
            
            for user_id, event in result.items():
                
                user = await self.bot.fetch_user(user_id)  # API call
                remind_schedule = discord.Embed(title=f'📌 Hello, {user}❗', description=f"Here is your schedule for **`{today}`**  🗺️." if len(event) < 2 else f"Here is your schedules for **`{today}`**  🗺️.", colour=discord.Colour.brand_red())       
                remind_schedule.set_image(url='http://bestanimations.com/HomeOffice/Clocks/Alarm/funny-alarm-clock-animated-gif-2.gif')
                remind_schedule.set_footer(text='Class Companion', icon_url=self.bot.user.display_avatar.url)
                
                for schedule in event:
                    remind_schedule.add_field(name=f'**`Schedule {counter}`** ⏰', value=f'> Time:   **{schedule[1][1:]}**\n> Schedule:   **{schedule[0]}** ' if schedule[1].startswith('0') else f'> Time:   **{schedule[1]}**\n> Schedule:   **{schedule[0]}** ', inline=False)
                    counter += 1
                    
                counter = 1
                await user.send(embed=remind_schedule, delete_after=21600) # 6 hours before disappering

        if hours not in [0, 6, 12]: # so the reminder will only occur once
            self.shedule_stopper = False

    @tasks.loop(minutes=1)
    async def remind_activites(self): # for reminding activities
        
        _, __, today = datetime.now(self.ph_time).strftime("%H %M %A").split(' ') # for fetching the current time hours, minutes day
        hours, minutes = int(_), int(__)
        
        if hours in [0, 6, 12] and minutes == 0 and not self.remind_activites:
            self.activity_stopper = True
            for guild_id, events in query.activity_remind().items():
                
                guild = await self.bot.fetch_guild(guild_id) 
                fetch_channel = await guild.fetch_channels()
                channel = discord.utils.get(fetch_channel, name="《🔔》event-schedule")
                
                if not channel: # if channel is hindi pa na ccreate, mag rereturn imbis na mag proceed ung remind para hindi mag error
                    continue
                
                for event in events: # for sending activities to the event-schedule channel
                    
                    text, time = event
                    expiry_date = str(time).split(' ')[:-1][0]

                    remind_activity = discord.Embed(title=f'🔔 **Reminder** 🔔 ', description='', color=discord.Colour.dark_gold())
                    remind_activity.add_field(name='', value=f'> Activity: ** {text.capitalize()} ** \n> Deadline: ** {expiry_date} **', inline=False)
                    remind_activity.set_thumbnail(url='https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3N6ZG0zODFmemo5YzdndHd3dW16cWwxMTVkZmN6czE4dGFoczY1OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PefhJNutC9LVrmDFjx/giphy.gif')
                    remind_activity.set_footer(text='Class Companion', icon_url=self.bot.user.display_avatar.url)
                
                    await channel.send(embed=remind_activity, delete_after=21600) # 6 hours before disappearing
                
                mention = discord.Embed(title=f"📌 @everyone as of {today}.", description="> These are the activities, check if you haven't done this activity yet." ,timestamp=datetime.now(self.ph_time), color=discord.Colour.dark_orange())
                mention.set_image(url='https://cdn.dribbble.com/userupload/23917499/file/original-f0fec54e6c9d49c25c75e1b443f03b0b.gif')
                await channel.send(embed=mention, delete_after=21600)
                await channel.send(f'@everyone❗', delete_after=21600)
                
        if hours not in [0, 6, 12]: # so the reminder will occur once
            self.remind_activites = False
        
    @tasks.loop(minutes=1)
    async def check_expiration_date(self): # loop for checking the expiration date
        query.check_date()

    @remind_schedule.before_loop
    @remind_activites.before_loop
    async def before_remind(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminder(bot))