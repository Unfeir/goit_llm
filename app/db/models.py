import enum

from sqlalchemy import Boolean, Column, Enum, func, Integer, String
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import ForeignKey

from db.db import Base


class PDFfile(Base):
    __tablename__ = 'pdffiles'
    id = Column(Integer, primary_key=True)
    filename = Column(String(50), nullable=False, unique=False)
    context = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserRole(enum.Enum):
    ADMIN: str = 'admin'
    USER: str = 'user'



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(30), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    avatar = Column(String(500), nullable=True)
    role = Column('role', Enum(UserRole), default=UserRole.USER)
    confirmed = Column(Boolean, default=True)
    status_active = Column(Boolean, default=True)

    __mapper_args__ = {"eager_defaults": True}

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role.value,
            'status_active': self.status_active
        }

    @property
    def mapper(self) -> dict:
        return {
            'username': 'username',
            'email': 'email',
            'password': 'password',
            'avatar': 'avatar',
            'role': 'role',
            'confirmed': 'confirmed',
            'status_active': 'status_active',
        }
