from discord.ext.commands import Cog
from discord.ext.commands import MissingRequiredArgument, CheckFailure

from utils import create_embed

class ErrorHandlerCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        super().__init__()

    # @Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        
        embed = create_embed(
            title="**❌ Error ❌**",
            footer="Requested by " + ctx.author.name,
        )

        if isinstance(error, MissingRequiredArgument):
            embed.description = "Missing Argument!"
            embed.add_field(name="Argument", value=str(error.param.name), inline=False)
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command} <{error.param.name}>`", inline=False)
            await ctx.send(embed=embed)

        if isinstance(error, CheckFailure):
            embed.description = "You can not use this command!"
            await ctx.send(embed=embed)

        else:
            embed.description = error.__class__.__name__
            embed.add_field(name="Error Message", value=f"❌ Error: {str(error)}", inline=False)
            await ctx.send(embed = embed)

    @Cog.listener()
    async def on_ready(self):
        cog_name = __name__.split(".")[-1]
        self.log.info("   |-" + cog_name + " cog ready")
        await self.bot.mark_cog_ready(cog_name)

async def setup(bot):
    await bot.add_cog(ErrorHandlerCog(bot))