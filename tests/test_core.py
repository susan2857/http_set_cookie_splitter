import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from http_set_cookie_splitter import parse_set_cookies, Cookie, ParseError


class TestParseSetCookies(unittest.TestCase):

    def test_none_returns_empty(self):
        self.assertEqual(parse_set_cookies(None), [])

    def test_single_string_is_one_header(self):
        h = "sid=abc123; Path=/; HttpOnly"
        cookies = parse_set_cookies(h)
        self.assertEqual(len(cookies), 1)
        c = cookies[0]
        self.assertEqual(c.name, "sid")
        self.assertEqual(c.value, "abc123")
        self.assertEqual(c.attributes["path"], "/")
        self.assertEqual(c.attributes["httponly"], "")

    def test_list_of_headers(self):
        cookies = parse_set_cookies(["a=1", "b=2"])
        self.assertEqual([c.name for c in cookies], ["a", "b"])
        self.assertEqual([c.value for c in cookies], ["1", "2"])

    def test_value_with_equals_signs(self):
        c = parse_set_cookies("data=a=b=c; Path=/")[0]
        self.assertEqual(c.name, "data")
        self.assertEqual(c.value, "a=b=c")
        self.assertEqual(c.attributes["path"], "/")

    def test_no_attributes(self):
        c = parse_set_cookies("plain=42")[0]
        self.assertEqual(c.name, "plain")
        self.assertEqual(c.value, "42")
        self.assertEqual(c.attributes, {})

    def test_secure_flag_has_empty_string_value(self):
        c = parse_set_cookies("sid=1; Secure")[0]
        self.assertEqual(c.attributes["secure"], "")

    def test_httponly_flag_has_empty_string_value(self):
        c = parse_set_cookies("sid=1; HttpOnly")[0]
        self.assertEqual(c.attributes["httponly"], "")

    def test_attribute_names_are_lowercased(self):
        c = parse_set_cookies("sid=1; SAMESITE=Strict; DOMAIN=example.org")[0]
        self.assertEqual(c.attributes["samesite"], "Strict")
        self.assertEqual(c.attributes["domain"], "example.org")

    def test_attribute_values_keep_case(self):
        c = parse_set_cookies("sid=1; Path=/App; Domain=Example.ORG")[0]
        self.assertEqual(c.attributes["path"], "/App")
        self.assertEqual(c.attributes["domain"], "Example.ORG")

    def test_surrounding_whitespace_stripped(self):
        c = parse_set_cookies("  sid = abc ;  Path = /  ")[0]
        self.assertEqual(c.name, "sid")
        self.assertEqual(c.value, "abc")
        self.assertEqual(c.attributes["path"], "/")

    def test_value_with_embedded_space_kept(self):
        c = parse_set_cookies("pref=dark mode; Path=/")[0]
        self.assertEqual(c.value, "dark mode")

    def test_empty_header_raises(self):
        with self.assertRaises(ParseError):
            parse_set_cookies("")

    def test_missing_equals_in_first_segment_raises(self):
        with self.assertRaises(ParseError):
            parse_set_cookies("just-a-cookie; Path=/")

    def test_empty_name_raises(self):
        with self.assertRaises(ParseError):
            parse_set_cookies("=value; Path=/")

    def test_empty_attribute_part_skipped(self):
        c = parse_set_cookies("sid=1;; Path=/;;")[0]
        self.assertEqual(c.attributes["path"], "/")

    def test_empty_attribute_key_skipped(self):
        c = parse_set_cookies("sid=1; =x; Path=/")[0]
        self.assertNotIn("", c.attributes)
        self.assertEqual(c.attributes["path"], "/")

    def test_flag_with_explicit_empty_value_treated_as_flag(self):
        c = parse_set_cookies("sid=1; Secure=")[0]
        self.assertEqual(c.attributes["secure"], "")

    def test_flag_with_value_keeps_value(self):
        # Secure is just an example here; the library treats ALL attributes
        # uniformly — there is no special flag list. A value means a value.
        c = parse_set_cookies("sid=1; Secure=yes")[0]
        self.assertEqual(c.attributes["secure"], "yes")

    def test_expires_value_with_comma_preserved_within_segment(self):
        # Each header string is one cookie. The comma here is inside a single
        # attribute value and survives because we split on ";", not ",".
        h = "token=abc; Expires=Wed, 09 Jun 2021 10:18:14 GMT; Path=/"
        c = parse_set_cookies(h)[0]
        self.assertEqual(c.attributes["expires"], "Wed, 09 Jun 2021 10:18:14 GMT")

    def test_cookie_return_type(self):
        c = parse_set_cookies("sid=1")[0]
        self.assertIsInstance(c, Cookie)

    def test_attributes_is_dict(self):
        c = parse_set_cookies("sid=1; Path=/")[0]
        self.assertIsInstance(c.attributes, dict)


if __name__ == "__main__":
    unittest.main()
