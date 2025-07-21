from discord.ext.commands import Bot as BotBase
from discord import Intents

import logging
from pathlib import Path


PREFIX = "+"
OWNER_IDS = ["295377538967142410"]


class Bot(BotBase):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        self.ready = False

        self.log = logging.getLogger("discord")

        super().__init__(intents=intents, command_prefix=PREFIX, owner_ids=OWNER_IDS)

    async def setup_hook(self):
        self.log.info("Initializing Cogs")

        cogs_dir = Path(__file__).parent / "cogs"
        cog_files = [p for p in cogs_dir.glob("*.py") if p.name != "__init__.py"]
        cog_modules = [f"cogs.{p.stem}" for p in cog_files]
        
        for cog in cog_modules:
            await self.load_extension(cog)

    def run(self):
        self.log.info("Starting Bot")

        with open("token.0", "r", encoding="UTF-8") as token:
            self.token = token.read()

        super().run(self.token)

    async def on_ready(self):
        self.log.info(f'Logged in as {self.user}')


if __name__ == "__main__":
    bot = Bot()
    bot.run()