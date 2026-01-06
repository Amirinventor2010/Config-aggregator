from __future__ import annotations

import re
from typing import List
from urllib.parse import urlparse


URI_RE = re.compile(r'(?i)\b([a-z][a-z0-9+\-.]*://\S+)')


def is_vmess(uri: str) -> bool:
    return uri.strip().lower().startswith("vmess://")


def has_hash_name(uri: str) -> bool:
    return "#" in uri


def rewrite_uri_fixed_name(uri: str, fixed_name: str) -> str:
    base = uri.split("#", 1)[0].strip()
    return f"{base}#{fixed_name}"


def extract_candidate_uris(text: str) -> List[str]:
    if not text:
        return []
    return [m.group(1).strip() for m in URI_RE.finditer(text)]


def process_message(text: str, fixed_name: str) -> List[str]:
    uris = extract_candidate_uris(text)
    out: List[str] = []

    for uri in uris:
        if is_vmess(uri):
            continue
        if not has_hash_name(uri):
            continue
        out.append(rewrite_uri_fixed_name(uri, fixed_name))

    return out


def make_dedupe_key(uri: str) -> str:
    """
    Dedup فقط بر اساس UUID:
    - اگر username (UUID) داشت → scheme://uuid
    - اگر نداشت → کل URI بدون #
    """
    base = uri.split("#", 1)[0].strip()
    parsed = urlparse(base)

    scheme = (parsed.scheme or "").lower()
    username = parsed.username

    if scheme and username:
        return f"{scheme}://{username}"

    return base
