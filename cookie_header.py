# -*- coding: utf-8 -*-
"""Pure helpers for converting Set-Cookie headers to a Cookie header."""

import re

try:
    text_type = unicode
except NameError:  # Python 3 test/runtime compatibility.
    text_type = str

COOKIE_NAME = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")
COOKIE_VALUE = re.compile(r"[\x21\x23-\x2b\x2d-\x3a\x3c-\x5b\x5d-\x7e]*\Z")


def _as_text(value):
    if isinstance(value, text_type):
        return value
    return text_type(value)


def extract_cookie_pairs(headers):
    """Return ordered (name, value) pairs from physical Set-Cookie headers.

    Each header is handled independently. In particular, values are never split
    on commas because an Expires attribute legitimately contains a comma.
    """
    pairs = []
    if headers is None:
        return pairs

    for header in headers:
        if header is None:
            continue
        header_text = _as_text(header)
        if "\r" in header_text or "\n" in header_text:
            continue
        colon_index = header_text.find(":")
        if colon_index <= 0:
            continue

        header_name = header_text[:colon_index]
        if header_name.lower() != "set-cookie":
            continue

        set_cookie_value = header_text[colon_index + 1:]
        semicolon_index = set_cookie_value.find(";")
        if semicolon_index >= 0:
            set_cookie_value = set_cookie_value[:semicolon_index]

        equals_index = set_cookie_value.find("=")
        if equals_index <= 0:
            continue

        cookie_name = set_cookie_value[:equals_index].strip(" \t")
        cookie_value = set_cookie_value[equals_index + 1:].strip(" \t")
        unquoted = cookie_value
        if len(cookie_value) >= 2 and cookie_value[0] == cookie_value[-1] == '"':
            unquoted = cookie_value[1:-1]
        if not COOKIE_NAME.match(cookie_name) or not COOKIE_VALUE.match(unquoted):
            continue

        pairs.append((cookie_name, cookie_value))

    return pairs


def build_cookie_header(headers):
    """Build a request-ready Cookie header, or an empty string if none exist."""
    return format_cookie_header(extract_cookie_pairs(headers))


def format_cookie_header(pairs):
    if not pairs:
        return ""

    cookie_value = "; ".join(
        "%s=%s" % (cookie_name, cookie_value)
        for cookie_name, cookie_value in pairs
    )
    return "Cookie: " + cookie_value
