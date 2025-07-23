from discord.ext.commands import Bot as BotBase
from discord import Intents

import logging
from pathlib import Path
from db_utils import user_exists, insert_user
from dotenv import load_dotenv
import os

load_dotenv()
PEPPER=os.getenv("PASSWORD_PEPPER")

PREFIX = "!"
OWNER_IDS = [295377538967142410]
ADMINS = []
SERVER_ID = 749234556577513492
MINECRAFT_CHANNEL = 1300647901311139921


class Bot(BotBase):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        self.ready = False
        self.cogs_ready = {}

        self.log = logging.getLogger("discord")

        super().__init__(intents=intents, command_prefix=PREFIX, owner_ids=OWNER_IDS)

    async def setup_hook(self):
        self.add_check(self.globally_block_dms)
        self.log.info("Initializing Cogs")

        cogs_dir = Path(__file__).parent / "cogs"
        cog_files = [p for p in cogs_dir.glob("*.py") if p.name != "__init__.py"]
        cog_modules = [f"cogs.{p.stem}" for p in cog_files]
        
        for cog in cog_modules:
            self.log.info("{} cog loaded".format(cog.split(".")[-1]))
            self.cogs_ready[cog.split('.')[-1]] = False
            await self.load_extension(cog)

        self.log.info("All cogs loaded")

    async def mark_cog_ready(self, cog_name):
        self.cogs_ready[cog_name] = True
        if all(self.cogs_ready.values()) and not self.ready:
            self.ready = True
            self.log.info(f'Logged in as {self.user} ({self.user.id})')
            self.log.info("✅ Setup complete")


    def run(self):
        self.log.info("Starting Bot")

        self.token = os.getenv("DISCORD_API_KEY")
        super().run(self.token)

    async def on_ready(self):
        self.log.info("Syncing user database...")
        for guild in self.guilds:
            if guild.id == SERVER_ID:
                async for member in guild.fetch_members(limit=None):
                        if member.bot:
                            continue
                        if not user_exists(member.id):
                            insert_user(member.name, member.id)
                            self.log.info(f"   |-Added new user to DB: {member.name} ({member.id})")
        self.log.info("User database sync complete")

    async def globally_block_dms(self, ctx):
        return ctx.guild is not None
if __name__ == "__main__":
    bot = Bot()
    bot.run()