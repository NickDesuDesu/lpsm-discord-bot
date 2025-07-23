from discord.ext.commands import Cog
from discord.ext.commands import command

from utils import create_embed

class MinecraftCog(Cog, name="MinecraftServer"):
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        super().__init__()

    @command(name="test")
    async def test(self, ctx):
        embed = create_embed(
            title="Bot Info",
            description="This is a super cool bot 😎",
            fields=[
                ("Owner", "Nick", True),
                ("Version", "1.0", True),
                ("Language", "Python 🐍", False)
            ],
            footer="Requested by " + ctx.author.name,
            thumbnail_url=ctx.guild.icon.url if ctx.guild.icon else None,
            author_name=ctx.guild.name if ctx.guild else None,
            author_icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None
        )
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        cog_name = __name__.split(".")[-1]
        self.log.info("   |-" + cog_name + " cog ready")
        await self.bot.mark_cog_ready(cog_name)

async def setup(bot):
    await bot.add_cog(MinecraftCog(bot))