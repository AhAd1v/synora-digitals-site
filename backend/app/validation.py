import re

# Mirrors consult.html's client-side looksLikeValidEmail/looksLikeRealName/
# looksLikeValidPhone — the client checks exist for instant UX feedback, but
# a request can always bypass the browser entirely (curl, a script, a
# modified page), so every one of these is re-checked here independently.

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

KEYBOARD_MASH = {
    "qwerty", "qwertyuiop", "asdf", "asdfgh", "asdfghjkl",
    "zxcv", "zxcvbn", "zxcvbnm", "asdasd", "qweqwe",
}
NAME_CHARS_RE = re.compile(r"^[a-zA-ZÀ-ſ' -]+$")
VOWEL_RE = re.compile(r"[aeiouAEIOUÀ-ſ]")
CONSONANT_RUN_RE = re.compile(r"[^aeiouAEIOU'-]{5,}", re.IGNORECASE)
REPEATED_CHAR_RE = re.compile(r"(.)\1{3,}")

# Same approximate national-number digit-count ranges as the client's
# PHONE_DIGIT_RANGES in consult.html — not authoritative telecom rules, just
# enough to catch an obviously wrong/incomplete number for the chosen
# country. +1 extra digit tolerated for users who type the local leading 0
# alongside the country code.
PHONE_DIGIT_RANGES = {
    "+92": (10, 11), "+971": (8, 9), "+966": (8, 9), "+974": (7, 8), "+965": (7, 8),
    "+973": (7, 8), "+968": (7, 8), "+44": (9, 10), "+49": (6, 11), "+33": (9, 9),
    "+31": (9, 9), "+34": (9, 9), "+39": (8, 10), "+46": (7, 10), "+47": (8, 8),
    "+45": (8, 8), "+353": (7, 9), "+41": (9, 9), "+32": (8, 9), "+43": (4, 13),
    "+48": (9, 9), "+351": (9, 9), "+1": (10, 10), "+52": (10, 10), "+7": (10, 10),
}

MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "xls", "xlsx", "csv"}


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match((email or "").strip()))


def looks_like_real_name(name: str) -> bool:
    name = (name or "").strip()
    if len(name) < 2:
        return False
    if not NAME_CHARS_RE.match(name):
        return False
    if REPEATED_CHAR_RE.search(name):
        return False
    for word in re.split(r"[\s-]+", name):
        if not word:
            continue
        if word.lower() in KEYBOARD_MASH:
            return False
        if not VOWEL_RE.search(word):
            return False
        if CONSONANT_RUN_RE.search(word):
            return False
    return True


def is_valid_phone(phone: str, dial_code: str) -> bool:
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return True  # caller only invokes this when the (optional) field is non-empty
    lo, hi = PHONE_DIGIT_RANGES.get(dial_code, (6, 14))
    return lo <= len(digits) <= hi + 1


def file_extension(filename: str) -> str:
    m = re.search(r"\.([a-zA-Z0-9]+)$", filename or "")
    return m.group(1).lower() if m else ""
