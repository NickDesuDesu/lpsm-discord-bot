from discord.ext.commands import Cog, check
from discord.ext.commands import command, Context
from discord import Embed, Member

from asyncio import TimeoutError

from db_utils import get_users, insert_user, get_user, QUERY
from utils import create_embed, format_table, get_user_from_target
from main import OWNER_IDS, ADMINS

class DatabaseCog(Cog, name="Database"):
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        super().__init__()

    def is_allowed_user():
        async def predicate(ctx):
            return ctx.author.id in OWNER_IDS or ctx.author.id in ADMINS
        return check(predicate)
    
    @command(
        name="add",
        help="Add a user to the database (admin only).",
        description="Adds a Discord user to the database by mention, username, or ID. Admin only."
    )
    @is_allowed_user()
    async def add_user(self, ctx: Context, target):
        user = None

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            user = await get_user_from_target(self.bot, target)

        if target == None:
            await ctx.send("❌ Invalid command usage. Please use a mention, username, or ID.", delete_after=120)
            return

        if user is None:
            await ctx.send("❌ Couldn't find user by that input. Please use a mention, username, or ID.", delete_after=120)
            return

        insert_user(user.name, user.id)
        await ctx.send(f"✅ Added **{user.name}** to the database~!", delete_after=120)

    @command(
        name="list",
        help="List users from the database.",
        description="Lists users from the database. Use '!list' for all users or '!list mc' for Minecraft-linked users.",
        usage="+list"
    )
    async def list_users_command(self, ctx, type:str = None):

        all_users = get_user(QUERY.minecraft.exists()) if type in ["mc", "minecraft"] else get_users(True)

        if not all_users:
            await ctx.send("No users found.", delete_after=120)
            return
        
        users_per_page = 10
        pages = [all_users[i:i + users_per_page] for i in range(0, len(all_users), users_per_page)]
        total_pages = len(pages)
        current_page = 0

        def get_page_embed(index: int):
            page_users = pages[index]
            table = format_table(
                ["#", "Username", "MC Username"],
                [[
                    i + 1 + (index * users_per_page),
                    user['username'],
                    user.get('minecraft', {}).get("username", "N/A")
                ] for i, user in enumerate(page_users)],
                spacing=3
            )
            embed = create_embed(
                title=f"📋 User List (Page {index + 1}/{total_pages})",
                description=table,
                footer="Requested by " + ctx.author.name
            )
            return embed

        message = await ctx.send(embed=get_page_embed(current_page), delete_after=120)

        if total_pages == 1:
            return 

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return (
                user == ctx.author and
                reaction.message.id == message.id and
                str(reaction.emoji) in ["⬅️", "➡️"]
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction, user)

                if str(reaction.emoji) == "➡️":
                    current_page = (current_page + 1) % total_pages
                elif str(reaction.emoji) == "⬅️":
                    current_page = (current_page - 1) % total_pages

                await message.edit(embed=get_page_embed(current_page))

            except TimeoutError:
                try:
                    await message.clear_reactions()
                except Exception:
                    pass
                break
    
    @Cog.listener()
    async def on_ready(self):
        cog_name = __name__.split(".")[-1]
        self.log.info("   |-" + cog_name + " cog ready")
        await self.bot.mark_cog_ready(cog_name)

async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))