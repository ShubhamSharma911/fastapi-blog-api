from jose import JWTError, jwt
from fastapi import Request, HTTPException
from functools import wraps
from app.config import settings
from app.database import SessionLocal
from app.models import User
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

def require_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid Authorization header",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = auth_header.split(" ")[1]

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("user_id")
                role = payload.get("role")

                if not user_id or not role:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Token missing user_id or role",
                    )

                if role not in allowed_roles:
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail=f"Access denied for role '{role}'",
                    )

                # Fetch user from DB safely
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        raise HTTPException(
                            status_code=HTTP_401_UNAUTHORIZED,
                            detail="User not found"
                        )
                    kwargs["current_user"] = user
                finally:
                    db.close()

            except JWTError:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator 