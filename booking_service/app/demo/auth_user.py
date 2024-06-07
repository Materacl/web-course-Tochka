import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Header, HTTPException
from fastui.auth import AuthRedirect
from typing_extensions import Self
import httpx

JWT_SECRET = 'secret'


@dataclass
class User:
    email: str | None
    extra: dict[str, Any]

    def encode_token(self) -> str:
        payload = asdict(self)
        payload['exp'] = datetime.now() + timedelta(hours=1)
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256', json_encoder=CustomJsonEncoder)

    @classmethod
    async def from_request(cls, authorization: Annotated[str, Header()] = '') -> Self:
        user = await cls.from_request_opt(authorization)
        if user is None:
            raise AuthRedirect('/auth/login/password')
        else:
            return user

    @classmethod
    async def from_request_opt(cls, authorization: Annotated[str, Header()] = '') -> Self | None:
        try:
            token = authorization.split(' ', 1)[1]
        except IndexError:
            return None

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail='Invalid token')
        else:
            payload.pop('exp', None)
            return cls(**payload)

    @staticmethod
    async def fetch_token(username: str, password: str) -> str:
        async with httpx.AsyncClient(base_url='http://localhost:8000') as client:
            response = await client.post('/api/v1/auth/token',
                                         data={"username": username, "password": password})
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Incorrect email or password")
            token_data = response.json()
            return token_data['access_token']


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super().default(obj)


# Example usage of fetch_token (you can integrate this into your logic as needed)
async def get_user_token(email: str, password: str) -> str:
    token = await User.fetch_token(email, password)
    print(token)
    return token
