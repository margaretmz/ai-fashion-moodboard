import re


_REAL_TIME_DIRECT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(2025|2026|latest|trend\w*|fashion week|met gala)\b",
        r"\btoday'?s weather\b",
        r"\btoday'?s temperature\b",
        r"\bweather (forecast|report|update)s?\b",
        r"\brain (radar|tracker)\b",
        r"\bair\s+quality\b",
        r"\bcrypto (price|chart|update)\b",
        r"\bbitcoin (price|chart|update)\b",
        r"\bmarket (open|close)\b",
        r"\blatest news\b",
        r"\brecent events?\b",
        r"\blive (news|coverage|feed)\b",
        r"\bfashion week (schedule|calendar|lineup)\b",
        r"\bfashion show (schedule|livestream|coverage)\b",
        r"\brunway (schedule|livestream|coverage)\b",
        r"\bred carpet (coverage|arrivals)\b",
        r"\baward show (lineup|coverage)\b",
        r"\blast night'?s (runway|red carpet|show)\b",
        r"\b(celebrity|influencer)\s+(look|outfit)\s+(today|tonight|last\s+night)\b",
        r"\bcollection drop\b",
        r"\brelease date\b",
    )
]

_REAL_TIME_TIME_PATTERN = (
    r"(?:"
    r"today(?:'s)?|tonight|tomorrow|current(?:ly)?|latest|recent|breaking|"
    r"live|upcoming|right\s+now|real[-\s]?time|this\s+week|next\s+week|"
    r"this\s+month|next\s+month|this\s+season|next\s+season|forecast|update|"
    r"up[-\s]?to[-\s]?date|today\s+only"
    r")"
)

_REAL_TIME_TOPIC_PATTERN = (
    r"(?:"
    r"event|events|headline|runway|fashion\s+week|fashion\s+show|runway\s+show|"
    r"collection\s+drop|capsule\s+drop|product\s+drop|restock|release|lineup|"
    r"schedule|calendar|red\s+carpet|award\s+show|premiere|street\s+style|"
    r"lookbook|front\s+row"
    r")"
)

