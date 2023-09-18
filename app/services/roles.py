from typing import List

from conf.messages import Msg
from db.models import User, UserRole
from fastapi import Depends, HTTPException, Request, status
from services.auth.user import AuthUser


class UserRoleAccess:
    def __init__(self, allowed_roles: List[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(AuthUser.get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_forbidden.value)


allowed_all_roles_access = UserRoleAccess([UserRole.ADMIN, UserRole.USER])
allowed_admin = UserRoleAccess([UserRole.ADMIN])
