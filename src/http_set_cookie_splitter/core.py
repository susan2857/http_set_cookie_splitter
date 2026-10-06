from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Union

__all__ = ["Cookie", "ParseError", "parse_set_cookies"]


@dataclass
class Cookie:
    """One parsed Set-Cookie header.

    name:       cookie name.
    value:      cookie value (raw, including any equals signs after the first).
    attributes: map of lowercased attribute name -> string value.
                Flags like HttpOnly carry the empty string as their value, making
                the map homogeneous and avoiding the presence/absence ambiguity
                that plagues optional dict values.
    """
    name: str
    value: str
    attributes: Dict[str, str]


class ParseError(Exception):
    """Raised when a Set-Cookie header is structurally malformed."""
    pass


def parse_set_cookies(headers: Union[str, List[str], None]) -> List[Cookie]:
    """Parse one or more Set-Cookie headers into Cookie objects.

    Accepts None (returns []), a single header string, or a list of strings
    (the form a real HTTP library typically exposes). Each string is treated as
    exactly one Set-Cookie header; callers are responsible for the split-point
    between headers — joining on ", " is not attempted because Expires dates
    embed commas and any join rule produces a class of cookies that silently
    vanish.
    """
    if headers is None:
        return []
    if isinstance(headers, str):
        raw_list: List[str] = [headers]
    else:
        raw_list = list(headers)
    return [_parse_one(h) for h in raw_list]


_FLAGS = {"httponly", "secure"}


def _parse_one(header: str) -> Cookie:
    if header is None:
        raise ParseError("Set-Cookie value was None")
    if not isinstance(header, str):
        raise ParseError(
            "Set-Cookie must be a str, got %s" % type(header).__name__
        )
    s = header.strip()
    if not s:
        raise ParseError("empty Set-Cookie header")
    # Split off the first segment (name=value). We use split with maxsplit=1
    # because attribute separators are semicolons, not whitespace, so a
    # cookie value may legally contain spaces.
    if ";" in s:
        first, rest = s.split(";", 1)
    else:
        first, rest = s, ""
    first = first.strip()
    if "=" not in first:
        raise ParseError(
            "Set-Cookie first segment lacks '=': %r" % first
        )
    name, _, value = first.partition("=")
    name = name.strip()
    value = value.strip()
    if not name:
        raise ParseError("empty cookie name in %r" % header)
    attrs: Dict[str, str] = {}
    if rest:
        for part in rest.split(";"):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                k, _, v = part.partition("=")
                k = k.strip().lower()
                v = v.strip()
                if not k:
                    continue
                if k in _FLAGS and v == "":
                    attrs[k] = ""
                else:
                    attrs[k] = v
            else:
                key = part.lower()
                if key:
                    attrs[key] = ""
    return Cookie(name=name, value=value, attributes=attrs)
