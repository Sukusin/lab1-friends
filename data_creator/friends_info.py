import asyncio, aiohttp, ssl, json
from data_creator.vk_api import vk_request
from datetime import datetime


MAX_CONCURRENT = 2

def load_json(json_name: str):
    try:
        with open(json_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError as e:
        print(f'Не удалось считать json! Ошибка: {e}')

def get_sex_display(sex_code: int) -> str:
    """Преобразует код пола в текст"""
    sex_map = {1: 'женский', 2: 'мужской', 0: 'не указан'}
    return sex_map.get(sex_code, 'не указан')

def calculate_age(bdate: str) -> int | None:
    """Вычисляет возраст по дате рождения"""
    if not bdate:
        return None

    try:
        # Форматы: "10.10.2007" или "10.10" (без года)
        parts = bdate.split('.')
        if len(parts) < 3:
            return None

        day, month, year = map(int, parts)
        today = datetime.now()
        age = today.year - year

        # Проверяем, был ли уже день рождения в этом году
        if (today.month, today.day) < (month, day):
            age -= 1

        return age

    except (ValueError, IndexError):
        return None

def process_career(career_data: list[dict]) -> list[dict]:
    """Обрабатывает данные о карьере"""
    processed = []
    for job in career_data:
        processed_job = {
            'company': job.get('company'),
            'position': job.get('position'),
            'start_year': job.get('from'),
            'end_year': job.get('until')
        }
        # Убираем пустые значения
        processed_job = {k: v for k, v in processed_job.items() if v is not None}
        if processed_job:
            processed.append(processed_job)

    return processed

def process_universities(universities_data: list[dict]) -> list[dict]:
    """Обрабатывает данные об университетах"""
    processed = []
    for uni in universities_data:
        processed_uni = {
            'name': uni.get('name'),
            'city': uni.get('city_name'),
            'graduation': uni.get('graduation')
        }
        processed_uni = {k: v for k, v in processed_uni.items() if v is not None}
        if processed_uni:
            processed.append(processed_uni)
    return processed

def count_non_empty_interests(user: dict) -> int:
    """Считает количество заполненных интересов"""
    interest_fields = ['activities', 'interests', 'music', 'movies', 'books', 'games']
    return sum(1 for field in interest_fields if user.get(field))

def extract_basic_info(user: dict) -> dict:
    """Извлекает базовую информацию"""
    return {
        'id': user.get('id'),
        'first_name': user.get('first_name'),
        'last_name': user.get('last_name'),
        'domain': user.get('domain'),
        'is_closed': user.get('is_closed', False)
    }

def extract_demographics(user: dict) -> dict:
    """Извлекает демографические данные"""
    return {
        'sex': get_sex_display(user.get('sex')),
        'birth_date': user.get('bdate'),
        'age': calculate_age(user.get('bdate')),
        'city': user.get('city', {}).get('title') if user.get('city') else None,
        'country': user.get('country', {}).get('title') if user.get('country') else None
    }

def extract_education_career(user: dict) -> dict:
    """Извлекает данные об образовании и карьере"""
    return {
        'education': {
            'university': user.get('university_name'),
            'faculty': user.get('faculty_name'),
            'graduation': user.get('graduation')
        },
        'career': process_career(user.get('career', [])),
        'universities': process_universities(user.get('universities', []))
    }

def extract_social_connections(user: dict) -> dict:
    """Извлекает социальные связи"""
    connections = user.get('connections', {})
    return {
        'skype': connections.get('skype'),
        'facebook': connections.get('facebook'),
        'twitter': connections.get('twitter'),
        'instagram': connections.get('instagram')
    }

def extract_interests(user: dict) -> dict:
    """Извлекает интересы и увлечения"""
    return {
        'activities': user.get('activities'),
        'interests': user.get('interests'),
        'music': user.get('music'),
        'movies': user.get('movies'),
        'books': user.get('books'),
        'games': user.get('games')
    }

def extract_metadata(user: dict) -> dict:
    """Извлекает метаданные"""
    return {
        'data_retrieved': datetime.now().isoformat(),
        'has_education': bool(user.get('university_name')),
        'has_career': bool(user.get('career')),
        'interests_count': count_non_empty_interests(user)
    }

def process_users_data(users_data: dict) -> list:
    """Обрабатывает и структурирует данные пользователей"""
    processed_users = []

    for user in users_data:
        processed_user = {
            'basic_info': extract_basic_info(user),
            'demographics': extract_demographics(user),
            'education_career': extract_education_career(user),
            'social_connections': extract_social_connections(user),
            'interests': extract_interests(user),
            'metadata': extract_metadata(user)
        }
        processed_users.append(processed_user)

    return processed_users

async def create_friends_info(
        access_token: str = '',
        api_version: str = '',
        file_friends_map: str = ''
) -> dict | None:
    data = load_json(file_friends_map)

    uids = set()
    for uid, friends in data.items():
        uids.add(uid)
        for friend in friends:
            uids.add(friend)
    uids = list(uids)

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            sem = asyncio.Semaphore(MAX_CONCURRENT)
            processed_data: dict[int, list] = {}

            async def process(_uids: list[int]):
                fields = (
                        'sex,bdate,city,country,'
                        'education,career,connections,'
                        'activities,interests,music,'
                        'movies,books,games'
                )

                async with sem:
                    user_data_list = await vk_request(
                       session,
                       'users.get',
                       {'user_ids': ','.join(map(str, _uids)) , 'fields': fields},
                       access_token,
                       api_version
                    )

                    processed_user = process_users_data(user_data_list)
                    for user_obj in processed_user:
                        _uid = user_obj['basic_info']['id']
                        processed_data[_uid] = user_obj

            batch_size = 100
            uid_batches = [uids[i:i + batch_size] for i in range(0, len(uids), batch_size)]

            await asyncio.gather(*[process(batch) for batch in uid_batches])

            return processed_data

    except aiohttp.ClientError as e:
        print(f'Ошибка сессии: {e}')
        return None