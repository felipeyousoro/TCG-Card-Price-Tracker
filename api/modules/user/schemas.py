from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...common.schemas import PersistentDeletion, TimestampSchema


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[
        str,
        Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"]),
    ]


class User(TimestampSchema, UserBase, PersistentDeletion):
    """Complete user model with all fields."""

    hashed_password: str
    # is_superuser: bool = False
    profile_image_url: Annotated[
        str,
        Field(
            default="https://www.profileimageurl.com",
            description="URL of the user's profile image",
        ),
    ]
    # tier_id: int | None = None


class UserRead(BaseModel):
    """Schema for reading user data, excludes sensitive information."""

    id: int
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[
        str,
        Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"]),
    ]
    profile_image_url: str
    is_deleted: bool = False
    # tier_id: int | None
    # is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: Annotated[
        str,
        Field(
            min_length=8,
            description=(
                "Password must be at least 8 characters long and include a number,"
                "uppercase letter, lowercase letter, and special character"
            ),
            examples=["Str1ngst!"],
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
        ),
    ]

    model_config = ConfigDict(extra="forbid")


class UserCreateInternal(UserBase):
    """Internal schema for user creation with hashed password."""

    hashed_password: str


class UserUpdate(BaseModel):
    """Schema for updating user data."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str | None,
        Field(min_length=2, max_length=30, examples=["User Userberg"], default=None),
    ]
    username: Annotated[
        str | None,
        Field(
            min_length=2,
            max_length=20,
            pattern=r"^[a-z0-9]+$",
            examples=["userberg"],
            default=None,
        ),
    ]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            examples=["https://www.profileimageurl.com"],
            default=None,
        ),
    ]


class UserUpdateInternal(UserUpdate):
    """Internal schema for user updates."""

    updated_at: datetime


class UserTierUpdate(BaseModel):
    """Schema for updating a user's tier."""

    tier_id: int


class UserDelete(BaseModel):
    """Schema for soft-deleting a user."""

    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserAnonymize(BaseModel):
    """Schema for GDPR/LGPD compliant user anonymization.

    This schema includes all fields that need to be updated during
    the user anonymization process for privacy compliance.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    username: str
    hashed_password: str | None = None
    profile_image_url: str | None = None
    # tier_id: int | None = None
    # is_superuser: bool = False

class UserRestoreDeleted(BaseModel):
    """Schema for restoring a deleted user."""

    is_deleted: bool