"""Agenda da Equipe MaLuê — visualização sem valores.

Lê os dados da planilha pública Agenda MaLuê 2026 e mostra os shows
em cards bonitos, no estilo do portfólio (preto + verde-limão).
"""
from __future__ import annotations

import io
from datetime import date

import pandas as pd
import requests
import streamlit as st

# ============================================================
# Config
# ============================================================
SHEET_ID = "13ibY4_88N7pTK2lrLkNcudGeVyh78Kry6Y60Ijp0JD4"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
LOGO_URL = "https://raw.githubusercontent.com/malueoficial/malue-contratos/main/malue_icon.png"

st.set_page_config(
    page_title="Agenda MaLuê — Equipe",
    page_icon=LOGO_URL,
    layout="centered",
)

# ============================================================
# Brand CSS (preto + verde-limão, igual portfólio)
# ============================================================
st.markdown(
    """
    <style>
      :root {
        --bg: #0a0a0a;
        --card: #161616;
        --card-hover: #1f1f1f;
        --lime: #c8f032;
        --text: #f5f5f5;
        --muted: #8a8a8a;
      }
      .stApp { background: var(--bg) !important; }
      html, body, [class*="css"] {
        color: var(--text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      }
      .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 720px !important;
      }
      h1, h2, h3, h4 { color: var(--text); font-weight: 800; letter-spacing: -0.5px; }
      .stMarkdown p { color: var(--text); }

      .header-wrap { text-align: center; margin-bottom: 1.4rem; }
      .header-logo {
        width: 110px;
        height: 110px;
        border-radius: 20px;
        margin: 0 auto 0.6rem;
        display: block;
      }
      .header-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: var(--text);
        line-height: 1;
        margin: 0.3rem 0 0.2rem 0;
      }
      .header-sub {
        color: var(--lime);
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
      }

      /* Filter tabs */
      .stRadio > div { flex-direction: row !important; justify-content: center; gap: 0.3rem; }
      .stRadio label {
        background: var(--card);
        border: 1px solid #2a2a2a;
        padding: 0.4rem 1rem !important;
        border-radius: 999px !important;
        cursor: pointer;
        color: var(--text) !important;
      }
      .stRadio label:hover { border-color: var(--lime); }

      /* Card */
      .show-card {
        background: var(--card);
        border: 1px solid #222;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.7rem;
        display: flex;
        gap: 1rem;
        align-items: center;
      }
      .show-card:hover { background: var(--card-hover); border-color: var(--lime); }
      .date-block {
        background: var(--lime);
        color: #0a0a0a;
        border-radius: 12px;
        padding: 0.6rem 0.4rem;
        min-width: 64px;
        text-align: center;
        font-weight: 900;
      }
      .date-day { font-size: 1.6rem; line-height: 1; display: block; }
      .date-month {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: block;
        margin-top: 0.15rem;
      }
      .show-info { flex: 1; min-width: 0; }
      .show-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
        margin: 0;
        word-break: break-word;
      }
      .show-meta { color: var(--muted); font-size: 0.85rem; margin-top: 0.2rem; }
      .show-time-badge {
        background: rgba(200, 240, 50, 0.12);
        color: var(--lime);
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-left: 0.3rem;
      }

      /* Detalhes */
      .detalhe-bloco {
        background: var(--card);
        border-left: 3px solid var(--lime);
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin: -0.3rem 0 0.6rem 0;
      }
      .detalhe-row {
        display: flex;
        justify-content: space-between;
        padding: 0.35rem 0;
        border-bottom: 1px solid #222;
        font-size: 0.92rem;
      }
      .detalhe-row:last-child { border-bottom: none; }
      .detalhe-label {
        color: var(--muted);
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 1px;
        font-weight: 700;
      }
      .detalhe-value {
        color: var(--text);
        font-weight: 600;
        text-align: right;
        max-width: 60%;
        word-break: break-word;
      }
      .detalhe-empty { color: #555; font-style: italic; font-weight: 400; }

      /* Status pills */
      .status-pill {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .status-confirmado { background: rgba(200,240,50,0.18); color: var(--lime); }
      .status-realizado { background: #2a2a2a; color: #888; }
      .status-pago { background: rgba(100,200,100,0.18); color: #6fc66f; }
      .status-contrato { background: rgba(100,160,255,0.18); color: #7eb6ff; }
      .status-cancelado { background: rgba(255,100,100,0.18); color: #ff7a7a; }
      .status-folga { background: rgba(255,180,80,0.15); color: #ffb04a; }

      [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
        margin-top: -0.7rem;
        margin-bottom: 0.6rem;
      }
      [data-testid="stExpander"] summary {
        color: var(--lime) !important;
        font-weight: 700;
        font-size: 0.85rem;
      }
      .reload-btn button {
        background: var(--lime) !important;
        color: #0a0a0a !important;
        font-weight: 700 !important;
        border-radius: 999px !important;
        padding: 0.4rem 1.2rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Header
# ============================================================
st.markdown(
    f"""
    <div class="header-wrap">
      <img class="header-logo" src="{LOGO_URL}" alt="MaLuê">
      <div class="header-title">AGENDA DA EQUIPE</div>
      <div class="header-sub">Música com energia · 2026</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Load data
# ============================================================
MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


@st.cache_data(ttl=60)
def carregar_agenda() -> pd.DataFrame:
    r = requests.get(CSV_URL, timeout=10)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df["_data_dt"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["_data_dt"])
    return df.sort_values("_data_dt").reset_index(drop=True)


try:
    df = carregar_agenda()
except Exception as e:
    st.error(
        "Não consegui carregar a agenda. "
        "Verifique se a planilha está compartilhada como 'qualquer pessoa com o link pode visualizar'."
    )
    st.caption(f"Detalhe técnico: {e}")
    st.stop()

# ============================================================
# Filtros
# ============================================================
filtro = st.radio(
    "Filtro",
    ["Próximos", "Esta semana", "Este mês", "Todos"],
    horizontal=True,
    label_visibility="collapsed",
)

hoje = pd.Timestamp(date.today())
if filtro == "Próximos":
    df_view = df[df["_data_dt"] >= hoje]
elif filtro == "Esta semana":
    fim_semana = hoje + pd.Timedelta(days=7)
    df_view = df[(df["_data_dt"] >= hoje) & (df["_data_dt"] < fim_semana)]
elif filtro == "Este mês":
    df_view = df[
        (df["_data_dt"] >= hoje)
        & (df["_data_dt"].dt.month == hoje.month)
        & (df["_data_dt"].dt.year == hoje.year)
    ]
else:
    df_view = df

if df_view.empty:
    st.markdown(
        "<div style='text-align:center;color:#666;padding:2rem;'>"
        "Nenhum show nesse período.</div>",
        unsafe_allow_html=True,
    )
    st.stop()


def status_pill(status: str) -> str:
    if not status:
        return ""
    s = status.lower()
    classe = "status-confirmado"
    if "realizado" in s: classe = "status-realizado"
    elif "pago" in s: classe = "status-pago"
    elif "contrato" in s: classe = "status-contrato"
    elif "cancela" in s: classe = "status-cancelado"
    elif "folga" in s: classe = "status-folga"
    return f"<span class='status-pill {classe}'>{status}</span>"


def detalhe_row(label: str, value: str) -> str:
    if not value or not value.strip():
        value_html = "<span class='detalhe-empty'>a definir</span>"
    else:
        value_html = value
    return (
        f"<div class='detalhe-row'>"
        f"<span class='detalhe-label'>{label}</span>"
        f"<span class='detalhe-value'>{value_html}</span>"
        f"</div>"
    )


# ============================================================
# Cards
# ============================================================
for idx, row in df_view.iterrows():
    d = row["_data_dt"]
    dia_num = d.day
    mes = MESES_PT[d.month - 1]
    dia_sem = row.get("Dia", "") or d.strftime("%A").capitalize()
    horario = row.get("Horário Show", "")
    horario_badge = f"<span class='show-time-badge'>{horario}</span>" if horario else ""
    local = row.get("Local", "") or "—"
    cidade = row.get("Cidade", "")
    cidade_str = f" · {cidade}" if cidade else ""
    status_html = status_pill(row.get("Status", ""))

    st.markdown(
        f"""
        <div class="show-card">
          <div class="date-block">
            <span class="date-day">{dia_num:02d}</span>
            <span class="date-month">{mes}</span>
          </div>
          <div class="show-info">
            <div class="show-title">{local}{horario_badge}</div>
            <div class="show-meta">{dia_sem}{cidade_str} {status_html}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Ver detalhes"):
        partes = [
            detalhe_row("Horário do show", row.get("Horário Show", "")),
            detalhe_row("Passagem de som", row.get("Passagem de Som", "")),
            detalhe_row("Local", row.get("Local", "")),
            detalhe_row("Cidade", row.get("Cidade", "")),
            detalhe_row("Tipo de evento", row.get("Tipo Evento", "")),
            detalhe_row("Traje", row.get("Traje", "")),
            detalhe_row("Empresa de som", row.get("Empresa de Som", "")),
            detalhe_row("Contratante", row.get("Contratante", "")),
        ]
        obs = row.get("Observações", "")
        if obs:
            partes.append(detalhe_row("Observações", obs))
        st.markdown(
            "<div class='detalhe-bloco'>" + "".join(partes) + "</div>",
            unsafe_allow_html=True,
        )

# ============================================================
# Footer
# ============================================================
st.markdown(
    "<div style='text-align:center;margin-top:2rem;color:#444;font-size:0.78rem;'>"
    "Atualizado automaticamente. Para forçar refresh:"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("<div class='reload-btn'>", unsafe_allow_html=True)
if st.button("↻ Atualizar agora"):
    st.cache_data.clear()
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
