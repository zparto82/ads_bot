
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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
api_id = 86576
api_hash = '385886b58b21b7f3762e1cde2d651925'
bot_token = config.read("telegram", "bot_token")
if config.read('telegram', 'proxy') == 'True':
    bot = TelegramClient('bot', api_id, api_hash, proxy=('socks5', '127.0.0.1', 1082))
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
                'status': msg.read_msg('channel_active'),
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
            log_coin_change = coins.coin(user_id,-pending_coin,msg.read_msg('reason_Advertising_order'),change_date,db)

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
                Button.inline(str(msg.read_msg('back')), b'back')
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
                Button.inline(str(msg.read_msg('back')), b'back')
            ],

        ]
        await bot.send_message(user_id,msg.read_msg('Ad_receiver_menu'),buttons=Ad_receiver_menu_keyboard)
    elif event.data == b'coin_management':
        coin_management_keyboard = [
            [
                Button.inline(str(msg.read_msg('buy_coins')), b'buy_coins')
            ],
            [
                Button.inline(str(msg.read_msg('reports')), b'coin_management_reports')
            ],
            [
                Button.inline(str(msg.read_msg('help')), b'help_in_coin_management')
            ],
            [
                Button.inline(str(msg.read_msg('back')), b'back')
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

                count_if = 0
                if i == 6:
                    count_if +=1

                    keyboard_next_page = [
                        [
                            # nxn = next button number
                            Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')), data=str.encode('nxn:' + str(count_if))),
                            Button.inline(str(msg.read_msg('back')), b'back'),

                        ]
                    ]
                    await bot.send_message(user_id,msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page)
                    break
                else:
                    pass
                find_ads = db.ads.find_one({'_id': ads_id})
                try:
                    find_pending = db.ad_pending.find_one({'ad_id':ads_id})
                    if find_pending is None:
                        status_new = 'ad_status_new'
                        keyboard_new = [
                            [
                                Button.inline(msg.read_msg("release_new"), data=str.encode('ad:' + ads_id)),
                                Button.inline(msg.read_msg("edit"), data=b'edit'),
                                Button.inline(msg.read_msg("delete"), data=b'delete'),
                                Button.inline(str(msg.read_msg('back')), b'back')
                            ]
                        ]

                        try:
                            text = find_ads.get('text')
                            link = find_ads.get('link')
                            perfect_ads = f"{text}\n{link}\n{msg.read_msg(status_new)}"
                            await bot.send_message(user_id, perfect_ads, buttons=keyboard_new)
                        except Exception as e:
                            print('e new',e)
                    elif find_pending is not None:
                        showing = db.ad_pending.find({'ad_id':ads_id,'Number_of_coins': {'$gt': 0}})
                        show = 0
                        for index in showing:

                            show +=1
                        if show == 0:
                            status_finish = 'Finish_the_show'
                            keyboard_finish = [
                                [
                                    Button.inline(msg.read_msg("release_finish_show"), data=str.encode('ad:' + ads_id)),
                                    Button.inline(msg.read_msg("edit"), data=b'edit'),
                                    Button.inline(msg.read_msg("delete"), data=b'delete'),
                                    Button.inline(msg.read_msg("reports"), data=b'reports'),
                                    Button.inline(str(msg.read_msg('back')), b'back')
                                ],
                            ]

                            try:

                                text = find_ads.get('text')
                                link = find_ads.get('link')
                                perfect_ads = f"{text}\n{link}\n{msg.read_msg(status_finish)}"
                                await bot.send_message(user_id, perfect_ads, buttons=keyboard_finish)
                            except Exception as e:
                                print(e)
                        else:
                            status_show = 'ad_status_Showing'

                            keyboard_show = [
                                [
                                    Button.inline(msg.read_msg("add_coin"), data=str.encode('ad:' + ads_id)),
                                    Button.inline(msg.read_msg("edit"), data=b'edit'),
                                    Button.inline(msg.read_msg("Stop_the_show"), data=b'stop_show'),
                                    Button.inline(msg.read_msg("reports"), data=b'reports'),
                                    Button.inline(str(msg.read_msg('back')), b'back')
                                ]
                            ]


                            try:
                                text = find_ads.get('text')

                                link = find_ads.get('link')

                                perfect_ads = f"{text}\n{link}\n{msg.read_msg(status_show)}"


                                await bot.send_message(user_id, perfect_ads,buttons=keyboard_show)

                            except Exception as e:

                                print('e',e)
                    else:
                        pass

                except:
                    pass

                i = i + 1
    elif event.data == b'show_ad_in_Ad_receiver_menu':
        try:

            await bot.send_message(user_id,msg.read_msg('welcome_show_channel'))
            find_connection = db.connections.find({'owner': user_id}).limit(5).sort('members',-1)
            if find_connection is None:
                await bot.send_message(user_id, msg.read_msg('channel_not_created'))
            else:
                pass

            for index,channel in enumerate(find_connection):
                channel_title = channel.get('title')
                channel_members = channel.get('members')
                channel_status = channel.get('status')

                full_channel = f'{msg.read_msg("channel_title")}:{channel_title}\n{msg.read_msg("channel_member")}:{channel_members}\n{msg.read_msg("channel_status")}:{channel_status}'
                await bot.send_message(user_id, full_channel)
                count_for = 0
                if index == 4:
                    count_for +=1
                    keyboard_next_page = [
                        [
                            # ncn = next channel number
                            Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')), data=str.encode('ncn:' + str(count_for))),
                            Button.inline(str(msg.read_msg('back')), b'back')
                        ]
                    ]
                    await bot.send_message(user_id,msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page)
                    break
                else:
                    pass
        except Exception() as e:
            print(e)

    elif event.data == b'buy_coins':
        help_buy_coin = msg.read_msg('Guide_to_buying_coins')
        await bot.send_message(user_id,help_buy_coin.replace('$','\n'))
    elif event.data == b'coin_management_reports':
        await bot.send_message(user_id, msg.read_msg('welcome_show_coins'))
        coin_find = db.coins.find({'user' : user_id}).sort('change_date',-1).limit(5)
        for index,coin in enumerate(coin_find):
            coin_change = coin.get('coin_change')
            reason = coin.get('reason')
            coin_date = coin.get('change_date')
            if reason == msg.read_msg('reason_Advertising_order'):
                reason = msg.read_msg('reason_Advertising_order_fa')
            elif reason == msg.read_msg('reason_Show_ad') :
                reason = msg.read_msg('reason_Show_ad_fa')
            coin_report = f'{msg.read_msg("coin_change")}:{coin_change}\n{msg.read_msg("reason_coin")}:{reason}\n{msg.read_msg("coin_date")}:{coin_date}'
            await bot.send_message(user_id,coin_report)
            count_if_coin = 0
            if index == 4:
                count_if_coin += 1
                keyboard_next_page_coin = [
                    [
                        # nsn = next score number
                        Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')),data=str.encode('nsn:' + str(count_if_coin))),
                        Button.inline(str(msg.read_msg('back')), b'back')
                    ]
                ]
                await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page_coin)
                break
            else:
                pass
    elif event.data == b'Advertiser_reports':
        find_log = db.coins.find({'user':user_id,'reason':msg.read_msg('reason_Advertising_order')}).sort('change_date',-1).limit(5)
        if find_log is None:
            await bot.send_message(user_id, msg.read_msg('coin_not_changed'))
        else:
            pass
        for index,log in enumerate(find_log):
            coin_change = log.get('coin_change')
            reason = log.get('reason')
            coin_date = log.get('change_date')
            if reason == msg.read_msg('reason_Advertising_order'):
                reason = msg.read_msg('reason_Advertising_order_fa')
            elif reason == msg.read_msg('reason_Show_ad') :
                reason = msg.read_msg('reason_Show_ad_fa')
            coin_report = f'{msg.read_msg("coin_change")}:{coin_change}\n{msg.read_msg("reason_coin")}:{reason}\n{msg.read_msg("coin_date")}:{coin_date}'
            await bot.send_message(user_id,coin_report)
            count_if_coin = 0
            if index == 4:
                count_if_coin += 1
                keyboard_next_page_coin = [
                    [
                        # nan = next Advertising order number
                        Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')),data=str.encode('nan:' + str(count_if_coin))),
                        Button.inline(str(msg.read_msg('back')), b'back')
                    ]
                ]
                await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page_coin)
                break
            else:
                pass
    elif event.data == b'Ad_receiver_menu_reports':
        find_log = db.coins.find({'user':user_id,'reason':msg.read_msg('reason_Show_ad')}).sort('change_date',-1).limit(5)
        if find_log is None:
            await bot.send_message(user_id, msg.read_msg('coin_not_changed'))
        else:
            pass
        for index,log in enumerate(find_log):
            coin_change = log.get('coin_change')
            reason = log.get('reason')
            coin_date = log.get('change_date')
            if reason == msg.read_msg('reason_Advertising_order'):
                reason = msg.read_msg('reason_Advertising_order_fa')
            elif reason == msg.read_msg('reason_Show_ad') :
                reason = msg.read_msg('reason_Show_ad_fa')
            coin_report = f'{msg.read_msg("coin_change")}:{coin_change}\n{msg.read_msg("reason_coin")}:{reason}\n{msg.read_msg("coin_date")}:{coin_date}'
            await bot.send_message(user_id,coin_report)
            count_if_coin = 0
            if index == 4:
                count_if_coin += 1
                keyboard_next_page_coin = [
                    [
                        # nrn = next Ad receiver page number
                        Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')),data=str.encode('nrn:' + str(count_if_coin))),
                        Button.inline(str(msg.read_msg('back')), b'back')
                    ]
                ]
                await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page_coin)
                break
            else:
                pass
@bot.on(events.CallbackQuery(pattern=b'back'))
async def start_back(event):
    user_id = event.original_update.user_id
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
@bot.on(events.CallbackQuery(pattern='nrn:*'))
async def nrn_handler(event):
    user_id = event.original_update.user_id
    nrn_number = int(event.data.decode().split(':')[1])+1
    skip_number = (nrn_number * 5)-5
    try:
        keyboard_next_page = [
            [
                # nrn = next Ad receiver page number
                Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')),data=str.encode('nrn:' + str(nrn_number))),
                Button.inline(str(msg.read_msg('back')), b'back')
            ]
        ]

        find = db.coins.find({'user': user_id,'reason':msg.read_msg('reason_Show_ad')}).sort('change_date', -1).skip(skip_number).limit(5)
        if find is None:
            await bot.send_message(user_id, msg.read_msg('coin_not_changed'))
        else:
            pass
        count = 0
        for coin in find:
            count +=1
            coin_change = coin.get('coin_change')
            reason = coin.get('reason')
            coin_date = coin.get('change_date')
            coin_report = f'{msg.read_msg("coin_change")}:{coin_change}\n{msg.read_msg("reason_coin")}:{reason}\n{msg.read_msg("coin_date")}:{coin_date}'
            await bot.send_message(user_id,coin_report)
            if count == 5:
                count = 0

                await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page)
            else:
                pass
    except Exception() as error:
        print('error',error)

@bot.on(events.CallbackQuery(pattern='nan:*'))
async def nan_handler(event):
    user_id = event.original_update.user_id
    nan_number = int(event.data.decode().split(':')[1])+1
    skip_number = (nan_number * 5)-5
    try:
        keyboard_next_page = [
            [
                # nan = next score number
                Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')),data=str.encode('nan:' + str(nan_number))),
                Button.inline(str(msg.read_msg('back')), b'back')
            ]
        ]

        find = db.coins.find({'user': user_id,'reason':msg.read_msg('reason_Advertising_order')}).sort('change_date', -1).skip(skip_number).limit(5)
        if find is None:
            await bot.send_message(user_id, msg.read_msg('coin_not_changed'))
        else:
            pass
        count = 0
        for coin in find:
            count +=1
            coin_change = coin.get('coin_change')
            reason = coin.get('reason')
            coin_date = coin.get('change_date')
            coin_report = f'{msg.read_msg("coin_change")}:{coin_change}\n{msg.read_msg("reason_coin")}:{reason}\n{msg.read_msg("coin_date")}:{coin_date}'
            await bot.send_message(user_id,coin_report)
            if count == 5:
                count = 0

                await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page)
            else:
                pass
    except Exception() as error:
        print('error',error)

@bot.on(events.CallbackQuery(pattern='nsn:*'))
async def nsn_handler(event):
    user_id = event.original_update.user_id
    nsn_number = int(event.data.decode().split(':')[1])+1
    skip_number = (nsn_number * 5)-5
    try:
        keyboard_next_page = [
            [
                # nsn = next score number
                Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')),data=str.encode('nsn:' + str(nsn_number))),
                Button.inline(str(msg.read_msg('back')), b'back')
            ]
        ]

        find = db.coins.find({'user': user_id}).sort('change_date', -1).skip(skip_number).limit(5)
        if find is None:
            await bot.send_message(user_id, msg.read_msg('coin_not_changed'))
        else:
            pass
        count = 0
        for coin in find:
            count +=1
            coin_change = coin.get('coin_change')
            reason = coin.get('reason')
            coin_date = coin.get('change_date')
            coin_report = f'{msg.read_msg("coin_change")}:{coin_change}\n{msg.read_msg("reason_coin")}:{reason}\n{msg.read_msg("coin_date")}:{coin_date}'
            await bot.send_message(user_id,coin_report)
            if count == 5:
                count = 0

                await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page)
            else:
                pass
    except Exception() as error:
        print('error',error)


@bot.on(events.CallbackQuery(pattern='ncn:*'))
async def ncn_handler(event):
    user_id = event.original_update.user_id
    ncn_number = int(event.data.decode().split(':')[1])+1
    skip_number = (ncn_number * 5)-5
    try:
        keyboard_next_page = [
            [
                # ncn = next channel number
                Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')),data=str.encode('ncn:' + str(ncn_number))),
                Button.inline(str(msg.read_msg('back')), b'back')
            ]
        ]
        await bot.send_message(user_id, msg.read_msg('welcome_show_channel'))
        find = db.connections.find({'owner': user_id}).sort('members', -1).skip(skip_number).limit(5)
        if find is None:
            await bot.send_message(user_id, msg.read_msg('channel_not_created'))
        else:
            pass
        count = 0
        for channel in find:
            count +=1
            channel_title = channel.get('title')
            channel_members = channel.get('members')
            channel_status = channel.get('status')
            if channel_status == 'active':
                channel_status = msg.read_msg('channel_active')
            else:
                channel_status = msg.read_msg('channel_inactive')
            full_channel = f'{msg.read_msg("channel_title")}:{channel_title}\n{msg.read_msg("channel_member")}:{channel_members}\n{msg.read_msg("channel_status")}:{channel_status}'
            await bot.send_message(user_id, full_channel)
            if count == 5:
                count = 0

                await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'),buttons=keyboard_next_page)
            else:
                pass
    except Exception() as error:
        print('error',error)


@bot.on(events.CallbackQuery(pattern='nxn:*'))
async def nxn_handler(event):
    user_id = event.original_update.user_id
    nxn_number = int(event.data.decode().split(':')[1])+1
    skip_number = (nxn_number * 5)-5
    find = db.ads.find({'owner_id':user_id}).sort('date',-1).skip(skip_number).limit(5)
    keyboard_next_page = [
        [
            # nxn = next button number
            Button.inline(str(msg.read_msg('next_page_in_Advertiser_menu')), data=str.encode('nxn:' + str(nxn_number))),
            Button.inline(str(msg.read_msg('back')), b'back')
        ]
    ]
    count_for = 0
    for i in find:
        count_for +=1
        ads_id = i.get('_id')
        try:
            find_pending = db.ad_pending.find_one({'ad_id': ads_id})
            if find_pending is None:
                status_new = 'ad_status_new'
                keyboard_new = [
                    [
                        Button.inline(msg.read_msg("release_new"), data=str.encode('ad:' + ads_id)),
                        Button.inline(msg.read_msg("edit"), data=b'edit'),
                        Button.inline(msg.read_msg("delete"), data=b'delete'),
                        Button.inline(str(msg.read_msg('back')), b'back')
                    ]
                ]

                try:
                    text = i.get('text')
                    link = i.get('link')
                    perfect_ads = f"{text}\n{link}\n{msg.read_msg(status_new)}"
                    await bot.send_message(user_id, perfect_ads, buttons=keyboard_new)
                except Exception as e:
                    print('e new', e)
            elif find_pending is not None:
                showing = db.ad_pending.find({'ad_id': ads_id, 'Number_of_coins': {'$gt': 0}})
                show = 0
                for index in showing:
                    show += 1
                if show == 0:
                    status_finish = 'Finish_the_show'
                    keyboard_finish = [
                        [
                            Button.inline(msg.read_msg("release_finish_show"), data=str.encode('ad:' + ads_id)),
                            Button.inline(msg.read_msg("edit"), data=b'edit'),
                            Button.inline(msg.read_msg("delete"), data=b'delete'),
                            Button.inline(msg.read_msg("reports"), data=b'reports'),
                            Button.inline(str(msg.read_msg('back')), b'back')
                        ],
                    ]

                    try:

                        text = i.get('text')
                        link = i.get('link')
                        perfect_ads = f"{text}\n{link}\n{msg.read_msg(status_finish)}"
                        await bot.send_message(user_id, perfect_ads, buttons=keyboard_finish)
                    except Exception as e:
                        print(e)
                else:
                    status_show = 'ad_status_Showing'

                    keyboard_show = [
                        [
                            Button.inline(msg.read_msg("add_coin"), data=str.encode('ad:' + ads_id)),
                            Button.inline(msg.read_msg("edit"), data=b'edit'),
                            Button.inline(msg.read_msg("Stop_the_show"), data=b'stop_show'),
                            Button.inline(msg.read_msg("reports"), data=b'reports'),
                            Button.inline(str(msg.read_msg('back')), b'back')
                        ]
                    ]

                    try:
                        text = i.get('text')

                        link = i.get('link')

                        perfect_ads = f"{text}\n{link}\n{msg.read_msg(status_show)}"
                        await bot.send_message(user_id, perfect_ads, buttons=keyboard_show)

                    except Exception as e:
                        print('e', e)
            else:
                pass

        except:
            pass


        if count_for == 5:
            count_for = 0
            await bot.send_message(user_id, msg.read_msg('next_page_in_Advertiser_menu'), buttons=keyboard_next_page)
        else:
            pass
def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
