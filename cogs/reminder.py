import pytz
import discord
import asyncpg
from datetime import datetime
from discord.ext import tasks, commands
from utils.sql_func_reminder import Reminder_Query as query
from utils.embed_helper import make_embed  


class Reminder(commands.Cog):

    ph_time = pytz.timezone('Asia/Manila')

    def __init__(self, bot):
        self.bot = bot
        self.remind_schedule.add_exception_type(asyncpg.PostgresConnectionError)
        self.remind_schedule.start()
        self.remind_activities.start()
        self.check_expiration_date.start()
        self.schedule_stopper = False
        self.activity_stopper = False

    def cog_unload(self):
        self.remind_schedule.cancel()
        self.remind_activities.cancel()
        self.check_expiration_date.cancel()

    @tasks.loop(minutes=1)
    async def remind_schedule(self):
        counter = 1
        _, __, today = datetime.now(self.ph_time).strftime("%H %M %A").split(' ')
        hours, minutes = int(_), int(__)

        if hours in [0, 6, 12] and minutes < 59 and not self.schedule_stopper:
            self.schedule_stopper = True
            result = query.schedule_remind()

            for user_id, event in result.items():
                user = await self.bot.fetch_user(user_id)

                desc = f"Here is your schedule for **`{today}`** 🗺️." if len(event) < 2 else f"Here are your schedules for **`{today}`** 🗺️."
                remind_schedule = make_embed(
                    self.bot,
                    title=f'📌 Hello, {user}❗',
                    description=desc,
                    color=discord.Color.brand_red(),
                    image='http://bestanimations.com/HomeOffice/Clocks/Alarm/funny-alarm-clock-animated-gif-2.gif'
                )

                for schedule in event:
                    remind_schedule.add_field(name=f'**`Schedule {counter}`** ⏰', value=f'> Time: **{schedule[1].lstrip("0")}**\n> Schedule: **{schedule[0]}**', inline=False)
                    counter += 1

                counter = 1
                await user.send(embed=remind_schedule, delete_after=21600)

        if hours not in [0, 6, 12]:
            self.schedule_stopper = False

    @tasks.loop(minutes=1)
    async def remind_activities(self):
        _, __, today = datetime.now(self.ph_time).strftime("%H %M %A").split(' ')
        hours, minutes = int(_), int(__)

        if hours in [0, 6, 12] and minutes < 59 and not self.activity_stopper:
            self.activity_stopper = True

            for guild_id, events in query.activity_remind().items():
                guild = await self.bot.fetch_guild(guild_id)
                fetch_channel = await guild.fetch_channels()
                channel = discord.utils.get(fetch_channel, name="《🔔》event-schedule")

                if not channel:
                    continue

                for event in events:
                    text, time = event
                    expiry_date = str(time).split(' ')[:-1][0]

                    remind_activity = make_embed(
                        self.bot,
                        title='🔔⟣┄─⟣┄─ ** Reminder ** ┄─⟣┄─⟣ 🔔',
                        description=f'> Activity: **{text.capitalize()}**\n> Deadline: **{expiry_date}**',
                        color=discord.Colour.dark_gold(),
                        thumbnail='https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3N6ZG0zODFmemo5YzdndHd3dW16cWwxMTVkZmN6czE4dGFoczY1OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PefhJNutC9LVrmDFjx/giphy.gif'
                    )

                    await channel.send(embed=remind_activity, delete_after=21600)

                mention = make_embed(
                    self.bot,
                    title=f"📌 @everyone as of {today}.",
                    description="> Here are the activities. Please check if you haven’t completed them yet.",
                    color=discord.Colour.dark_orange(),
                    image='https://cdn.dribbble.com/userupload/23917499/file/original-f0fec54e6c9d49c25c75e1b443f03b0b.gif'
                )

                await channel.send(embed=mention, delete_after=21600)
                await channel.send('@everyone❗', delete_after=21600)

        if hours not in [0, 6, 12]:
            self.activity_stopper = False

    @tasks.loop(minutes=1)
    async def check_expiration_date(self):
        query.check_date()

    @remind_schedule.before_loop
    @remind_activities.before_loop
    async def before_remind(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Reminder(bot))
