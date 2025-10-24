from data_creator.friends_map_creator import create_friends_map
from data_creator.friends_info import create_friends_info
import json


async def create_friends_map_json(
        start_links: list[str],
        access_token: str = '',
        api_version: str = '',
        depth: int = 2,
        file_out_name: str = ''
):
    friends_map = await create_friends_map(start_links, depth, access_token, api_version)
    if friends_map:
        try:
            with open(file_out_name, "w", encoding='utf-8') as f:
                json.dump(friends_map, f, ensure_ascii=False, indent=2)
                print(f"\nСохранено в {file_out_name}")
        except FileNotFoundError as e:
            print(f'\nОшибка открытия json файла: {e}')
    else:
        print(f'Не удалось создать dataset {file_out_name}')

async def create_friends_info_json(
        access_token: str = '',
        api_version: str = '',
        file_friends_map: str = '',
        file_out_name: str = ''
):
    friends_info = await create_friends_info(access_token, api_version, file_friends_map)
    if friends_info:
        try:
            with open(file_out_name, "w", encoding='utf-8') as f:
                json.dump(friends_info, f, ensure_ascii=False, indent=2)
                print(f"\nДанные {len(friends_info)} пользователей сохранены в {file_out_name}")
        except FileNotFoundError as e:
            print(f'\nОшибка открытия json файла: {e}')
    else:
        print(f'Не удалось создать dataset {file_out_name}')
