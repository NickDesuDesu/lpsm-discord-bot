import discord
from typing import Optional, List, Tuple

from main import SERVER_ID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ARGON2 = PasswordHasher()

def create_embed(
        title: str,
        description: str = "",
        color: discord.Color = 0x87ceeb,
        fields: Optional[List[Tuple[str, str, bool]]] = None,  # (name, value, inline)
        footer: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        author_name: Optional[str] = None,
        author_icon_url: Optional[str] = None,
    ) -> discord.Embed:
    """
    Creates and returns a Discord Embed with optional customization.

    Parameters:
    ----------
    title : str
        The title of the embed (bold text at the top).
    description : str, optional
        The main body text of the embed.
    color : discord.Color, optional
        The color of the embed's sidebar. Defaults to discord.Color.blue().
    fields : list of tuples (str, str, bool), optional
        A list of fields to add. Each field should be a tuple in the format:
        (name, value, inline), where `inline` controls if it's side-by-side.
    footer : str, optional
        Text to show at the bottom of the embed.
    thumbnail_url : str, optional
        URL of an image to show in the top-right corner as a thumbnail.
    author_name : str, optional
        Text to show as the author of the embed.
    author_icon_url : str, optional
        URL of an icon to appear next to the author name.

    Returns:
    -------
    discord.Embed
        The fully constructed embed object, ready to be sent via ctx.send(embed=embed).

    Example:
    -------
    embed = create_embed(
        title="Hello!",
        description="This is an example embed.",
        fields=[("Field 1", "Some value", True)],
        footer="Requested by Nick",
        thumbnail_url="https://example.com/image.png",
        author_name="BotName",
        author_icon_url="https://example.com/icon.png"
    )
    await ctx.send(embed=embed)
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    if footer:
        embed.set_footer(text=footer)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    if author_name:
        embed.set_author(name=author_name, icon_url=author_icon_url or discord.Embed.Empty)

    return embed

def format_table(columns: list[str], rows: list[list], spacing: int = 2) -> str:
    """
    Formats a list of rows and column headers into a Discord-friendly table string
    using code block formatting. Automatically aligns text by column.

    Parameters:
    -----------
    columns : list of str
        The column headers (e.g., ["#", "Username", "Discord ID", "Minecraft"])
    rows : list of list
        The rows of data, where each sublist matches the columns order.

    Returns:
    --------
    str
        A string formatted as a code block representing the table.
    """
    col_widths = [len(col) for col in columns]

    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell)
            col_widths[i] = max(col_widths[i], len(cell_str))

    table = "```\n"

    header = (" " * spacing).join(f"{col:<{col_widths[i]}}" for i, col in enumerate(columns))
    table += header + "\n"

    divider = "-" * sum(col_widths) + ("-" * spacing) * (len(columns) - 1)
    table += divider + "\n"

    for row in rows:
        row_str = (" " * spacing).join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row))
        table += row_str + "\n"

    table += "```"
    return table

def get_guild(bot, guild_id):
    return bot.get_guild(guild_id)

async def get_user_from_target(bot, target):
        user = None

        if target.isdigit():
            id = int(target)
            for member in get_guild(bot, SERVER_ID).members:
                if member.id == id:
                    user = member
                    break
        else:
            for member in get_guild(bot, SERVER_ID).members:
                if member.name == target or member.display_name == target:
                    user = member
                    break
        return user

# METHODS FOR PASSOWRD HASHING
def hash_password(raw_password: str, pepper: str):
    combined = raw_password + pepper
    hash_value = ARGON2.hash(combined)
    
    return hash_value

def verify_password(input_password: str, stored_hash: str, pepper: str) -> bool:
    try:
        ARGON2.verify(stored_hash, input_password + pepper)
        return True
    except VerifyMismatchError:
        return False