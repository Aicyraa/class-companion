import discord
import re
from datetime import datetime 
from discord.ext import commands
from utils.sql_func_helpers import Query
from utils.sql_func_reminder import Reminder_Query

# Config file

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

    @commands.command()
    async def showCmd(self, ctx):  # for sending a guide

        embed = discord.Embed(title="📍 Class Companion Commands", description="""Use the `//` prefix before the command """, color=discord.Colour.og_blurple(),)
        embed.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
        embed.add_field(name="`schedule`", value='> followed by schedule', inline=False)
        embed.add_field(name="`view`", value='> to view current schedule', inline=False)
        embed.add_field(name="`update`", value='> to update', inline=False)
        embed.add_field(name="`delete`", value='> to delete', inline=False)
        embed.add_field(name="`activity`", value='> for creating a new activity reminder', inline=False)
        embed.add_field(name="`quiz`", value='> for converting file to quiz', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def schedule(self, ctx, *args):  # for schedule command

        if ctx.guild is not None:
            notify = discord.Embed(title=f"{ctx.author.display_name or ctx.author.name}", description=f"A message has been sent to you!", color=discord.Colour.og_blurple(),)
            await ctx.send(embed=notify,  delete_after=1000)

        if not args or len(args) < 2:
            guide = discord.Embed(title="🗺️ Schedule Command Guide", description="**⟣┄ˑ◌ The command `schedule` should be followed by the User Schedule in `DST` format. `NOTE`, you can add multiple schedule separated with space**", color=discord.Colour.og_blurple())
            guide.set_thumbnail(url=self.bot.user.avatar)
            guide.description += f"`\n\n𖥔 Day`:  ( Monday - Sunday )\n`𖥔 Subject`:  Users Subject for that day\n𖥔 Time`:  12-Hour AM/PM format e.g (1PM || 1:35PM)"
            await ctx.author.send(embed=guide)
            return

        schedule_set = discord.Embed(title="⌛ Schedule is set!", description='', color=discord.Colour.og_blurple())

        for i in range(0, len(args), 3):
           
            userSchedule = args[i : i + 3]

            if userSchedule[0].lower() not in ("monday","tuesday","wednesday","thursday","friday","saturday", "sunday") or len(userSchedule) < 3:
                await ctx.send(f"❌ Invalid format! Check your format length or text! {len(userSchedule)} || {userSchedule[0]}",  delete_after=10)
                continue
            elif not re.match(r"^(0?[1-9]|1[0-2])(:[0-5][0-9])?(AM|PM)$", userSchedule[2].strip().upper()):
                await ctx.send(f"❌ Invalid time format: `{userSchedule[2]}`. Use like `1PM`, `1:00PM`, or `11:30PM`.", delete_after=10)
                continue
            else:
                Query.insert_schedule(ctx.author.id, userSchedule)
                day, subj, time = userSchedule
                schedule_set.description =( schedule_set.description or '')+ f'\n` 𖥔 {day.upper()}`:  {subj},  {time}'

        await ctx.author.send(embed=schedule_set)

    @commands.command()
    async def view(self, ctx):
        
        schedule = Query.fetch(ctx.author.id)
        
        for day, events in schedule.items():
            embed = discord.Embed(title=f'📌 **{day}** 📌', description=f'> {"\n > ".join(events)}', color=discord.Color.blurple())
            await ctx.send(embed=embed)
                 
    @commands.command()
    async def update(self, ctx):
        ''' For updating the schedule'''
        pass
    
    @commands.command()
    async def delete(self, ctx, *args):
        
        if not args or len(args) < 2:
            guide = discord.Embed(title="🗺️ Delete Command Guide", description="**⟣┄ˑ◌ The command `delete` should be followed by the User Schedule in `DET` format.**", color=discord.Colour.og_blurple())
            guide.set_thumbnail(url=self.bot.user.avatar)
            guide.add_field(name="`𖥔 Day Event Time`", value="", inline=False)
            await ctx.author.send(embed=guide)
            return
        
        result = Query.delete(ctx.author.id, args[0], args[1], datetime.strptime(args[2], "%I%p").time())
        
        if result:
            embed = discord.Embed(title='✅ Successfuly deleted!', description=f'> {args[0]}-{args[1]}-{args[2]}', color=discord.Color.dark_red())
            await ctx.send(embed=embed)
            return 
        
        embed = discord.Embed(title='❌ Error while deleting!', description=f'Schedule does not match anything!',  color=discord.Color.dark_red()) # if hindi successful
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.has_permissions(administrator=True, manage_channels=True, manage_guild=True)
    async def activity(self, ctx, *message):  # for sever owner or admins
       
        config = {
            "name": "《🔔》event-schedule",
            "permission": {
                ctx.guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                create_public_threads=False,
                create_private_threads=False,
                send_messages_in_threads=False
            ),
                ctx.guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                create_public_threads=True,
                create_private_threads=True,
                send_messages_in_threads=True,
                mention_everyone=True
            )},
            "get": discord.utils.get(ctx.guild.text_channels, name="《🔔》event-schedule"),
        }

        if not config["get"]: 
            await ctx.guild.create_text_channel(name=config["name"], overwrites=config["permission"])
            await ctx.send(f'📌 {config["name"]} is created!', delete_after=60)
            return

        if len(message) < 2: 
            await ctx.send('❌ Invalid parameters! Usage: `//activity "Event Name" 1H`', delete_after=60)
            return
    
        duration = message[-1]         
        event = " ".join(message[:-1]) 

        expiry = Reminder_Query.convert_to_expiry(duration)
        if not expiry:
            await ctx.send(f"❌ Invalid duration format: `{duration}` (use 1D, 2H, 30M)", delete_after=60)
            return

        Query.insert_activity(ctx.guild.id, event, expiry)
        await ctx.send(f'📌 @everyone, a new activity has been added!', delete_after=60)

async def setup(bot):
    await bot.add_cog(Commands(bot))
