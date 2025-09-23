from discord.ext import commands

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} is now online!')
        
        
async def setup(bot):
    await bot.add_cog(Event(bot))
    