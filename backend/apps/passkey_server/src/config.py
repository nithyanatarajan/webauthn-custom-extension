import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


class Config:
    # WebAuthn RP config
    RP_ID = os.getenv('RP_ID', 'localhost')
    RP_NAME = os.getenv('RP_NAME', 'Passkey POC')
    ORIGIN = os.getenv('ORIGIN', 'http://localhost:8000')

    # JWT settings
    JWT_ISSUER = 'relying-party'
    JWT_ORIGINAL_ISSUER = 'identity-provider'
    JWT_AUDIENCE = 'relying-party-server'
    JWT_SECRET = os.getenv('JWT_SECRET', 'super-secure-token')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRY_SECONDS = int(os.getenv('JWT_EXPIRY', '60'))  # Default to 60 seconds
    JWT_LEEWAY_SECONDS = 30

    # CORS (optional)
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')

    USER_KEY = 'user'
    ACCOUNT_ID_KEY = 'account_id'
