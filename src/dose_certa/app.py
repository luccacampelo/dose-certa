from __future__ import annotations

import hmac
import html
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

if __package__ in {None, ""}:
    src_path = Path(__file__).resolve().parents[1]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from dose_certa.alarm_links import (  # noqa: E402
    build_alarm_message,
    build_android_set_alarm_intent,
)
from dose_certa.service import (  # noqa: E402
    STATUS_LATE,
    STATUS_PENDING,
    STATUS_TAKEN,
    ValidationError,
    add_medication,
    create_medication,
    daily_summary,
    deactivate_medication,
    list_daily_doses,
    parse_times,
    record_dose,
)
from dose_certa.storage import load_database, save_database  # noqa: E402


def _read_secret_value(key: str) -> str:
    try:
        value = st.secrets.get(key, "")
    except Exception:
        value = ""
    return str(value).strip()


def _app_password() -> str:
    return _read_secret_value("app_password") or os.getenv("DOSE_CERTA_APP_PASSWORD", "").strip()


def _resolve_data_file() -> Path:
    default_path = Path(__file__).resolve().parents[2] / "data" / "dose_certa.json"
    configured_path = (
        _read_secret_value("dose_certa_data_file")
        or os.getenv("DOSE_CERTA_DATA_FILE", "").strip()
    )
    if not configured_path:
        return default_path
    return Path(configured_path).expanduser()


def _load_data() -> dict[str, list[dict[str, Any]]]:
    return load_database(_resolve_data_file())


def _save_data(database: dict[str, list[dict[str, Any]]]) -> None:
    try:
        save_database(_resolve_data_file(), database)
    except OSError as error:
        raise ValueError("Falha ao salvar dados no armazenamento configurado.") from error


def _render_auth_gate() -> None:
    password = _app_password()
    if not password:
        return

    is_authenticated = st.session_state.get("authenticated", False)
    if is_authenticated:
        with st.sidebar:
            st.caption("Ambiente protegido")
            if st.button("Sair"):
                st.session_state["authenticated"] = False
                st.rerun()
        return

    st.title("DoseCerta - acesso restrito")
    st.caption("Informe a senha para entrar no ambiente de testes.")

    typed_password = st.text_input("Senha", type="password")
    if st.button("Entrar", type="primary"):
        if hmac.compare_digest(typed_password, password):
            st.session_state["authenticated"] = True
            st.rerun()
        st.error("Senha invalida.")

    st.stop()


def _render_registration_form(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Cadastro de medicamento")
    with st.form("medication-form", clear_on_submit=True):
        name = st.text_input("Nome do medicamento")
        dosage = st.text_input("Dosagem")
        times_raw = st.text_input(
            "Horarios (HH:MM, separados por virgula)",
            placeholder="08:00, 20:00",
        )
        notes = st.text_area("Observacoes (opcional)")
        submitted = st.form_submit_button("Salvar medicamento")

    if not submitted:
        return

    try:
        times = parse_times(times_raw)
        medication = create_medication(name=name, dosage=dosage, times=times, notes=notes)
        add_medication(database, medication)
        _save_data(database)
        st.success("Medicamento cadastrado com sucesso.")
        st.rerun()
    except ValidationError as error:
        st.error(str(error))


def _render_medications(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Medicamentos ativos")
    active_medications = [
        item for item in database.get("medications", []) if item.get("active", True)
    ]

    if not active_medications:
        st.info("Nenhum medicamento ativo cadastrado.")
        return

    for medication in active_medications:
        col_data, col_action = st.columns([4, 1])
        with col_data:
            times = ", ".join(medication.get("times", []))
            notes = medication.get("notes", "")
            st.write(
                f"**{medication.get('name')}** - {medication.get('dosage')} | Horarios: {times}"
            )
            if notes:
                st.caption(f"Observacoes: {notes}")
        with col_action:
            if st.button("Desativar", key=f"deactivate-{medication.get('id')}"):
                deactivate_medication(database, medication.get("id"))
                _save_data(database)
                st.rerun()


def _render_daily_panel(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Painel diario de doses")
    selected_date = st.date_input("Data de referencia", value=date.today(), format="DD/MM/YYYY")

    doses = list_daily_doses(database=database, target_date=selected_date, now=datetime.now())
    summary = daily_summary(doses)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total", summary["total"])
    metric_cols[1].metric("Tomadas", summary[STATUS_TAKEN])
    metric_cols[2].metric("Pendentes", summary[STATUS_PENDING])
    metric_cols[3].metric("Atrasadas", summary[STATUS_LATE])

    if not doses:
        st.info("Nenhuma dose cadastrada para a data selecionada.")
        return

    for dose in doses:
        with st.container(border=True):
            st.write(
                f"**{dose['time']}** | {dose['name']} ({dose['dosage']}) - "
                f"Status: **{dose['status']}**"
            )

            if dose["status"] == STATUS_TAKEN:
                st.caption(f"Dose registrada em: {dose['taken_at']}")
                continue

            if selected_date > date.today():
                st.caption("Marcacao so disponivel no dia da medicacao.")
                continue

            if st.button(
                "Marcar como tomada",
                key=f"take-{dose['medication_id']}-{selected_date.isoformat()}-{dose['time']}",
            ):
                created = record_dose(
                    database=database,
                    medication_id=dose["medication_id"],
                    dose_date=selected_date,
                    dose_time=dose["time"],
                )
                if created:
                    _save_data(database)
                    st.success("Dose registrada com sucesso.")
                    st.rerun()
                else:
                    st.warning("Essa dose ja foi registrada anteriormente.")


def _render_alarm_automation(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Automacao de alarmes no celular")
    st.caption(
        "Gera atalhos para abrir o app Relogio do celular e salvar alarmes com horario, "
        "titulo e observacoes do remedio."
    )

    active_medications = [
        item for item in database.get("medications", []) if item.get("active", True)
    ]
    if not active_medications:
        st.info("Cadastre um medicamento para gerar alarmes no celular.")
        return

    platform = st.radio(
        "Sistema do celular",
        options=["Android", "iPhone (iOS)"],
        horizontal=True,
    )

    if platform != "Android":
        st.warning(
            "No iPhone, o navegador nao cria alarme no app Relogio automaticamente. "
            "Use os dados exibidos para cadastrar no app Relogio ou no app Atalhos."
        )
        for medication in active_medications:
            times = ", ".join(medication.get("times", []))
            st.write(
                f"- **{medication.get('name')}** ({medication.get('dosage')}) | Horarios: {times}"
            )
            notes = medication.get("notes", "")
            if notes:
                st.caption(f"Observacoes: {notes}")
        return

    st.info(
        "Android: abra no Chrome do celular e toque no link para abrir o Relogio. "
        "Depois confirme o alarme."
    )
    st.caption(
        "Se o aparelho bloquear abertura externa, use o texto exibido abaixo para cadastro manual."
    )
    for medication in active_medications:
        st.markdown(f"**{medication.get('name')}** ({medication.get('dosage')})")
        notes = medication.get("notes", "")

        for dose_time in medication.get("times", []):
            message = build_alarm_message(
                medication_name=str(medication.get("name", "")).strip(),
                dosage=str(medication.get("dosage", "")).strip(),
                dose_time=dose_time,
                notes=notes,
            )
            intent_link = build_android_set_alarm_intent(
                dose_time=dose_time,
                message=message,
                vibrate=True,
                skip_ui=False,
                fallback_url="https://dose-certa.streamlit.app/",
            )
            link_label = html.escape(f"Abrir Relogio e criar alarme das {dose_time}")
            safe_link = html.escape(intent_link, quote=True)
            st.markdown(
                (
                    f'<a href="{safe_link}" target="_self" '
                    'style="display:inline-block;padding:0.55rem 0.9rem;'
                    'border:1px solid #d1d5db;border-radius:0.5rem;'
                    'text-decoration:none;font-weight:600;">'
                    f"{link_label}</a>"
                ),
                unsafe_allow_html=True,
            )
            st.caption(message)

        st.divider()


def run() -> None:
    st.set_page_config(page_title="DoseCerta", layout="wide")
    _render_auth_gate()

    st.title("DoseCerta")
    st.caption("Controle simples de medicamentos para apoiar rotinas de cuidado.")

    try:
        database = _load_data()
    except ValueError as error:
        st.error(f"Falha ao carregar dados: {error}")
        st.stop()
        return

    col_left, col_right = st.columns([1, 1])

    with col_left:
        _render_registration_form(database)
        st.divider()
        _render_medications(database)

    with col_right:
        _render_daily_panel(database)
        st.divider()
        _render_alarm_automation(database)


if __name__ == "__main__":
    run()
