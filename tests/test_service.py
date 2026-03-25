from __future__ import annotations

from datetime import date, datetime

import pytest

from dose_certa.service import (
    STATUS_LATE,
    STATUS_PENDING,
    STATUS_TAKEN,
    ValidationError,
    add_medication,
    create_medication,
    list_daily_doses,
    parse_times,
    record_dose,
)
from dose_certa.storage import empty_database


def test_parse_times_sorts_and_deduplicates() -> None:
    assert parse_times("20:00, 08:00, 08:00") == ["08:00", "20:00"]


def test_parse_times_rejects_invalid_input() -> None:
    with pytest.raises(ValidationError):
        parse_times("08:00, 25:00")


def test_record_dose_rejects_duplicate_registration() -> None:
    database = empty_database()
    medication = create_medication(name="Losartana", dosage="50mg", times=["08:00"])
    add_medication(database, medication)

    created_first = record_dose(
        database=database,
        medication_id=medication["id"],
        dose_date=date(2026, 3, 25),
        dose_time="08:00",
        taken_at=datetime(2026, 3, 25, 8, 5),
    )
    created_second = record_dose(
        database=database,
        medication_id=medication["id"],
        dose_date=date(2026, 3, 25),
        dose_time="08:00",
        taken_at=datetime(2026, 3, 25, 8, 6),
    )

    assert created_first is True
    assert created_second is False
    assert len(database["dose_logs"]) == 1


def test_list_daily_doses_handles_pending_late_and_taken() -> None:
    database = empty_database()
    medication = create_medication(name="Metformina", dosage="500mg", times=["08:00", "22:00"])
    add_medication(database, medication)

    record_dose(
        database=database,
        medication_id=medication["id"],
        dose_date=date(2026, 3, 25),
        dose_time="08:00",
        taken_at=datetime(2026, 3, 25, 8, 15),
    )

    doses_21h = list_daily_doses(
        database=database,
        target_date=date(2026, 3, 25),
        now=datetime(2026, 3, 25, 21, 0),
    )
    by_time_21h = {dose["time"]: dose["status"] for dose in doses_21h}

    assert by_time_21h["08:00"] == STATUS_TAKEN
    assert by_time_21h["22:00"] == STATUS_PENDING

    doses_23h = list_daily_doses(
        database=database,
        target_date=date(2026, 3, 25),
        now=datetime(2026, 3, 25, 23, 0),
    )
    by_time_23h = {dose["time"]: dose["status"] for dose in doses_23h}

    assert by_time_23h["22:00"] == STATUS_LATE
