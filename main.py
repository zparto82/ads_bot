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
    # 1562095035
    # 1778853564
    pass


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
            Button.inline(str(msg.read_msg('connect')), b'connect'),
            Button.inline(str(msg.read_msg("create")), b"create"),
        ],
        [
            Button.inline(msg.read_msg("show"), b"show"),
            Button.inline(msg.read_msg("settings"), b"settings")
        ],
        [
            Button.inline(msg.read_msg("buy coins"), b"buy coins"),
            Button.inline(msg.read_msg("help"), b"help")
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
        return

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
    if event.data == b'connect':
        user_id = event.original_update.user_id
        await bot.send_message(user_id,msg.read_msg('join'))
        await bot.send_message(user_id, msg.read_msg('code'))
        await bot.send_message(user_id, code_2)
    elif event.data == b'create':

        user_id = event.original_update.user_id
        async with bot.conversation(user_id) as conv:
            msg1 = await conv.send_message(msg.read_msg('ads_text'))
            text = await conv.get_response(timeout=1000000000)
            ads_text = text.message
            msg2 = await conv.send_message(msg.read_msg('ads_link'))
            link = await conv.get_response(timeout=10000000000)
            ads_link = link.message
        count = db.ads.count_documents(({"owner_id" : user_id}))
        print(count)
        ads_id = str(user_id) + str("_") + str(count)
        print(ads_id)
        try:
            db.ads.insert_one({
                "_id" : ads_id,
                "text" : ads_text,
                "link" : ads_link,
                "owner_id" : user_id
            })
            print('ok')
        except:
            print('error')


    elif event.data == b'show':
        user_id = event.original_update.user_id
        i = 0
        count = db.ads.count_documents(({"owner_id": user_id}))
        keyboard = [
            [
                Button.inline(msg.read_msg("select"),data=b'select')
            ]
        ]
        while i < count :
            count_2 = count-i
            ads_id = str(user_id) + str("_") + str(count_2)
            find = db.ads.find_one({
                '_id': ads_id
            })
            try:
                text = find.get('text')
                link = find.get('link')
                read = db.connections.find_one({
                    'owner' : user_id
                })
                chat_id = read.get('_id')
                if text is None:
                    text = msg.read_msg('text not found')
                else:
                    pass
                if link is None:
                    link = msg.read_msg('link not found')
                perfect_ads = f"{text}\n{link}"

                await bot.send_message(user_id, perfect_ads, buttons=keyboard)
            except:
                pass

            else:
                pass


            i = i + 1

    elif event.data == b'select':
        user_id = event.original_update.user_id
        async with bot.conversation(user_id) as conv:
            msg1 = await conv.send_message(msg.read_msg('how many coins'))
            text = await conv.get_response(timeout=1000000000)
            ads_text = text.message



    else:
        pass


def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
