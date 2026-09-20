"""Маршрутизация запросов по отделам: словари, уверенность, эскалация."""

from __future__ import annotations

import re

from pydantic import BaseModel

DEPARTMENTS: dict[str, list[str]] = {
    "billing": [
        "invoice", "bill", "charge", "payment", "refund", "subscription", "price",
        "счёт", "счет", "оплата", "платёж", "платеж", "возврат", "подписка", "тариф",
    ],
    "technical": [
        "error", "bug", "crash", "login", "password", "api", "integration", "broken",
        "ошибка", "баг", "падает", "вход", "пароль", "интеграция", "сломан",
    ],
    "sales": [
        "buy", "purchase", "demo", "trial", "pricing", "discount", "quote", "contract",
        "купить", "покупка", "демо", "триал", "скидка", "договор", "тарифы",
    ],
}

URGENT_MARKERS = {"urgent", "asap", "critical", "emergency", "срочно", "критично", "авария"}

_WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ]+")


class RouteResult(BaseModel):
    department: str
    confidence: float
    escalate: bool
    matched: list[str]


def route_query(text: str, escalate_below: float = 0.4) -> RouteResult:
    """Классифицировать запрос. Детерминировано, без сети."""
    if not text or not text.strip():
        raise ValueError("text must not be empty")
    words = _WORD_RE.findall(text.lower())
    word_set = set(words)
    scores: dict[str, list[str]] = {}
    for department, keywords in DEPARTMENTS.items():
        matched = sorted({kw for kw in keywords if kw in word_set})
        scores[department] = matched
    best = max(scores, key=lambda dept: (len(scores[dept]), dept))
    best_hits = len(scores[best])
    total_hits = sum(len(hits) for hits in scores.values())
    if best_hits == 0:
        return RouteResult(department="general", confidence=0.0, escalate=True, matched=[])
    confidence = round(best_hits / total_hits, 2) if total_hits else 0.0
    urgent = bool(word_set & URGENT_MARKERS)
    escalate = urgent or confidence < escalate_below
    return RouteResult(
        department=best, confidence=confidence, escalate=escalate, matched=scores[best]
    )


def describe_departments() -> dict[str, list[str]]:
    return {dept: list(keywords) for dept, keywords in DEPARTMENTS.items()}
