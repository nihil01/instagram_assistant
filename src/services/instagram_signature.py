import hmac
import hashlib
from config.app_config import settings


def verify_signature(body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False

    try:
        sha_name, signature = signature_header.split("=")
    except ValueError:
        return False

    if sha_name != "sha256":
        return False

    expected = hmac.new(
        settings.INSTAGRAM_APP_SECRET.encode(),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)