from pymongo import MongoClient
mongo_client = MongoClient('127.0.0.1:27017')
db = mongo_client.user


def coin(user, coin_change, reason, change_data):
    insert = db.coins.insert_one({
        'user': user,
        'coin_change': coin_change,
        'reason': reason,
        'change_data' : change_data,
    })

    return insert
