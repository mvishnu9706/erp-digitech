from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.user import (
    UserCreate,
    AdminUserCreate,
    UserUpdate,
    UserResponse,
    PasswordChangeRequest,
)

from app.services.user_service import (
    UserService,
)

from app.core.dependencies import (
    get_current_admin,
    get_current_super_admin,
)


# =====================================================
# Router
# =====================================================

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# =====================================================
# CREATE USER
# =====================================================
#
# POST /users/
#
# ADMIN / SUPER_ADMIN can create users.
#
# CUSTOMER users:
#
#     customer_id is REQUIRED
#
# Example:
#
# {
#     "full_name": "ABC Customer",
#     "email": "abc@gmail.com",
#     "phone": "9876543210",
#     "password": "123456",
#     "role": "CUSTOMER",
#     "customer_id": 5
# }
#
# This links:
#
# users.id
#      ↓
# users.customer_id
#      ↓
# customers.id
#
# =====================================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
)
def create_user(
    user: UserCreate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    return UserService.create_user(
        db=db,
        data=user,
        current_user=current_user,
    )


# =====================================================
# CREATE USER WITH ROLE
# =====================================================
#
# POST /users/with-role
#
# SUPER_ADMIN:
#     Can create any role.
#
# ADMIN:
#     Can create any role except SUPER_ADMIN.
#
# CUSTOMER:
#     customer_id is REQUIRED.
#
# =====================================================

@router.post(
    "/with-role",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User With Role",
)
def create_user_with_role(
    user: AdminUserCreate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    return UserService.create_user(
        db=db,
        data=user,
        current_user=current_user,
    )


# =====================================================
# GET ALL USERS
# =====================================================
#
# GET /users/
#
# ADMIN / SUPER_ADMIN only.
#
# The response now also contains customer_id through
# UserResponse.
#
# =====================================================

@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Get All Users",
)
def get_users(
    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    return UserService.get_users(
        db
    )


# =====================================================
# GET USER BY ID
# =====================================================
#
# GET /users/{user_id}
#
# ADMIN / SUPER_ADMIN only.
#
# =====================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User",
)
def get_user(
    user_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    user = UserService.get_user(
        db,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    return user


# =====================================================
# UPDATE USER
# =====================================================
#
# PUT /users/{user_id}
#
# Can update:
#
# - Company Name
# - Contact Person Name
# - Full Name
# - Email
# - Phone
# - Role
# - Customer ID
# - Active Status
#
# CUSTOMER USER:
#
#     customer_id can be changed.
#
# =====================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update User",
)
def update_user(
    user_id: int,

    user: UserUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    updated_user = UserService.update_user(
        db=db,
        user_id=user_id,
        data=user,
        current_user=current_user,
    )

    if not updated_user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    return updated_user


# =====================================================
# CHANGE USER PASSWORD
# =====================================================
#
# PUT /users/{user_id}/password
#
# SUPER_ADMIN:
#     Can change any user's password.
#
# ADMIN:
#     Can change every user's password except
#     SUPER_ADMIN.
#
# ENGINEER / CUSTOMER / SALES_PERSON:
#     Not allowed.
#
# =====================================================

@router.put(
    "/{user_id}/password",
    status_code=status.HTTP_200_OK,
    summary="Change User Password",
)
def change_user_password(
    user_id: int,

    password_data: PasswordChangeRequest,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    updated_user = UserService.change_password(
        db=db,
        user_id=user_id,
        data=password_data,
        current_user=current_user,
    )

    if not updated_user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    return {
        "success": True,

        "message": (
            "Password Changed Successfully"
        ),

        "user_id": updated_user.id,
    }


# =====================================================
# DELETE USER
# =====================================================
#
# DELETE /users/{user_id}
#
# ONLY SUPER_ADMIN can permanently delete users.
#
# =====================================================

@router.delete(
    "/{user_id}",
    summary="Delete User",
)
def delete_user(
    user_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_super_admin
    ),
):

    # ---------------------------------------------
    # Prevent Self Deletion
    # ---------------------------------------------

    if current_user.id == user_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "You cannot delete your own account"
            ),
        )

    # ---------------------------------------------
    # Delete User
    # ---------------------------------------------

    deleted = UserService.delete_user(
        db,
        user_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    return {
        "success": True,

        "message": (
            "User Deleted Successfully"
        ),
    }