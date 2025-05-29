import asyncio
import logging
import time
from collections import defaultdict

import aiohttp

import global_value as g
from fuyuka_helper import Fuyuka
from random_helper import is_hit_by_message_json
from showroom_comment_log_analyzer import ShowroomCommentLogAnalyzer
from showroom_message_helper import create_message_json
from showroom_onlives_analyzer import ShowroomOnlivesAnalyzer

logger = logging.getLogger(__name__)


class ShowroomBot:

    # ギフトメッセージの区切りと判断するまでの時間（秒）
    GIFTMESSAGE_TIMEOUT_SECONDS = 15

    def __init__(self):
        config_sr = g.config["showroom"]
        self.main_name = config_sr["mainName"]
        self.chat_polling_interval = config_sr["chatPollingIntervalSec"]
        self.scla = ShowroomCommentLogAnalyzer()
        self.room_id = None
        self.bcsvr_key = None
        # ギフトメッセージを保持する辞書
        # キーはユーザーID、値は { "giftmessage": dict[str, any], "last_giftmessage_time": 最終ギフトメッセージのタイムスタンプ }
        self.user_giftmessage_buffers = defaultdict(
            lambda: {"giftmessage": None, "last_giftmessage_time": 0.0}
        )

    async def handle_incoming_giftmessage(
        self, user_id: str, giftmessage: dict[str, any]
    ):
        """
        新しいギフトメッセージを受け取ったときに呼び出される関数。
        ギフトメッセージをユーザーのバッファに追加し、最終ギフトメッセージ時刻を更新します。
        """
        current_time = time.time()
        self.user_giftmessage_buffers[user_id]["giftmessage"] = giftmessage
        self.user_giftmessage_buffers[user_id]["last_giftmessage_time"] = current_time

    async def giftmessage_buffer_monitor(self):
        """
        定期的に各ユーザーのギフトメッセージバッファを監視し、
        タイムアウトしたギフトメッセージをAIに渡すタスク。
        """
        while True:
            current_time = time.time()

            # ユーザーIDのリストをコピーしてイテレートする
            # （処理中にuser_giftmessage_buffersが変更される可能性があるため）
            for user_id in list(self.user_giftmessage_buffers.keys()):
                user_data = self.user_giftmessage_buffers[user_id]

                # ギフトメッセージが全くない、または最後のギフトメッセージからタイムアウト時間を過ぎていない場合はスキップ
                if not user_data["giftmessage"] or (
                    current_time - user_data["last_giftmessage_time"]
                    < self.GIFTMESSAGE_TIMEOUT_SECONDS
                ):
                    continue

                # タイムアウトした場合、ギフトメッセージをAIに渡し、バッファをクリア
                giftmessages_to_process = user_data["giftmessage"]
                await Fuyuka.send_message_by_json_with_buf(
                    giftmessages_to_process, True
                )

                # 元のバッファをクリアして新しいコメントを受け入れられるようにする
                # 処理後にバッファをクリア
                self.user_giftmessage_buffers[user_id]["giftmessage"] = None
                # タイムアウト処理後も新規ギフトメッセージが来る可能性があるため、現在の時刻にリセット
                self.user_giftmessage_buffers[user_id][
                    "last_giftmessage_time"
                ] = current_time

            # 1秒ごとにチェック
            await asyncio.sleep(1)

    async def on_message_from_ws(self, json_ws):
        if "ac" not in json_ws:
            return

        id = str(json_ws["u"])
        if id in g.set_exclude_id:
            # 無視するID
            return

        json_data = create_message_json(json_ws)
        if "g" in json_ws:
            # 新しいギフトメッセージを受け取った
            await self.handle_incoming_giftmessage(id, json_data)
            return

        answerLevel = g.config["fuyukaApi"]["answerLevel"]
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

        # ギフトメッセージ監視タスクを開始
        asyncio.create_task(self.giftmessage_buffer_monitor())

        while True:
            if g.websocket_showroom_live:
                await g.websocket_showroom_live.send(f"SUB\t{self.bcsvr_key}")
                break
            await asyncio.sleep(self.chat_polling_interval)
