import json
import os
import re
import unicodedata

import gspread
import pandas as pd
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
        try:
            info = json.loads(svc_json)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"GOOGLE_SERVICE_ACCOUNT_JSON is set but isn't valid JSON ({e}). "
                "It must hold the full JSON key *content*, not a file path."
            ) from e
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)

    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path:
        if not os.path.exists(key_path):
            raise RuntimeError(
                f"GOOGLE_APPLICATION_CREDENTIALS points to a missing file: {key_path}"
            )
        creds = Credentials.from_service_account_file(key_path, scopes=scopes)
        return gspread.authorize(creds)

    raise RuntimeError(
        "No Google credentials found — neither GOOGLE_SERVICE_ACCOUNT_JSON nor "
        "GOOGLE_APPLICATION_CREDENTIALS is set (both were empty, not invalid).\n"
        "  • GitHub Actions: add a repo secret named GOOGLE_SERVICE_ACCOUNT_JSON "
        "containing the full service-account JSON content.\n"
        "  • Local: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json\n"
        "Then confirm the Sheet is shared with that key's client_email as Editor."
    )


def load_secret(name: str, prompt_text: str | None = None,
                allow_missing: bool = False) -> str:
    """Env var first, then optional interactive prompt for local runs."""
    env_val = os.environ.get(name)
    if env_val:
        return env_val
    if prompt_text:
        try:
            value = input(prompt_text).strip()
            if value:
                return value
        except (EOFError, KeyboardInterrupt):
            pass
    if allow_missing:
        print(f"⚠️  {name} not set — continuing without it")
        return ""
    raise RuntimeError(f"Missing required secret: {name}")


def load_sheet_grid(ws) -> tuple[list[str], list[list[str]]]:
    """Raw header + data rows, preserving sheet row position."""
    values = ws.get_all_values()
    if not values:
        return [], []
    return values[0], values[1:]


def safe_records_df(ws) -> pd.DataFrame:
    try:
        records = ws.get_all_records(default_blank="")
    except Exception:
        return pd.DataFrame()
    return pd.DataFrame(records or [])


def normalize_confidence(val, allowed=("SMASH", "STRONG", "LEAN"), default="LEAN") -> str:
    conf = str(val or "").strip().upper()
    allowed_set = {str(item).strip().upper() for item in allowed}
    return conf if conf in allowed_set else str(default).strip().upper()


def normalize_person_name(value, *, keep_digits: bool = False, strip_chars: str = "",
                          decompose_unicode: bool = True) -> str:
    text = str(value or "")
    if decompose_unicode:
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    if strip_chars:
        text = re.sub("[" + re.escape(strip_chars) + "]", "", text)
    pattern = r"[^a-z0-9 ]" if keep_digits else r"[^a-z ]"
    text = re.sub(pattern, " ", text)
    return re.sub(r"\s+", " ", text).strip()
