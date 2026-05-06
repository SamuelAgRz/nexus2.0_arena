import re
from difflib import SequenceMatcher
from typing import Dict, Any, List


DOMAIN_HINTS = {
    "metrics": [
        "NSR", "BOTTLER_NET_SALES_REVENUE_AMOUNT", "SALES_IN_UNIT_CASE_AMOUNT",
        "DISCOUNT_AMOUNT", "PRICE_PER_UC", "SHARE_OF_TOTAL"
    ],
    "time": [
        "YTD", "MTD", "WTD", "QTD", "DTD", "CURRENT_YEAR", "LAST_YEAR",
        "CURRENT_MONTH", "LAST_MONTH", "TREND", "MONTH", "WEEK", "YEAR"
    ],
    "comparison": [
        "YOY_CHANGE", "GROWTH", "DECLINE", "TOP_N", "BOTTOM_N", "RANKING"
    ],
    "channel": [
        "TRADITIONAL", "MODERN", "ON_PREMISE", "OFF_PREMISE", "CHANNEL"
    ],
    "geography": [
        "NATIONAL", "REGION", "ZONE", "CITY", "COLOMBIA"
    ],
    "product": [
        "BRAND", "TRADEMARK", "BRAND_GROUP", "CATEGORY", "SUBCATEGORY",
        "BEVERAGE_PRODUCT_NAME", "SKU", "FLAVOR"
    ],
    "package": [
        "REFILLABILITY", "SERVING_SIZE_TYPE",
        "PRIMARY_CONTAINER_VOLUME_CAPACITY_ML",
        "IMMEDIATE_CONSUMPTION_FLAG"
    ],
}


DEFAULT_ALWAYS_INCLUDE = [
    "BOTTLER_NET_SALES_REVENUE_AMOUNT",
    "SALES_IN_UNIT_CASE_AMOUNT",
    "YTD",
    "MTD",
    "YOY_CHANGE",
    "CURRENT_YEAR",
    "LAST_YEAR",
    "CHANNEL",
    "NATIONAL",
    "COLOMBIA",
    "NSR_DEFINITION",
    "445_CALENDAR",
]


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\-áéíóúñü]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def fuzzy_score(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def parse_synonyms(raw_synonyms: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Supports either:
    KEY: ["syn1", "syn2"]
    KEY: "syn1, syn2, syn3"
    """
    parsed = {}

    for key, value in raw_synonyms.items():
        if isinstance(value, list):
            parsed[key] = [str(v).strip() for v in value if str(v).strip()]
        elif isinstance(value, str):
            parsed[key] = [v.strip() for v in value.split(",") if v.strip()]
        else:
            parsed[key] = []

    return parsed


def detect_domains(user_query: str, synonyms: Dict[str, List[str]]) -> List[str]:
    query = normalize_text(user_query)
    detected = set()

    for domain, keys in DOMAIN_HINTS.items():
        for key in keys:
            if key not in synonyms:
                continue

            key_text = normalize_text(key)
            if key_text in query:
                detected.add(domain)

            for syn in synonyms[key]:
                syn_norm = normalize_text(syn)
                if syn_norm and syn_norm in query:
                    detected.add(domain)

    return list(detected)


def select_relevant_synonyms(
    user_query: str,
    raw_synonyms: Dict[str, Any],
    max_keys: int = 40,
    fuzzy_threshold: float = 0.86,
    include_domain_context: bool = True,
) -> Dict[str, List[str]]:
    """
    Returns a compact runtime synonym dictionary for prompt injection.

    Selection logic:
    1. Always include critical business terms.
    2. Include exact matches from user query.
    3. Include fuzzy matches.
    4. Include domain context if a domain is detected.
    5. Cap output to avoid prompt bloat.
    """

    synonyms = parse_synonyms(raw_synonyms)
    query_norm = normalize_text(user_query)

    selected = {}
    scores = {}

    # 1. Always include critical defaults
    for key in DEFAULT_ALWAYS_INCLUDE:
        if key in synonyms:
            selected[key] = synonyms[key]
            scores[key] = 1.0

    # 2. Exact + substring matching
    for key, values in synonyms.items():
        key_norm = normalize_text(key)

        if key_norm in query_norm:
            selected[key] = values
            scores[key] = max(scores.get(key, 0), 0.98)
            continue

        for syn in values:
            syn_norm = normalize_text(syn)
            if not syn_norm:
                continue

            if syn_norm in query_norm:
                selected[key] = values
                scores[key] = max(scores.get(key, 0), 0.95)
                break

    # 3. Fuzzy matching
    query_tokens = query_norm.split()

    for key, values in synonyms.items():
        if key in selected:
            continue

        candidates = [key] + values

        for candidate in candidates:
            candidate_norm = normalize_text(candidate)

            if len(candidate_norm) < 4:
                continue

            # compare against full query
            score = fuzzy_score(candidate_norm, query_norm)

            # compare against query tokens / short phrases
            for token in query_tokens:
                score = max(score, fuzzy_score(candidate_norm, token))

            if score >= fuzzy_threshold:
                selected[key] = values
                scores[key] = score
                break

    # 4. Domain expansion
    if include_domain_context:
        detected_domains = detect_domains(user_query, synonyms)

        for domain in detected_domains:
            for key in DOMAIN_HINTS.get(domain, []):
                if key in synonyms:
                    selected[key] = synonyms[key]
                    scores[key] = max(scores.get(key, 0), 0.75)

    # 5. Limit output by score
    ordered_keys = sorted(
        selected.keys(),
        key=lambda k: scores.get(k, 0),
        reverse=True,
    )

    limited_keys = ordered_keys[:max_keys]

    return {key: selected[key] for key in limited_keys}


def format_synonyms_for_prompt(selected_synonyms: Dict[str, List[str]]) -> str:
    """
    Converts selected synonyms into compact prompt text.
    """
    lines = []

    for key, values in selected_synonyms.items():
        compact_values = ", ".join(values[:20])
        lines.append(f"{key}: {compact_values}")

    return "\n".join(lines)