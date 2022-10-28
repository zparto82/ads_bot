import send_ads
import coins
import msg
import datetime
import config
from pymongo import MongoClient
from telethon.sync import TelegramClient
api_id = 86576
api_hash = '385886b58b21b7f3762e1cde2d651925'
bot_token = config.read("telegram", "bot_token")
client = TelegramClient('bot_background', api_id, api_hash, proxy=('socks5', '127.0.0.1', 1080))
client.start(bot_token=bot_token)
mongo_client = MongoClient('127.0.0.1:27017')
db = mongo_client.user

date_time = datetime.datetime.now()
# check ad_pending
ad_pending_find = db.ad_pending.find({'Number_of_coins': {'$gt': 0}}).sort('Number_of_coins', -1).limit(1)
ad_id, number_of_coin, real_id = None, 0, 0
for ad in ad_pending_find:
    ad_id = ad.get('ad_id')
    number_of_coin = ad.get('Number_of_coins')
    real_id = ad.get('_id')
# get ad
find_ads = db.ads.find_one({'_id': ad_id})
text = find_ads.get('text')
link = find_ads.get('link')
# check connections

find_connections = db.connections.find({'members': {'$lte': number_of_coin}})
for index, group in enumerate(find_connections):
    channel_id = group.get('_id')
    members = group.get('members')
    owner_id = group.get('owner')
    ads_owner = db.ads.find_one({'_id':ad_id})
    if ads_owner['owner_id'] == owner_id:
        continue
    if number_of_coin < members:
        continue
    try:
        filter_24h = db.ad_connection.find({'connection_id': channel_id}).sort('start_date', -1).limit(1)
        start_date = 0
        for ad_24h in filter_24h:
            start_date = ad_24h.get('start_date')
        if date_time - start_date < datetime.timedelta(days=1):
            continue
    except:
        pass
    try:
        send_ads_in_back = send_ads.send_ads(text, link, channel_id, client)
        post_id = send_ads_in_back.id
    except Exception as error:
        print(error)
        continue

    # ad_pending --
    number_of_coin = number_of_coin - members
    print(number_of_coin, members)
    update = db.ad_pending.update_one({'_id': real_id}, {'$set': {'Number_of_coins': number_of_coin}})
    # owner_connections ++
    update_user_coin = db.users.update_one({'_id': owner_id}, {'$inc': {'coin': members}})
    # log coins collection
    log_coin_change = coins.coin(owner_id, members, msg.read_msg('reason_Show_ad'), date_time, db)
    ad_connection = db.ad_connection.insert_one({
        "ad_id": ad_id,
        "post_id": post_id,
        "connection_id": channel_id,
        "start_date": date_time,
    })

mongo_client.close()

client.disconnect()