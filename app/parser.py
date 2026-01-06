from __future__ import annotations

import re
from typing import List, Optional


# هر چیزی که شبیه scheme://something باشه (تا اولین فاصله)
# توی کانال‌های کانفیگ معمولاً لینک‌ها جداگانه میاد، اما این حالت هم امنه.
URI_RE = re.compile(r'(?i)\b([a-z][a-z0-9+\-.]*://\S+)')


def is_vmess(uri: str) -> bool:
    return uri.strip().lower().startswith("vmess://")


def has_hash_name(uri: str) -> bool:
    return "#" in uri


def rewrite_uri_fixed_name(uri: str, fixed_name: str) -> str:
    """
    هرچی بعد از اولین # حذف، و یک نام ثابت جایگزین می‌شود.
    """
    base = uri.split("#", 1)[0]
    return f"{base}#{fixed_name}"


def extract_candidate_uris(text: str) -> List[str]:
    """
    از متن پیام، URIهای کاندید را استخراج می‌کند.
    """
    if not text:
        return []
    return [m.group(1).strip() for m in URI_RE.finditer(text)]


def process_message(text: str, fixed_name: str) -> List[str]:
    """
    خروجی: لیست کانفیگ‌های قابل قبول و rename شده.
    قوانین:
      - vmess حذف
      - بدون # حذف
      - باقی: rename ثابت
    """
    uris = extract_candidate_uris(text)
    out: List[str] = []
    for uri in uris:
        if is_vmess(uri):
            continue
        if not has_hash_name(uri):
            continue
        out.append(rewrite_uri_fixed_name(uri, fixed_name))
    return out
