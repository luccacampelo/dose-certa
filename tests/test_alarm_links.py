from __future__ import annotations

import pytest

from dose_certa.alarm_links import (
    build_alarm_message,
    build_android_set_alarm_intent,
    parse_hour_minute,
)


def test_parse_hour_minute_accepts_valid_time() -> None:
    assert parse_hour_minute("08:30") == (8, 30)


def test_parse_hour_minute_rejects_invalid_time() -> None:
    with pytest.raises(ValueError):
        parse_hour_minute("25:99")


def test_build_alarm_message_includes_notes() -> None:
    message = build_alarm_message(
        medication_name="Losartana",
        dosage="50mg",
        dose_time="08:00",
        notes="Tomar com agua.",
    )

    assert "Titulo: Losartana (50mg)" in message
    assert "Horario: 08:00" in message
    assert "Observacoes: Tomar com agua." in message


def test_build_alarm_message_without_notes_uses_default() -> None:
    message = build_alarm_message(
        medication_name="Metformina",
        dosage="500mg",
        dose_time="20:00",
        notes="",
    )

    assert "Observacoes: sem observacoes" in message


def test_build_android_set_alarm_intent_has_required_fields() -> None:
    link = build_android_set_alarm_intent(
        dose_time="20:15",
        message="Titulo: Remedio X",
        vibrate=True,
        skip_ui=False,
    )

    assert link.startswith("intent://set_alarm/#Intent;action=android.intent.action.SET_ALARM;")
    assert "category=android.intent.category.DEFAULT;" in link
    assert "i.android.intent.extra.alarm.HOUR=20;" in link
    assert "i.android.intent.extra.alarm.MINUTES=15;" in link
    assert "S.android.intent.extra.alarm.MESSAGE=Titulo%3A%20Remedio%20X;" in link
    assert "B.android.intent.extra.alarm.VIBRATE=true;" in link
    assert "B.android.intent.extra.alarm.SKIP_UI=false;" in link
    assert "S.browser_fallback_url=https%3A%2F%2Fdose-certa.streamlit.app%2F;" in link
    assert link.endswith("end;")
