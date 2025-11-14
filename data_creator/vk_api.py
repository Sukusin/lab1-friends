import asyncio, aiohttp, sys
from enum import Enum


API_URL = 'https://api.vk.com/method/'

class APIError(Enum):
    NONE = 0
    RETRY = 1
    CRITICAL = 2

async def check_api_error(data: dict) -> APIError:
    error = data.get('error')
    if not error:
        return APIError.NONE

    if error.get('error_code') == 6:
        '''Ошибка слишком частых запросов в сек'''
        return APIError.RETRY
    elif error.get('error_code') == 30:
        '''Ошибка, что пользователь в бане'''
        return APIError.NONE
    elif error.get('error_code') == 18:
        '''Ошибка, что у пользователя закрытый профиль'''
        return APIError.NONE
    else:
        print(f"code: {error['error_code']} - {error['error_msg']}")
        return APIError.CRITICAL

async def vk_request(
        session: aiohttp.ClientSession,
        method: str,
        params: dict,
        access_token: str,
        api_version: str,
        retries: int = 5
) -> dict:
    params = params.copy()
    params.update({'access_token': access_token, 'v': api_version})

    for attempt in range(retries):
        try:
            async with session.get(url=API_URL + method, params=params) as response:
                data = await response.json()
                error_type = await check_api_error(data)

                if error_type == APIError.RETRY:
                    timeout = 0.33 * (attempt + 1)
                    await asyncio.sleep(timeout)
                    continue
                elif error_type == APIError.CRITICAL:
                    print('Поймана критическая ошибка API! Завершаем программу!')
                    sys.exit(-13)

                return data.get('response', {})

        except aiohttp.ClientError as e:
            print(f'Ошибка сети: {e}')
        except Exception as e:
            print(f'Неожиданная ошибка: {e}')
        except SystemExit as e:
            sys.exit(e.code)

        await asyncio.sleep(1)

    return {}