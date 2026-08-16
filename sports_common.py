import json
import os
import re
import unicodedata

import gspread
from google.oauth2.service_account import Credentials


def col_letter(idx: int) -> str:
    if idx < 26:
        return chr(65 + idx)
    return chr(64 + idx // 26) + chr(65 + idx % 26)


def get_gspread_client():
    """Authorize gspread from service-account JSON content or a key path."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    svc_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") or os.environ.get("GSPREAD_SERVICE_ACCOUNT_JSON")
    if svc_json:
        creds = Credentials.from_service_account_info(json.loads(svc_json), scopes=scopes)
        return gspread.authorize(creds)

    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path and os.path.exists(key_path):
        creds = Credentials.from_service_account_file(key_path, scopes=scopes)
        return gspread.authorize(creds)

    raise RuntimeError(
        "No Google credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON (JSON content) "
        "or GOOGLE_APPLICATION_CREDENTIALS (path to key file)."
    )


def normalize_confidence(val, allowed=("SMASH", "STRONG", "LEAN"), default="LEAN") -> str:
    conf = str(val or "").strip().upper()
    allowed_set = {str(item).strip().upper() for item in allowed}
    return conf if conf in allowed_set else str(default).strip().upper()


def normalize_person_name(value, *, keep_digits: bool = False, strip_chars: str = "") -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    if strip_chars:
        text = re.sub("[" + re.escape(strip_chars) + "]", "", text)
    pattern = r"[^a-z0-9 ]" if keep_digits else r"[^a-z ]"
    text = re.sub(pattern, " ", text)
    return re.sub(r"\s+", " ", text).strip()
