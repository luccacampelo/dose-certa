from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from dose_certa.storage import empty_database, load_database, save_database

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATA_DIR = PROJECT_ROOT / "data" / "_test"
RUN_ID = uuid4().hex[:8]


def _test_db_path(file_name: str) -> Path:
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_DATA_DIR / f"{RUN_ID}_{file_name}"


def test_load_database_creates_file_when_missing() -> None:
    database_file = _test_db_path("load_creates_missing.json")

    loaded = load_database(database_file)

    assert database_file.exists()
    assert loaded == empty_database()


def test_save_and_load_database_roundtrip() -> None:
    database_file = _test_db_path("roundtrip.json")
    payload = {
        "medications": [
            {"id": "1", "name": "Losartana", "dosage": "50mg", "times": ["08:00"], "active": True}
        ],
        "dose_logs": [
            {"medication_id": "1", "date": "2026-03-25", "time": "08:00", "status": "Tomada"}
        ],
    }

    save_database(database_file, payload)
    loaded = load_database(database_file)

    assert loaded == payload


def test_load_database_rejects_invalid_json() -> None:
    database_file = _test_db_path("invalid_json.json")
    database_file.write_text("{json invalido", encoding="utf-8")

    with pytest.raises(ValueError):
        load_database(database_file)


def test_load_database_rejects_invalid_list_structure() -> None:
    database_file = _test_db_path("invalid_structure.json")
    database_file.write_text(
        json.dumps({"medications": {"id": "1"}, "dose_logs": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_database(database_file)

