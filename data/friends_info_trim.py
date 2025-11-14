import json


with open('small_friends_map.json', 'r') as file:
    small_map = json.load(file)

allowed_ids = set(map(str, small_map.keys()))

with open('friends_info.json', 'r', encoding='utf-8') as file:
    all_info = json.load(file)

filtered_info = {uid: info for uid, info in all_info.items() if uid in allowed_ids}

with open('friends_info.json', 'w', encoding='utf-8') as file:
    json.dump(filtered_info, file, ensure_ascii=False, indent=2)

print(f"Сохранено {len(filtered_info)} пользователей в small_friends_info.json")
