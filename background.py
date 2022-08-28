import send_ads
import coins
import msg
import datetime
def background(ad_id,owner_id,post_id,peer_id,client,db):
        # check ad_pending
        ad_pending_find = db.ad_pending.find_one({'ad_id':ad_id})
        number_of_coin = ad_pending_find.get('Number_of_coins')
        # check connections
        find_connections = db.connections.find_one({'_id':peer_id})
        channel_id = find_connections.get('_id')
        members = find_connections.get('members')
        find_ads = db.ads.find_one({'owner_id':owner_id})
        text = find_ads.get('text')
        link = find_ads.get('link')

        if number_of_coin > members:
               send_ads.send_ads(text,link,channel_id,client)
               update = db.ad_pending.update_one({'ad_id':ad_id},{'$set': {'Number_of_coins': -number_of_coin}})
               print('update_in_back_ad_pending',update)
               # ad_pending --
               # owner_connections ++
               update_user_coin = db.users.update_one({'_id': owner_id}, {'$set': {'coin': +number_of_coin}})
               print('user_coin_update', update_user_coin)
               # log coins collection
               log_coin_change = coins.coin(owner_id,+number_of_coin,msg.read_msg('reason_Show_ad'),datetime.datetime.now(),client)
        # ad_pending: 1000 / [g1: 327, g2: 23551, ...] - send_ads
