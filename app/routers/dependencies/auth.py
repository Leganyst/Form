from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from app.core.config import settings
from app.crud.group import get_group_by_vk_id
from app.core.database import get_db

from hashlib import sha256
from hmac import HMAC
from base64 import b64encode
from urllib.parse import urlparse, parse_qsl, urlencode


async def get_token(authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
    """
    Зависимость для получения строки авторизации из заголовка Authorization
    """
    return authorization.credentials


async def check_valid_token(token: str = Depends(get_token)) -> bool:
    """
    Зависимость для проверки токена
    """
    """
    Функция аутентификации, расшифровывающая по частям
    строку токена пользователя, а затем сверяющего подпись.
    Результат сверки подписи возвращается обратно.
    """
    
    query_params = dict(
        parse_qsl(
            urlparse(token).query,
            keep_blank_values=True
        )
    )
    
    if not query_params.get("sign"):
        return False
    
    vk_subset = sorted(
        filter(
            lambda key: key.startswith("vk_"),
            query_params
        )
    )
    ordered = {k: query_params[k] for k in vk_subset}
    hash_code = b64encode(
        HMAC(
            settings.application_secret_key.encode(),
            urlencode(ordered, doseq=True).encode(),
            sha256
        ).digest()
    ).decode("utf-8")

    if hash_code[-1] == "=":
        hash_code = hash_code[:-1]

    fixed_hash = hash_code.replace('+', '-').replace('/', '_')
    return query_params.get("sign") == fixed_hash


async def get_query_params(token: str = Depends(get_token)) -> dict:
    """
    Зависимость для получения параметров запроса
    """
    query_params = dict(
        parse_qsl(
            urlparse(token).query,
            keep_blank_values=True
        )
    )
    return query_params


async def verification_group(token_is_valid: bool = Depends(check_valid_token), token: str = Depends(get_token), session: AsyncSession = Depends(get_db)):
    """
    Зависимость для проверки токена и получения пользователя
    """
    if not token_is_valid:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
    query_params = await get_query_params(token)
    group_id = query_params.get("vk_group_id")
    
    if not group_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    
    group = await get_group_by_vk_id(session, group_id) 
    if not group:
        return None

    return group


async def get_group_depend(group: dict = Depends(verification_group)):
    """
    Зависимость для получения пользователя
    """
    return group