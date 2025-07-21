from tinymongo import TinyMongoClient

client = TinyMongoClient()
db = client.myauthdb

users = db.users  

def user_exists(discord_id) -> bool:
    return True if get_user_by_discord_id(discord_id) else False

def insert_user(username, discord_id):
    existing = users.find_one({"username": username})
    if existing:
        users.update({"_id": existing["_id"]}, {"username": username, "discord_id": discord_id})
    else:
        users.insert_one({"username": username, "discord_id": discord_id})

def get_user_by_discord_id(discord_id):
    user = users.find_one({"discord_id": discord_id})
    return user if user else None

def get_user_by_username(username):
    user = users.find_one({"username": username})
    return user if user else None

def delete_user(username):
    return users.delete_one({"username": username})

def list_users():
    return list(users.find({}))