import pytz
from datetime import datetime, time
from discord.ext import tasks, commands
from utils.sql_func_reminder import Reminder_Query as rq

class Reminder(commands.Cog):

    ph_time = pytz.timezone('Asia/Manila')

    def __init__ (self, bot):
        self.bot = bot
        self.time_checker.start()
        self.stopper = False

    def cog_unload(self):
        self.time_checker.cancel()

    @tasks.loop(minutes=1)
    async def time_checker(self):
        time, _ = datetime.now(self.ph_time).strftime("%I:%M %p").split(' ')
        hours, __ = time.split(':')

        if int(hours) == 9 and not self.stopper:
            self.stopper = True
            
            rq.midnight_remind()

        if not int(hours) == 9:
            self.stopper = False

async def setup(bot):
    await bot.add_cog(Reminder(bot))