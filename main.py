import config
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
    print(event.message.message)
    keyboard = [
        [
            Button.inline("اتصال گروه / کانال",b'1'),
            Button.inline("ایجاد تبلیغ جدید", "2"),
        ],
        [
            Button.inline("نمایش تبلیغات", "3"),
            Button.inline("مدیریت و تنظیمات", "4")
        ],
        [
            Button.inline("خرید سکه", "5"),
            Button.inline("راهنما", "6")
        ]
    ]

    await bot.send_message(z,"این ربات چه میکند:این ربات برای تبلیغات است شما میتوانید با کمترین هزینه برای اشتغال خود تبلیغ کنید و کسب و کار خود را گسترش دهید" , buttons=keyboard)

@bot.on(events.CallbackQuery())
async def handler(event):
    pass
def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()