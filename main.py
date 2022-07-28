import config
import code_creator
import msg
import datetime
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from pymongo import MongoClient
from telethon.sync import TelegramClient, events
from telethon import Button
from telethon.tl.functions.channels import GetFullChannelRequest
api_id = 86576
api_hash = '385886b58b21b7f3762e1cde2d651925'
bot_token = config.read("telegram", "bot_token")

bot = TelegramClient('bot', api_id, api_hash, proxy=('socks5', '127.0.0.1', 1080))
bot.start(bot_token=bot_token)

mongo_client = MongoClient('127.0.0.1:27017')
db = mongo_client.user


@bot.on(events.NewMessage())
async def h(event):
    print(event.message)


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    z = event.message.peer_id.user_id
    t = datetime.datetime.now()
    code_3 = code_creator.code()
    try:
        db.users.insert_one({
            "_id": z,
            "coin": 0,
            "registration_date": t,
            "code": code_3,
        })
    except:
        pass
    keyboard = [
        [
            Button.inline(str(msg.read_msg('connect')), b'1'),
            Button.inline(str(msg.read_msg("create")), b"2"),
        ],
        [
            Button.inline(msg.read_msg("show"), b"3"),
            Button.inline(msg.read_msg("settings"), b"4")
        ],
        [
            Button.inline(msg.read_msg("buy coins"), b"5"),
            Button.inline(msg.read_msg("help"), b"6")
        ]
    ]

    await bot.send_message(z, msg.read_msg('Introduction'), buttons=keyboard)


@bot.on(events.NewMessage(pattern="code:*"))
async def code(event):
    global owner
    join_date = datetime.datetime.now()
    message_text = event.message.message

    if type(event.message.peer_id) == PeerChannel:
        chat_type = 'channel'
        peer_id = event.message.peer_id.channel_id
    elif type(event.message.peer_id) == PeerChat:
        chat_type = 'group'
        peer_id = event.message.peer_id.chat_id
    elif type(event.message.peer_id) == PeerUser:
        chat_type = 'user'
        peer_id = event.message.peer_id.user_id
    else:
        chat_type = None
        peer_id = 0

    if chat_type == 'group' or chat_type == 'channel':
        pass
    else:
        await bot.send_message(peer_id, msg.read_msg('Error location'))

    code_user = message_text
    try:
        find = db.users.find_one({
            'code': code_user
        })
        owner = find.get('_id')
    except:
        await bot.send_message(peer_id, msg.read_msg('code error'))
        return

    connection = await bot.get_entity(event.message.peer_id)
    full_info = await bot(GetFullChannelRequest(connection))
    chat_title = full_info.chats[0].title
    chat_info = full_info.full_chat.about
    chat_members = full_info.full_chat.participants_count
    try:
        db.connections.insert_one({
            '_id': peer_id,
            'owner': owner,
            'title': chat_title,
            'type': chat_type,
            'join_date': join_date,
            'members': chat_members,
            'status': 'active',
            'info': chat_info
        })
        print('ok')
    except:
        print('error')


@bot.on(events.CallbackQuery())
async def handler(event):
    find = db.users.find_one({'_id': event.original_update.user_id})
    code_2 = find.get('code')
    if event.data == b'1':
        z = event.original_update.user_id
        await bot.send_message(z, msg.read_msg('code'))
        await bot.send_message(z, code_2)
    else:
        pass


def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
