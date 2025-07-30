from discord.ext.commands import Cog
from aiohttp import web
import asyncio

from utils import get_user_from_target, create_embed, get_guild, hash_password, verify_password
from db_utils import get_user, link_minecraft, QUERY
from main import SERVER_ID, PEPPER
import time

class APICog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        self.app = web.Application()
        self.app.add_routes([
            web.post('/minecraft/verify', self.minecraft_verify_registration),
            web.post('/minecraft/register', self.minecraft_register),
            web.post('/minecraft/login', self.minecraft_login),
            web.get('/minecraft/user', self.minecraft_get_user)
        ])
        self.pending_registrations = {}
        self.registration_cleanup_tasks = {}

        self.runner = web.AppRunner(self.app)

    async def start_server(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', 8000)
        await site.start()
        
        self.log.info("   |-API server Running")

    async def minecraft_register(self, request):
        params = request.query

        minecraft_username = params.get("minecraft_username")
        discord_identifier = params.get("discord_identifier")
        password = params.get("password")
        otp = params.get("otp")

        if (not minecraft_username or
            not discord_identifier or
            not password or
            not otp):
            return web.json_response(
                {"error": "Missing parameters."},
                status=400
            )
        
        if self.pending_registrations.get(discord_identifier):
            return web.json_response(
                {"error": f"There is already an ongoing registration for {discord_identifier}."},
                status=403
            )

        user = await get_user_from_target(self.bot, discord_identifier)
        guild = get_guild(self.bot, SERVER_ID)
        

        if user:
            discord_entry = {} if get_user(QUERY.discord_id == int(user.id)) == None else get_user(QUERY.discord_id == int(user.id))
            minecraft_entry = {} if get_user(QUERY.minecraft.username == minecraft_username) == None else get_user(QUERY.minecraft.username == minecraft_username)

            if discord_entry.get("minecraft", {}).get("linked", False):
                return web.json_response(
                    {"error": f"There is already a minecraft account linked to {discord_identifier}."},
                    status=403
                )
            
            if minecraft_entry.get("minecraft", {}).get("linked", False):
                return web.json_response(
                    {"error": f"There is already a discord account linked to {minecraft_username}."},
                    status=403
            )
        
            embed = create_embed(
                title = "**🔑 Minecraft OTP 🔑**",
                description = "Use the OTP below to verify your account in Let's Play's Minecraft Server.",
                fields = [("OTP", otp, True)],
                footer = "This OTP will stop working after 3 minutes.",
                author_name=guild.name if guild else None,
                author_icon_url=guild.icon.url if guild and guild.icon else None
            )

            await user.send(embed=embed, delete_after=180)

            self.pending_registrations[discord_identifier] = {
                    "minecraft_username": minecraft_username,
                    "password": password,
                    "otp": otp,
                    "timestamp": time.time()
                }
            
            task = self.registration_cleanup_tasks.get(discord_identifier)
            if task:
                task.cancel()

            async def cleanup_registration():
                try:
                    await asyncio.sleep(60)
                    if discord_identifier in self.pending_registrations:
                        del self.pending_registrations[discord_identifier]
                        self.log.info(f"[Auto-Cleanup] Removed expired registration for {discord_identifier}")
                except asyncio.CancelledError:
                    pass

            cleanup_task = asyncio.create_task(cleanup_registration())
            self.registration_cleanup_tasks[discord_identifier] = cleanup_task


            return web.json_response(
                {
                    "message": "Registration request accepted. Waiting for Minecraft client confirmation."
                },
                status=202
            )
        else:
            return web.json_response(
                {
                    "error": "Discord account provided is not a member of the 'Let's Play' discord server. You must first join the discord server to create an account."
                },
                status=403
            )

    async def minecraft_verify_registration(self, request):
        params = request.query
        discord_identifier = params.get("discord_identifier")
        otp_confirmed = bool(params.get("otp_confirmed"))

        if not discord_identifier or not isinstance(otp_confirmed, bool) :
            return web.json_response(
                {"error": "Missing or invalid parameters."},
                status=400
            )

        registration = self.pending_registrations.get(discord_identifier)
        if not registration:
            return web.json_response(
                {"error": "No pending registration for this Discord user."},
                status=404
            )

        if otp_confirmed:
            mc_username = registration.get("minecraft_username")
            password = registration.get("password")

            user = await get_user_from_target(self.bot, discord_identifier)

            link_minecraft(user.id, 
                           mc_username, 
                           hash_password(password, PEPPER))
            
            self.log.info(f"Succesfully linked {mc_username} to {discord_identifier}")

            del self.pending_registrations[discord_identifier]

            return web.json_response(
                {"message": "Registration completed successfully."},
                status=201
            )
        else:
            del self.pending_registrations[discord_identifier]
            return web.json_response(
                {"error": "OTP was not confirmed. Registration cancelled."},
                status=403
            )

    async def minecraft_login(self, request):
        params = request.query

        minecraft_username = params.get("minecraft_username")
        password = params.get("password")

        if (not minecraft_username or not password):
            return web.json_response(
                {"error": "Missing parameters."},
                status=400
            )
        
        minecraft_entry = get_user(QUERY.minecraft.username==minecraft_username)

        if minecraft_entry:
            password_hash = minecraft_entry.get("minecraft", {}).get("password", None)

            if verify_password(password, password_hash, PEPPER):
                return web.json_response(
                    {"message": "Login Successful"},
                    status=200
                )

            return web.json_response(
                {"error": "Invalid credentials."},
                status=403
            )

        return web.json_response(
            {"error": "Non existent account"},
            status=404
        )

    async def minecraft_get_user(self, request):
        params = request.query

        minecraft_username = params.get("minecraft_username")

        if (not minecraft_username):
            return web.json_response(
                {"error": "Missing parameters."},
                status=400
            )
        
        minecraft_entry = get_user(QUERY.minecraft.username==minecraft_username)

        if minecraft_entry:
            return web.json_response(
                {"message": "Account exists."},
                status=200
            )
        else:
            return web.json_response(
                {"error": "Account does not exist."},
                status=404
            )
        

        

    def cog_unload(self):
        asyncio.create_task(self.runner.cleanup())

    @Cog.listener()
    async def on_ready(self):
        await self.bot.loop.create_task(self.start_server())

        cog_name = __name__.split(".")[-1]
        self.log.info("   |-" + cog_name + " cog ready")

        await self.bot.mark_cog_ready(cog_name)

async def setup(bot):
    await bot.add_cog(APICog(bot))