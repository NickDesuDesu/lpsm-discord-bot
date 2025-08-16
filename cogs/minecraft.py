from discord.ext.commands import Cog
from discord.ext.commands import command, check, cooldown, BucketType

from db_utils import get_user, QUERY

from utils import create_embed, format_table
import asyncio
from asyncrcon import AsyncRCON, AuthenticationException
import os
import re
import platform
import subprocess

from datetime import datetime

class MinecraftCog(Cog, name="MinecraftServer"):
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        self.empty_counter = 0
        self.shutdown_threshold = 5
        self.bot.loop.create_task(self.monitor_empty_server())
        super().__init__()

    @command(
        name="test",
        help="Shows bot info and version.",
        description="Displays information about the bot, including owner, version, and language."
    )
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
        await ctx.send(embed=embed, delete_after=120)
    
    async def run_rcon_async(self, command):
        rcon = AsyncRCON('localhost:25575', 'eduard32')
        try:
            await rcon.open_connection()
        except AuthenticationException:
            self.log.warning('Login failed: Unauthorized.')
            return
            
        res = await rcon.command(command)
        rcon.close()
        return res
    
    async def get_server_status(self, ctx):
        resp = await self.run_rcon_async("/forge tps")

        if resp.lower().startswith("unknown"):
            resp = await self.run_rcon_async("/fabric tps")
        
        pattern = re.compile(
            r"(?:(Dim minecraft:(?P<dimension>\w+))|(?P<overall>Overall))([^:]*:*\w*\): |(: ))Mean tick time: (?P<tick_time>[\d.]+) ms. Mean TPS: (?P<tps>[\d.]+)"
        )
        
        concat_resp = {}

        for match in pattern.finditer(resp):
            dim = match.group("dimension") or match.group("overall")
            tick_time = float(match.group("tick_time"))
            tps = float(match.group("tps"))
            concat_resp[dim] = {"tick_time": tick_time, "tps": tps}


        table = format_table(["Dimension", "Mean Tick Time", "Mean TPS"],
                                [[dim, stat["tick_time"], stat["tps"]] for dim, stat in concat_resp.items()])

        embed = create_embed(
            title="⛏️ Minecraft Server Status » Online 🟢",
            description=table,
            footer="Requested by " + ctx.author.name,
        )

        await ctx.send(embed=embed, delete_after=120)

    async def get_server_players(self, ctx):
        resp = await self.run_rcon_async("/list")

        pattern = re.compile(
            r"There are (?P<current>\d+) of a max of (?P<max>\d+) players online:(?P<names>.*)"
        )
        
        concat_resp = {}
        match = pattern.search(resp)
        if match:
            concat_resp["current"] = int(match.group("current"))
            concat_resp["max"] = int(match.group("max"))
            concat_resp["players"] = [s.strip() for s in match.group("names").split(",")] if len(match.group("names")) > 1 else match.group("names").strip()

        users = []
        for player in concat_resp["players"]:
            user = get_user(QUERY.minecraft.username==player)

            if user:
                users.append([player, user.get("username")])
            else:
                users.append([player, "Unregistered"])

        table = format_table(["Minecraft Username", "Discord Username"], users)
        
        embed = create_embed(
            title=f"⛏️ Minecraft Server Players » ({concat_resp['current']}/{concat_resp['max']})👤",
            description=table,
            footer="Requested by " + ctx.author.name,
        )

        await ctx.send(embed=embed, delete_after=120)

    async def get_server_info(self, ctx):
        from discord import Embed

        server_name = os.getenv("SERVER_NAME", "Unknown Server")
        server_domain = os.getenv("SERVER_DOMAIN", "Unknown Domain")
        server_version = os.getenv("SERVER_VERSION", "Unknown Version")
        mod_loader = os.getenv("MOD_LOADER", "Unknown Loader")

        is_online = True
        try:
            await self.run_rcon_async("/list")
        except:
            is_online = False

        embed = create_embed(
            title="🌐 Minecraft Server Info",
            description="Here is the current server setup and status:",
            fields=[
                ("Server Name", server_name, True),
                ("Server Domain", server_domain, True),
                ("Version", server_version, True),
                ("Mod Loader", mod_loader, True),
                ("Modpack Download", f"[Click here]({os.getenv('MODPACK_URL')})", True),
                ("Status", "🟢 Online" if is_online else "🔴 Offline", False),
            ],
            footer="Requested by " + ctx.author.name
        )

        await ctx.send(embed=embed, delete_after=120)

    @command(
        name="mcs",
        help="Check Minecraft server status, players, or info.",
        description="Usage: !mcs <status|players|info>. Shows server TPS, online players, or server info."
    )
    async def rcon(self, ctx, *args):
        if not args:
            await ctx.send("Please specify what you want to check: `status`, `players`, or `info`", delete_after=120)
            return

        subcommand = args[0].lower()

        try:
            match subcommand:
                case "status": 
                    await self.get_server_status(ctx)
                case "players":
                    await self.get_server_players(ctx)
                case "info":
                    await self.get_server_info(ctx)
                case _:
                    await ctx.send("Please specify what you want to check: `status` or `players`", delete_after=120)
        except:
            await ctx.send("Server is offline", delete_after=20)

    @command(
        name="infome",
        help="Shows your Discord info for Minecraft registration.",
        description="Displays your Discord username, display name, and user ID for Minecraft server registration."
    )
    async def infome(self, ctx):
        user = ctx.author
        member = ctx.guild.get_member(user.id)

        embed = create_embed(
            title="Your Info 💖",
            description="Here's what I know about you~\n***You can use the details below as your discord identifier for registering in the minecraft server.***",
            fields=[
                ("Username", f"{user}", True),
                ("Display Name", f"{member.display_name if member else user.display_name}", True),
                ("User ID", f"{user.id}", True),
            ],
            footer="Requested by " + user.name,
            thumbnail_url=user.avatar.url if user.avatar else None,
            author_name=ctx.guild.name if ctx.guild else None,
            author_icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None
        )

        await ctx.send(embed=embed, delete_after=120)

    def has_role_id(role_id):
        async def predicate(ctx):
            return any(role.id == role_id for role in ctx.author.roles)
        return check(predicate)

    @has_role_id(1301513812196855848) 
    @command(
        name="mcserverstart",
        help="Start the Minecraft server (Must Have @cobblemon role).",
        description="Starts the Minecraft server if it is offline. Requires admin role."
    )
    @cooldown(1, 60, BucketType.default) 
    async def startserver(self, ctx):
        server_path = os.getenv("SERVER_PATH")
        try:
            await self.run_rcon_async("/forge tps")

            await ctx.send("**🟢 Server is already online 🟢**", delete_after=120)
        except:
            try:
                if not server_path or not os.path.isfile(server_path):
                    await ctx.send("❌ Invalid or missing server path in `.env` file.", delete_after=120)
                    return

                server_dir = os.path.dirname(server_path)

                if platform.system() == "Windows":
                    subprocess.Popen(["cmd", "/c", "start", "", server_path], cwd=server_dir, shell=True)
                else:
                    subprocess.Popen(
                        f"tmux new-session -d -s mcserver 'bash \"{server_path}\"'",
                        cwd=server_dir,
                        shell=True,
                        executable="/bin/bash"
                    )

                await ctx.send("✅ Server start command executed.", delete_after=120)
            except Exception as e:
                await ctx.send(f"❌ Failed to start server: `{str(e)}`", delete_after=120)
        
    async def monitor_empty_server(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                resp = await self.run_rcon_async("/list")
                pattern = re.compile(
                    r"There are (?P<current>\d+) of a max of (?P<max>\d+) players online:(?P<names>.*)"
                )
                match = pattern.search(resp)
                if match:
                    current_players = int(match.group("current"))
                    if current_players == 0:
                        self.empty_counter += 1
                        self.log.info(f"No players online. Idle counter: {self.empty_counter}/{self.shutdown_threshold}")
                        
                        if self.empty_counter == 4:
                            channel = self.bot.get_channel(1300647901311139921)
                            if channel:
                                await channel.send("🛑 Shutting down the server in **1 minute** due to inactivity...", delete_after=60)
                    else:
                        self.empty_counter = 0

                    if self.empty_counter >= self.shutdown_threshold:
                        self.log.info("No players for 5 minutes. Shutting down server.")
                        await self.run_rcon_async("/say [LPSM] Shutting down in 10 seconds due to inactivity. This can not be cancelled.")
                        await asyncio.sleep(10)
                        await self.run_rcon_async("/stop")
                        channel = self.bot.get_channel(1300647901311139921)
                        if channel:
                            await channel.send("🛑 Server Offline... 🛑", delete_after=120)

                        self.empty_counter = 0  
                        
            except Exception as e:
                self.empty_counter = 0 

            await asyncio.sleep(60)

    async def cog_after_invoke(self, ctx):
        args = ctx.args[2:]
        kwargs = ctx.kwargs

        args_list = [str(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()]
        args_str = ", ".join(args_list) if args_list else "None"
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        embed = create_embed(
            title="📜 Command Executed",
            fields=[
                ("Command", f"`{ctx.command}`", False),
                ("Parameters", args_str, False),
                ("User", f"{ctx.author} ({ctx.author.mention})", True),
                ("Channel", f"{ctx.channel.mention}", True),
                ("Datetime", now, False),
            ],
            footer="MinecraftCog Logger"
        )

        channel = self.bot.get_channel(1406101545363308582)
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        cog_name = __name__.split(".")[-1]
        self.log.info("   |-" + cog_name + " cog ready")
        await self.bot.mark_cog_ready(cog_name)

async def setup(bot):
    await bot.add_cog(MinecraftCog(bot))