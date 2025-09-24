import asyncio
import json
import logging
import os
import sys

import global_value as g

g.app_name = "showroom_chat_bot"
g.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

from config_helper import read_config
from one_comme_users import OneCommeUsers
from showroom_bot import ShowroomBot
from text_helper import read_text, read_text_set
from websocket_helper import websocket_listen_forever

print("前回の続きですか？(y/n) ", end="")
is_continue = input() == "y"

g.ADDITIONAL_REQUESTS_PROMPT = read_text("prompts/additional_requests_prompt.txt")

g.config = read_config()

# ロガーの設定
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

g.map_is_first_on_stream = {}
g.set_exclude_id = read_text_set("exclude_id.txt")
g.websocket_showroom_live = None
g.websocket_fuyuka = None


async def main():
    def get_fuyukaApi_baseUrl() -> str:
        conf_fa = g.config["fuyukaApi"]
        if not conf_fa:
            return ""
        return conf_fa["baseUrl"]

    def set_ws_showroom_live(ws) -> None:
        g.websocket_showroom_live = ws

    async def recv_showroom_live_response(message: str) -> None:
        messages = message.split()
        try:
            # JSON文字列が分割される事あるので連結する
            json_str = "".join(messages[2:])
            json_ws = json.loads(json_str)
            await bot.on_message_from_ws(json_ws)
        except json.JSONDecodeError as e:
            logger.error(f"Error JSONDecode: {e}")
        except Exception as e:
            logger.error(f"Error : {e}")

    def set_ws_fuyuka(ws) -> None:
        g.websocket_fuyuka = ws

    async def recv_fuyuka_response(message: str) -> None:
        return

    websocket_uri = "wss://online.showroom-live.com"
    asyncio.create_task(
        websocket_listen_forever(
            websocket_uri, recv_showroom_live_response, set_ws_showroom_live
        )
    )

    bot = ShowroomBot()

    if is_continue and OneCommeUsers.load_is_first_on_stream():
        print("挨拶キャッシュを復元しました。")

    await bot.run()

    fuyukaApi_baseUrl = get_fuyukaApi_baseUrl()
    if fuyukaApi_baseUrl:
        websocket_uri = f"{fuyukaApi_baseUrl}/chat/{g.app_name}"
        asyncio.create_task(
            websocket_listen_forever(websocket_uri, recv_fuyuka_response, set_ws_fuyuka)
        )

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass
    finally:
        pass


if __name__ == "__main__":
    asyncio.run(main())
