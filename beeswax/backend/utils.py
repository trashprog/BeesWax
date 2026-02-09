from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv
import hashlib
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')     # should be kept secret
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')      # should be kept secret

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_id(token):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])

def get_hashed_password(password: str) -> str:
    sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return password_context.hash(sha256)


def verify_password(password: str, hashed_pass: str) -> bool:
    sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return password_context.verify(sha256, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)


def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)

def hashDomain(domain):
    return hashlib.sha256(domain.encode()).hexdigest()[:5]

def update_date(coupon): # supposed to be run every day to update dates. not automated yet lol

    if coupon.get('startDate'):
        if coupon.get('startDate'):
                start = datetime.strptime(coupon['startDate'], '%d-%m-%Y')
                expiry = datetime.strptime(coupon['expiryDate'], '%d-%m-%Y')

                start = start.replace(year=datetime.now().year)
                expiry = expiry.replace(year=datetime.now().year)

                if start > expiry:
                    expiry = expiry.replace(year = datetime.now().year +1)

                if start <= datetime.now() <= expiry:
                    coupon['hidden'] = False
                else:
                    coupon['hidden'] = True


        elif datetime.now() > datetime.strptime(coupon['expiryDate'] , '%d-%m-%Y'):
            coupon['hidden'] = True

    if not coupon.get("hash"):
        coupon['hash'] = hashDomain(coupon.get('website'))

    return coupon

