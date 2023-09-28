from bisleri_product import telegram_bot
from replit_keep_alive import start

def start_bisleri_processor():
    bot = telegram_bot.BotGadu()
    start("Bisleri Processor On Force")
    bot.run()

if __name__ == "__main__":
    start_bisleri_processor()

