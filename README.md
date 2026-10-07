# HTTP Set-Cookie Splitter

Parses raw `Set-Cookie` header strings into a list of `Cookie` objects, separating each cookie's name-value pair from its attributes (Path, Domain, SameSite, HttpOnly, Secure, Expires, etc.).

## Usage

```python
from http_set_cookie_splitter import parse_set_cookies

cookies = parse_set_cookies(["sid=abc123; Path=/; HttpOnly", "lang=en; Secure"])
for c in cookies:
    print(c.name, c.value, c.attributes)
# sid abc123 {'path': '/', 'httponly': ''}
# lang en {'secure': ''}
```

The function accepts `None`, a single header string, or a list of strings. Each string is treated as exactly one `Set-Cookie` header. Returns a list of `Cookie` dataclass instances with fields `name`, `value`, and `attributes` (a `dict` mapping lowercased attribute names to string values; boolean flags like `HttpOnly` map to the empty string).

## Why this exists

When you read a raw HTTP response, `Set-Cookie` is awkward: there can be several of them, and each one is a semicolon-separated list with no quoting rule worth speaking of. This library does one narrow job — split name-value from attributes — and does not attempt cookie jar semantics, expiration computation, or validation against any cookie RFC. Attribute names are lowercased for case-insensitive lookup; attribute values are left untouched.

## The awkward edge

Each string passed in is one cookie. If you have a single string that concatenates multiple `Set-Cookie` headers with `", "`, this library will not split it for you — `Expires` values contain commas, so any automatic comma-join or comma-split is wrong by construction. Split into separate strings upstream (any real HTTP client gives you a list of header values already), then pass that list here.
