import asyncio
from dataclasses import dataclass
from datetime import datetime

import aiohttp
import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


@dataclass
class Env:
    TOKEN: str = ""
    CHAT_ID: str = "-"
    API_URL: str = "https://itunes.apple.com/lookup?id=686449807"
    DOWNLOAD_URL: str = "https://apps.apple.com/app/telegram-messenger/id686449807"
    INTERVAL: int = 60  # minutes


class UpdateBot:
    def __init__(self):
        self.env = Env()
        self.bot = Bot(token=self.env.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self.dp.message.register(self.cmd_start, CommandStart())
        self.current_version = None
        self.app_name = None

    async def fetch_data(self) -> dict | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.env.API_URL) as response:
                if response.status == 200:
                    data = await response.json(content_type='text/javascript')
                    return data["results"][0] if data["resultCount"] > 0 else None
        return None

    def make_message(self, version: str, date: str, notes: str) -> tuple[str, InlineKeyboardMarkup]:
        version_text = f"{self.current_version} -> {version}" if self.current_version else version
        date_formatted = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y %H:%M:%S")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔄 Update Now", url=self.env.DOWNLOAD_URL)
        ]])

        message = (
            f"<b>🚀 New {self.app_name} Update Available!</b>\n\n"
            f"<b>📱 Version:</b> {version_text}\n"
            f"<b>🗓️ Released:</b> {date_formatted}\n"
            f"<b>📝 Changes:</b> <code>{notes}</code>"
        )

        return message, keyboard

    async def check_for_updates(self):
        app_info = await self.fetch_data()

        if app_info:
            self.app_name = app_info.get("trackName", "App")
            version = app_info.get("version")

            if version != self.current_version:
                release_date = app_info.get("currentVersionReleaseDate", "N/A")
                release_notes = app_info.get("releaseNotes", "No release notes.")

                message, keyboard = self.make_message(version, release_date, release_notes)
                await self.bot.send_message(self.env.CHAT_ID, message, reply_markup=keyboard)
                self.current_version = version

    async def cmd_start(self, message: Message):
        if not self.app_name:
            app_info = await self.fetch_data()
            self.app_name = app_info.get("trackName", "App") if app_info else "App"

        await message.answer(
            f"<b>👋 Hello! I'll notify about new {self.app_name} updates "
            "on App Store.</b>"
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
    bot = UpdateBot()
    asyncio.run(bot.main())
