import json

with open('friends_map.json', 'r') as file:
    data = json.load(file)

keep_keys = list(data.keys())[:150]
allowed = set(keep_keys)

result = {}
for i in keep_keys:
    friends = data.get(i, [])
    filtered_friends = [fid for fid in friends if str(fid) in allowed]
    if filtered_friends:
        result[i] = filtered_friends

with open('small_friends_map.json', 'w') as file:
    json.dump(result, file, ensure_ascii=False, indent=2)
