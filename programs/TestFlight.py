import aiohttp
import aioschedule
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Env:
    TOKEN: str = ""
    CHAT_ID: str = "-"
    TESTFLIGHT_URL: str = "https://testflight.apple.com/join/u6iogfd0"
    INTERVAL: int = 10  # minutes


class TestFlightBot:
    def __init__(self):
        self.env = Env()
        self.bot = Bot(token=self.env.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self.dp.message.register(self.cmd_start, CommandStart())
        self.last_status = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }

    async def fetch_status(self) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.env.TESTFLIGHT_URL, headers=self.headers) as response:
                    if response.status != 200:
                        return f"Failed to fetch the page. Status code: {response.status}"

                    page_content = await response.text()

                    status_patterns = {
                        "FULL": "This beta is full",
                        "CLOSED": "This beta isn't accepting any new testers right now",
                        "AVAILABLE": "Join"
                    }

                    return next(
                        (status for status, pattern in status_patterns.items()
                         if pattern in page_content),
                        "UNKNOWN"
                    )

        except Exception as e:
            return f"ERROR: {str(e)}"

    def make_message(self, status: str) -> tuple[str, InlineKeyboardMarkup | None]:
        status_emoji = {
            "AVAILABLE": "✅",
            "FULL": "❌",
            "CLOSED": "🔒",
            "UNKNOWN": "❓"
        }

        status_text = {
            "AVAILABLE": "Beta slots are available!",
            "FULL": "Beta is full",
            "CLOSED": "Beta is not accepting new testers",
            "UNKNOWN": "Unable to determine status"
        }

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📱 Open TestFlight", url=self.env.TESTFLIGHT_URL)
        ]]) if status == "AVAILABLE" else None

        message = (
            f"<b>{status_emoji.get(status, '❓')} TestFlight Status Update</b>\n\n"
            f"<b>Status:</b> {status_text.get(status, 'Unknown status')}\n"
            f"<b>Time:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )

        return message, keyboard

    async def check_for_updates(self):
        status = await self.fetch_status()

        if status != self.last_status:
            message, keyboard = self.make_message(status)
            await self.bot.send_message(self.env.CHAT_ID, message, reply_markup=keyboard)
            self.last_status = status

    async def cmd_start(self, message: Message):
        await message.answer(
            "<b>👋 Hello! I'll notify you about TestFlight beta slot availability.</b>\n"
            f"Currently monitoring: {self.env.TESTFLIGHT_URL}"
        )

    async def scheduler(self):
        aioschedule.every(self.env.INTERVAL).minutes.do(self.check_for_updates)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    async def main(self):
        await self.check_for_updates()
        asyncio.create_task(self.scheduler())
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    bot = TestFlightBot()
    asyncio.run(bot.main())
