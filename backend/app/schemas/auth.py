from typing import Optional

from pydantic import BaseModel, Field


# =====================================================
# Login Request
# =====================================================
#
# The user can login using either:
#
# Email:
#     admin@digitech.com
#
# OR Mobile:
#     9876500011
#
# Password is required in both cases.
#
# =====================================================

class LoginRequest(BaseModel):

    identifier: str = Field(
        ...,
        min_length=3,
        max_length=150,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


# =====================================================
# Login Response
# =====================================================
#
# CUSTOMER:
#
#     role = CUSTOMER
#     customer_id = linked customers.id
#
# ADMIN / ENGINEER / SALES_PERSON:
#
#     customer_id = None
#
# =====================================================

class Token(BaseModel):

    access_token: str

    token_type: str

    role: str

    customer_id: Optional[int] = None