from discord.ext import commands

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='q')
    async def quiz(self):
        print('working...')

    @staticmethod
    def extract():
        pass
            


async def setup(bot):
    await bot.add_cog(Quiz(bot))