import discord
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True

token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='//', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello {message.author.mention}!')

    await bot.process_commands(message)


@bot.command()
async def showCmd(ctx):

    embed = discord.Embed(
        title="📍 Class Companion Commands",
        description='''Use the `//` prefix before the command ''',
        color=discord.Colour.og_blurple()
    )

    embed.set_footer(text="Class Companion", icon_url=bot.user.avatar)
    embed.add_field(name="", value="`schedule`", inline=True)
    embed.add_field(name="", value="`viewSchedule`", inline=True)
    embed.add_field(name="", value="`updateSchedule`", inline=True)
    embed.add_field(name="", value="`setActivty`", inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def schedule(ctx, *args):
    days = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday')

    if not args:
        embed = discord.Embed(title='Schedule Command Guide',
                              description='**⟣┄─ ˑ ◌ ִ The command `schedule` should be followed by the `User Schedule` in `DST` format.**',
                              color=discord.Colour.og_blurple())

        embed.set_thumbnail(url=bot.user.avatar)
        embed.add_field( name="", value="`𖥔 Day`:  ( Monday - Saturday )", inline=False)
        embed.add_field(name="", value=" 𖥔 Subject`:  Users Subject for that day", inline=False)
        embed.add_field(name="", value="`𖥔 Time`:  12-Hour AM/PM format", inline=False)

        await ctx.send(embed=embed)
        return

    if args[0].lower() not in days:
        await ctx.send(f'{ctx.author.mention}, invalid day text / format')
    else:
        day, subj, time = args
        embed = discord.Embed(title="⌛ Schdule is set successfuly!",
                              description=f"` 𖥔 {day.upper()}`: {subj},  {time} ",
                              color=discord.Colour.og_blurple())
        await ctx.send(embed=embed)

# @bot.command()


async def viewSchedule():
    pass

# @bot.command()


async def updateSchedule():
    pass

# @bot.command()


async def setActivity():
    pass

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
