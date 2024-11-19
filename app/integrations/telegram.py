import httpx
from typing import List
from app.core.config import settings

TELEGRAM_BOT_TOKEN = settings.telegram_bot_token
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

async def send_telegram_message(message: str, chat_ids: List[int]) -> None:
    """
    Отправить сообщение через Telegram бот.

    :param message: Текст сообщения.
    :param chat_ids: Список ID аккаунтов, куда отправить сообщение.
    """
    async with httpx.AsyncClient() as client:
        for chat_id in chat_ids:
            try:
                response = await client.post(
                    TELEGRAM_API_URL,
                    json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
                )
                response.raise_for_status()  # Проверяем, нет ли ошибок
            except httpx.HTTPError as exc:
                print(f"Ошибка при отправке сообщения пользователю {chat_id}: {exc}")
