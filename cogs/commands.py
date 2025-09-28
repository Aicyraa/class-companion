import discord
import re
from discord.ext import commands
from utils.sql_func import Query


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

        embed = discord.Embed(
            title="📍 Class Companion Commands",
            description="""Use the `//` prefix before the command """,
            color=discord.Colour.og_blurple(),
        )
        embed.set_footer(text="Class Companion", icon_url=self.bot.user.avatar)
        embed.add_field(name="", value="`schedule`", inline=True)
        embed.add_field(name="", value="`viewSchedule`", inline=True)
        embed.add_field(name="", value="`updateSchedule`", inline=True)
        embed.add_field(name="", value="`setActivty`", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def schedule(self, ctx, *args):  # for schedule command

        if ctx.guild is not None:
            embed = discord.Embed(
                title=f"{ctx.author.display_name or ctx.author.name}",
                description=f"A message has been sent to you!",
                color=discord.Colour.og_blurple(),
            )
            await ctx.send(embed=embed)

        if not args or len(args) < 2:
            embed = discord.Embed(
                title="🗺️ Schedule Command Guide",
                description="**⟣┄ˑ◌ The command `schedule` should be followed by the User Schedule in `DST` format. `NOTE`, you can add multiple schedule separated with space**",
                color=discord.Colour.og_blurple(),
            )
            embed.set_thumbnail(url=self.bot.user.avatar)
            embed.add_field(name="", value="`𖥔 Day`:  ( Monday - Saturday )", inline=False)
            embed.add_field(name="", value=" `𖥔 Subject`:  Users Subject for that day", inline=False)
            embed.add_field(name="",value="`𖥔 Time`:  12-Hour AM/PM format e.g (1PM || 1AM)",inline=False,)
            await ctx.author.send(embed=embed)
            return

        schedule_set = discord.Embed(title="⌛ Schedule is set!", color=discord.Colour.og_blurple())

        for i in range(0, len(args), 3):
            userSchedule = args[i : i + 3]

            if (
                userSchedule[0].lower()
                not in (
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                )
                or len(userSchedule) < 3
            ):
                await ctx.send(
                    f"Invalid format! Check your format length or text! {len(userSchedule)} || {userSchedule[0]}"
                )
                continue
            elif not re.match( r"^(1[0-2]|0?[1-9])(AM|PM)$", userSchedule[2], re.IGNORECASE):
                await ctx.send(f"Invalid time format: `{userSchedule[2]}`. Use like `1PM`, `11AM`.")
                continue
            else:
                Query.insert_schedule(ctx, userSchedule)
                day, subj, time = userSchedule
                schedule_set.add_field(name="", value=f"`𖥔 {day.upper()}`:  {subj},  {time}", inline=False)

        await ctx.author.send(embed=schedule_set)

    @commands.command
    async def viewSchedule(self):
        pass

    @commands.command
    async def updateSchedule(self):
        pass

    @commands.command()
    @commands.has_permissions(
        administrator=True, manage_channels=True, manage_guild=True
    )
    async def activity(self, ctx, *message):  # for sever owner or admins

        config = {
            "name": "《🔔》event-schedule",
            "permission": {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    view_channel=True, send_messages=False
                )
            },
            "get": discord.utils.get(ctx.guild.text_channels, name="《🔔》event-schedule"),
            "id": None,
        }

        if not config["get"]:  # for creating the channel
            channel = await ctx.guild.create_text_channel(
                name=config["name"], overwrites=config["permission"]
            )
            config["id"] = channel.id
            await ctx.send(f'{config["name"]} is created!', delete_after=100)
            return

        if len(message) < 2:  # Needs event + duration
            await ctx.send('❌ Invalid parameters! Usage: `//activity "Event Name" 1H`')
            return
    
        duration = message[-1]         # Example: "1H"
        event = " ".join(message[:-1]) # Example: "Math Homework"

        # --- CONVERT TO EXPIRY ---
        expiry = self.convert_to_expiry(duration)
        if not expiry:
            await ctx.send(f"❌ Invalid duration format: `{duration}` (use 1D, 2H, 30M)")
            return

        Query.insert_activity(ctx.guild.id, event=event, expiry=expiry)

async def setup(bot):
    await bot.add_cog(Commands(bot))
