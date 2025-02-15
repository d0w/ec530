
from typing import Optional
from enum import Enum

class UserPrivilege(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User:
    def __init__(
        self, 
        id: int,
        name: str,
        username: str,
        email: str,
        phone: str,
        privilege: UserPrivilege
    ):
        self.id = id
        self.name = name
        self.username = username
        self.email = email
        self.phone = phone
        self.privilege = privilege

        # add password later