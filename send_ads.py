import msg
from telethon.tl.types import PeerChannel, PeerChat


def send_ads(text, link, channel_id, client):
    # if text is None:
    #     text = msg.read_msg('text not found')
    # else:
    #     pass
    # if link is None:
    #     link = msg.read_msg('link not found')
    # else:
    #     pass
    perfect_ads = f"{text}\n{link}"
    try:
        sent = client.send_message(PeerChannel(channel_id=channel_id), perfect_ads)
    except:
        sent = client.send_message(PeerChat(chat_id=channel_id), perfect_ads)
    return sent