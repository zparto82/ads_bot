
def coin(user, coin_change, reason, change_date,client):
    insert = client.coins.insert_one({
        'user': user,
        'coin_change': coin_change,
        'reason': reason,
        'change_data' : change_date,
    })

    return insert