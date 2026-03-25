from __future__ import annotations

import re
from datetime import date, datetime, time
from typing import Any
from uuid import uuid4

TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

STATUS_TAKEN = "Tomada"
STATUS_PENDING = "Pendente"
STATUS_LATE = "Atrasada"


class ValidationError(ValueError):
    """Erro de validacao de regra de negocio."""


def _parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def parse_times(raw_times: str) -> list[str]:
    normalized = raw_times.replace(";", ",")
    times = [item.strip() for item in normalized.split(",") if item.strip()]

    if not times:
        raise ValidationError("Informe ao menos um horario no formato HH:MM.")

    invalid = [item for item in times if not TIME_PATTERN.fullmatch(item)]
    if invalid:
        raise ValidationError(
            f"Horarios invalidos: {', '.join(invalid)}. Use o formato HH:MM."
        )

    return sorted(set(times), key=_parse_time)


def create_medication(
    name: str,
    dosage: str,
    times: list[str],
    notes: str = "",
) -> dict[str, Any]:
    name = name.strip()
    dosage = dosage.strip()
    notes = notes.strip()

    if not name:
        raise ValidationError("Informe o nome do medicamento.")
    if not dosage:
        raise ValidationError("Informe a dosagem do medicamento.")
    if not times:
        raise ValidationError("Informe ao menos um horario valido.")

    for item in times:
        if not TIME_PATTERN.fullmatch(item):
            raise ValidationError(f"Horario invalido: {item}")

    return {
        "id": str(uuid4()),
        "name": name,
        "dosage": dosage,
        "times": times,
        "notes": notes,
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def add_medication(
    database: dict[str, list[dict[str, Any]]],
    medication: dict[str, Any],
) -> None:
    database.setdefault("medications", []).append(medication)


def deactivate_medication(
    database: dict[str, list[dict[str, Any]]],
    medication_id: str,
) -> bool:
    for medication in database.get("medications", []):
        if medication.get("id") == medication_id and medication.get("active", True):
            medication["active"] = False
            return True
    return False


def record_dose(
    database: dict[str, list[dict[str, Any]]],
    medication_id: str,
    dose_date: date,
    dose_time: str,
    taken_at: datetime | None = None,
) -> bool:
    medications = database.get("medications", [])
    medication_exists = any(item.get("id") == medication_id for item in medications)
    if not medication_exists:
        raise ValidationError("Medicamento nao encontrado.")

    if not TIME_PATTERN.fullmatch(dose_time):
        raise ValidationError("Horario da dose invalido.")

    logs = database.setdefault("dose_logs", [])
    dose_date_iso = dose_date.isoformat()

    for log in logs:
        if (
            log.get("medication_id") == medication_id
            and log.get("date") == dose_date_iso
            and log.get("time") == dose_time
        ):
            return False

    if taken_at is None:
        taken_at = datetime.now()

    logs.append(
        {
            "id": str(uuid4()),
            "medication_id": medication_id,
            "date": dose_date_iso,
            "time": dose_time,
            "taken_at": taken_at.isoformat(timespec="seconds"),
            "status": STATUS_TAKEN,
        }
    )
    return True


def list_daily_doses(
    database: dict[str, list[dict[str, Any]]],
    target_date: date,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    if now is None:
        now = datetime.now()

    target_date_iso = target_date.isoformat()
    logs = database.get("dose_logs", [])
    dose_index = {
        (log.get("medication_id"), log.get("date"), log.get("time")): log for log in logs
    }

    doses: list[dict[str, Any]] = []

    for medication in database.get("medications", []):
        if not medication.get("active", True):
            continue

        for dose_time in medication.get("times", []):
            scheduled_dt = datetime.combine(target_date, _parse_time(dose_time))
            key = (medication.get("id"), target_date_iso, dose_time)
            log = dose_index.get(key)

            if log:
                status = STATUS_TAKEN
            elif scheduled_dt < now:
                status = STATUS_LATE
            else:
                status = STATUS_PENDING

            doses.append(
                {
                    "medication_id": medication.get("id"),
                    "name": medication.get("name"),
                    "dosage": medication.get("dosage"),
                    "time": dose_time,
                    "scheduled_at": scheduled_dt,
                    "status": status,
                    "taken_at": log.get("taken_at") if log else None,
                }
            )

    doses.sort(key=lambda item: (item["time"], item["name"]))
    return doses


def daily_summary(doses: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        STATUS_TAKEN: 0,
        STATUS_PENDING: 0,
        STATUS_LATE: 0,
        "total": len(doses),
    }

    for dose in doses:
        status = dose.get("status")
        if status in summary:
            summary[status] += 1

    return summary
