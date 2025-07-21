from discord.ext.commands import Cog
from discord.ext.commands import command

class MinecraftCog(Cog, name="MinecraftServer"):
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        super().__init__()

    @command(name="test")
    async def test(self, ctx):
        await ctx.send("Test Done")

    @Cog.listener()
    async def on_ready(self):
        self.log.info(__name__ + " ready")

async def setup(bot):
    await bot.add_cog(MinecraftCog(bot))