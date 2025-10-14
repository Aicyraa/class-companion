import discord
import re
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from utils.sql_func_helpers import Query
from utils.time_converter import Time_Converter as tc
from utils.embed_helper import make_embed


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

    @app_commands.command(name="show_command", description="For displaying the available commands")
    async def showCmd(self, interaction: discord.Interaction):

        guide = make_embed(
            self.bot,
            title="📍 Class Companion Commands",
            description="Use the `//` prefix before the command",
            color=discord.Color.blurple()
        )

        guide.add_field(name="`schedule`", value='> followed by schedule\n> **//schedule Day Event Time**', inline=False)
        guide.add_field(name="`view`", value='> to view current schedule', inline=False)
        guide.add_field(name="`update`", value='> to update\n> **//update (old) Day Event Time - (new) Day Event Time**', inline=False)
        guide.add_field(name="`delete`", value='> to delete\n> **//delete Day Event Time**', inline=False)
        guide.add_field(name="`activity`", value='> create a new activity reminder\n> **/activity event:Text duration:1D | 1H | 10M | 1D1H10M**', inline=False)
        guide.add_field(name="`quiz`", value='> convert file to quiz', inline=False)

        await interaction.response.send_message(embed=guide, delete_after=1200)

    @commands.command()
    async def schedule(self, ctx, *args):
        if ctx.guild is not None:
            notify = make_embed(self.bot, title=f"{ctx.author.display_name or ctx.author.name}", description="A message has been sent to you!", color=discord.Color.og_blurple())
            await ctx.send(embed=notify, delete_after=1200)

        if not args or len(args) < 2:
            guide = make_embed(
                self.bot,
                "🗺️ Schedule Command Guide",
                "**⟣ˑ◌ The command `schedule` should be followed by your schedule in `DST` format. "
                "You can add multiple schedules separated by space.**\n\n"
                "`𖥔 Day`: (Monday - Sunday)\n`𖥔 Subject`: your subject for that day\n"
                "`𖥔 Time`: 12-hour AM/PM format (e.g. 1PM | 1:35PM)",
                color=discord.Color.og_blurple()
            )
            guide.set_thumbnail(url=self.bot.user.avatar)
            await ctx.author.send(embed=guide, delete_after=3600)
            return

        lines = []

        for i in range(0, len(args), 3):
            userSchedule = args[i:i + 3]

            if len(userSchedule) < 3 or userSchedule[0].lower() not in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
                await ctx.author.send(f"❌ Invalid format! Check your text format or text length! {len(userSchedule)} || {userSchedule[0] if userSchedule else 'N/A'}", delete_after=60)
                continue

            if not re.match(r"^(0?[1-9]|1[0-2])(:[0-5][0-9])?(AM|PM)$", userSchedule[2].strip().upper()):
                await ctx.author.send( f"❌ Invalid time format: `{userSchedule[2]}`. Use `1PM`, `1:00PM`, or `11:30PM`.", delete_after=60)
                continue

            Query.insert_schedule(ctx.author.id, userSchedule)
            day, subj, time = userSchedule
            lines.append(f'𖥔 {day.upper()}:  **{subj}**\n> Time:  **{time}** \n')

        if lines:
            schedule_set = make_embed(self.bot, "⟣┄─ ⌛ Schedule is set!", lines, discord.Color.og_blurple())
            await ctx.author.send(embed=schedule_set, delete_after=3600)
      
    @commands.command()
    async def view(self, ctx):
        schedule = Query.fetch(ctx.author.id)

        for day, events in schedule.items():
            view = make_embed(self.bot, f'⟣┄─⟣┄─ **{day}** ┄─⟣┄─⟣', [f"**{event}**" for event in events], discord.Color.dark_gold())
            await ctx.send(embed=view, delete_after=1200)

    @commands.command()
    async def update(self, ctx, *args):
        if not args or len(args) < 2:
            guide = make_embed(
                self.bot,
                "🗺️ Update Command Guide",
                "**⟣ˑ◌ The command `update` should be followed by `(OLD) DET - DET (NEW)` format.**\n\n"
                "`𖥔 Day Event Time`",
                color=discord.Color.og_blurple()
            )
            guide.set_thumbnail(url=self.bot.user.avatar)
            await ctx.send(embed=guide, delete_after=1200)
            return

        joined_args = " ".join(args)
        if " - " not in joined_args:
            error = make_embed(self.bot, "⟣┄─ ૮ Error: Invalid format! ❌", '', discord.Color.dark_red())
            await ctx.send(embed=error, delete_after=1200)
            return

        old, new = joined_args.split(" - ", 1)
        result = Query.edit(ctx.author.id, old.split(), new.split())

        if result:
            notify = make_embed(self.bot, "⟣┄─ ૮ Successfully Updated! ✅", f'> {" ".join(args)}', discord.Color.dark_green())
            await ctx.send(embed=notify, delete_after=1200)
        else:
            error = make_embed("⟣┄─ ૮ Error while updating! ❌", "Schedule does not match anything!", discord.Color.dark_red())
            await ctx.send(embed=error, delete_after=1200)

    @commands.command()
    async def delete(self, ctx, *args):
        if not args or len(args) < 3:
            guide = make_embed(
                self.bot,
                "🗺️ Delete Command Guide",
                "**⟣ˑ◌ The command `delete` should be followed by the User Schedule in `DET` format.**\n\n"
                "`𖥔 Day Event Time`",
                color=discord.Color.og_blurple()
            )
            guide.set_thumbnail(url=self.bot.user.avatar)
            await ctx.send(embed=guide, delete_after=1200)
            return

        result = Query.delete(ctx.author.id, args[0], args[1], tc.convert_to_24(args[2]))

        if result:
            success = make_embed(self.bot, "⟣┄─ ૮ Successfully deleted! ✅", f'> {args[0]} - {args[1]} - {args[2]}', discord.Color.dark_green())
            await ctx.send(embed=success, delete_after=1200)
        else:
            error = make_embed(self.bot, "⟣┄─ ૮ Error while deleting! ❌", "Schedule does not match anything!", discord.Color.dark_red())
            await ctx.send(embed=error, delete_after=1200)

    @app_commands.command(name='activity', description='Add an activity : /activity event:text duration: 1D | 2H | 30M | 1D2H30M')
    @app_commands.checks.has_permissions(administrator=True)
    async def activity(self, interaction: discord.Interaction, event: str, duration: str):
        guild = interaction.guild
        channel_name = "《🔔》presentation-event-schedule"
        event_channel = discord.utils.get(guild.text_channels, name=channel_name)

        # Defer immediately — gives you more control over follow-ups later
        await interaction.response.defer(ephemeral=True)

        if not event_channel:
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
            event_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
            await interaction.followup.send(f'📌 {channel_name} channel created!', ephemeral=True)

        expiry = tc.convert_to_expiry(duration)
        if not expiry:
            await interaction.followup.send(f"❌ Invalid duration format: `{duration}`. Use 1D | 2H | 30M | 1D2H30M", ephemeral=True)
            return

        Query.insert_activity(guild.id, event, expiry)

        notify = make_embed(
            self.bot,
            "📌 A new activity has been added!",
            f'**{event}** — expires in `{duration}`',
            discord.Color.dark_green(),
        )

        # Use the new channel after confirming it exists
        await event_channel.send('@everyone', embed=notify, delete_after=86400)
        await interaction.followup.send("✅ Activity added successfully!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Commands(bot))
