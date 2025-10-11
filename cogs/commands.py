import discord
import re
from datetime import datetime 
from discord.ext import commands
from discord import app_commands
from utils.sql_func_helpers import Query
from utils.time_converter import Time_Converter as tc

# Config file

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

    @app_commands.command(name="show_command", description="For displaying the available commands")
    async def showCmd(self, interaction: discord.Interaction):  # for sending a guide

        guide = discord.Embed(title="📍 Class Companion Commands", description="""Use the `//` prefix before the command """, color=discord.Colour.blurple())
        guide.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
        guide.add_field(name="`schedule`", value='> followed by schedule\n> **//schedule Day Event Time**', inline=False)
        guide.add_field(name="`view`", value='> to view current schedule', inline=False)
        guide.add_field(name="`update`", value='> to update\n> **//update (old) Day Event Time - (new) Day Event Time**', inline=False)
        guide.add_field(name="`delete`", value='> to delete\n> **//delete Day Event Time**', inline=False)
        guide.add_field(name="`activity`", value='> for creating a new activity reminder\n> **/activity event:Text duration: 1D | 1H | 10M | 1D1H10M)**', inline=False)
        guide.add_field(name="`quiz`", value='> for converting file to quiz', inline=False)
        await interaction.response.send_message(embed=guide)

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
        schedule_set.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
        
        
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
                schedule_set.description = (schedule_set.description or '')+ f'\n` 𖥔 {day.upper()}`:  {subj},  {time}'

        await ctx.author.send(embed=schedule_set)

    @commands.command()
    async def view(self, ctx): # for view command
        
        schedule = Query.fetch(ctx.author.id)
        
        for day, events in schedule.items():
            view = discord.Embed(title=f'📌 **{day}** 📌', description=f'> **{"\n > ".join(events)}**', color=discord.Color.dark_gold())
            view.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
            await ctx.send(embed=view, delete_after=1200)
                 
    @commands.command()
    async def update(self, ctx, *args): # for update command
            
        if not args or len(args) < 2:
            guide = discord.Embed(title="🗺️ Update Command Guide", description="**⟣┄ˑ◌ The command `update` should be followed by the User Schedule in `(OLD) DET - DET (NEW)` format.**\n\n`𖥔 Day Event Time`", color=discord.Colour.og_blurple())
            guide.set_thumbnail(url=self.bot.user.avatar)
            guide.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
            await ctx.send(embed=guide, delete_after=600)
            return
        
        if '-' not in args or len(args) > 7:
            error = discord.Embed(title='❌ Error', description='Invalid format!', color=discord.Color.dark_gold())
            await ctx.send(embed=error)
            return 
            
        old, new = (" ".join(args)).split(' - ')
        result = Query.edit(ctx.author.id, old.split(' '), new.split(' '))
        
        if result:
            notify = discord.Embed(title='✅ ⟣┄ˑ◌ Successfuly Updated!', description=f'> {args[0]} {args[1]} {args[2]} to {args[4]} {args[5]} {args[6]}', color=discord.Color.dark_green())
            notify.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
            await ctx.send(embed=notify, delete_after=600)
            return     
        
        error = discord.Embed(title='❌ Error while updating!', description=f'Schedule does not match anything!',  color=discord.Color.dark_red()) # if hindi successful
        error.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
        await ctx.send(embed=error, delete_after=600)
               
    @commands.command()
    async def delete(self, ctx, *args): # for //delete command
        
        if not args or len(args) < 2:
            guide = discord.Embed(title="🗺️ Delete Command Guide", description="**⟣┄ˑ◌ The command `delete` should be followed by the User Schedule in `DET` format.**\n\n`𖥔 Day Event Time`", color=discord.Colour.og_blurple())
            guide.set_thumbnail(url=self.bot.user.avatar)
            await ctx.send(embed=guide, delete_after=600)
            return
        
        result = Query.delete(ctx.author.id, args[0], args[1], tc.convert_to_24(args[2]) )
        
        if result:
            success = discord.Embed(title='✅ Successfuly deleted!', description=f'> {args[0]} - {args[1]} - {args[2]}', color=discord.Color.dark_green())
            success.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)   
            await ctx.send(embed=success, delete_after=600)
            return 
        
        error = discord.Embed(title='❌ Error while deleting!', description=f'Schedule does not match anything!',  color=discord.Color.dark_red()) # if hindi successful
        error.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
        await ctx.send(embed=error, delete_after=600)
        
    @app_commands.command(name='activity', description='Add an activity : /activity event:text duraition: 1D | 2H | 30M | 1D2H30M')
    @app_commands.checks.has_permissions(administrator=True, manage_channels=True, manage_guild=True)
    async def activity(self, interaction: discord.Interaction, event: str, duration: str):
        guild = interaction.guild

        # Define channel setup configuration
        config = {
            "name": "《🔔》event-schedule",
            "get": discord.utils.get(guild.text_channels, name="《🔔》event-schedule")
        }

        if not config["get"]:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    send_messages_in_threads=False
                ),
                guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    create_public_threads=True,
                    create_private_threads=True,
                    send_messages_in_threads=True,
                    mention_everyone=True
                )
            }
            await guild.create_text_channel(name=config["name"], overwrites=overwrites)
            await interaction.response.send_message(f'📌 {config["name"]} channel created!', ephemeral=True)
            return

        expiry = tc.convert_to_expiry(duration)
        if not expiry:
            await interaction.response.send_message(f"❌ Invalid duration format: `{duration}` (use 1D | 2H | 30M | 1D2H30M)", ephemeral=True )
            return

        Query.insert_activity(guild.id, event, expiry)

        notify = discord.Embed(title='📌 A new activity has been added!', description=f'**{event}** — expires in `{duration}`', color=discord.Color.dark_green())
        await config["get"].send('⟣┄ˑ◌ @everyone! \n ', embed=notify)
        await interaction.response.send_message("✅ Activity added successfully!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot))
