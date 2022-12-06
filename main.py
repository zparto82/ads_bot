import pymongo

import coins
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
if config.read('telegram', 'proxy') == 'True':
    bot = TelegramClient('bot', api_id, api_hash, proxy=('socks5', '127.0.0.1', 1080))
else:
    bot = TelegramClient('bot', api_id, api_hash)
bot.start(bot_token=bot_token)
mongo_client = MongoClient('127.0.0.1:27017')
db = mongo_client.user


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.message.peer_id.user_id
    time = datetime.datetime.now()
    code_3 = code_creator.code()
    try:
        db.users.insert_one({
            "_id": user_id,
            "coin": 100,
            "registration_date": time,
            "code": code_3,
        })
    except:
        pass
    # keyboard = [
    #     [
    #         Button.inline(str(msg.read_msg('connect')), b'connect'),
    #         Button.inline(str(msg.read_msg("create")), b"create"),
    #     ],
    #     [
    #         Button.inline(msg.read_msg("show"), b"show"),
    #         Button.inline(msg.read_msg("settings"), b"settings")
    #     ],
    #     [
    #         Button.inline(msg.read_msg("buy coins"), b"buy coins"),
    #         Button.inline(msg.read_msg("help"), b"help")
    #     ],
    #     [
    #         Button.inline(msg.read_msg('menu'),b'menu')
    #     ]
    # ]
    keyboard2 = [
        [
            Button.inline(str(msg.read_msg('Advertiser_menu')), b'Advertiser_menu')
        ],
        [
            Button.inline(str(msg.read_msg('Ad_receiver_menu')), b'Ad_receiver_menu')
        ],
        [
            Button.inline(str(msg.read_msg('coin_management')), b'coin_management')
        ],
        [
            Button.inline(str(msg.read_msg('help')), b'help_in_home')
        ],
    ]
    await bot.send_message(user_id, msg.read_msg('Introduction'), buttons=keyboard2)


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
        await bot.send_message(peer_id, msg.read_msg('error_code'))
        return
    try:
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
            await bot.send_message(peer_id, msg.read_msg("Channel_added_successfully"))
        except:
            await bot.send_message(peer_id,msg.read_msg("This_channel/group_has_already_been_added"))
    except:
        pass

@bot.on(events.CallbackQuery(pattern='ad:*'))
async def ad_handler(event):
    post_id = event.original_update.msg_id
    ad_id = event.data.decode().split(':')[1]
    user_id = event.original_update.user_id
    async with bot.conversation(user_id, timeout=1000) as conv:
        is_coin_number = False
        while not is_coin_number:
            msg1 = await conv.send_message(msg.read_msg('how many coins'))
            quantity = await conv.get_response(timeout=1000)
            try:
                pending_coin = int(quantity.message)
                is_coin_number = True
            except:
                await bot.send_message(user_id,msg.read_msg('waring_number'))
        # check if user has enough coin
        find = db.users.find_one({'_id':user_id})
        coin = find.get('coin')
        if coin < pending_coin or pending_coin <= 0:
            await bot.send_message(user_id,msg.read_msg("don't_have_enough_coins"))
        else:
            # deduct coins from user's balance
            new_coin = coin-pending_coin
            update = db.users.update_one({'_id':user_id},{'$set':{'coin':new_coin}})

            # log coin change
            change_date = datetime.datetime.now()
            log_coin_change = coins.coin(user_id,-pending_coin,msg.read_msg('reason'),change_date,db)

            # insert into ad_pending
            try:
                insert = db.ad_pending.insert_one({
                    'Number_of_coins' : pending_coin,
                    'ad_id' : ad_id,
                })
                await bot.send_message(user_id,msg.read_msg('The_coin_was_spent_successfully'))
            except:
                pass




@bot.on(events.CallbackQuery())
async def handler(event):
    user_id = event.original_update.user_id
    find = db.users.find_one({'_id': event.original_update.user_id})
    code_2 = find.get('code')
    global keyboard
    if event.data == b'Advertiser_menu':
        Advertiser_menu_keyboard = [
            [
                Button.inline(str(msg.read_msg('create')), b'create_ad_in_Advertiser_menu')
            ],
            [
                Button.inline(str(msg.read_msg('show_ad_in_Advertiser_menu')), b'show_ad_in_Advertiser_menu')
            ],
            [
                Button.inline(str(msg.read_msg('reports')), b'Advertiser_reports')
            ],
            [
                Button.inline(str(msg.read_msg('help')), b'help_in_Advertiser_menu')
            ],
            [
                Button.inline(str(msg.read_msg('back')), b'back_in_Advertiser_menu')
            ]

        ]
        await bot.send_message(user_id,msg.read_msg('Advertiser_menu'),buttons=Advertiser_menu_keyboard)


    elif event.data == b'Ad_receiver_menu':
        Ad_receiver_menu_keyboard = [
            [
                Button.inline(str(msg.read_msg('connect')), b'connect')
            ],
            [
                Button.inline(str(msg.read_msg('show_ad_in_Ad_receiver_menu')), b'show_ad_in_Ad_receiver_menu')
            ],
            [
                Button.inline(str(msg.read_msg('reports')), b'Ad_receiver_menu_reports')
            ],
            [
                Button.inline(str(msg.read_msg('help')), b'help_in_Ad_receiver_menu')
            ],
            [
                Button.inline(str(msg.read_msg('back')), b'back_in_Ad_receiver_menu')
            ],

        ]
        await bot.send_message(user_id,msg.read_msg('Ad_receiver_menu'),buttons=Ad_receiver_menu_keyboard)
    elif event.data == b'coin_management':
        coin_management_keyboard = [
            [
                Button.inline(str(msg.read_msg('buy_coins')), b'coin_management')
            ],
            [
                Button.inline(str(msg.read_msg('reports')), b'coin_management_reports')
            ],
            [
                Button.inline(str(msg.read_msg('help')), b'help_in_coin_management')
            ],
            [
                Button.inline(str(msg.read_msg('back')), b'back_in_coin_management')
            ],

        ]
        await bot.send_message(user_id,msg.read_msg('coin_management'),buttons=coin_management_keyboard)
    elif event.data == b'connect':
        await bot.send_message(user_id,msg.read_msg('join'))
        await bot.send_message(user_id, msg.read_msg('code'))
        await bot.send_message(user_id, code_2)
    elif event.data == b'create_ad_in_Advertiser_menu':
        date = datetime.datetime.now()

        async with bot.conversation(user_id, timeout=1000) as conv:
            msg1 = await conv.send_message(msg.read_msg('ads_text'))
            text = await conv.get_response(timeout=1000)
            ads_text = text.message
            msg2 = await conv.send_message(msg.read_msg('ads_link'))
            link = await conv.get_response(timeout=1000)
            ads_link = link.message
            count = db.ads.count_documents(({"owner_id" : user_id}))
            ads_id = str(user_id) + str("_") + str(count)
            try:
                db.ads.insert_one({
                    "_id" : ads_id,
                    "text" : ads_text,
                    "link" : ads_link,
                    "owner_id" : user_id,
                    'date': str(date),
                })
                await bot.send_message(user_id,msg.read_msg('The_ad_was_created_successfully'))
            except:
                pass
    elif event.data == b'show_ad_in_Advertiser_menu':
            user_id = event.original_update.user_id
            i = 1

            count = db.ads.count_documents(({"owner_id": user_id}))
            while i <= count:
                count_2 = count - i
                ads_id = str(user_id) + str("_") + str(count_2)
                keyboard = [
                    [
                        Button.inline(msg.read_msg("select"), data=str.encode('ad:' + ads_id))
                    ]
                ]
                count_if = 0
                if i == 6:
                    count_if +=1

                    keyboard_next_page = [
                        [
                            # nxn = next button number
                            Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')), data=str.encode('nxn:' + str(count_if)))
                        ]
                    ]
                    await bot.send_message(user_id,msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page)
                    break
                else:
                    pass
                find_ads = db.ads.find_one({'_id': ads_id})
                try:
                    text = find_ads.get('text')
                    link = find_ads.get('link')
                    if text is None:
                        text = msg.read_msg('text not found')
                    if link is None:
                        link = msg.read_msg('link not found')
                    perfect_ads = f"{text}\n{link}"
                    await bot.send_message(user_id, perfect_ads, buttons=keyboard)
                except Exception as e:
                    print(e)
                i = i + 1

@bot.on(events.CallbackQuery(pattern='nxn:*'))
async def nxn_handler(event):
    user_id = event.original_update.user_id
    nxn_number = int(event.data.decode().split(':')[1])+1
    zarb = nxn_number * 5
    find = db.ads.find({'owner_id':user_id}).sort('date',-1).skip(zarb)
    keyboard_next_page = [
        [
            # nxn = next button number
            Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')), data=str.encode('nxn:' + str(nxn_number)))
        ]
    ]
    for i in find:
        try:
            text = i.get('text')
            link = i.get('link')
            if text is None:
                text = msg.read_msg('text not found')
            if link is None:
                link = msg.read_msg('link not found')
            perfect_ads = f"{text}\n{link}"
            await bot.send_message(user_id, perfect_ads, buttons=keyboard)
        except Exception as e:
            print(e)
    await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'), buttons=keyboard_next_page)

def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
