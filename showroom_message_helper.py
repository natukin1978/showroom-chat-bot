import datetime

from one_comme_users import OneCommeUsers


def create_message_json(comment) -> dict[str, any]:
    localtime = datetime.datetime.now()
    localtime_iso_8601 = localtime.isoformat()
    json_data = {
        "dateTime": localtime_iso_8601,
        "id": str(comment["user_id"]),
        "displayName": comment["name"],
        "nickname": None,  # すぐ下で設定する
        "content": comment["comment"],
        "isFirst": False,
        "isFirstOnStream": None,  # すぐ下で設定する
        "noisy": False,
        "additionalRequests": None,  # すぐ下で設定する
    }
    OneCommeUsers.update_message_json(json_data)
    return json_data


def create_message_json_from_ws(json_ws) -> dict[str, any]:
    localtime = datetime.datetime.now()
    localtime_iso_8601 = localtime.isoformat()
    json_data = {
        "dateTime": localtime_iso_8601,
        "id": str(json_ws["u"]),
        "displayName": json_ws["ac"],
        "nickname": None,  # すぐ下で設定する
        "content": "",  # すぐ下で設定する
        "isFirst": False,
        "isFirstOnStream": None,  # すぐ下で設定する
        "noisy": False,
        "additionalRequests": None,  # すぐ下で設定する
    }
    if "cm" in json_ws:
        json_data["content"] = json_ws["cm"]
    if "g" in json_ws:
        json_data["content"] += " ギフトをプレゼント！"
    OneCommeUsers.update_message_json(json_data)
    return json_data
