from passlib.context import CryptContext


class AuthPassword:

    @staticmethod
    def get_hash_password(password: str) -> str:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return pwd_context.verify(password, hashed_password)

