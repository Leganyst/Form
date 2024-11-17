from app.core.config import settings

import httpx

def get_user_full_name(user_id: int) -> str:
    """
    Получить полное имя пользователя ВКонтакте.

    :param user_id: ID пользователя VK.
    :return: Полное имя пользователя (ФИО) в формате "Имя Фамилия".
    """
    params = {
        "user_ids": user_id,
        "access_token": settings.application_secret_key,
        "v": "5.131"
    }
    
    try:
        response = httpx.get("https://api.vk.com/method/users.get", params=params)
        response.raise_for_status()  # Поднимает исключение, если статус код не 200
        data = response.json()

        if "response" in data:
            user_info = data["response"][0]
            full_name = f"{user_info['first_name']} {user_info['last_name']}"
            return full_name
        else:
            error_message = data.get("error", {}).get("error_msg", "Unknown error")
            raise ValueError(f"API Error: {error_message}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch user full name: {e}")
    

async def get_user_info(user_id: int) -> dict:
    """
    Получить информацию о пользователе ВКонтакте.

    :param user_id: ID пользователя VK.
    :return: Словарь с полным именем, vk_id и ссылкой на фото.
    """
    params = {
        "user_ids": user_id,
        "fields": "photo_200",  # Указываем поле для фотографии
        "access_token": settings.application_secret_key,
        "v": "5.131"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.vk.com/method/users.get", params=params)
            response.raise_for_status()
            data = response.json()

        if "response" in data:
            user_info = data["response"][0]
            return {
                "vk_id": user_info["id"],
                "full_name": f"{user_info['first_name']} {user_info['last_name']}",
                "photo_200": user_info.get("photo_200", None)
            }
        else:
            error_message = data.get("error", {}).get("error_msg", "Unknown error")
            raise ValueError(f"API Error: {error_message}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch user info: {e}")
