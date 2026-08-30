from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash_pwd(password: str):
    return pwd_context.hash(password)

def verify_pwd(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)