import re
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters, Client, enums
from plugins.database import unpack_new_file_id
from clone_plugins.users_api import get_user, get_short_link
import base64

@Client.on_message(filters.command(['link', 'plink']))
async def gen_link_s(client: Client, message):
    replied = message.reply_to_message
    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')
    file_type = replied.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("Reply to a supported media")
    if message.has_protected_content:
        return await message.reply("okDa")

    
    file_id, ref = unpack_new_file_id((getattr(replied, file_type.value)).file_id)
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    # Get the bot's username
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={outstr}"
    short_link = await get_short_link(user, share_link)
    keyboard = [[InlineKeyboardButton("Original Link", url=share_link)]]
    if short_link:
        keyboard[0].insert(0, InlineKeyboardButton("Short Link", url=short_link))
        reply_text = f"╭━━❰ 𝗬𝗢𝗨𝗥 𝗟𝗜𝗡𝗞 𝗜𝗦 𝗥𝗘𝗔𝗗𝗬 ❱━━➣\n┣\n┣🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}\n┣\n┣\n┣🔗 sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n┣\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━➣"
    else:
        reply_text = f"╭━━❰ 𝗬𝗢𝗨𝗥 𝗟𝗜𝗡𝗞 𝗜𝗦 𝗥𝗘𝗔𝗗𝗬 ❱━━➣\n┣\n┣🔗 ᴏʀɪɢɪɴᴀʟ ʟᴏɴᴋ :- {share_link}\n┣\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━➣"
    await message.reply(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
  
