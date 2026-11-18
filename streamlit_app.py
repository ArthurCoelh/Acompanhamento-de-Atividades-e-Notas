"""Versão web (Streamlit) do Acompanhamento de Atividades e Notas.

Executar: streamlit run streamlit_app.py
"""
import sqlite3
from datetime import date
from html import escape
from string import Template

import streamlit as st

from calculos import resumo_disciplina
from database import Banco

STATUS = {"pendente": "Pendente", "em_andamento": "Em andamento", "concluida": "Concluída"}

# ---------------- temas
TEMA_PADRAO = "Azul"
PERSONALIZADA = "Personalizada"

# Cada tema tem uma paleta para o modo claro e outra para o escuro.
TEMAS = {
    "Azul": {
        "claro": dict(fundo="#f4f7fc", superficie="#ffffff", lateral="#e8eff9", texto="#0f1f3d",
                      suave="#52627f", borda="#d3deee", destaque="#1d4ed8"),
        "escuro": dict(fundo="#0b1220", superficie="#121c30", lateral="#0e1627", texto="#e6edf8",
                       suave="#9aabc7", borda="#243350", destaque="#60a5fa"),
    },
    "Preto e branco": {
        "claro": dict(fundo="#ffffff", superficie="#f6f6f6", lateral="#efefef", texto="#111111",
                      suave="#5c5c5c", borda="#d4d4d4", destaque="#111111"),
        "escuro": dict(fundo="#0a0a0a", superficie="#161616", lateral="#101010", texto="#f5f5f5",
                       suave="#a3a3a3", borda="#2e2e2e", destaque="#f5f5f5"),
    },
    "Verde": {
        "claro": dict(fundo="#f3f9f5", superficie="#ffffff", lateral="#e5f2ea", texto="#10281b",
                      suave="#4d6b5a", borda="#cfe3d6", destaque="#15803d"),
        "escuro": dict(fundo="#09140e", superficie="#0f1f16", lateral="#0b1811", texto="#e4f3ea",
                       suave="#96b5a3", borda="#1f3a2a", destaque="#4ade80"),
    },
    "Roxo": {
        "claro": dict(fundo="#f7f5fd", superficie="#ffffff", lateral="#eeeafa", texto="#1e1636",
                      suave="#605580", borda="#ddd6f1", destaque="#6d28d9"),
        "escuro": dict(fundo="#100c1c", superficie="#181230", lateral="#130e24", texto="#ece8fa",
                       suave="#a79fcb", borda="#2d2550", destaque="#a78bfa"),
    },
    "Rosa": {
        "claro": dict(fundo="#fdf5f8", superficie="#ffffff", lateral="#fbe9f0", texto="#3a1020",
                      suave="#7d4a5f", borda="#f2d2de", destaque="#be185d"),
        "escuro": dict(fundo="#1a0b13", superficie="#25101b", lateral="#1e0d16", texto="#fbe8f0",
                       suave="#cfa0b5", borda="#452031", destaque="#f472b6"),
    },
}

# situação -> (classe CSS, (fundo, texto) no modo claro, (fundo, texto) no modo escuro)
SITUACAO = {
    "Aprovado": ("aprovado", ("#dcfce7", "#14532d"), ("#14532d", "#bbf7d0")),
    "No caminho": ("caminho", ("#e0f2fe", "#0c4a6e"), ("#0c4a6e", "#bae6fd")),
    "Atenção": ("atencao", ("#fef9c3", "#713f12"), ("#713f12", "#fef08a")),
    "Em risco": ("risco", ("#fee2e2", "#7f1d1d"), ("#7f1d1d", "#fecaca")),
    "Reprovado": ("reprovado", ("#fecaca", "#7f1d1d"), ("#991b1b", "#fee2e2")),
    "Sem notas": ("sem", ("#f1f5f9", "#334155"), ("#1e293b", "#cbd5e1")),
}
# quanto menor, mais urgente aparece nas sugestões
PRIORIDADE = {"Em risco": 0, "Reprovado": 1, "Atenção": 2, "Sem notas": 3, "No caminho": 4, "Aprovado": 5}


def _rgb(cor):
    cor = cor.lstrip("#")
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))


def misturar(a, b, t):
    """Mistura a cor `a` em direção à `b` (t de 0 a 1)."""
    return "#%02x%02x%02x" % tuple(round(x * (1 - t) + y * t) for x, y in zip(_rgb(a), _rgb(b)))


def contraste(cor):
    """Texto escuro ou branco, o que ficar mais legível sobre `cor`."""
    r, g, b = _rgb(cor)
    return "#0f172a" if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.6 else "#ffffff"


def paleta(nome, escuro, cor_custom):
    modo = "escuro" if escuro else "claro"
    p = dict(TEMAS[TEMA_PADRAO if nome == PERSONALIZADA else nome][modo])
    if nome == PERSONALIZADA:
        p["destaque"] = cor_custom
    p["sobre_destaque"] = contraste(p["destaque"])
    p["tinta"] = misturar(p["superficie"], p["destaque"], 0.14)
    p["destaque_hover"] = misturar(p["destaque"], "#ffffff" if escuro else "#000000", 0.15)
    p["esquema"] = "dark" if escuro else "light"
    p["modo_inativo"] = ".st-key-modo_claro" if escuro else ".st-key-modo_escuro"
    regras = []
    for slug, claro, noturno in SITUACAO.values():
        fundo, texto = noturno if escuro else claro
        regras.append(f".na-selo-{slug}, .na-card-{slug} {{ background: {fundo}; color: {texto}; }}"
                      f" .na-card-{slug} {{ border-left-color: {texto}; }}")
    p["situacoes"] = "\n".join(regras)
    return p


CSS = Template("""
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap");
:root { color-scheme: $esquema; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: $fundo; color: $texto; }
[data-testid="stHeader"] { background: $fundo; }
[data-testid="stHeader"] button, [data-testid="stHeader"] svg, [data-testid="stToolbar"] * { color: $texto; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background: $lateral; border-right: 1px solid $borda; }
.st-key-modo_claro button, .st-key-modo_escuro button { width: 100%; min-height: 2.4rem; padding: .2rem 0; }
$modo_inativo button { opacity: .5; }
$modo_inativo button:hover { opacity: 1; }
.st-key-excluir_aluno button { width: auto !important; min-height: 0 !important; height: auto !important; padding: .15rem .6rem !important; }
.st-key-excluir_aluno button p { font-size: .75rem !important; line-height: 1.2 !important; }
[data-testid="stElementContainer"]:has(style), .element-container:has(style) { display: none; }

h1, h2, h3, h4, h5, h6, label,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p { color: $texto; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: $suave; }
a { color: $destaque; }
hr { border-color: $borda; }

[data-testid="stMetric"] { background: $superficie; border: 1px solid $borda; border-radius: 10px; padding: .75rem 1rem; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: $suave !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color: $texto !important; }

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, [data-testid="stHeading"], [data-testid="stHeading"] *,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *, [data-testid="stCheckbox"] label p, [data-testid="stCheckbox"] label span,
[data-testid="stRadio"] label p { color: $texto !important; }

[data-testid="stTab"] p { color: $suave !important; }
[data-testid="stTab"][aria-selected="true"] p { color: $destaque !important; }
[data-testid="stTab"][aria-selected="true"] { border-bottom-color: $destaque !important; }
[data-testid="stTab"]::before, [data-testid="stTab"]::after, [data-testid="stTab"] > div:last-child:empty { background-color: transparent !important; }
[data-testid="stTab"][aria-selected="true"]::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 2px;
  background-color: $destaque !important; }
[data-testid="stTab"] { position: relative; }
[role="tablist"] { border-bottom: 1px solid $borda; }

[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stNumberInputContainer"],
[data-testid="stDateInputField"], [data-testid="stTimeInput"] [role="combobox"], [data-testid="stSelectbox"] [role="combobox"],
[data-testid="stSelectbox"] div:has(> [role="combobox"]) {
  background-color: $superficie !important; border-color: $borda !important; color: $texto !important; }
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within,
[data-testid="stDateInputField"]:focus-within { border-color: $destaque !important; }
input, textarea { background-color: transparent !important; color: $texto !important;
  -webkit-text-fill-color: $texto !important; caret-color: $texto; }
input::placeholder, textarea::placeholder { color: $suave !important; -webkit-text-fill-color: $suave !important; opacity: .8; }
[data-testid="stSelectbox"] [role="combobox"], [data-testid="stSelectbox"] [role="combobox"] * { color: $texto !important; }
[data-testid="stSelectbox"] svg, [data-testid="stSelectboxIcon"] { fill: $suave !important; color: $suave !important; }
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {
  background-color: $tinta !important; color: $texto !important; border-color: $borda !important; }

[data-testid="stSelectboxVirtualDropdown"], [role="listbox"], [data-testid="stColorPickerPopover"], [data-testid="stMainMenuPopover"],
[data-testid="stDateInputQuickSelectPopover"], [data-testid="stDateInputHeaderPickerPopover"], [data-testid="stPopoverBody"] {
  background-color: $superficie !important; color: $texto !important; border: 1px solid $borda; }
[role="option"], [role="option"] *, [data-testid="stMainMenuList"] *, [role="listbox"] * { color: $texto !important; }
[role="option"] { background-color: $superficie !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background-color: $tinta !important; }
[data-testid="stDateInputCalendar"], [data-testid="stDateInputCalendar"] * { background-color: $superficie !important; color: $texto !important; }
[data-testid="stDateInputCalendar"] [aria-selected="true"], [data-testid="stDateInputCalendar"] [aria-selected="true"] * {
  background-color: $destaque !important; color: $sobre_destaque !important; }

[data-testid="stForm"] { background: $superficie; border: 1px solid $borda; border-radius: 12px; }
[data-testid="stExpander"] details, [data-testid="stExpanderDetails"] { background: $superficie !important; border: 1px solid $borda; border-radius: 10px; }
[data-testid="stExpander"] summary { background: $superficie !important; border-radius: 10px; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: $texto !important; }
[data-testid="stExpander"] summary:hover { background: $tinta !important; }
[data-testid="stAlert"], [data-testid="stAlertContainer"] { background: $tinta !important; border: 1px solid $borda; border-radius: 10px; }
[data-testid="stAlert"] *, [data-testid="stAlertContainer"] * { color: $texto !important; }
[data-testid="stToast"], [data-testid="stToast"] * { background-color: $superficie; color: $texto !important; }

.stButton > button, [data-testid="stFormSubmitButton"] > button {
  background: $superficie !important; color: $texto !important; border: 1px solid $borda !important; border-radius: 8px; }
:is(button[kind="secondary"], button[kind="secondaryFormSubmit"], button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-secondaryFormSubmit"]) :is(p, span) { color: $texto !important; }
:is(button[kind="secondary"], button[kind="secondaryFormSubmit"], button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-secondaryFormSubmit"]):is(:hover, :focus, :active, :focus-visible) {
  border-color: $destaque !important; box-shadow: 0 0 0 .18rem $tinta !important; outline: none !important; }
:is(button[kind="secondary"], button[kind="secondaryFormSubmit"], button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-secondaryFormSubmit"]):is(:hover, :focus, :active, :focus-visible) :is(p, span) { color: $destaque !important; }
:is(button[kind="primary"], button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"]) { background: $destaque !important; color: $sobre_destaque !important; border: 1px solid $destaque !important; }
:is(button[kind="primary"], button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"]) :is(p, span) { color: $sobre_destaque !important; }
:is(button[kind="primary"], button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"]):is(:hover, :focus, :active, :focus-visible) {
  background: $destaque_hover !important; border-color: $destaque_hover !important; color: $sobre_destaque !important;
  box-shadow: 0 0 0 .18rem $tinta !important; outline: none !important; }
:is(button[kind="primary"], button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"]):is(:hover, :focus, :active, :focus-visible) :is(p, span) { color: $sobre_destaque !important; }

[data-testid="stMarkdownContainer"] .na-tabela-wrap { overflow-x: auto; border: 1px solid $borda; border-radius: 10px;
  background: $superficie; margin: .25rem 0 1rem; }
[data-testid="stMarkdownContainer"] .na-tabela { width: 100%; border-collapse: collapse; font-size: .92rem; margin: 0; }
[data-testid="stMarkdownContainer"] .na-tabela th { text-align: left; padding: .6rem .8rem; background: $tinta; color: $suave;
  font-weight: 600; border: 0; border-bottom: 1px solid $borda; white-space: nowrap; }
[data-testid="stMarkdownContainer"] .na-tabela td { padding: .55rem .8rem; background: transparent; color: $texto;
  border: 0; border-bottom: 1px solid $borda; }
[data-testid="stMarkdownContainer"] .na-tabela tbody tr:last-child td { border-bottom: 0; }
[data-testid="stMarkdownContainer"] .na-tabela tbody tr:hover td { background: $tinta; }
.na-selo { display: inline-block; padding: .12rem .6rem; border-radius: 999px; font-size: .8rem; font-weight: 600; white-space: nowrap; }
.na-card { border: 1px solid $borda; border-left-width: 4px; border-radius: 10px; padding: .7rem .9rem;
  margin-bottom: .6rem; line-height: 1.45; font-size: .93rem; }
.na-card-t { display: flex; justify-content: space-between; gap: .5rem; margin-bottom: .15rem; }
.na-card-r { font-size: .78rem; font-weight: 600; opacity: .85; white-space: nowrap; }
.stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp button, .stApp input, .stApp textarea,
[role="option"] { font-family: "Plus Jakarta Sans", "Source Sans", sans-serif; }
[data-testid="stMain"] h3 { font-size: 1.15rem; font-weight: 700; margin-top: .5rem; }
[data-testid="stMetric"] { border-left: 4px solid $destaque; border-radius: 12px; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { font-size: 1.9rem !important; font-weight: 700 !important; }
.na-hero { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;
  background: $destaque; color: $sobre_destaque; border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 1rem; }
.na-hero-s { font-size: .85rem; font-weight: 500; opacity: .85; }
.na-hero-t { font-size: 1.7rem; font-weight: 700; line-height: 1.2; }
.na-hero-d { font-size: .9rem; font-weight: 600; background: rgba(255,255,255,.18); border-radius: 999px; padding: .35rem .9rem; }
.na-dc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: .8rem; margin: .25rem 0 1rem; }
.na-dc { background: $superficie; border: 1px solid $borda; border-radius: 14px; padding: 1rem 1.1rem; }
.na-dc:hover { border-color: $destaque; }
.na-dc-h { display: flex; justify-content: space-between; align-items: flex-start; gap: .5rem; margin-bottom: .8rem; }
.na-dc-n { font-weight: 700; font-size: 1rem; line-height: 1.25; color: $texto; }
.na-dc-p { font-size: .8rem; color: $suave; }
.na-barra { position: relative; height: 8px; border-radius: 999px; background: $tinta; margin-bottom: .7rem; }
.na-barra-p { height: 100%; border-radius: 999px; background: $destaque; }
.na-barra-m { position: absolute; top: -4px; width: 2px; height: 16px; background: $texto; border-radius: 2px; }
.na-dc-f { display: flex; justify-content: space-between; gap: .4rem; font-size: .78rem; color: $suave; }
.na-dc-f strong { display: block; font-size: 1rem; color: $texto; }
.na-card { border-radius: 12px; }
.st-key-modo_claro button p, .st-key-modo_escuro button p { font-size: 1.25rem; line-height: 1; }
$situacoes
""")

st.set_page_config(page_title="Notas & Atividades", layout="wide")


@st.cache_resource
def banco():
    return Banco()


db = banco()
if "aviso" in st.session_state:
    st.toast(st.session_state.pop("aviso"), icon="✅")


def fmt(v, casas=1):
    return "—" if v is None else f"{v:.{casas}f}".replace(".", ",")


def br(iso):
    return date.fromisoformat(iso).strftime("%d/%m/%Y") if iso else "—"


def salvo(msg):
    st.session_state["aviso"] = msg
    st.rerun()


def quando(dias):
    return f"atrasada {-dias} d" if dias < 0 else "hoje" if dias == 0 else f"em {dias} d"


def tabela(linhas, col_situacao=None, alvo=st):
    """Tabela HTML que acompanha as cores do tema (st.dataframe não muda de cor em tempo real)."""
    if not linhas:
        return
    cab = "".join(f"<th>{escape(c)}</th>" for c in linhas[0])
    corpo = []
    for linha in linhas:
        celulas = []
        for col, valor in linha.items():
            if col == col_situacao:
                celulas.append(f'<td><span class="na-selo na-selo-{SITUACAO[valor][0]}">{escape(valor)}</span></td>')
            else:
                celulas.append(f"<td>{escape(str(valor))}</td>")
        corpo.append("<tr>" + "".join(celulas) + "</tr>")
    alvo.markdown(f'<div class="na-tabela-wrap"><table class="na-tabela"><thead><tr>{cab}</tr></thead>'
                  f'<tbody>{"".join(corpo)}</tbody></table></div>', unsafe_allow_html=True)


def cartao(slug, titulo, texto, etiqueta="", alvo=st):
    """Cartão de sugestão. `texto` já deve vir escapado/seguro; título e etiqueta são escapados aqui."""
    r = f'<span class="na-card-r">{escape(etiqueta)}</span>' if etiqueta else ""
    alvo.markdown(f'<div class="na-card na-card-{slug}"><div class="na-card-t"><strong>{escape(titulo)}</strong>{r}</div>'
                  f"<div>{texto}</div></div>", unsafe_allow_html=True)


DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]


def cabecalho(nome, hoje):
    data = f"{DIAS[hoje.weekday()]}, {hoje.day} de {MESES[hoje.month - 1]}"
    st.markdown(f'<div class="na-hero"><div><div class="na-hero-s">Painel acadêmico</div>'
                f'<div class="na-hero-t">Olá, {escape(nome)}</div></div><div class="na-hero-d">{data}</div></div>',
                unsafe_allow_html=True)


def painel_disciplinas(por_id, resumo):
    """Um cartão por disciplina: situação, barra da média parcial (marca = média mínima) e nota necessária."""
    cartoes = []
    for i, d in por_id.items():
        r, parcial = resumo[i], resumo[i]["media_parcial"]
        pct = 0 if parcial is None else min(parcial / 10, 1) * 100
        cartoes.append(
            f'<div class="na-dc"><div class="na-dc-h"><div><div class="na-dc-n">{escape(d["nome"])}</div>'
            f'<div class="na-dc-p">{escape(d["periodo"])}</div></div>'
            f'<span class="na-selo na-selo-{SITUACAO[r["situacao"]][0]}">{escape(r["situacao"])}</span></div>'
            f'<div class="na-barra"><div class="na-barra-p" style="width:{pct:.0f}%"></div>'
            f'<div class="na-barra-m" style="left:{d["media_minima"] * 10:.0f}%"></div></div>'
            f'<div class="na-dc-f"><span>Média parcial<strong>{fmt(parcial)}</strong></span>'
            f'<span>Mínima<strong>{fmt(d["media_minima"])}</strong></span>'
            f'<span>Nota necessária<strong>{fmt(r["necessaria"])}</strong></span></div></div>')
    st.markdown('<div class="na-dc-grid">' + "".join(cartoes) + "</div>", unsafe_allow_html=True)


def montar_sugestoes(por_id, resumo, ativ, proxima, atrasadas, semana):
    """Sugestões para todas as disciplinas (não só as em alerta), da mais urgente à menos urgente."""
    itens = []
    if atrasadas:
        n, p = len(atrasadas), atrasadas[0]
        quantas = "1 atividade passou do prazo" if n == 1 else f"{n} atividades passaram do prazo"
        itens.append(("risco", "Atividades atrasadas",
                      f"{quantas}. Comece por “{escape(p['titulo'])}” ({escape(p['disciplina'])}) e, se precisar, "
                      "combine uma nova data com o professor.", ""))
    if semana:
        nomes = ", ".join(f"“{escape(p['titulo'])}” ({escape(p['disciplina'])})" for p in semana[:3])
        extra = f" e mais {len(semana) - 3}" if len(semana) > 3 else ""
        itens.append(("caminho", "Próximos 7 dias",
                      f"Vencem em breve: {nomes}{extra}. Separe um horário fixo para cada uma.", ""))

    ordem = sorted(por_id, key=lambda i: (PRIORIDADE[resumo[i]["situacao"]], por_id[i]["nome"].lower()))
    for i in ordem:
        d, r = por_id[i], resumo[i]
        sit, minima, nec = r["situacao"], fmt(d["media_minima"]), fmt(r["necessaria"])
        if sit == "Em risco":
            texto = (f"Atingir {minima} exigiria mais que 10 nas avaliações restantes. Busque reforço "
                     "(monitoria, listas de exercícios) e converse com o professor sobre as alternativas.")
        elif sit == "Reprovado":
            texto = (f"Todas as avaliações foram lançadas e a média ficou abaixo de {minima}. Veja com o professor "
                     "ou a secretaria as opções de recuperação ou reposição.")
        elif sit == "Atenção":
            texto = (f"É preciso média {nec} nas avaliações restantes (média parcial {fmt(r['media_parcial'])}, "
                     f"mínima {minima}). Reserve mais tempo de estudo para esta disciplina.")
        elif sit == "Sem notas":
            texto = ("Nenhuma nota lançada ainda. Lance as notas conforme saírem para acompanhar a projeção."
                     if ativ[i] else
                     "Nenhuma atividade cadastrada. Cadastre as avaliações previstas, com os pesos, para calcular a nota necessária.")
        elif sit == "No caminho":
            texto = f"Bom andamento. Basta média {nec} nas avaliações restantes: mantenha a rotina de estudo."
        else:  # Aprovado
            texto = f"Média mínima ({minima}) garantida. Mantenha uma revisão leve e use o tempo extra onde mais precisar."
        if i in proxima and sit not in ("Aprovado", "Reprovado"):
            texto += f" Priorize “{escape(proxima[i][0])}” ({proxima[i][1]})."
        itens.append((SITUACAO[sit][0], d["nome"], texto, sit))

    if por_id:
        itens.append(("sem", "Dica de rotina",
                      "Estude em blocos de 25 a 40 minutos, com pausas curtas, e distribua a revisão ao longo da "
                      "semana em vez de concentrar tudo na véspera.", ""))
    else:
        itens.append(("sem", "Comece por aqui",
                      "Cadastre suas disciplinas e atividades para receber sugestões de estudo personalizadas.", ""))
    return itens


# ---------------- barra lateral: aparência
st.session_state.setdefault("tema", TEMA_PADRAO)
if st.session_state["tema"] not in (*TEMAS, PERSONALIZADA):
    st.session_state["tema"] = TEMA_PADRAO
st.session_state.setdefault("escuro", False)
st.session_state.setdefault("cor_custom", "#2563eb")


def definir_modo(escuro):
    st.session_state["escuro"] = escuro


st.sidebar.title("Notas & Atividades")
st.sidebar.markdown("**Aparência**")
m1, m2, _ = st.sidebar.columns([1, 1, 4], gap="small")
m1.button("☀", help="Modo claro", on_click=definir_modo, args=(False,), key="modo_claro",
          type="primary")
m2.button("☾", help="Modo escuro", on_click=definir_modo, args=(True,), key="modo_escuro",
          type="primary")
st.sidebar.selectbox("Cores do tema", [*TEMAS, PERSONALIZADA], key="tema")
if st.session_state["tema"] == PERSONALIZADA:
    st.sidebar.color_picker("Cor de destaque", key="cor_custom")

st.markdown(f"<style>{CSS.substitute(paleta(st.session_state['tema'], st.session_state['escuro'], st.session_state['cor_custom']))}</style>",
            unsafe_allow_html=True)

# ---------------- barra lateral: alunos
st.sidebar.divider()
alunos = {f"{a['nome']} (#{a['id']})": a["id"] for a in db.listar_alunos()}
escolha = st.sidebar.selectbox("Aluno", list(alunos)) if alunos else None
aluno = alunos.get(escolha)

with st.sidebar.expander("Novo aluno", expanded=not alunos):
    with st.form("novo_aluno", clear_on_submit=True):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail (opcional)")
        if st.form_submit_button("Cadastrar", type="primary"):
            if not nome.strip():
                st.error("Informe o nome.")
            else:
                try:
                    db.add_aluno(nome.strip(), email.strip() or None)
                except sqlite3.IntegrityError:
                    st.error("Esse e-mail já está cadastrado.")
                else:
                    salvo("Aluno cadastrado")

if aluno and st.sidebar.checkbox("Habilitar exclusão do aluno"):
    if st.sidebar.button("Excluir aluno", key="excluir_aluno", help="Apaga o aluno e seus dados"):
        db.excluir_aluno(aluno)
        salvo("Aluno excluído")

if not aluno:
    st.info("Cadastre um aluno no menu lateral para começar.")
    st.stop()

# ---------------- dados do aluno
disc = db.listar_disciplinas(aluno)
por_id = {d["id"]: d for d in disc}
ativ = {d["id"]: db.listar_atividades(d["id"]) for d in disc}
resumo = {i: resumo_disciplina(d["media_minima"], [(a["peso"], a["nota"]) for a in ativ[i]])
          for i, d in por_id.items()}
rotulo = lambda i: f"{por_id[i]['nome']} ({por_id[i]['periodo']})"  # noqa: E731

cabecalho(escolha.rsplit(" (#", 1)[0], date.today())
aba_painel, aba_disc, aba_ativ = st.tabs(["Painel", "Disciplinas", "Atividades e notas"])

# ---------------- painel
with aba_painel:
    hoje, prazos = date.today(), db.proximos_prazos(aluno)
    alertas = [i for i in por_id if resumo[i]["situacao"] in ("Atenção", "Em risco")]
    abertas = sum(a["status"] != "concluida" for v in ativ.values() for a in v)
    c = st.columns(4)
    c[0].metric("Disciplinas", len(disc))
    c[1].metric("Atividades em aberto", abertas)
    c[2].metric("Próximo prazo", br(prazos[0]["prazo"])[:5] if prazos else "—")
    c[3].metric("Disciplinas em alerta", len(alertas))

    st.subheader("Desempenho por disciplina")
    if disc:
        painel_disciplinas(por_id, resumo)
    else:
        st.caption("Cadastre disciplinas na aba Disciplinas.")

    esq, dir_ = st.columns(2)
    proxima, linhas, atrasadas, semana = {}, [], [], []
    for p in prazos:
        dias = (date.fromisoformat(p["prazo"]) - hoje).days
        proxima.setdefault(p["disciplina_id"], (p["titulo"], quando(dias)))
        linhas.append({"Disciplina": p["disciplina"], "Atividade": p["titulo"], "Prazo": br(p["prazo"]),
                       "Quando": quando(dias)})
        if dias < 0:
            atrasadas.append(p)
        elif dias <= 7:
            semana.append(p)
    esq.subheader("Próximos prazos")
    if linhas:
        tabela(linhas, alvo=esq)
    else:
        esq.caption("Nenhum prazo em aberto.")
    dir_.subheader("Sugestões de estudo")
    for slug, titulo, texto, etiqueta in montar_sugestoes(por_id, resumo, ativ, proxima, atrasadas, semana):
        cartao(slug, titulo, texto, etiqueta, alvo=dir_)

# ---------------- disciplinas
with aba_disc:
    with st.form("nova_disc", clear_on_submit=True):
        a, b, c = st.columns([3, 1, 1])
        nome = a.text_input("Disciplina")
        periodo = b.text_input("Período", placeholder="2026.1")
        media = c.number_input("Média mínima", 0.0, 10.0, 7.0, 0.5)
        if st.form_submit_button("Adicionar disciplina", type="primary"):
            if not nome.strip() or not periodo.strip():
                st.error("Informe a disciplina e o período.")
            else:
                db.add_disciplina(aluno, nome.strip(), periodo.strip(), media)
                salvo("Disciplina adicionada")
    if disc:
        tabela([{"Disciplina": d["nome"], "Período": d["periodo"], "Média mínima": fmt(d["media_minima"])}
                for d in disc])
        with st.expander("Editar ou excluir"):
            sel = st.selectbox("Disciplina", list(por_id), format_func=rotulo, key="sel_disc")
            d = por_id[sel]
            with st.form(f"ed_disc_{sel}"):
                a, b, c = st.columns([3, 1, 1])
                nome = a.text_input("Disciplina", d["nome"])
                periodo = b.text_input("Período", d["periodo"])
                media = c.number_input("Média mínima", 0.0, 10.0, float(d["media_minima"]), 0.5)
                c1, c2 = st.columns(2)
                if c1.form_submit_button("Salvar alterações") and nome.strip() and periodo.strip():
                    db.atualizar_disciplina(sel, nome.strip(), periodo.strip(), media)
                    salvo("Disciplina atualizada")
                if c2.form_submit_button("Excluir disciplina e atividades"):
                    db.excluir_disciplina(sel)
                    salvo("Disciplina excluída")


# ---------------- atividades e notas
def campos(k, a=None):
    c1, c2 = st.columns(2)
    titulo = c1.text_input("Título", a["titulo"] if a else "", key=f"{k}_t")
    desc = c2.text_input("Descrição", a["descricao"] if a else "", key=f"{k}_d")
    c3, c4, c5, c6 = st.columns(4)
    prazo = c3.date_input("Prazo", date.fromisoformat(a["prazo"]) if a and a["prazo"] else None,
                          format="DD/MM/YYYY", key=f"{k}_p")
    peso = c4.number_input("Peso", 0.1, 100.0, float(a["peso"]) if a else 1.0, 0.5, key=f"{k}_w")
    status = c5.selectbox("Status", list(STATUS), index=list(STATUS).index(a["status"]) if a else 0,
                          format_func=STATUS.get, key=f"{k}_s")
    tem_nota = c6.checkbox(
        "Lançar nota agora",
        value=bool(a is not None and a["nota"] is not None),
        key=f"{k}_tem_nota",
    )
    nota = None
    if tem_nota:
        nota = c6.number_input(
            "Nota (0–10)",
            min_value=0.0,
            max_value=10.0,
            value=float(a["nota"]) if a is not None and a["nota"] is not None else 0.0,
            step=0.5,
            key=f"{k}_n",
        )
    return titulo.strip(), desc.strip(), prazo.isoformat() if prazo else None, peso, status, nota


def gravar(id_, did, dados):
    titulo, desc, prazo, peso, status, nota = dados
    if not titulo:
        st.error("Informe o título da atividade.")
        return
    status = "concluida" if nota is not None else status
    if id_ is None:
        id_ = db.add_atividade(did, titulo, desc, prazo, peso, status)
    else:
        db.atualizar_atividade(id_, titulo, desc, prazo, peso, status)
    if nota is None:
        db.remover_nota(id_)
    else:
        db.lancar_nota(id_, nota)
    salvo("Atividade salva")


with aba_ativ:
    if not disc:
        st.info("Cadastre uma disciplina na aba Disciplinas.")
    else:
        did = st.selectbox("Disciplina", list(por_id), format_func=rotulo, key="disc_ativ")
        r, lista = resumo[did], ativ[did]
        m = st.columns(3)
        m[0].metric("Média parcial", fmt(r["media_parcial"]))
        m[1].metric("Nota necessária", fmt(r["necessaria"]))
        m[2].metric("Situação", r["situacao"])
        if lista:
            tabela([{"Atividade": a["titulo"], "Descrição": a["descricao"], "Prazo": br(a["prazo"]),
                     "Peso": fmt(a["peso"], 2), "Status": STATUS[a["status"]], "Nota": fmt(a["nota"])}
                    for a in lista])
        with st.form("nova_ativ", clear_on_submit=True):
            dados = campos("nova")
            if st.form_submit_button("Adicionar atividade", type="primary"):
                gravar(None, did, dados)
        if lista:
            with st.expander("Editar ou excluir"):
                pa = {a["id"]: a for a in lista}
                sel = st.selectbox("Atividade", list(pa), format_func=lambda i: pa[i]["titulo"], key=f"sel_a_{did}")
                with st.form(f"ed_a_{sel}"):
                    dados = campos(f"ed{sel}", pa[sel])
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("Salvar alterações"):
                        gravar(sel, did, dados)
                    if c2.form_submit_button("Excluir atividade"):
                        db.excluir_atividade(sel)
                        salvo("Atividade excluída")
