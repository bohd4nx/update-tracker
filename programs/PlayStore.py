import asyncio
from dataclasses import dataclass
from datetime import datetime

import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from google_play_scraper import app


@dataclass
class Env:
    TOKEN: str = ""
    CHAT_ID: str = "-"
    PACKAGE_NAME: str = "org.telegram.messenger"
    DOWNLOAD_URL: str = "https://play.google.com/store/apps/details?id=org.telegram.messenger"
    INTERVAL: int = 60


class UpdateBot:
    def __init__(self):
        self.env = Env()
        self.bot = Bot(token=self.env.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self.dp.message.register(self.cmd_start, CommandStart())
        self.current_version = None
        self.app_name = None

    async def fetch_data(self) -> dict | None:
        try:
            result = app(
                self.env.PACKAGE_NAME,
                lang='en',
                country='US'
            )

            return {
                "version": result.get('version'),
                "updated": datetime.fromtimestamp(result.get('updated', 0)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "releaseNotes": result.get('recentChanges', 'No release notes'),
                "trackName": result.get('title', 'App')
            }
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def make_message(self, version: str, date: str, notes: str) -> tuple[str, InlineKeyboardMarkup]:
        version_text = f"{self.current_version} -> {version}" if self.current_version else version
        date_formatted = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y %H:%M:%S")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🤖 Update Now", url=self.env.DOWNLOAD_URL)
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
                release_date = app_info.get("updated", "N/A")
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
            "on Google Play.</b>"
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
