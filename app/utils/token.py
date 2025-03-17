import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
secret_key = "my_secret_key"

def generate_token(user_id: int, expires_in: int = 24) -> str:
    token_data = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_in)
    }
    token = jwt.encode(token_data, secret_key, algorithm="HS256")
    return token

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")