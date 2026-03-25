from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

if __package__ in {None, ""}:
    src_path = Path(__file__).resolve().parents[1]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

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

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "dose_certa.json"


def _load_data() -> dict[str, list[dict[str, Any]]]:
    return load_database(DATA_FILE)


def _save_data(database: dict[str, list[dict[str, Any]]]) -> None:
    save_database(DATA_FILE, database)


def _render_registration_form(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Cadastro de Medicamento")
    with st.form("medication-form", clear_on_submit=True):
        name = st.text_input("Nome do medicamento")
        dosage = st.text_input("Dosagem")
        times_raw = st.text_input(
            "Horários (HH:MM, separados por vírgula)",
            placeholder="08:00, 20:00",
        )
        notes = st.text_area("Observações (opcional)")
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
    st.subheader("Medicamentos Ativos")
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
                f"**{medication.get('name')}** - {medication.get('dosage')} | Horários: {times}"
            )
            if notes:
                st.caption(f"Observações: {notes}")
        with col_action:
            if st.button("Desativar", key=f"deactivate-{medication.get('id')}"):
                deactivate_medication(database, medication.get("id"))
                _save_data(database)
                st.rerun()


def _render_daily_panel(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Painel Diário de Doses")
    selected_date = st.date_input("Data de referência", value=date.today(), format="DD/MM/YYYY")

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
                st.caption("A marcação de dose fica disponível a partir da data da medicação.")
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
                    st.warning("Essa dose já foi registrada anteriormente.")


def run() -> None:
    st.set_page_config(page_title="DoseCerta", layout="wide")
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


if __name__ == "__main__":
    run()
