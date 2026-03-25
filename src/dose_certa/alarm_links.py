from __future__ import annotations

from urllib.parse import quote


def parse_hour_minute(time_value: str) -> tuple[int, int]:
    parts = time_value.split(":")
    if len(parts) != 2:
        raise ValueError("Horario invalido.")

    hour = int(parts[0])
    minute = int(parts[1])

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Horario invalido.")

    return hour, minute


def build_alarm_message(
    medication_name: str,
    dosage: str,
    dose_time: str,
    notes: str = "",
) -> str:
    base = f"Titulo: {medication_name} ({dosage}) | Horario: {dose_time}"
    cleaned_notes = notes.strip()
    if not cleaned_notes:
        return f"{base} | Observacoes: sem observacoes"
    return f"{base} | Observacoes: {cleaned_notes}"


def build_android_set_alarm_intent(
    dose_time: str,
    message: str,
    vibrate: bool = True,
    skip_ui: bool = False,
    fallback_url: str = "https://dose-certa.streamlit.app/",
) -> str:
    hour, minute = parse_hour_minute(dose_time)
    encoded_message = quote(message, safe="")
    encoded_fallback_url = quote(fallback_url, safe="")
    vibrate_literal = "true" if vibrate else "false"
    skip_ui_literal = "true" if skip_ui else "false"

    return (
        "intent://set_alarm/#Intent;"
        "action=android.intent.action.SET_ALARM;"
        "category=android.intent.category.DEFAULT;"
        f"i.android.intent.extra.alarm.HOUR={hour};"
        f"i.android.intent.extra.alarm.MINUTES={minute};"
        f"S.android.intent.extra.alarm.MESSAGE={encoded_message};"
        f"B.android.intent.extra.alarm.VIBRATE={vibrate_literal};"
        f"B.android.intent.extra.alarm.SKIP_UI={skip_ui_literal};"
        f"S.browser_fallback_url={encoded_fallback_url};"
        "end;"
    )
