from datetime import (
    datetime,
    timedelta,
    timezone,
)

from jose import jwt

from passlib.context import CryptContext

from app.core.config import settings


# =====================================================
# Password Hashing
# =====================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# =====================================================
# Hash Password
# =====================================================

def hash_password(
    password: str,
) -> str:

    return pwd_context.hash(
        password
    )


# =====================================================
# Verify Password
# =====================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# =====================================================
# Create Access Token
# =====================================================

def create_access_token(
    data: dict,
) -> str:

    # -------------------------------------------------
    # Copy payload
    # -------------------------------------------------

    to_encode = data.copy()

    # -------------------------------------------------
    # Normalize role if supplied
    #
    # AuthService already supplies the role, but
    # normalizing here provides an additional safeguard.
    # -------------------------------------------------

    if "role" in to_encode:

        to_encode["role"] = (
            str(
                to_encode["role"]
            )
            .strip()
            .upper()
        )

    # -------------------------------------------------
    # Token expiration
    # -------------------------------------------------

    expire = (
        datetime.now(
            timezone.utc
        )
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    # -------------------------------------------------
    # JWT claims
    # -------------------------------------------------

    to_encode.update(
        {
            "exp": expire,
        }
    )

    # -------------------------------------------------
    # Encode JWT
    # -------------------------------------------------

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )