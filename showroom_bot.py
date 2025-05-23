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
        self.bcsvr_key = None

    async def on_message_from_ws(self, json_ws):
        if "ac" not in json_ws:
            return

        id = str(json_ws["u"])
        if id in g.set_exclude_id:
            # 無視するID
            return

        json_data = create_message_json(json_ws)

        answerLevel = g.config["fuyukaApi"]["answerLevel"]
        if "g" in json_ws:
            answerLevel = 100

        needs_response = is_hit_by_message_json(answerLevel, json_data)
        await Fuyuka.send_message_by_json_with_buf(json_data, needs_response)

    async def get_live(self):
        try:
            url = "https://www.showroom-live.com/api/live/onlives"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response_json = await response.json()
                    soa = ShowroomOnlivesAnalyzer()
                    soa.merge(response_json)
                    live = soa.get_live(self.main_name)
                    return live
        except Exception as e:
            logger.error(f"Error getting Room ID: {e}")
            return None

    async def run(self):
        while True:
            live = await self.get_live()
            if live:
                self.room_id = live["room_id"]
                self.bcsvr_key = live["bcsvr_key"]
                break
            await asyncio.sleep(self.chat_polling_interval)

        while True:
            if g.websocket_showroom_live:
                await g.websocket_showroom_live.send(f"SUB\t{self.bcsvr_key}")
                break
            await asyncio.sleep(self.chat_polling_interval)
