"""Unit-тесты маршрутизатора: без сети, детерминированы."""

import pytest

from app.services.router import describe_departments, route_query


def test_billing_route() -> None:
    result = route_query("My invoice has a wrong charge, refund please")
    assert result.department == "billing"
    assert result.confidence == 1.0
    assert result.escalate is False
    assert result.matched == ["charge", "invoice", "refund"]


def test_technical_urgent_escalates() -> None:
    result = route_query("App crash on login, urgent fix needed")
    assert result.department == "technical"
    assert result.escalate is True


def test_sales_route_ru() -> None:
    result = route_query("Хочу купить подписку, покажите демо и скидку")
    assert result.department == "sales"
    assert result.escalate is False


def test_general_fallback() -> None:
    result = route_query("xyzzy blorp frobnicator")
    assert result.department == "general"
    assert result.confidence == 0.0
    assert result.escalate is True
    assert result.matched == []


def test_empty_rejected() -> None:
    with pytest.raises(ValueError):
        route_query("   ")


def test_departments_described() -> None:
    described = describe_departments()
    assert set(described) == {"billing", "technical", "sales"}
