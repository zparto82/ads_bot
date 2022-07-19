import config
import code_creator
import msg
import json
from telethon.sync import TelegramClient,events
from telethon.tl.types import PeerUser
from telethon import Button
api_id = 86576
api_hash = '385886b58b21b7f3762e1cde2d651925'
bot_token = config.read("telegram","bot_token")

bot = TelegramClient('bot', api_id, api_hash,proxy=('socks5','127.0.0.1',1080))
bot.start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    z = event.message.peer_id
    print(event.message)
    keyboard = [
        [
            Button.inline(str(msg.read_msg('connect')),b'1'),
            Button.inline(str(msg.read_msg("create")), b"2"),
        ],
        [
            Button.inline(msg.read_msg("show"), b"3"),
            Button.inline(msg.read_msg("settings"), b"4")
        ],
        [
            Button.inline(msg.read_msg("buy coins"), b"5"),
            Button.inline(msg.read_msg("help"), b"6")
        ]
    ]

    await bot.send_message(z,msg.read_msg('Introduction') , buttons=keyboard)

@bot.on(events.NewMessage(pattern="code:*"))
async def code(event):
    print(event.message.peer_id)

d = {

}
@bot.on(events.CallbackQuery())
async def handler(event):
    if event.data == b'1':
        z = event.original_update.user_id
        if z in d.keys():
            await bot.send_message(z,d[z])
        else:
            z = event.original_update.user_id
            code = code_creator.code()
            c = d[z] = code
            await bot.send_message(z,msg.read_msg('code'))
            await bot.send_message(z,d[z])


def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()