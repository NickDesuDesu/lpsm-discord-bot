from discord.ext.commands import Cog, command

from utils import create_embed

class GeneralCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        super().__init__()
    
    @command(
        name="about",
        help="About the Let's Play Server Manager bot.",
        description="Shows information about the bot, its features, and links to the source code."
    )
    async def about(self, ctx):
        embed = create_embed(
            title="💖 Let's Play Server Manager (LPSM) » Info",
            description=
                """Hiya~! I'm your friendly server assistant here to help manage the Let's Play's Game servers! ✨\n
                **What I do:**\n
                • Start and monitor the server automatically 🛠️\n
                • Let users register securely using their Discord identity 🔐\n
                • Auto-shutdown the server when it's inactive ⏲️\n
                **Security:**\n
                Your passwords are *securely hashed and never stored in plain text.* 🔒\n
                Everything I do is open-source, so feel free to check the code and see for yourself~!"""
            ,
            fields=[
                ("📁 LPSAuth Forge (Minecraft Mod)", "[View on GitHub](https://github.com/NickDesuDesu/LPSAuth)", True),
                ("📁 LPSAuth Fabric(Minecraft Mod)" "[View on Github](https://github.com/NickDesuDesu/LPSAuth-Fabric-1.21.1)", True)
                ("🤖 LPSM (Discord Bot)", "[View on GitHub](https://github.com/NickDesuDesu/lpsm-discord-bot)", True)
            ],
            footer="*Bot lovingly created and maintained by NickXD 💻💖*",
            thumbnail_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None,
            author_name=ctx.guild.name if ctx.guild else None,
            author_icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None
        )

        await ctx.send(embed=embed, delete_after=120)


    @Cog.listener()
    async def on_ready(self):
        cog_name = __name__.split(".")[-1]
        self.log.info("   |-" + cog_name + " cog ready")
        await self.bot.mark_cog_ready(cog_name)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))