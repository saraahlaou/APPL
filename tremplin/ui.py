"""Design system de Tremplin : palette, CSS global et composants HTML/SVG.

Streamlit ne permet pas de contrôler chaque pixel nativement : on injecte donc
une feuille de style globale et on construit des cartes / graphiques en HTML
et SVG pour obtenir une interface soignée sans dépendance front-end.
"""

from __future__ import annotations

import html
import math

import streamlit as st

# --------------------------------------------------------------------------- #
# Palette
# --------------------------------------------------------------------------- #

INK = "#10231F"
INK_SOFT = "#3D4C46"
PAPER = "#F7F6F1"
CARD = "#FFFFFF"
LINE = "#E7E4D9"
PRIMARY = "#17795E"
PRIMARY_DARK = "#0B3D2E"
PRIMARY_SOFT = "#E4F2EC"
LIME = "#D9F55C"
CORAL = "#E4573D"
CORAL_SOFT = "#FBE9E5"
AMBER = "#DE9A22"
AMBER_SOFT = "#FCF1DC"
BLUE = "#4B5D9E"
BLUE_SOFT = "#E9ECF7"
VIOLET = "#7A5CC6"
VIOLET_SOFT = "#EFEAF9"
MUTED = "#6E7B76"


def score_color(score: float) -> str:
    if score >= 80:
        return PRIMARY
    if score >= 65:
        return "#4C9A3F"
    if score >= 50:
        return AMBER
    return CORAL


def score_tone(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 65:
        return "lime"
    if score >= 50:
        return "amber"
    return "coral"


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


# --------------------------------------------------------------------------- #
# CSS global
# --------------------------------------------------------------------------- #

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap');

:root {
  --ink: #10231F;
  --ink-soft: #3D4C46;
  --paper: #F7F6F1;
  --card: #FFFFFF;
  --line: #E7E4D9;
  --primary: #17795E;
  --primary-dark: #0B3D2E;
  --primary-soft: #E4F2EC;
  --lime: #D9F55C;
  --coral: #E4573D;
  --coral-soft: #FBE9E5;
  --amber: #DE9A22;
  --amber-soft: #FCF1DC;
  --blue: #4B5D9E;
  --blue-soft: #E9ECF7;
  --violet: #7A5CC6;
  --violet-soft: #EFEAF9;
  --muted: #6E7B76;
  --radius: 20px;
  --shadow: 0 1px 2px rgba(16,35,31,.05), 0 10px 30px -18px rgba(16,35,31,.22);
}

html, body, [class*="st-"], .stApp, button, input, textarea, select {
  font-family: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', sans-serif;
}

/* Les icônes Material Symbols doivent garder leur police dédiée :
   sinon le nom de l'icône (« keyboard_double_arrow_left ») s'affiche en texte. */
[data-testid="stIconMaterial"] {
  font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
}

.stApp {
  background:
    radial-gradient(1200px 500px at 85% -10%, rgba(217,245,92,.35), transparent 60%),
    radial-gradient(900px 500px at -10% 10%, rgba(23,121,94,.10), transparent 55%),
    var(--paper);
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
  background: transparent;
  height: 2.4rem;
}
[data-testid="stToolbar"] { right: 1rem; }

.block-container, [data-testid="stMainBlockContainer"] {
  padding-top: 1.1rem;
  padding-bottom: 4rem;
  max-width: 1240px;
}

/* ------------------------------ Sidebar ------------------------------ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0C1F1A 0%, #0F2C24 60%, #123528 100%);
  border-right: 1px solid rgba(255,255,255,.06);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.1rem; }
[data-testid="stSidebar"] * { color: #EAF2ED; }
[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  justify-content: flex-start;
  text-align: left;
  background: transparent;
  border: 1px solid transparent;
  color: #C8D6CF;
  border-radius: 12px;
  padding: .62rem .8rem;
  font-weight: 600;
  font-size: .93rem;
  transition: all .18s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,.07);
  color: #FFFFFF;
  border-color: rgba(255,255,255,.08);
  transform: none;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--lime);
  color: #0C1F1A;
  border-color: transparent;
  box-shadow: 0 6px 18px -8px rgba(217,245,92,.8);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background: #E4FA7C;
  color: #0C1F1A;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.09); }
[data-testid="stSidebar"] .stProgress > div > div > div > div { background: var(--lime); }
[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 14px;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary { color: #EAF2ED; }

/* ---- Bouton replier / déplier la barre latérale ---- */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] {
  visibility: visible !important;
  opacity: 1 !important;
  pointer-events: auto !important;
}
[data-testid="stSidebarCollapseButton"] button {
  background: rgba(255,255,255,.14) !important;
  border: 1px solid rgba(255,255,255,.32) !important;
  border-radius: 10px !important;
  width: 34px !important; height: 34px !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  padding: 0 !important;
  box-shadow: none !important;
  transition: all .18s ease;
}
[data-testid="stSidebarCollapseButton"] button:hover {
  background: var(--lime) !important;
  border-color: transparent !important;
}
[data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"] {
  color: #EAF2ED !important; font-size: 20px;
}
[data-testid="stSidebarCollapseButton"] button:hover [data-testid="stIconMaterial"] {
  color: #0C1F1A !important;
}
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"] button {
  background: #FFFFFF !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
  width: 34px !important; height: 34px !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  padding: 0 !important;
  box-shadow: var(--shadow) !important;
  transition: all .18s ease;
}
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
  border-color: var(--primary) !important;
  transform: translateY(-1px);
}
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapsedControl"] button [data-testid="stIconMaterial"] {
  color: var(--ink) !important; font-size: 20px;
}
[data-testid="stSidebar"] .tm-brand {
  display: flex; align-items: center; gap: .65rem;
  padding: .35rem .2rem .8rem;
}
[data-testid="stSidebar"] .tm-logo {
  width: 42px; height: 42px; border-radius: 14px;
  background: linear-gradient(135deg, #D9F55C, #7FD48A);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; box-shadow: 0 8px 18px -10px rgba(217,245,92,.9);
}
[data-testid="stSidebar"] .tm-brand-name {
  font-family: Fraunces, Georgia, serif; font-weight: 700;
  font-size: 1.32rem; color: #FFFFFF; line-height: 1.05;
}
[data-testid="stSidebar"] .tm-brand-tag {
  font-size: .72rem; color: #9DB8AC; letter-spacing: .04em;
}
.tm-ai-state {
  display: inline-block; padding: .32rem .6rem; border-radius: 999px;
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.12);
  color: #B9CCC2; font-size: .72rem; font-weight: 600;
}
.tm-ai-state.on { background: rgba(217,245,92,.16); border-color: rgba(217,245,92,.4); color: #D9F55C; }
.tm-side-foot {
  font-size: .72rem; color: #8FA79B; line-height: 1.55;
  padding: .2rem .2rem 1rem; border-top: 1px solid rgba(255,255,255,.08);
  margin-top: .4rem; padding-top: .8rem;
}

/* ------------------------------ Boutons ------------------------------ */
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
  border-radius: 999px;
  font-weight: 700;
  border: 1px solid var(--line);
  padding: .5rem 1.1rem;
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
  box-shadow: 0 1px 2px rgba(16,35,31,.05);
}
.stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px -12px rgba(16,35,31,.5);
  border-color: #CFCBBE;
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
  background: var(--primary);
  border-color: var(--primary);
  color: #FFFFFF;
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}
.stLinkButton > a { background: #FFFFFF; color: var(--ink) !important; text-decoration: none !important; }

/* ------------------------------ Cartes Streamlit ------------------------------ */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--card);
  border: 1px solid var(--line) !important;
  border-radius: var(--radius);
  padding: .35rem .35rem;
  box-shadow: var(--shadow);
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
  box-shadow: none;
  background: #FBFAF6;
}

/* ------------------------------ Champs ------------------------------ */
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  border-radius: 12px !important;
  border-color: var(--line) !important;
  background: #FFFFFF !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within,
[data-baseweb="select"] > div:focus-within {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(23,121,94,.14) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label,
.stSlider label, .stNumberInput label, .stFileUploader label, .stSelectSlider label {
  font-weight: 600 !important;
  color: var(--ink) !important;
  font-size: .88rem !important;
}
.stCaption, [data-testid="stCaptionContainer"] { color: var(--muted) !important; }

/* ------------------------------ Onglets ------------------------------ */
.stTabs [data-baseweb="tab-list"] {
  gap: .35rem;
  background: #ECE9DF;
  padding: .3rem;
  border-radius: 999px;
  width: fit-content;
  max-width: 100%;
  overflow-x: auto;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 999px;
  padding: .35rem 1rem;
  height: auto;
  font-weight: 600;
  color: var(--ink-soft);
}
.stTabs [aria-selected="true"] {
  background: var(--ink) !important;
  color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ------------------------------ Divers Streamlit ------------------------------ */
[data-testid="stExpander"] {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow);
  overflow: hidden;
}
[data-testid="stExpander"] summary { font-weight: 700; }
[data-testid="stFileUploaderDropzone"] {
  background: #FBFAF6;
  border: 1.5px dashed #C9C4B4;
  border-radius: 16px;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--primary); }
[data-testid="stAlert"] { border-radius: 14px; }
.stProgress > div > div > div > div { background: linear-gradient(90deg, var(--primary), #4C9A3F); }
.stSlider [data-baseweb="slider"] div[role="slider"] { background: var(--primary); }
[data-testid="stMetric"] {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: .8rem 1rem;
}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 14px; }
[data-testid="stToast"] { border-radius: 14px; }

/* ------------------------------ Composants Tremplin ------------------------------ */
.tm-section { margin: 1.6rem 0 .8rem; }
.tm-eyebrow {
  text-transform: uppercase;
  letter-spacing: .14em;
  font-size: .72rem;
  font-weight: 800;
  color: var(--primary);
}
.tm-section h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.65rem;
  line-height: 1.15;
  margin: .15rem 0 .2rem;
  color: var(--ink);
  letter-spacing: -.01em;
}
.tm-section p { color: var(--muted); margin: 0; font-size: .95rem; }

.tm-hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(125deg, #0B3D2E 0%, #11503C 55%, #17795E 100%);
  color: #F2F8F3;
  border-radius: 28px;
  padding: 2.2rem 2.2rem 2rem;
  box-shadow: 0 30px 60px -40px rgba(11,61,46,.9);
  animation: tmFadeUp .5s ease both;
}
.tm-hero:before {
  content: "";
  position: absolute;
  width: 420px; height: 420px; right: -140px; top: -180px;
  background: radial-gradient(circle, rgba(217,245,92,.55), transparent 65%);
  border-radius: 50%;
}
.tm-hero:after {
  content: "";
  position: absolute;
  width: 260px; height: 260px; right: 90px; bottom: -170px;
  background: radial-gradient(circle, rgba(255,255,255,.16), transparent 65%);
  border-radius: 50%;
}
.tm-hero h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 600;
  font-size: clamp(1.9rem, 3.4vw, 3rem);
  line-height: 1.06;
  margin: .5rem 0 .7rem;
  color: #FFFFFF;
  letter-spacing: -.015em;
  position: relative; z-index: 2;
}
.tm-hero h1 em { font-style: italic; color: var(--lime); }
.tm-hero p { color: #CFE3D8; max-width: 620px; font-size: 1rem; position: relative; z-index: 2; }
.tm-hero .tm-hero-content { position: relative; z-index: 2; }
.tm-hero-badge {
  display: inline-flex; align-items: center; gap: .4rem;
  background: rgba(217,245,92,.16);
  border: 1px solid rgba(217,245,92,.35);
  color: var(--lime);
  padding: .32rem .7rem; border-radius: 999px;
  font-size: .76rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
}
.tm-hero-points { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem; position: relative; z-index: 2; }
.tm-hero-points span {
  background: rgba(255,255,255,.10);
  border: 1px solid rgba(255,255,255,.14);
  padding: .34rem .7rem; border-radius: 999px;
  font-size: .8rem; color: #E7F2EA;
}

.tm-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.2rem 1.25rem;
  box-shadow: var(--shadow);
  animation: tmFadeUp .45s ease both;
}
.tm-card.tight { padding: .85rem 1rem; }
.tm-card-title { font-weight: 800; color: var(--ink); font-size: 1rem; margin-bottom: .15rem; }
.tm-card-sub { color: var(--muted); font-size: .87rem; }

.tm-stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .75rem; }
.tm-stat {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: .85rem 1rem;
  box-shadow: var(--shadow);
}
.tm-stat .label { font-size: .74rem; text-transform: uppercase; letter-spacing: .09em; color: var(--muted); font-weight: 700; }
.tm-stat .value { font-family: 'Fraunces', Georgia, serif; font-size: 1.7rem; color: var(--ink); line-height: 1.1; margin-top: .15rem; }
.tm-stat .sub { color: var(--muted); font-size: .8rem; margin-top: .1rem; }

.tm-chip {
  display: inline-flex; align-items: center; gap: .3rem;
  border-radius: 999px; padding: .28rem .65rem;
  font-size: .78rem; font-weight: 600;
  border: 1px solid var(--line);
  background: #F3F1E9; color: var(--ink-soft);
  margin: .12rem .15rem .12rem 0;
}
.tm-chip.green { background: var(--primary-soft); border-color: #BFE0D2; color: #0E5B45; }
.tm-chip.lime { background: #F1FAD2; border-color: #D9EC9A; color: #4A5A16; }
.tm-chip.amber { background: var(--amber-soft); border-color: #F3D9A8; color: #8A5A0B; }
.tm-chip.coral { background: var(--coral-soft); border-color: #F3C6BC; color: #A03621; }
.tm-chip.blue { background: var(--blue-soft); border-color: #CDD5EC; color: #354576; }
.tm-chip.violet { background: var(--violet-soft); border-color: #D8CCF1; color: #57408F; }
.tm-chip.ghost { background: transparent; }

.tm-bar { height: 9px; border-radius: 999px; background: #ECE9DF; overflow: hidden; }
.tm-bar > span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--primary), #5CB36B); transition: width .8s ease; }
.tm-bar.amber > span { background: linear-gradient(90deg, var(--amber), #E7B558); }
.tm-bar.coral > span { background: linear-gradient(90deg, var(--coral), #E8846F); }

.tm-gauge-wrap { display: flex; flex-direction: column; align-items: center; gap: .55rem; }
.tm-gauge { position: relative; width: 168px; height: 168px; flex: 0 0 auto; }
.tm-gauge svg { transform: rotate(-90deg); }
.tm-gauge .tm-gauge-center {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: .1rem;
}
.tm-gauge .score { font-family: 'Fraunces', Georgia, serif; font-size: 2.6rem; line-height: 1; color: var(--ink); }
.tm-gauge .outof { font-size: .74rem; color: var(--muted); font-weight: 700; letter-spacing: .08em; }
.tm-gauge-label {
  font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
  color: var(--muted); text-align: center;
}
.tm-gauge circle.tm-track { stroke: #ECE9DF; }
.tm-gauge circle.tm-value { stroke-linecap: round; animation: tmDash 1.1s ease both; }

.tm-dots { display: inline-flex; gap: 3px; vertical-align: middle; }
.tm-dots i { width: 9px; height: 9px; border-radius: 50%; background: #E2DFD4; display: inline-block; }
.tm-dots i.on { background: var(--primary); }
.tm-dots i.on.amber { background: var(--amber); }
.tm-dots i.on.coral { background: var(--coral); }

.tm-gap {
  border: 1px solid var(--line);
  border-left: 5px solid var(--amber);
  border-radius: 14px;
  padding: .8rem .95rem;
  background: var(--card);
  margin-bottom: .55rem;
}
.tm-gap.critique { border-left-color: var(--coral); background: #FFFBF9; }
.tm-gap.important { border-left-color: var(--amber); }
.tm-gap.bonus { border-left-color: var(--blue); }
.tm-gap .head { display: flex; justify-content: space-between; gap: .5rem; align-items: baseline; flex-wrap: wrap; }
.tm-gap .title { font-weight: 800; color: var(--ink); }
.tm-gap .impact { font-size: .78rem; font-weight: 700; color: var(--muted); white-space: nowrap; }
.tm-gap .why { color: var(--ink-soft); font-size: .88rem; margin-top: .2rem; }

.tm-strength {
  display: flex; gap: .6rem; align-items: flex-start;
  padding: .55rem .2rem; border-bottom: 1px dashed var(--line);
}
.tm-strength:last-child { border-bottom: none; }
.tm-strength .mark { color: var(--primary); font-weight: 800; }
.tm-strength .title { font-weight: 700; color: var(--ink); }
.tm-strength .detail { color: var(--muted); font-size: .85rem; }

.tm-phase {
  border-left: 3px solid var(--primary);
  padding-left: 1rem;
  margin: 1.1rem 0 .3rem;
}
.tm-phase .tag {
  font-size: .72rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase;
  color: var(--primary);
}
.tm-phase h3 { font-family: 'Fraunces', Georgia, serif; font-size: 1.25rem; margin: .1rem 0 .1rem; color: var(--ink); }
.tm-phase p { color: var(--muted); margin: 0 0 .4rem; font-size: .88rem; }

.tm-action-title { font-weight: 800; color: var(--ink); font-size: .96rem; }
.tm-action-detail { color: var(--ink-soft); font-size: .87rem; margin-top: .1rem; }
.tm-action-meta { color: var(--muted); font-size: .78rem; margin-top: .35rem; }

.tm-resource {
  border: 1px solid var(--line); border-radius: 14px; padding: .8rem .9rem;
  background: var(--card); height: 100%;
}
.tm-resource .provider { font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--primary); }
.tm-resource .title { font-weight: 700; color: var(--ink); font-size: .92rem; margin: .15rem 0; }
.tm-resource .meta { color: var(--muted); font-size: .78rem; }

.tm-empty {
  text-align: center; padding: 2.2rem 1.2rem;
  border: 1.5px dashed #D5D0C1; border-radius: var(--radius);
  background: rgba(255,255,255,.6);
}
.tm-empty .icon { font-size: 2rem; }
.tm-empty h3 { font-family: 'Fraunces', Georgia, serif; color: var(--ink); margin: .4rem 0 .2rem; }
.tm-empty p { color: var(--muted); margin: 0 auto; max-width: 460px; font-size: .9rem; }

.tm-job-head { display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; align-items: flex-start; }
.tm-job-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; color: var(--ink); margin: 0; line-height: 1.15; }
.tm-job-company { color: var(--ink-soft); font-weight: 600; margin-top: .15rem; }
.tm-job-meta { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .6rem; }
.tm-job-summary { color: var(--ink-soft); font-size: .93rem; margin-top: .6rem; }

.tm-score-pill {
  display: inline-flex; flex-direction: column; align-items: center; justify-content: center;
  min-width: 78px; padding: .5rem .8rem; border-radius: 16px;
  border: 1px solid var(--line); background: var(--card);
}
.tm-score-pill .num { font-family: 'Fraunces', Georgia, serif; font-size: 1.55rem; line-height: 1; color: var(--ink); }
.tm-score-pill .lab { font-size: .66rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }

.tm-timeline { position: relative; margin-left: .4rem; padding-left: 1.1rem; border-left: 2px dashed #D8D4C7; }
.tm-timeline .item { margin-bottom: 1rem; position: relative; }
.tm-timeline .item:before {
  content: ""; position: absolute; left: -1.48rem; top: .25rem;
  width: 12px; height: 12px; border-radius: 50%;
  background: var(--primary); border: 3px solid var(--paper);
}

.tm-note {
  background: var(--primary-soft);
  border: 1px solid #C8E4D8;
  border-radius: 14px;
  padding: .7rem .9rem;
  color: #124A39;
  font-size: .88rem;
}
.tm-note.warn { background: var(--amber-soft); border-color: #F0D9A9; color: #7A5108; }
.tm-note.coral { background: var(--coral-soft); border-color: #F0C8BE; color: #8E2F1C; }

.tm-divider { height: 1px; background: var(--line); margin: 1.2rem 0; border: none; }

@keyframes tmFadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes tmDash {
  from { stroke-dashoffset: var(--tm-dash-total); }
}
@media (max-width: 720px) {
  .tm-hero { padding: 1.4rem; border-radius: 22px; }
  .tm-gauge { width: 140px; height: 140px; }
  .tm-gauge .score { font-size: 2.1rem; }
  .block-container { padding-left: 1rem; padding-right: 1rem; }
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Composants HTML
# --------------------------------------------------------------------------- #

def section_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="tm-section">
          <div class="tm-eyebrow">{esc(eyebrow)}</div>
          <h2>{esc(title)}</h2>
          {f'<p>{esc(subtitle)}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(badge: str, title_html: str, subtitle: str, points: list[str] | None = None) -> None:
    chips = "".join(f"<span>{esc(point)}</span>" for point in (points or []))
    st.markdown(
        f"""
        <div class="tm-hero">
          <div class="tm-hero-content">
            <div class="tm-hero-badge">{esc(badge)}</div>
            <h1>{title_html}</h1>
            <p>{esc(subtitle)}</p>
            <div class="tm-hero-points">{chips}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_grid(stats: list[dict]) -> None:
    """stats : [{"label","value","sub"}]"""
    items = "".join(
        f"""<div class="tm-stat">
              <div class="label">{esc(item.get('label',''))}</div>
              <div class="value">{item.get('value','')}</div>
              <div class="sub">{esc(item.get('sub',''))}</div>
            </div>"""
        for item in stats
    )
    st.markdown(f'<div class="tm-stat-grid">{items}</div>', unsafe_allow_html=True)


def chips(items: list[str], tone: str = "", limit: int | None = None) -> str:
    shown = items[:limit] if limit else items
    return "".join(f'<span class="tm-chip {tone}">{esc(item)}</span>' for item in shown)


def gauge(score: float, label: str = "compatibilité", size: int = 168) -> str:
    color = score_color(score)
    radius = 66
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - max(0.0, min(1.0, score / 100)))
    gradient_id = f"tmGrad{int(score)}{size}"
    return f"""
    <div class="tm-gauge-wrap">
      <div class="tm-gauge" style="width:{size}px;height:{size}px">
        <svg width="{size}" height="{size}" viewBox="0 0 168 168">
          <defs>
            <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="{color}"/>
              <stop offset="100%" stop-color="#8FD36F"/>
            </linearGradient>
          </defs>
          <circle class="tm-track" cx="84" cy="84" r="{radius}" fill="none" stroke-width="12"/>
          <circle class="tm-value" cx="84" cy="84" r="{radius}" fill="none" stroke="url(#{gradient_id})"
                  stroke-width="12" stroke-dasharray="{circumference:.1f}"
                  stroke-dashoffset="{offset:.1f}"
                  style="--tm-dash-total:{circumference:.1f}"/>
        </svg>
        <div class="tm-gauge-center">
          <div class="score">{int(round(score))}</div>
          <div class="outof">/ 100</div>
        </div>
      </div>
      {f'<div class="tm-gauge-label">{esc(label)}</div>' if label else ''}
    </div>
    """


def score_pill(score: float, label: str = "match") -> str:
    return f"""<div class="tm-score-pill"><div class="num">{int(round(score))}</div><div class="lab">{esc(label)}</div></div>"""


def progress_bar(value: float, tone: str = "") -> str:
    value = max(0, min(100, value))
    return f'<div class="tm-bar {tone}"><span style="width:{value:.0f}%"></span></div>'


def dots(level: int, required: int | None = None) -> str:
    parts = []
    for index in range(1, 6):
        classes = "on"
        if required is not None and index <= required:
            classes += ""
        parts.append(f'<i class="{classes if index <= int(level or 0) else ""}"></i>')
    return f'<span class="tm-dots">{"".join(parts)}</span>'


def radar(subscores: dict, size: int = 330) -> str:
    """Radar SVG 5 axes à partir des sous-scores."""
    labels = list(subscores.keys())
    values = [max(0, min(100, subscores[key])) for key in labels]
    count = len(labels)
    center = size / 2
    radius = size * 0.31
    angle_step = 2 * math.pi / count

    def point(index: int, ratio: float) -> tuple[float, float]:
        angle = -math.pi / 2 + index * angle_step
        return (center + radius * ratio * math.cos(angle), center + radius * ratio * math.sin(angle))

    grid = []
    for ratio in (0.25, 0.5, 0.75, 1.0):
        points = " ".join(f"{point(i, ratio)[0]:.1f},{point(i, ratio)[1]:.1f}" for i in range(count))
        grid.append(f'<polygon points="{points}" fill="none" stroke="#E7E4D9" stroke-width="1"/>')
    axes = []
    for index in range(count):
        x, y = point(index, 1.0)
        axes.append(f'<line x1="{center}" y1="{center}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E7E4D9" stroke-width="1"/>')
    data_points = " ".join(
        f"{point(index, values[index] / 100)[0]:.1f},{point(index, values[index] / 100)[1]:.1f}"
        for index in range(count)
    )
    dots_html = []
    label_html = []
    for index, label in enumerate(labels):
        x, y = point(index, values[index] / 100)
        dots_html.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#17795E"/>')
        lx, ly = point(index, 1.22)
        anchor = "middle"
        if lx > center + 10:
            anchor = "start"
        elif lx < center - 10:
            anchor = "end"
        short = label.replace(" & certifications", "").replace(" & expérience", "")
        label_html.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-family="Plus Jakarta Sans, sans-serif" font-size="11.5" font-weight="700" fill="#3D4C46">{esc(short)}</text>'
        )
    return f"""
    <svg width="100%" viewBox="0 0 {size} {size}" style="max-width:{size}px;display:block;margin:0 auto">
      {"".join(grid)}
      {"".join(axes)}
      <polygon points="{data_points}" fill="rgba(23,121,94,.20)" stroke="#17795E" stroke-width="2.4" stroke-linejoin="round"/>
      {"".join(dots_html)}
      {"".join(label_html)}
    </svg>
    """


def strength_items(strengths: list[dict]) -> str:
    if not strengths:
        return '<div class="tm-card-sub">Aucun point fort détecté pour le moment : complète ton profil pour en faire apparaître.</div>'
    rows = []
    for item in strengths:
        rows.append(
            f"""<div class="tm-strength">
                  <div class="mark">✓</div>
                  <div>
                    <div class="title">{esc(item['title'])}</div>
                    <div class="detail">{esc(item['detail'])}</div>
                  </div>
                </div>"""
        )
    return "".join(rows)


def gap_cards(gaps: list[dict], limit: int = 6, show_how: bool = True) -> str:
    if not gaps:
        return '<div class="tm-note">Aucune lacune majeure détectée. Travaille maintenant la préparation d\'entretien et le réseau.</div>'
    severity_labels = {"critique": "Critique", "important": "Important", "bonus": "Bonus"}
    severity_tones = {"critique": "coral", "important": "amber", "bonus": "blue"}
    rows = []
    for gap in gaps[:limit]:
        severity = gap.get("severity", "important")
        rows.append(
            f"""<div class="tm-gap {esc(severity)}">
                  <div class="head">
                    <div class="title">{esc(gap['title'])}</div>
                    <div class="impact">
                      <span class="tm-chip {severity_tones.get(severity,'amber')}">{severity_labels.get(severity,'Important')}</span>
                      +{gap.get('impact_points', 0):.0f} pts potentiels
                    </div>
                  </div>
                  <div class="why">{esc(gap['why'])}</div>
                </div>"""
        )
    return "".join(rows)


def skill_matrix_rows(details: list[dict]) -> str:
    status_labels = {
        "acquise": ("Acquise", "green"),
        "presque": ("Presque", "lime"),
        "partielle": ("Partielle", "amber"),
        "manquante": ("Manquante", "coral"),
    }
    rows = []
    for detail in details:
        label, tone = status_labels.get(detail["status"], ("—", ""))
        rows.append(f"""
        <tr>
          <td style="padding:.5rem .4rem;border-bottom:1px solid #EFECE2">
            <div style="font-weight:700;color:#10231F">{esc(detail['skill'])}</div>
            <div style="color:#6E7B76;font-size:.75rem">{esc(detail['source'])}</div>
          </td>
          <td style="padding:.5rem .4rem;border-bottom:1px solid #EFECE2">{progress_bar(detail['coverage']*100, score_tone(detail['coverage']*100))}
            <div style="font-size:.72rem;color:#6E7B76;margin-top:.2rem">{detail['coverage']*100:.0f}% couvert</div>
          </td>
          <td style="padding:.5rem .4rem;border-bottom:1px solid #EFECE2;white-space:nowrap">{context_dots(detail)}</td>
          <td style="padding:.5rem .4rem;border-bottom:1px solid #EFECE2;text-align:right"><span class="tm-chip {tone}">{label}</span></td>
        </tr>""")
    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:.86rem">
      <thead>
        <tr style="text-align:left;color:#6E7B76;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em">
          <th style="padding:.3rem .4rem">Compétence</th>
          <th style="padding:.3rem .4rem">Couverture</th>
          <th style="padding:.3rem .4rem">Toi / Attendu</th>
          <th style="padding:.3rem .4rem;text-align:right">Statut</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


def context_dots(detail: dict) -> str:
    current = int(detail.get("current_level") or 0)
    required = int(detail.get("required_level") or 0)
    return (
        f"<span style='font-weight:700'>{current}</span>/<span style='color:#6E7B76'>{required}</span> "
        f"{dots(current)}"
    )


def empty_state(icon: str, title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="tm-empty">
          <div class="icon">{esc(icon)}</div>
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(text: str, tone: str = "") -> None:
    st.markdown(f'<div class="tm-note {tone}">{text}</div>', unsafe_allow_html=True)


def job_header(job: dict, score: float | None = None) -> str:
    skills = chips([r["skill"] for r in job.get("required_skills", [])], tone="ghost", limit=6)
    meta = chips(
        [m for m in [job.get("contract"), job.get("duration"), job.get("location"), job.get("remote"), job.get("salary")] if m],
        tone="",
    )
    score_html = score_pill(score, "estimé") if score is not None else ""
    return f"""
    <div class="tm-card">
      <div class="tm-job-head">
        <div style="max-width:640px">
          <div class="tm-eyebrow">{esc(job.get('domain',''))}</div>
          <h3 class="tm-job-title">{esc(job.get('title',''))}</h3>
          <div class="tm-job-company">{esc(job.get('company',''))} · {esc(job.get('company_type',''))}</div>
          <div class="tm-job-meta">{meta}</div>
        </div>
        {score_html}
      </div>
      <div class="tm-job-summary">{esc(job.get('summary',''))}</div>
      <div style="margin-top:.6rem">{skills}</div>
    </div>
    """
