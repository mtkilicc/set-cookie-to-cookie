# -*- coding: utf-8 -*-

import os
import sys
import unittest


PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIRECTORY not in sys.path:
    sys.path.insert(0, PROJECT_DIRECTORY)

from cookie_header import build_cookie_header, extract_cookie_pairs


class CookieHeaderTests(unittest.TestCase):
    def test_single_cookie_becomes_request_header(self):
        headers = [
            "HTTP/1.1 200 OK",
            "Set-Cookie: session=demo-only; Path=/; Secure; HttpOnly",
        ]

        self.assertEqual("Cookie: session=demo-only", build_cookie_header(headers))

    def test_multiple_physical_headers_keep_order(self):
        headers = [
            "HTTP/1.1 200 OK",
            "Set-Cookie: SID=abc; Path=/",
            "Set-Cookie: theme=dark; SameSite=Lax",
        ]

        self.assertEqual(
            "Cookie: SID=abc; theme=dark",
            build_cookie_header(headers),
        )

    def test_expires_comma_does_not_split_cookie(self):
        headers = [
            "HTTP/1.1 200 OK",
            "Set-Cookie: lang=en-US; Expires=Wed, 21 Oct 2030 07:28:00 GMT",
        ]

        self.assertEqual("Cookie: lang=en-US", build_cookie_header(headers))

    def test_equals_characters_in_value_are_preserved(self):
        headers = ["Set-Cookie: token=abc==; Path=/"]

        self.assertEqual("Cookie: token=abc==", build_cookie_header(headers))

    def test_empty_value_is_preserved(self):
        headers = ["Set-Cookie: logout=; Max-Age=0"]

        self.assertEqual("Cookie: logout=", build_cookie_header(headers))

    def test_duplicate_and_case_sensitive_names_are_preserved(self):
        headers = [
            "Set-Cookie: id=root; Path=/",
            "Set-Cookie: id=admin; Path=/admin",
            "Set-Cookie: ID=upper; Path=/",
        ]

        self.assertEqual(
            "Cookie: id=root; id=admin; ID=upper",
            build_cookie_header(headers),
        )

    def test_header_name_is_case_insensitive(self):
        headers = ["set-cookie: a=1", "SET-COOKIE: b=2"]

        self.assertEqual("Cookie: a=1; b=2", build_cookie_header(headers))

    def test_non_cookie_and_malformed_headers_are_ignored(self):
        headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            "Set-Cookie: no_equals",
            "Set-Cookie: =empty-name",
        ]

        self.assertEqual([], extract_cookie_pairs(headers))
        self.assertEqual("", build_cookie_header(headers))

    def test_invalid_pairs_are_skipped_without_changing_valid_ones(self):
        headers = [
            None,
            "Set-Cookie: a=1, b=2",
            " Set-Cookie: folded=value",
            "Set-Cookie: bad name=value",
            "Set-Cookie: bad=value\r\nX-Injected: synthetic",
            "Set-Cookie: bad=\"unclosed",
            "Set-Cookie: demo=\"value==\"; Secure",
            "Set-Cookie: empty=; Path=/",
        ]

        self.assertEqual('Cookie: demo="value=="; empty=', build_cookie_header(headers))


if __name__ == "__main__":
    unittest.main()
