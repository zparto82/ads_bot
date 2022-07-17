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
    z = event.message.peer_id.user_id
    code = code_creator.code()
    d = {
        z : code
    }
    if z in d.keys():
        await bot.send_message(z,d[z])
    print(z)
    print(event.message)
    keyboard = [
        [
            Button.inline(str(msg.read_msg('connect')),b'1'),
            Button.inline(str(msg.read_msg("create")), "2"),
        ],
        [
            Button.inline(msg.read_msg("show"), "3"),
            Button.inline(msg.read_msg("settings"), "4")
        ],
        [
            Button.inline(msg.read_msg("buy coins"), "5"),
            Button.inline(msg.read_msg("help"), "6")
        ]
    ]

    await bot.send_message(z,msg.read_msg('Introduction') , buttons=keyboard)

@bot.on(events.NewMessage(pattern="code:*"))
async def code(event):
    print(event.message.peer_id)

@bot.on(events.CallbackQuery())
async def handler(event):
    pass


def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()