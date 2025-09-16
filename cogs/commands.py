import discord
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return
        
        await self.bot.process_commands(msg)
        
    @commands.command
    async def showCmd(ctx): # for sending a guide

        embed = discord.Embed( title="📍 Class Companion Commands", description='''Use the `//` prefix before the command ''',color=discord.Colour.og_blurple())
        embed.set_footer(text="Class Companion", icon_url=bot.user.avatar)
        embed.add_field(name="", value="`schedule`", inline=True)
        embed.add_field(name="", value="`viewSchedule`", inline=True)
        embed.add_field(name="", value="`updateSchedule`", inline=True)
        embed.add_field(name="", value="`setActivty`", inline=True)

        await ctx.send(embed=embed)
        
    @commands.command
    async def schedule(ctx, *args): # for schedule command

        if ctx.guild is not None:
            embed = discord.Embed(title=f"{ctx.author.display_name or ctx.author.name}",description=f"A message has been sent to you!", color=discord.Colour.og_blurple())
            await ctx.send(embed=embed)

        if not args:
            embed = discord.Embed(title='🗺️ Schedule Command Guide', description='**⟣┄ˑ◌ The command `schedule` should be followed by the User Schedule in `DST` format. `NOTE`, you can add multiple schedule separated with space**',color=discord.Colour.og_blurple())
            embed.set_thumbnail(url=bot.user.avatar)
            embed.add_field(name="", value="`𖥔 Day`:  ( Monday - Saturday )", inline=False)
            embed.add_field(name="", value=" `𖥔 Subject`:  Users Subject for that day", inline=False)
            embed.add_field(name="", value="`𖥔 Time`:  12-Hour AM/PM format", inline=False)
            await ctx.author.send(embed=embed)
            return

        schedule_set = discord.Embed(title="⌛ Schedule is set!", color=discord.Colour.og_blurple())
        for i in range(0, len(args), 3):
            userSchedule = args[i:i+3]
            if userSchedule[0].lower() not in ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'):
                await ctx.send(f'{ctx.author.mention}, invalid format! {userSchedule[0]}')
                break
            else:
                day, subj, time = userSchedule
                schedule_set.add_field(name="", value=f"`𖥔 {day.upper()}`:  {subj},  {time}", inline=False)

            await ctx.author.send(embed=schedule_set)

    @commands.command    
    async def viewSchedule():
        pass
    
    @commands.command
    async def updateSchedule():
        pass    

    @commands.command    
    async def setActivity(): # for sever owner or admins
        pass

async def setup(bot):
    await bot.add_cog(Commands(bot))