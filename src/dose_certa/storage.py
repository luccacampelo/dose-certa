from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def empty_database() -> dict[str, list[dict[str, Any]]]:
    return {"medications": [], "dose_logs": []}


def load_database(path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.exists():
        database = empty_database()
        save_database(path, database)
        return database

    with path.open("r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError("Arquivo de dados inválido.") from error

    if not isinstance(data, dict):
        raise ValueError("Arquivo de dados inválido: estrutura principal precisa ser objeto.")

    medications = data.get("medications", [])
    dose_logs = data.get("dose_logs", [])

    if not isinstance(medications, list) or not isinstance(dose_logs, list):
        raise ValueError("Arquivo de dados inválido: listas esperadas não encontradas.")

    return {"medications": medications, "dose_logs": dose_logs}


def save_database(path: Path, database: dict[str, list[dict[str, Any]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(database, file, ensure_ascii=False, indent=2)
