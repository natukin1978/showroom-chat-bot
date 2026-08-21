import datetime

from one_comme_users import OneCommeUsers


def create_message_json(json_ws) -> dict[str, any]:
    localtime = datetime.datetime.now()
    localtime_iso_8601 = localtime.isoformat()
    json_data = {
        "dateTime": localtime_iso_8601,
        "id": str(json_ws["u"]),
        "displayName": json_ws.get("ac"),
        "nickname": None,  # すぐ下で設定する
        "content": json_ws.get("cm", ""),
        "isFirst": False,
        "isFirstOnStream": None,  # すぐ下で設定する
        "noisy": False,
        # "additionalRequests": None,  # すぐ下で設定する
    }
    if "g" in json_ws:
        json_data["content"] += " ギフトをプレゼント！"
    if "ua" in json_ws and json_ws["ua"] == 2:
        json_data["isFirst"] = True
    OneCommeUsers.update_message_json(json_data)
    return json_data
