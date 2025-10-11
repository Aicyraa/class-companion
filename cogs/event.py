from discord.ext import commands

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.synced = False  # flag to prevent double-syncing
        
    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self, "synced"):
            self.synced = False

        if not self.synced:  # only sync once
            await self.bot.tree.sync()
            self.synced = True

        print(f"{self.bot.user} is now online and slash commands are synced!")
        
async def setup(bot):
    await bot.add_cog(Event(bot))