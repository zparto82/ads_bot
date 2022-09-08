import send_ads
import coins
import msg
import datetime
async def background(ad_id,user_id,client,db):
        date_time = datetime.datetime.now()
        # check ad_pending
        ad_pending_find = db.ad_pending.find_one({'ad_id':ad_id})
        number_of_coin = ad_pending_find.get('Number_of_coins')
        # get ad
        find_ads = db.ads.find_one({'_id': ad_id})
        text = find_ads.get('text')
        link = find_ads.get('link')
        # check connections
        try:
            find_connections = db.connections.find({'members':{'$lte': number_of_coin}})
            for index,group in enumerate(find_connections):
                print('group',group)
                print('group_index',index)
                channel_id = group.get('_id')
                members = group.get('members')
                send_ads_in_back = await send_ads.send_ads(text, link, channel_id, client)
                post_id = send_ads_in_back.id
                owner_id = group.get('owner_id')
                print('owner_id :',owner_id)
                print('post_id is :', post_id)
                ad_connection = db.ad_connection.insert_one({
                    "_id": ad_id,
                    "post_id": post_id,
                    "connection_id": channel_id,
                    "start_date": date_time,
                })
                # ad_pending --
                number_of_coin = number_of_coin - members
                print('number_of_coin : ',number_of_coin)
                update = db.ad_pending.update_one({'ad_id': ad_id}, {'$set': {'Number_of_coins': number_of_coin}})
                print('update_in_back_ad_pending', update)
                # owner_connections ++
                update_user_coin = db.users.update_one({'_id': owner_id}, {'$inc': {'coin': number_of_coin}})
                print('user_coin_update', update_user_coin)
                # log coins collection
                log_coin_change = coins.coin(owner_id, number_of_coin, msg.read_msg('reason_Show_ad'), date_time, db)
        except:
            pass

                # ad_pending: 1000 / [g1: 327, g2: 23551, ...] - send_ads
