import uuid
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer

import jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)

passwd_context = CryptContext(schemes=["bcrypt"])
ACCESS_TOKEN_EXPIRY = 3600

def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def generate_passwd_hash(password: str) -> str:
    hash = passwd_context.hash(password)
    logger.debug("Password hash generated")
    return hash

def verify_password(password: str, hash: str) -> bool:
    result = passwd_context.verify(password, hash)
    if not result:
        logger.warning("Password verification failed")
    return result

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {
        "user": user_data,
        "exp": datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    token_type = "refresh" if refresh else "access"
    logger.info(f"Created {token_type} token for user: {user_data.get('email', 'unknown')}")
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        logger.debug(f"Token decoded successfully for user: {token_data.get('user', {}).get('email', 'unknown')}")
        return token_data
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.exception(f"Error decoding token: {str(e)}")
        return None

email_verification_serializer = URLSafeTimedSerializer(
    secret_key=settings.JWT_SECRET, 
    salt="email-verification"
)

password_reset_serializer = URLSafeTimedSerializer(
    secret_key=settings.JWT_SECRET, 
    salt="password-reset"
)

def create_url_safe_token(data: dict, purpose: str = "email-verification"):
    """Create a URL-safe token for email verification or password reset."""
    serializer = email_verification_serializer if purpose == "email-verification" else password_reset_serializer
    token = serializer.dumps(data)
    logger.info(f"URL safe token created for: {data.get('email', 'unknown')} (purpose: {purpose})")
    return token

def decode_url_safe_token(token: str, purpose: str = "email-verification"):
    """Decode a URL-safe token for email verification or password reset."""
    try:
        serializer = email_verification_serializer if purpose == "email-verification" else password_reset_serializer
        token_data = serializer.loads(token)
        logger.info(f"URL safe token decoded successfully for: {token_data.get('email', 'unknown')} (purpose: {purpose})")
        return token_data
    except Exception as e:
        logger.error(f"Error decoding URL safe token: {str(e)}")
        return None

async def send_email(to_addresses, subject, html_content):
    """Send email using Gmail SMTP."""
    try:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured, skipping email send")
            return True

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        logger.info(f"Attempting to send email to: {to_addresses}")
        
        msg = MIMEMultipart()
        msg['From'] = f"{settings.APP_NAME} <{settings.SMTP_USERNAME}>"
        msg['To'] = ", ".join(to_addresses)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to: {to_addresses}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False