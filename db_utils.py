from tinydb import TinyDB, Query

db = TinyDB("database.json")
collection = db.table("users")
QUERY = Query()

def user_exists(discord_id: int) -> bool:
    """
    Checks if a user exists in the database based on their Discord ID.

    Parameters:
    -----------
    discord_id : int or str
        The Discord user ID to check.

    Returns:
    --------
    bool
        True if the user exists, False otherwise.
    """
    return get_user(QUERY.discord_id==discord_id) is not None

def insert_user(username, discord_id):
    """
    Inserts a new user into the database. Does nothing if the user already exists.
    Parameters:
    -----------
    username : str
        The user's Discord username (not their full tag).
    discord_id : int or str
        The user's Discord ID.
    """
    if not user_exists(discord_id):
        collection.insert(
            {"username": username, 
             "discord_id": discord_id
            },
        )

def update_user(discord_id: int, new_data: dict):
    """
    Updates user data for a given Discord ID.

    Parameters:
    -----------
    discord_id : int or str
        The user's Discord ID to locate the document.
    new_data : dict
        A dictionary containing the fields to update.
        Example: {"username": "NewName", "minecraft": True}
    """

    if user_exists(discord_id):
        collection.update(new_data, QUERY.discord_id == discord_id)

def get_user(query: Query):
    """
    Retrieves user documents from the database by query.

    Parameters:
    -----------
    query : str
        The query.

    Returns:
    --------
    dict or None
        The user document if found, otherwise None.
    """
    return collection.get(query)

def delete_user(username):
    """
    Deletes a user from the database by their username.

    Parameters:
    -----------
    username : str
        The username of the user to delete.

    Returns:
    --------
    list of int
        List of removed document IDs.
    """
    return collection.remove(QUERY.username == username)

def get_users(is_sorted:bool = False):
    """
    Retrieves a list of users from the database.

    Parameters:
    -----------
    is_sorted : bool
        Sorting the data before returning.

    Returns:
    --------
    list of dict
        A list of user documents.
    """
    if is_sorted:
        return sorted(collection.all(), key=lambda user: user.get("username", "").lower())
    
    return collection.all()

def link_minecraft(discord_id:int, minecraft_username:str, minecraft_password:str):
    """
    Links a minecraft account to an existing discord account

    Parameters:
    -----------
    discord_id : int
        Discord ID of the account that will be linked to the given minecraft account.
    minecraft_username : str
        Username of the minecraft account.
    minecraft_pasword : str
        Hashed password.
    """
    data = {"minecraft":{
                "username": minecraft_username,
                "password": minecraft_password,
                "linked": True,
                }
            }
    update_user(discord_id, data)