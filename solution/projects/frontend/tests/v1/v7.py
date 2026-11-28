import itertools
import urllib.parse
import random
import string

# === 1) SCHEMES (БЕЗОПАСНЫЕ / НЕВРЕДОНОСНЫЕ) ===
SCHEMES = [
    "http", "https",
    "HtTp", "hTTps",
    "http:", "https:",
    "http:/", "https:/",
    "http://", "https://",
    "h%74tp", "h%74tps",
    "h%252574tp", "h%252575tps",
    "http꞉//", "https꞉//",
    "http:///", "https////",
    "http:////////",
    "ＨＴＴＰ://", "ＨＴＴＰＳ://",         # full-width unicode
    "http:＼＼", "https:＼＼",               # unicode slash
]

# === 2) HOSTS (ВСЕ — ЛОКАЛЬНЫЕ, БЕЗОПАСНЫЕ) ===
HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "[::1]",
    "localhost.localdomain",

    # альтернативные локальные представления
    "127.000.000.001",
    "127.1",
    "127.0.1",
    "2130706433",                # decimal
    "0x7f000001",                # hex

    # dummy local
    "local",
    "dev.local",
    "test.local",
]

# === 3) PATHS (ОБЕЗВРЕЖЕННЫЕ) ===
PATHS = [
    "/", "/api", "/go", "/x", "/r", "/redir", "/jump",
    "/..", "/./", "//", "///", "////",
    "/%2e%2e/", "/%2e/", "/%2F/",
    "/~user/", "/~root/",
    "/％２Ｆ/", "/＼", "/／",
    "/path", "/path/", "/path//extra",
]

# === 4) RANDOM JUNK (Только для нагрузки)
JUNK_CHARS = [";", "|", "%00", "%09", "%0d", "%0a", "%20", "%2f", "%5c", "⁄", "∕", "⧸"]

def rand_junk():
    return "".join(random.choice(JUNK_CHARS) for _ in range(random.randint(0, 4)))

def rand_token(n=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def generate_safe_fuzz(limit=500):
    count = 0
    for scheme, host, path in itertools.product(SCHEMES, HOSTS, PATHS):
        if count >= limit:
            return
        count += 1

        q = rand_token()
        junk = rand_junk()

        url = f"{scheme}{host}{path}{junk}?q={q}"

        # 20% шанс добавить двойное кодирование
        if random.random() < 0.2:
            url = urllib.parse.quote(url, safe="%:/?=")

        # 10% шанс тройного кодирования
        if random.random() < 0.1:
            url = urllib.parse.quote(urllib.parse.quote(url, safe="%:/?="), safe="%")

        # случайный префикс слэшей
        url = "/" * random.randint(0, 10) + url

        yield url


if __name__ == "__main__":
    for u in generate_safe_fuzz(limit=300):
        print(u)
