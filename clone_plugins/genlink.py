import re
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
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
    # Define the ascending part of the link
    ascending_start = 1  # Starting number for ascending link
    ascending_end = 10   # Ending number for ascending link
    for i in range(ascending_start, ascending_end + 1):
        # Create a unique string for each ascending link
        string = f'file_{i}_' if message.text.lower().strip() == "/plink" else f'filep_{i}_'
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
        else:
            keyboard[0].insert(0, InlineKeyboardButton("Copy Original Link", callback_data=f"copy_link:{share_link}"))
        await message.reply(f"╭━━❰ 𝗬𝗢𝗨𝗥 𝗟𝗜𝗡𝗞 𝗜𝗦 𝗥𝗘𝗔𝗗𝗬 ❱━━➣\n┣\n┣🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}\n┣\n┣🔗 sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n┣\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━➣", reply_markup=InlineKeyboardMarkup(keyboard))

@Client.on_callback_query(filters.regex(r'^copy_link:(.*)$'))
async def copy_link(client: Client, query: CallbackQuery):
    link = query.data.split(":")[1]
    await query.message.copy(chat_id=query.from_user.id, reply_markup=None, caption=f"🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ: {link}")
    await query.answer("Link copied!", show_alert=True)

