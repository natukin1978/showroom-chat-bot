import asyncio
import logging

import aiohttp

import global_value as g
from fuyuka_helper import Fuyuka
from random_helper import is_hit_by_message_json
from showroom_comment_log_analyzer import ShowroomCommentLogAnalyzer
from showroom_message_helper import create_message_json
from showroom_onlives_analyzer import ShowroomOnlivesAnalyzer

logger = logging.getLogger(__name__)


class ShowroomBot:

    def __init__(self):
        config_sr = g.config["showroom"]
        self.main_name = config_sr["mainName"]
        self.chat_polling_interval = config_sr["chatPollingIntervalSec"]
        self.scla = ShowroomCommentLogAnalyzer()
        self.room_id = None
        self.chat_task = None

    async def on_message(self, comments):
        for comment in comments:
            json_data = create_message_json(comment)

            id = json_data["id"]
            if id in g.set_exclude_id:
                # 無視するID
                return

            answerLevel = g.config["fuyukaApi"]["answerLevel"]
            needs_response = is_hit_by_message_json(answerLevel, json_data)
            await Fuyuka.send_message_by_json_with_buf(json_data, needs_response)

    async def get_room_id(self) -> int | None:
        try:
            url = "https://www.showroom-live.com/api/live/onlives"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response_json = await response.json()
                    soa = ShowroomOnlivesAnalyzer()
                    soa.merge(response_json)
                    live = soa.get_live(self.main_name)
                    if not live:
                        return None
                    return live["room_id"]
        except Exception as e:
            logger.error(f"Error getting Room ID: {e}")
            return None

    async def get_chat_messages(self):
        if not self.room_id:
            logger.error("Room ID is not set. Please call get_room_id first.")
            return

        try:
            url = "https://www.showroom-live.com/api/live/comment_log"
            params = {
                "room_id": self.room_id,
            }
            while True:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        response_json = await response.json()
                        self.scla.merge(response_json)
                        new_comments = self.scla.get_new_comments()
                        await self.on_message(new_comments)
                        await asyncio.sleep(self.chat_polling_interval)
        except asyncio.CancelledError:
            logger.error("Chat message task cancelled.")
        except Exception as e:
            logger.error(f"Chat message get error:{e}")

    async def run(self):
        while True:
            room_id = await self.get_room_id()
            if room_id:
                self.room_id = room_id
                break
            await asyncio.sleep(self.chat_polling_interval)

        self.chat_task = asyncio.create_task(self.get_chat_messages())
