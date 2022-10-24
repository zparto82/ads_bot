import msg


def send_ads(text, link, channel_id, client):
    if text is None:
        text = msg.read_msg('text not found')
    else:
        pass
    if link is None:
        link = msg.read_msg('link not found')
    else:
        pass
    perfect_ads = f"{text}\n{link}"
    return client.send_message(channel_id, perfect_ads)