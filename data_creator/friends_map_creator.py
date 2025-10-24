import asyncio, aiohttp, ssl
from data_creator.vk_api import vk_request


MAX_CONCURRENT = 2

async def user_url_to_id(
        session,
        user_url: str,
        access_token: str = '',
        api_version: str = ''
) -> int | None:
    name = user_url.split('/')[-1]

    result = await vk_request(
        session,
        'users.get',
        {'user_id': name},
        access_token,
        api_version
    )

    if result:
        return result[0]["id"]

    return None

async def create_friends_map(
        start_uids: list[str],
        depth: int = 2,
        access_token: str = '',
        api_version: str = ''
) -> dict[int, list[int]]:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            friends_map: dict[int, list[int]] = {}
            uids_to_visit = set()
            uids_is_visited = set()

            for uid in start_uids:
                uid = await user_url_to_id(session, uid, access_token, api_version)
                if uid is not None:
                    uids_to_visit.add(uid)

            sem = asyncio.Semaphore(MAX_CONCURRENT)

            for level in range(depth):
                new_uids_to_visit = set()
                async def process(_uid: int):
                    async with sem:
                        try:
                            response = await vk_request(session,
                                                 'friends.get',
                                                 {'user_id': _uid},
                                                 access_token,
                                                 api_version
                            )

                            if response:
                                friends = response.get('items', [])
                            else:
                                friends_map[_uid] = []

                            friends_map[_uid] = friends
                            new_uids_to_visit.update(friends)

                        except Exception as e:
                            pass

                await asyncio.gather(*[process(uid) for uid in uids_to_visit])
                uids_is_visited.update(uids_to_visit)
                uids_to_visit = new_uids_to_visit - uids_is_visited

            return friends_map

    except aiohttp.ClientError as e:
        print(f'Ошибка сессии: {e}')
        return {}