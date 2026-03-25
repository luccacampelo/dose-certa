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


def _inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=DM+Sans:wght@400;500;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at 0% 0%, rgba(0, 139, 139, 0.14), transparent 38%),
                radial-gradient(circle at 100% 0%, rgba(0, 90, 156, 0.14), transparent 36%),
                linear-gradient(180deg, #f4f9ff 0%, #f8fbff 55%, #f2f8f4 100%);
        }

        html, body, [class*="css"] {
            font-family: "DM Sans", "Segoe UI", sans-serif;
            color: #12263a;
        }

        h1, h2, h3, h4 {
            font-family: "Manrope", "Segoe UI", sans-serif;
            color: #0f2742;
            letter-spacing: -0.02em;
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.2rem;
            max-width: 1200px;
        }

        .hero {
            background: linear-gradient(130deg, #0f5ca8 0%, #0f8c7a 100%);
            border-radius: 18px;
            padding: 1.2rem 1.3rem;
            color: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 14px 32px rgba(15, 92, 168, 0.24);
        }

        .hero-title {
            font-family: "Manrope", "Segoe UI", sans-serif;
            font-size: 1.24rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .hero-subtitle {
            font-size: 0.96rem;
            opacity: 0.96;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #dbe6f2;
            border-radius: 14px;
            padding: 0.75rem 0.85rem;
            min-height: 96px;
            box-shadow: 0 8px 18px rgba(12, 53, 95, 0.08);
        }

        .metric-label {
            font-size: 0.8rem;
            color: #4a6178;
            margin-bottom: 0.2rem;
        }

        .metric-value {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0f2742;
            line-height: 1.2;
        }

        .metric-detail {
            font-size: 0.78rem;
            color: #607387;
            margin-top: 0.24rem;
        }

        .status-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.2rem 0.62rem;
            font-size: 0.77rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }

        .status-tomada {
            color: #0b5d3f;
            background: #daf7eb;
            border: 1px solid #9de3c3;
        }

        .status-pendente {
            color: #835b08;
            background: #fff3d6;
            border: 1px solid #f1d18a;
        }

        .status-atrasada {
            color: #8b1728;
            background: #ffe2e6;
            border: 1px solid #f4a8b4;
        }

        .time-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.34rem;
            margin-top: 0.32rem;
            margin-bottom: 0.35rem;
        }

        .time-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.13rem 0.54rem;
            background: #edf4fb;
            border: 1px solid #cfdfee;
            color: #235177;
            font-size: 0.77rem;
            font-weight: 700;
        }

        .alarm-link {
            display: inline-block;
            width: 100%;
            text-align: center;
            padding: 0.53rem 0.7rem;
            border-radius: 10px;
            border: 1px solid #adc6df;
            background: #edf5ff;
            text-decoration: none;
            color: #0f4c81;
            font-weight: 700;
            margin-top: 0.2rem;
            margin-bottom: 0.2rem;
            transition: 0.18s ease;
        }

        .alarm-link:hover {
            border-color: #0f5ca8;
            color: #0f5ca8;
            background: #e5f0fe;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px;
            border-color: #dce6f1;
            background: rgba(255, 255, 255, 0.94);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f2742 0%, #153b63 100%);
            color: #f2f8ff;
        }

        section[data-testid="stSidebar"] * {
            color: #f2f8ff !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.3rem 0.82rem;
            border: 1px solid #d5e2ef;
            background: #ffffff;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background: #e8f2ff;
            border-color: #b2cfee;
            color: #0f4f88;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def _active_medications(database: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item for item in database.get("medications", []) if item.get("active", True)]


def _metric_card(label: str, value: str | int, detail: str) -> None:
    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    safe_detail = html.escape(detail)
    st.markdown(
        (
            "<div class='metric-card'>"
            f"<div class='metric-label'>{safe_label}</div>"
            f"<div class='metric-value'>{safe_value}</div>"
            f"<div class='metric-detail'>{safe_detail}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _status_chip(status: str) -> str:
    class_name = {
        STATUS_TAKEN: "status-tomada",
        STATUS_PENDING: "status-pendente",
        STATUS_LATE: "status-atrasada",
    }.get(status, "status-pendente")
    safe_status = html.escape(status)
    return f"<span class='status-chip {class_name}'>{safe_status}</span>"


def _render_auth_gate() -> None:
    password = _app_password()
    if not password:
        return

    is_authenticated = st.session_state.get("authenticated", False)
    if is_authenticated:
        with st.sidebar:
            st.caption("Ambiente protegido")
            if st.button("Sair", use_container_width=True):
                st.session_state["authenticated"] = False
                st.rerun()
        return

    st.title("DoseCerta - acesso restrito")
    st.caption("Informe a senha para entrar no ambiente de testes.")

    typed_password = st.text_input("Senha", type="password")
    if st.button("Entrar", type="primary", use_container_width=True):
        if hmac.compare_digest(typed_password, password):
            st.session_state["authenticated"] = True
            st.rerun()
        st.error("Senha invalida.")

    st.stop()


def _render_sidebar(database: dict[str, list[dict[str, Any]]]) -> None:
    active_medications = _active_medications(database)
    today_doses = list_daily_doses(database=database, target_date=date.today(), now=datetime.now())
    today_summary = daily_summary(today_doses)

    st.sidebar.title("DoseCerta")
    st.sidebar.caption("Rotina de medicacao mais organizada")
    st.sidebar.divider()

    st.sidebar.markdown("### Resumo rapido")
    st.sidebar.write(f"- Medicamentos ativos: **{len(active_medications)}**")
    st.sidebar.write(f"- Doses hoje: **{today_summary['total']}**")
    st.sidebar.write(f"- Tomadas hoje: **{today_summary[STATUS_TAKEN]}**")

    st.sidebar.divider()
    st.sidebar.markdown("### Fluxo sugerido")
    st.sidebar.write("1. Cadastre os remedios")
    st.sidebar.write("2. Acompanhe o painel diario")
    st.sidebar.write("3. Marque as doses tomadas")
    st.sidebar.write("4. Gere alarmes para o celular")


def _render_hero(database: dict[str, list[dict[str, Any]]]) -> None:
    active_medications = _active_medications(database)
    today_doses = list_daily_doses(database=database, target_date=date.today(), now=datetime.now())
    today_summary = daily_summary(today_doses)

    total_today = today_summary["total"]
    taken_today = today_summary[STATUS_TAKEN]
    completion = int((taken_today / total_today) * 100) if total_today else 0

    st.markdown(
        (
            "<div class='hero'>"
            "<div class='hero-title'>DoseCerta | Cuidado diario com clareza</div>"
            "<div class='hero-subtitle'>"
            "Visual moderno para cadastro, acompanhamento e alarmes de medicacao."
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    card_cols = st.columns(4)
    with card_cols[0]:
        _metric_card("Medicamentos ativos", len(active_medications), "rotina em acompanhamento")
    with card_cols[1]:
        _metric_card("Doses hoje", total_today, "agendadas para o dia")
    with card_cols[2]:
        _metric_card("Tomadas", taken_today, "registradas no sistema")
    with card_cols[3]:
        _metric_card("Progresso", f"{completion}%", "objetivo: 100% de adesao")


def _render_registration_form(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Cadastrar medicamento")
    with st.container(border=True):
        with st.form("medication-form", clear_on_submit=True):
            col_left, col_right = st.columns(2)
            with col_left:
                name = st.text_input("Nome do medicamento", placeholder="Ex.: Losartana")
            with col_right:
                dosage = st.text_input("Dosagem", placeholder="Ex.: 50mg")

            times_raw = st.text_input(
                "Horarios (HH:MM, separados por virgula)",
                placeholder="08:00, 20:00",
            )
            notes = st.text_area(
                "Observacoes (opcional)",
                placeholder="Ex.: tomar apos refeicao da manha",
                height=110,
            )
            submitted = st.form_submit_button(
                "Salvar medicamento",
                type="primary",
                use_container_width=True,
            )

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
    active_medications = _active_medications(database)

    if not active_medications:
        st.info("Nenhum medicamento ativo cadastrado.")
        return

    query = st.text_input(
        "Buscar medicamento",
        placeholder="Digite o nome para filtrar",
        key="medication-search",
    ).strip()

    filtered_medications = [
        item
        for item in active_medications
        if not query or query.lower() in str(item.get("name", "")).lower()
    ]

    if not filtered_medications:
        st.warning("Nenhum medicamento encontrado com esse filtro.")
        return

    for medication in filtered_medications:
        with st.container(border=True):
            info_col, action_col = st.columns([5, 1])
            with info_col:
                st.markdown(f"**{medication.get('name')}** ({medication.get('dosage')})")
                times_html = "".join(
                    f"<span class='time-chip'>{html.escape(item)}</span>"
                    for item in medication.get("times", [])
                )
                st.markdown(
                    f"<div class='time-chip-row'>{times_html}</div>",
                    unsafe_allow_html=True,
                )

                notes = str(medication.get("notes", "")).strip()
                if notes:
                    st.caption(f"Observacoes: {notes}")

            with action_col:
                if st.button("Desativar", key=f"deactivate-{medication.get('id')}"):
                    deactivate_medication(database, str(medication.get("id", "")))
                    _save_data(database)
                    st.rerun()


def _render_daily_panel(database: dict[str, list[dict[str, Any]]]) -> None:
    st.subheader("Painel diario de doses")

    filter_cols = st.columns([1.1, 1.2, 1.4])
    with filter_cols[0]:
        selected_date = st.date_input(
            "Data de referencia",
            value=date.today(),
            format="DD/MM/YYYY",
            key="daily-date",
        )

    with filter_cols[1]:
        selected_statuses = st.multiselect(
            "Filtrar por status",
            options=[STATUS_PENDING, STATUS_LATE, STATUS_TAKEN],
            default=[STATUS_PENDING, STATUS_LATE, STATUS_TAKEN],
            key="daily-status-filter",
        )

    with filter_cols[2]:
        medication_query = st.text_input(
            "Filtrar por medicamento",
            placeholder="Ex.: metformina",
            key="daily-query",
        ).strip()

    doses = list_daily_doses(database=database, target_date=selected_date, now=datetime.now())
    summary = daily_summary(doses)

    total_doses = summary["total"]
    completion = int((summary[STATUS_TAKEN] / total_doses) * 100) if total_doses else 0
    st.progress(
        value=(completion / 100) if total_doses else 0,
        text=f"Progresso de doses tomadas: {completion}%",
    )

    metric_cols = st.columns(4)
    with metric_cols[0]:
        _metric_card("Total", summary["total"], "doses previstas")
    with metric_cols[1]:
        _metric_card("Tomadas", summary[STATUS_TAKEN], "registro confirmado")
    with metric_cols[2]:
        _metric_card("Pendentes", summary[STATUS_PENDING], "ainda dentro do horario")
    with metric_cols[3]:
        _metric_card("Atrasadas", summary[STATUS_LATE], "necessita atencao")

    filtered_doses = []
    for dose in doses:
        if selected_statuses and dose["status"] not in selected_statuses:
            continue
        if medication_query and medication_query.lower() not in str(dose["name"]).lower():
            continue
        filtered_doses.append(dose)

    if not filtered_doses:
        st.info("Nenhuma dose encontrada para os filtros selecionados.")
        return

    for dose in filtered_doses:
        with st.container(border=True):
            top_col, status_col = st.columns([5, 1])
            with top_col:
                st.markdown(f"**{dose['time']}** | {dose['name']} ({dose['dosage']})")
            with status_col:
                st.markdown(_status_chip(str(dose["status"])), unsafe_allow_html=True)

            if dose["status"] == STATUS_TAKEN:
                st.caption(f"Dose registrada em: {dose['taken_at']}")
                continue

            if selected_date > date.today():
                st.caption("Marcacao so disponivel no dia da medicacao.")
                continue

            if st.button(
                "Marcar como tomada",
                key=f"take-{dose['medication_id']}-{selected_date.isoformat()}-{dose['time']}",
                type="primary",
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
        "Crie atalhos para o app Relogio com horario, titulo do remedio e observacoes."
    )

    active_medications = _active_medications(database)
    if not active_medications:
        st.info("Cadastre um medicamento para gerar alarmes no celular.")
        return

    option_cols = st.columns([1.2, 1, 1])
    with option_cols[0]:
        platform = st.radio(
            "Sistema do celular",
            options=["Android", "iPhone (iOS)"],
            horizontal=True,
            key="alarm-platform",
        )
    with option_cols[1]:
        vibrate = st.toggle("Vibracao", value=True, key="alarm-vibrate")
    with option_cols[2]:
        skip_ui = st.toggle("Tentar sem tela", value=False, key="alarm-skip-ui")

    if platform != "Android":
        st.warning(
            "No iPhone, navegadores nao criam alarme no Relogio automaticamente. "
            "Use os dados exibidos para cadastrar no Relogio/Atalhos."
        )
        for medication in active_medications:
            with st.container(border=True):
                times = ", ".join(medication.get("times", []))
                st.write(
                    f"**{medication.get('name')}** ({medication.get('dosage')}) | Horarios: {times}"
                )
                notes = str(medication.get("notes", "")).strip() or "sem observacoes"
                st.caption(f"Observacoes: {notes}")
        return

    st.info(
        "Android: abra no Chrome do celular e toque no link para abrir o Relogio. "
        "Depois confirme o alarme."
    )

    for medication in active_medications:
        with st.container(border=True):
            st.markdown(f"**{medication.get('name')}** ({medication.get('dosage')})")
            notes = str(medication.get("notes", ""))

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
                    vibrate=vibrate,
                    skip_ui=skip_ui,
                    fallback_url="https://dose-certa.streamlit.app/",
                )
                safe_link = html.escape(intent_link, quote=True)
                safe_label = html.escape(f"Abrir Relogio e criar alarme das {dose_time}")
                st.markdown(
                    f"<a class='alarm-link' href='{safe_link}' target='_self'>{safe_label}</a>",
                    unsafe_allow_html=True,
                )
                st.caption(message)


def run() -> None:
    st.set_page_config(page_title="DoseCerta", layout="wide")
    _inject_custom_css()
    _render_auth_gate()

    st.title("DoseCerta")
    st.caption("Controle de medicamentos com interface moderna, dinamica e facil de usar.")

    try:
        database = _load_data()
    except ValueError as error:
        st.error(f"Falha ao carregar dados: {error}")
        st.stop()
        return

    _render_sidebar(database)
    _render_hero(database)

    tab_daily, tab_register, tab_medications, tab_alarms = st.tabs(
        ["Painel diario", "Cadastro", "Medicamentos", "Alarmes"]
    )

    with tab_daily:
        _render_daily_panel(database)

    with tab_register:
        _render_registration_form(database)

    with tab_medications:
        _render_medications(database)

    with tab_alarms:
        _render_alarm_automation(database)


if __name__ == "__main__":
    run()
