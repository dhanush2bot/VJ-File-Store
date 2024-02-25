import re
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters, Client, enums
from plugins.database import unpack_new_file_id
from clone_plugins.users_api import get_user, get_short_link
import base64
from pymongo import MongoClient
from config import DB_URI as MONGO_URL

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["cloned_vjbotz"]


async def verupikkals(bot, message):
    id = bot.me.id
    owner = mongo_db.bots.find_one({'bot_id': id})
    ownerid = int(owner['user_id'])
    if ownerid != message.from_user.id:
        await message.reply_text("Only the bot owner can use this command.")
        return False
    return True

@Client.on_message(filters.private & filters.command(['passlink']))
async def process_password(client: Client, message):
    if not await verupikkals(client, message):
        return

    if message.reply_to_message and message.reply_to_message.from_user.id == client.get_me().id and len(message.command) > 1 and len(message.command[1]) > 3:
        password = message.command[1]
        await message.reply(f"The password has been set to: {password}")
    else:
        await message.reply('Please reply to the command "/passlink" to provide the password.')

@Client.on_message(filters.private & filters.command(['link', 'plink']))
async def gen_link_s(client: Client, message):
    replied = message.reply_to_message
    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')
    file_type = replied.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("Reply to a supported media")
    if message.has_protected_content:
        return await message.reply("okDa")

    password = None
    if len(message.command) > 1 and len(message.command[1]) > 3:
        password = message.command[1]

    file_id, ref = unpack_new_file_id((getattr(replied, file_type.value)).file_id)
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={outstr}"
    short_link = await get_short_link(user, share_link)

    keyboard = [[InlineKeyboardButton("Original Link", url=share_link)]]
    if short_link:
        keyboard[0].insert(0, InlineKeyboardButton("Short Link", url=short_link))
    
    if password:
        share_link += f"&password={password}"
        reply_text = f"Password-protected link: {share_link}"
    else:
        reply_text = f"Shareable link: {share_link}"

    keyboard.append([InlineKeyboardButton("Copy Link", callback_data=f"copy_link:{share_link}")])
    
    await message.reply(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
