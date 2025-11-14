import asyncio, json, time
from data_creator.data_collector import create_friends_map_json
from data_creator.data_collector import create_friends_info_json
from centrality.centrality import get_centrality


ACCESS_TOKEN = 'vk1.a.k92dWl5YnAgjMzy4G1m4xzP9uQzbfq5EcZcMzulLDIrTAiHEn_XuemM4JVoF8qkuXiYFjpCJp3VFwpbElzoIrkhxqHGvw5zoYhVkTO-UPs2MQRLSfTvUcVAWyyxISvTP0SAYB7liQmXwNeRmVeTU9f8psigYSvLhh2xYlPvALWDl_SKr8fsPBcmQwqkR1AHHqMGz3AYFgHdetIvpvjHbpQ'
API_VERSION = '5.199'

async def get_all_data(
        start_uids: list[str],
        access_token: str,
        api_version: str,
        depth: int,
        file_out_friends_map: str,
        file_out_friends_info: str
):
    await create_friends_map_json(start_uids, access_token, api_version, depth, file_out_friends_map)
    await create_friends_info_json(access_token, api_version, file_out_friends_map, file_out_friends_info)\
    # pass

def fill_start_uids(file_name: str) -> list[str]:
    try:
        with open(file_name, 'r', encoding="utf-8") as f:
            uids = json.load(f)
    except FileNotFoundError as e:
        print(f"Ошибка открытия файла: {e}")
        return []

    filled_uids: list[str] = []
    for user_id, friends in uids.items():
        filled_uids.append(str(user_id))
        for friend_id in friends:
            filled_uids.append(str(friend_id))

    return filled_uids


START_UIDS = [
    "https://vk.com/lemoxxx",
    "https://vk.com/id154151541",
    "https://vk.com/fcmmp"
]
#START_UIDS = fill_start_uids("data/small_friends_map.json") # Тестовый вариант
file_out_friends_map = "data/friends_map.json"
file_out_name_info = "data/friends_info.json"

start = time.time()
asyncio.run(get_all_data(START_UIDS, ACCESS_TOKEN, API_VERSION, 2, file_out_friends_map, file_out_name_info))
print(f"\nВремя сбора данных составило: {time.time() - start}")

start = time.time()
get_centrality(file_out_friends_map)
print(f"\nВремя расчета центральностей составило: {time.time() - start}")