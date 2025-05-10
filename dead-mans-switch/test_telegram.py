import os
import asyncio
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = "-1002687819162"  # Your group/channel ID

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(chat_id=GROUP_ID, text="Test message from minimal script (async).")
        print("Message sent!")
    except Exception as e:
        print(f"Failed to send message: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 