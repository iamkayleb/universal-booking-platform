from datetime import datetime, timedelta
import os
from jose import jwt # The tool that makes the tokens
from passlib.context import CryptContext

# 1. CONFIGURATION
# In a real app, this secret key should be hidden in an environment variable!
# For now, we will use a hardcoded random string.
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 2. THE WRISTBAND MAKER
def create_access_token(data: dict):
    """
    Creates a digital token that expires in 30 minutes.
    """
    to_encode = data.copy()
    
    # Set expiration time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create the encoded token using our Secret Key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt