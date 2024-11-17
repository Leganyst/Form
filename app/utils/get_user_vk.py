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