import json
import os
import sys
import tempfile

import gradio as gr
import pandas as pd
import plotly.graph_objects as go

import config
import storage

ADMIN_PASSWORD = "sintef2024"

# Force light mode at the meta level
_FONTS_HEAD = (
    '<meta name="color-scheme" content="light">'
    '<meta name="theme-color" content="#F0F4FF">'
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@300;400;500;600;700&'
    'family=Barlow+Condensed:wght@500;600;700&'
    'family=JetBrains+Mono:wght@400;500;600'
    '&display=swap" rel="stylesheet">'
)

# ── Design tokens ──────────────────────────────────────────────────────────────
CUSTOM_CSS = """
/* ── FORCE LIGHT MODE ── */
:root,
:root.dark,
html[data-theme="dark"],
html.dark {
    color-scheme: light !important;

    --bg:        #EEF2FB;
    --surface:   #FFFFFF;
    --surface2:  #F7F9FE;
    --border:    #D1D9EE;
    --border-md: #A8B7D8;

    --blue:      #2563EB;
    --blue-dk:   #1D4ED8;
    --blue-xdk:  #1E40AF;
    --blue-lo:   rgba(37,99,235,0.06);
    --blue-mid:  rgba(37,99,235,0.16);
    --blue-glow: rgba(37,99,235,0.28);

    --teal:      #0D9488;
    --teal-lo:   rgba(13,148,136,0.06);

    --ink:       #0F172A;
    --ink2:      #1E293B;
    --ink3:      #334155;
    --muted:     #64748B;

    --red:       #BE123C;
    --red-lo:    rgba(190,18,60,0.06);
    --red-mid:   rgba(190,18,60,0.22);

    --green:     #15803D;
    --green-lo:  rgba(21,128,61,0.08);

    --r:         10px;
    --r-sm:      6px;
    --shadow-sm: 0 1px 3px rgba(15,23,42,0.07), 0 1px 2px rgba(15,23,42,0.04);
    --shadow:    0 4px 12px rgba(15,23,42,0.08), 0 1px 3px rgba(15,23,42,0.05);
    --shadow-md: 0 8px 24px rgba(15,23,42,0.10), 0 2px 6px rgba(15,23,42,0.06);

    --f-sans:  'Inter', sans-serif;
    --f-cond:  'Barlow Condensed', sans-serif;
    --f-mono:  'JetBrains Mono', monospace;
}

@media (prefers-color-scheme: dark) {
    :root { color-scheme: light !important; }
}

/* ── Base reset ── */
*, *::before, *::after {
    box-sizing: border-box;
}

html {
    background: var(--bg) !important;
    background-image:
        radial-gradient(circle, rgba(37,99,235,0.055) 1px, transparent 1px) !important;
    background-size: 24px 24px !important;
    background-attachment: fixed !important;
}

body, .dark body, html.dark body {
    background: transparent !important;
    color: var(--ink) !important;
}

.gradio-container,
.dark .gradio-container,
html.dark .gradio-container {
    background: transparent !important;
    font-family: var(--f-sans) !important;
    color: var(--ink) !important;
    max-width: 1240px !important;
}

.gradio-container *,
.dark .gradio-container * {
    color: var(--ink);
}

/* ── Hero header ── */
.app-hero {
    background: linear-gradient(135deg, #1E40AF 0%, #2563EB 45%, #0EA5E9 100%) !important;
    border-radius: var(--r) !important;
    padding: 2rem 2.5rem !important;
    margin-bottom: 0.5rem !important;
    box-shadow: var(--shadow-md) !important;
    position: relative;
    overflow: hidden;
}

.app-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 80% 50%, rgba(255,255,255,0.08) 0%, transparent 60%);
    pointer-events: none;
}

.app-hero h1 {
    font-family: var(--f-cond) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #fff !important;
    letter-spacing: -0.01em !important;
    margin: 0 0 0.35rem 0 !important;
    line-height: 1.1 !important;
}

.app-hero p {
    font-family: var(--f-sans) !important;
    font-size: 0.92rem !important;
    color: rgba(255,255,255,0.82) !important;
    margin: 0 !important;
    line-height: 1.5 !important;
    max-width: 640px !important;
}

/* ── Blocks and panels ── */
.block,
.form,
.panel,
.dark .block,
.dark .form,
.dark .panel {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow 0.15s !important;
}

.block:hover {
    box-shadow: var(--shadow) !important;
}

/* ── Labels ── */
label span,
label > span,
.block label span,
.label-wrap span,
.dark label span {
    font-family: var(--f-mono) !important;
    font-size: 0.66rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

.checkbox-group label span,
.radio-group label span,
.checkbox-group label,
.radio-group label,
.dark .checkbox-group label span {
    font-family: var(--f-sans) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    color: var(--ink2) !important;
}

/* ── Tab navigation ── */
.tab-nav,
.dark .tab-nav {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 5px !important;
    gap: 2px !important;
    box-shadow: var(--shadow-sm) !important;
    flex-wrap: wrap !important;
}

.tab-nav > button,
.tab-nav button,
.dark .tab-nav button {
    font-family: var(--f-cond) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: var(--ink3) !important;
    background: transparent !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    padding: 0.45rem 1rem !important;
    transition: color 0.1s, background 0.1s !important;
    white-space: nowrap !important;
    cursor: pointer !important;
}

.tab-nav > button:hover,
.tab-nav button:hover {
    color: var(--blue) !important;
    background: var(--blue-lo) !important;
}

.tab-nav > button.selected,
.tab-nav button.selected,
.tab-nav > button[aria-selected="true"],
.tab-nav button[aria-selected="true"],
.dark .tab-nav button.selected {
    color: #fff !important;
    background: var(--blue) !important;
    box-shadow: 0 2px 8px var(--blue-glow) !important;
    font-weight: 700 !important;
}

/* ── Text inputs ── */
input[type="text"],
input[type="password"],
input[type="number"],
input[type="search"],
input[type="email"],
textarea,
.input-wrap input,
.dark input[type="text"],
.dark textarea {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--r) !important;
    color: var(--ink) !important;
    font-family: var(--f-sans) !important;
    font-size: 0.93rem !important;
    padding: 0.5rem 0.7rem !important;
    transition: border-color 0.12s, box-shadow 0.12s !important;
    caret-color: var(--blue) !important;
}

input:focus,
textarea:focus {
    border-color: var(--blue) !important;
    border-width: 2px !important;
    box-shadow: 0 0 0 3px var(--blue-lo) !important;
    outline: none !important;
    background: #fff !important;
}

::placeholder { color: var(--border-md) !important; opacity: 1 !important; }

/* ── Range slider ── */
input[type="range"] { accent-color: var(--blue) !important; }

.slider .wrap, .slider output, input[type="range"] + * {
    color: var(--ink2) !important;
    font-family: var(--f-mono) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* ── Buttons ── */
button.primary,
.primary-btn,
.dark button.primary {
    background: var(--blue) !important;
    color: #fff !important;
    font-family: var(--f-cond) !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: var(--r) !important;
    box-shadow: 0 2px 8px var(--blue-glow) !important;
    transition: background 0.1s, box-shadow 0.1s, transform 0.08s !important;
    cursor: pointer !important;
}

button.primary:hover { background: var(--blue-dk) !important; box-shadow: 0 4px 16px var(--blue-glow) !important; }
button.primary:active { transform: scale(0.98) !important; }

button.secondary,
.secondary-btn,
.dark button.secondary {
    background: var(--surface) !important;
    color: var(--blue) !important;
    border: 1.5px solid var(--blue-mid) !important;
    font-family: var(--f-cond) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: var(--r) !important;
    transition: background 0.1s, border-color 0.1s !important;
    cursor: pointer !important;
}

button.secondary:hover { background: var(--blue-lo) !important; border-color: var(--blue) !important; }

button.stop,
.dark button.stop {
    background: var(--surface) !important;
    color: var(--red) !important;
    border: 1.5px solid var(--red-mid) !important;
    font-family: var(--f-cond) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: var(--r) !important;
    transition: background 0.1s !important;
    cursor: pointer !important;
}

button.stop:hover { background: var(--red-lo) !important; }

/* ── Checkboxes ── */
input[type="checkbox"] {
    accent-color: var(--blue) !important;
    width: 15px !important;
    height: 15px !important;
    cursor: pointer !important;
}

/* ── Dropdown / Multiselect ── */
.wrap-inner, .svelte-select .wrap-inner, .dark .wrap-inner {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--ink) !important;
}

.token, .dark .token {
    background: var(--blue-lo) !important;
    color: var(--blue-xdk) !important;
    border: 1px solid var(--blue-mid) !important;
    font-family: var(--f-mono) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
}

.item, .list-item, .dark .item {
    color: var(--ink) !important;
    font-family: var(--f-sans) !important;
}

.item:hover, .list-item:hover {
    background: var(--blue-lo) !important;
    color: var(--blue) !important;
}

/* ── Dataframe / Table ── */
.table-wrap, .svelte-table, .dark .table-wrap {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
}

.table-wrap table { background: var(--surface) !important; border-collapse: collapse !important; width: 100% !important; }

.table-wrap thead tr { border-bottom: 2px solid var(--blue) !important; background: var(--blue-lo) !important; }

.table-wrap thead th {
    font-family: var(--f-mono) !important;
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--blue-xdk) !important;
    padding: 0.6rem 0.9rem !important;
}

.table-wrap tbody tr { border-bottom: 1px solid var(--border) !important; transition: background 0.08s !important; }
.table-wrap tbody tr:hover { background: var(--blue-lo) !important; }
.table-wrap tbody td {
    color: var(--ink) !important;
    font-family: var(--f-sans) !important;
    font-size: 0.87rem !important;
    padding: 0.5rem 0.9rem !important;
}

/* ── Markdown ── */
.prose, .md, .dark .prose, .dark .md {
    color: var(--ink3) !important;
    font-family: var(--f-sans) !important;
}

.prose p, .md p, .prose li, .md li {
    color: var(--ink3) !important;
    font-size: 0.93rem !important;
    line-height: 1.65 !important;
}

.prose strong, .md strong { color: var(--blue-dk) !important; font-weight: 700 !important; }
.prose hr, .md hr { border: none !important; border-top: 1.5px solid var(--border) !important; margin: 1.25rem 0 !important; }

.prose h1, .md h1 {
    font-family: var(--f-cond) !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
    line-height: 1.15 !important;
    margin-bottom: 0.3rem !important;
}

.prose h2, .md h2 {
    font-family: var(--f-cond) !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
    border-bottom: 2px solid var(--blue) !important;
    padding-bottom: 0.2rem !important;
    margin-top: 1.2rem !important;
}

.prose h3, .md h3 {
    font-family: var(--f-mono) !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    color: var(--blue-dk) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

.prose code, .md code {
    font-family: var(--f-mono) !important;
    background: var(--blue-lo) !important;
    color: var(--blue-xdk) !important;
    padding: 0.1em 0.35em !important;
    border-radius: 4px !important;
    font-size: 0.83em !important;
    border: 1px solid var(--blue-mid) !important;
}

/* ── Status messages ── */
.status-md p, .status-md {
    font-family: var(--f-mono) !important;
    font-size: 0.76rem !important;
    color: var(--ink3) !important;
    line-height: 1.5 !important;
    min-height: 1.2em !important;
}

/* ── Slider area row ── */
.area-slider-row .prose p, .area-slider-row .md p,
.area-slider-row .prose strong, .area-slider-row .md strong {
    font-family: var(--f-sans) !important;
    font-size: 0.87rem !important;
    font-weight: 600 !important;
    color: var(--ink2) !important;
}

/* ── Danger zone ── */
.danger-zone, .dark .danger-zone {
    border: 2px solid var(--red-mid) !important;
    background: var(--red-lo) !important;
    border-radius: var(--r) !important;
    padding: 1.25rem !important;
}

/* ── Section dividers ── */
.section-label {
    font-family: var(--f-mono) !important;
    font-size: 0.66rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    margin: 1rem 0 0.5rem !important;
}

.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Rating instruction pill ── */
.rating-hint {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.4rem !important;
    background: var(--blue-lo) !important;
    border: 1px solid var(--blue-mid) !important;
    border-radius: 100px !important;
    padding: 0.25rem 0.75rem !important;
    font-family: var(--f-mono) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: var(--blue-dk) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-md); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue); }

/* ── Gradio dark overrides (nuclear option) ── */
.dark {
    --background-fill-primary: var(--surface) !important;
    --background-fill-secondary: var(--surface2) !important;
    --background-fill-tertiary: var(--bg) !important;
    --border-color-primary: var(--border) !important;
    --color-accent: var(--blue) !important;
    --body-text-color: var(--ink) !important;
    --body-text-color-subdued: var(--muted) !important;
}
"""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_json_col(series: pd.Series, default):
    def _safe(v):
        try:
            return json.loads(v) if isinstance(v, str) else default
        except Exception:
            return default
    return series.apply(_safe)


def build_radar(df: pd.DataFrame, names: list[str] | None = None) -> go.Figure:
    layout_base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1E293B"),
        height=680,
        margin=dict(l=100, r=100, t=80, b=80),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#D1D9EE",
            borderwidth=1,
            font=dict(size=11, color="#1E293B"),
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
        ),
    )

    def _empty_fig(msg):
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=msg, font=dict(color="#64748B", size=14, family="Inter, sans-serif")),
            **layout_base,
        )
        return fig

    if df.empty:
        return _empty_fig("No data yet — submit profiles first")

    if names:
        df = df[df["name"].isin(names)]
        if df.empty:
            return _empty_fig("No profiles for selected members")

    areas = config.EXTENDED_TECH_AREAS
    interests_all = _parse_json_col(df["interests_json"], {})
    expertise_all = _parse_json_col(df["expertise_json"], {})

    interest_avgs, expertise_avgs = [], []
    for area in areas:
        i_vals = [d.get(area, 0) for d in interests_all if isinstance(d, dict)]
        e_vals = [d.get(area, 0) for d in expertise_all if isinstance(d, dict)]
        interest_avgs.append(sum(i_vals) / len(i_vals) if i_vals else 0)
        expertise_avgs.append(sum(e_vals) / len(e_vals) if e_vals else 0)

    active = [(i, a) for i, a in enumerate(areas)
              if interest_avgs[i] > 0 or expertise_avgs[i] > 0]

    if active:
        idx_list   = [i for i, _ in active]
        areas_used = [a for _, a in active]
        i_used     = [interest_avgs[i] for i in idx_list]
        e_used     = [expertise_avgs[i] for i in idx_list]
    else:
        areas_used = areas
        i_used     = interest_avgs
        e_used     = expertise_avgs

    max_val = max(max(i_used, default=0.1), max(e_used, default=0.1))
    r_max   = min(5.0, max(max_val * 1.15, 1.0))

    n = len(areas_used)
    short = [a[:22] + "…" if len(a) > 22 else a for a in areas_used]
    theta = short + [short[0]]
    tick_vals = [round(r_max * t / 5, 2) for t in range(1, 6)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=i_used + [i_used[0]], theta=theta,
        fill="toself", name="Interest (avg)",
        line=dict(color="#2563EB", width=2.5),
        fillcolor="rgba(37,99,235,0.10)",
        marker=dict(size=5, color="#2563EB"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=e_used + [e_used[0]], theta=theta,
        fill="toself", name="Expertise (avg)",
        line=dict(color="#0D9488", width=2.5),
        fillcolor="rgba(13,148,136,0.09)",
        marker=dict(size=5, color="#0D9488"),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(247,249,254,0.85)",
            radialaxis=dict(
                visible=True,
                range=[0, r_max],
                tickvals=tick_vals,
                tickfont=dict(size=9, color="#94A3B8"),
                gridcolor="rgba(37,99,235,0.10)",
                linecolor="rgba(37,99,235,0.10)",
                tickcolor="rgba(37,99,235,0.18)",
            ),
            angularaxis=dict(
                gridcolor="rgba(37,99,235,0.08)",
                linecolor="rgba(37,99,235,0.12)",
                tickfont=dict(size=9 if n > 15 else 10, color="#334155"),
                direction="clockwise",
            ),
        ),
        title=dict(
            text=f"Team Deep Tech Radar  ·  {n} active area{'s' if n != 1 else ''}",
            font=dict(size=13, color="#1E293B", family="Barlow Condensed, sans-serif"),
            x=0.5,
            xanchor="center",
        ),
        **layout_base,
    )
    return fig


def find_collaborators(df: pd.DataFrame, areas: list[str], min_score: int = 3) -> pd.DataFrame:
    _cols = ["Name", "Org", "Matched Areas", "Interest", "Expertise", "Collab Goals"]
    _empty = pd.DataFrame(columns=_cols)
    if df.empty or not areas:
        return _empty

    rows = []
    interests_all = _parse_json_col(df["interests_json"], {})
    expertise_all = _parse_json_col(df["expertise_json"], {})
    goals_all     = _parse_json_col(df["collab_goals_json"], [])

    for idx, row in df.iterrows():
        i_dict = interests_all.iloc[idx] if isinstance(interests_all.iloc[idx], dict) else {}
        e_dict = expertise_all.iloc[idx]  if isinstance(expertise_all.iloc[idx],  dict) else {}
        goals  = goals_all.iloc[idx]      if isinstance(goals_all.iloc[idx],      list) else []

        matched = [a for a in areas if i_dict.get(a, 0) >= min_score or e_dict.get(a, 0) >= min_score]
        if not matched:
            continue

        avg_i = round(sum(i_dict.get(a, 0) for a in matched) / len(matched), 1)
        avg_e = round(sum(e_dict.get(a, 0) for a in matched) / len(matched), 1)
        rows.append({
            "Name":          row["name"],
            "Org":           row.get("org", ""),
            "Matched Areas": ", ".join(matched),
            "Interest":      avg_i,
            "Expertise":     avg_e,
            "Collab Goals":  ", ".join(goals),
        })

    return pd.DataFrame(rows) if rows else _empty


# ── Client-side JS ─────────────────────────────────────────────────────────────
# Handles two things:
#   1. Instantly shows/hides slider rows when checkboxes change (no server round-trip wait)
#   2. Forces light colour-scheme so OS dark-mode never activates
_JS_SETUP = """
() => {
  // Force light mode
  document.documentElement.classList.remove('dark');
  document.documentElement.removeAttribute('data-theme');
  document.documentElement.style.colorScheme = 'light';
  document.body.style.colorScheme = 'light';

  // Re-apply light mode after any framework re-render
  const obs = new MutationObserver(() => {
    if (document.documentElement.classList.contains('dark')) {
      document.documentElement.classList.remove('dark');
    }
  });
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });

  // Instant slider-row toggle on checkbox change
  document.addEventListener('change', function(e) {
    if (!e.target || e.target.type !== 'checkbox') return;
    var grp = document.getElementById('area-select-group');
    if (!grp || !grp.contains(e.target)) return;
    var boxes = Array.from(grp.querySelectorAll('input[type="checkbox"]'));
    boxes.forEach(function(cb, i) {
      var row = document.getElementById('area-row-' + i);
      if (row) {
        row.style.display = cb.checked ? '' : 'none';
        row.style.visibility = cb.checked ? 'visible' : '';
      }
    });
  });
}
"""


# ── UI ─────────────────────────────────────────────────────────────────────────

_THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.blue,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=gr.themes.GoogleFont("Inter"),
    font_mono=gr.themes.GoogleFont("JetBrains Mono"),
).set(
    body_background_fill="transparent",
    body_background_fill_dark="transparent",
    background_fill_primary="#FFFFFF",
    background_fill_primary_dark="#FFFFFF",
    background_fill_secondary="#F7F9FE",
    background_fill_secondary_dark="#F7F9FE",
    border_color_primary="#D1D9EE",
    border_color_primary_dark="#D1D9EE",
    color_accent="#2563EB",
    color_accent_soft="rgba(37,99,235,0.06)",
    body_text_color="#0F172A",
    body_text_color_dark="#0F172A",
    body_text_color_subdued="#64748B",
    body_text_color_subdued_dark="#64748B",
    block_background_fill="#FFFFFF",
    block_background_fill_dark="#FFFFFF",
    block_border_color="#D1D9EE",
    block_border_color_dark="#D1D9EE",
    block_shadow="0 1px 3px rgba(15,23,42,0.07), 0 1px 2px rgba(15,23,42,0.04)",
    input_background_fill="#F7F9FE",
    input_background_fill_dark="#F7F9FE",
    input_border_color="#D1D9EE",
    input_border_color_dark="#D1D9EE",
    input_shadow="none",
    button_primary_background_fill="#2563EB",
    button_primary_background_fill_dark="#2563EB",
    button_primary_text_color="#FFFFFF",
    button_primary_text_color_dark="#FFFFFF",
)


def build_ui() -> gr.Blocks:
    areas   = config.EXTENDED_TECH_AREAS
    n_areas = len(areas)

    with gr.Blocks(title=config.APP_TITLE) as demo:

        # Hero header
        gr.HTML(f"""
        <div class="app-hero">
          <h1>◈ {config.APP_TITLE}</h1>
          <p>{config.APP_SUBTITLE}</p>
        </div>
        """)

        # ── Tab 1: Submit / Update ─────────────────────────────────────────────
        with gr.Tab("📡  Submit / Update Profile"):

            with gr.Row():
                name_dd = gr.Dropdown(
                    choices=config.TEAM_MEMBERS + ["External Collaborator"],
                    label="Your name",
                    value=config.TEAM_MEMBERS[0],
                    scale=2,
                )
                org_box = gr.Textbox(label="Organisation (external only)", visible=False, scale=1)

            profile_status = gr.Markdown("", elem_classes=["status-md"])

            area_select = gr.CheckboxGroup(
                choices=areas,
                label="Select your active tech areas",
                elem_id="area-select-group",
            )

            gr.HTML('<div class="section-label">Rate each selected area</div>')
            gr.HTML('<span class="rating-hint">0 = not applicable &nbsp;·&nbsp; 5 = leading expert</span>')

            slider_rows       = []
            interest_sliders  = []
            expertise_sliders = []

            for j, area in enumerate(areas):
                with gr.Row(
                    visible=False,
                    elem_id=f"area-row-{j}",
                    elem_classes=["area-slider-row"],
                ) as area_row:
                    gr.Markdown(f"**{area}**")
                    i_s = gr.Slider(0, 5, step=1, value=0, label="Interest")
                    e_s = gr.Slider(0, 5, step=1, value=0, label="Expertise")
                slider_rows.append(area_row)
                interest_sliders.append(i_s)
                expertise_sliders.append(e_s)

            def show_sliders(selected_areas):
                return [
                    gr.update(visible=(a in (selected_areas or [])))
                    for a in areas
                ]

            # queue=False makes visibility updates bypass the queue for instant response
            area_select.change(
                show_sliders,
                inputs=area_select,
                outputs=slider_rows,
                show_progress="hidden",
                queue=False,
            )

            gr.HTML('<div class="section-label">Collaboration</div>')
            collab_goals = gr.CheckboxGroup(choices=config.COLLAB_GOALS, label="Collaboration goals")
            description  = gr.Textbox(
                lines=3,
                label="Current work / collaboration idea",
                placeholder="e.g. Building a privacy-preserving federated ML system for healthcare…",
            )

            submit_btn    = gr.Button("⬆  Save Profile", variant="primary")
            submit_status = gr.Markdown("", elem_classes=["status-md"])

            _name_outputs = [
                org_box,
                profile_status,
                area_select,
                *slider_rows,
                *interest_sliders,
                *expertise_sliders,
                collab_goals,
                description,
            ]

            def _blank_form():
                return (
                    gr.update(value=[]),
                    *[gr.update(visible=False) for _ in areas],
                    *[gr.update(value=0) for _ in areas],
                    *[gr.update(value=0) for _ in areas],
                    gr.update(value=[]),
                    gr.update(value=""),
                )

            def on_name_change(name):
                yield (
                    gr.update(visible=(name == "External Collaborator")),
                    "⏳ &nbsp; Loading profile…",
                    *([gr.update()] * (1 + n_areas * 3 + 2)),
                )

                if name == "External Collaborator":
                    yield (gr.update(visible=True), "", *_blank_form())
                    return

                profile = storage.get_profile_by_name(name)

                if profile is None:
                    yield (
                        gr.update(visible=False),
                        "🆕 &nbsp; No existing profile — fill in your details and save.",
                        *_blank_form(),
                    )
                    return

                sel   = profile["areas"]
                intr  = profile["interests"]
                expt  = profile["expertise"]
                goals = profile["collab_goals"]
                desc  = profile["description"]

                yield (
                    gr.update(visible=False),
                    "✅ &nbsp; Existing profile loaded — update any fields and save.",
                    gr.update(value=sel),
                    *[gr.update(visible=(a in sel)) for a in areas],
                    *[gr.update(value=intr.get(a, 0)) for a in areas],
                    *[gr.update(value=expt.get(a, 0)) for a in areas],
                    gr.update(value=goals),
                    gr.update(value=desc),
                )

            name_dd.change(
                on_name_change,
                inputs=name_dd,
                outputs=_name_outputs,
                show_progress="hidden",
            )

            def submit_profile(name, org, selected_areas, *rest):
                yield "⏳ &nbsp; Saving profile…"
                i_vals = list(rest[:n_areas])
                e_vals = list(rest[n_areas:2 * n_areas])
                goals  = rest[2 * n_areas]
                desc   = rest[2 * n_areas + 1]

                eff_name  = name if name != "External Collaborator" else (org or "Anonymous")
                interests = {a: int(i_vals[j]) for j, a in enumerate(areas) if a in (selected_areas or [])}
                expertise = {a: int(e_vals[j]) for j, a in enumerate(areas) if a in (selected_areas or [])}

                is_update = storage.get_profile_by_name(eff_name) is not None
                profile = {
                    "name":         eff_name,
                    "org":          org if name == "External Collaborator" else "SINTEF",
                    "areas":        selected_areas or [],
                    "interests":    interests,
                    "expertise":    expertise,
                    "collab_goals": goals or [],
                    "description":  desc or "",
                }
                try:
                    storage.save_profile(profile)
                    action = "updated" if is_update else "saved"
                    yield f"✅ &nbsp; Profile **{action}** successfully!"
                except Exception as e:
                    yield f"❌ &nbsp; Error: {e}"

            submit_btn.click(
                submit_profile,
                inputs=[name_dd, org_box, area_select,
                        *interest_sliders, *expertise_sliders,
                        collab_goals, description],
                outputs=submit_status,
                show_progress="hidden",
            )

        # ── Tab 2: Team Radar ──────────────────────────────────────────────────
        with gr.Tab("🎯  Team Radar"):
            with gr.Row():
                radar_filter  = gr.Dropdown(
                    choices=["All team"] + config.TEAM_MEMBERS,
                    value="All team", multiselect=True,
                    label="Filter by member(s)",
                    scale=3,
                )
                radar_refresh = gr.Button("🔄  Refresh", variant="secondary", scale=1)

            radar_status = gr.Markdown("", elem_classes=["status-md"])
            radar_plot   = gr.Plot(label="")

            def update_radar(filter_names):
                yield "⏳ &nbsp; Fetching team profiles…", gr.update()
                df    = storage.load_all_profiles()
                n     = len(df)
                names = None if "All team" in (filter_names or ["All team"]) else filter_names
                fig   = build_radar(df, names)
                yield f"✅ &nbsp; **{n}** profile{'s' if n != 1 else ''} loaded", fig

            def _initial_radar():
                df  = storage.load_all_profiles()
                n   = len(df)
                fig = build_radar(df, None)
                return f"✅ &nbsp; **{n}** profile{'s' if n != 1 else ''} loaded", fig

            radar_refresh.click(update_radar, inputs=radar_filter,
                                outputs=[radar_status, radar_plot], show_progress="hidden")
            radar_filter.change(update_radar, inputs=radar_filter,
                                outputs=[radar_status, radar_plot], show_progress="hidden")
            demo.load(_initial_radar, outputs=[radar_status, radar_plot])

        # ── Tab 3: Find Collaborators ──────────────────────────────────────────
        with gr.Tab("🔍  Find Collaborators"):
            collab_areas = gr.CheckboxGroup(choices=areas, label="I want to collaborate on…")
            with gr.Row():
                min_score_slider = gr.Slider(1, 5, step=1, value=3,
                                             label="Min. interest / expertise score",
                                             scale=3)
                find_btn = gr.Button("🔍  Search", variant="primary", scale=1)

            collab_status  = gr.Markdown("", elem_classes=["status-md"])
            collab_results = gr.Dataframe(label="Matching Collaborators")

            def do_find(selected, min_score):
                yield "⏳ &nbsp; Searching profiles…", gr.update()
                df     = storage.load_all_profiles()
                result = find_collaborators(df, selected or [], int(min_score))
                n      = len(result)
                yield f"✅ &nbsp; Found **{n}** matching collaborator{'s' if n != 1 else ''}", result

            find_btn.click(do_find, inputs=[collab_areas, min_score_slider],
                           outputs=[collab_status, collab_results], show_progress="hidden")
            collab_areas.change(do_find, inputs=[collab_areas, min_score_slider],
                                outputs=[collab_status, collab_results], show_progress="hidden")

        # ── Tab 4: All Submissions ─────────────────────────────────────────────
        with gr.Tab("📊  All Submissions"):
            with gr.Row():
                all_refresh  = gr.Button("🔄  Refresh", variant="secondary")
                all_download = gr.DownloadButton("⬇  Download CSV", visible=False)

            all_status = gr.Markdown("", elem_classes=["status-md"])
            all_table  = gr.Dataframe(label="Submitted Profiles", wrap=True)

            _csv_path = [None]

            def refresh_table():
                yield "⏳ &nbsp; Loading submissions…", gr.update(), gr.update()
                df = storage.load_all_profiles()
                n  = len(df)
                if not df.empty:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                    df.to_csv(tmp.name, index=False)
                    _csv_path[0] = tmp.name
                dl = gr.update(visible=not df.empty,
                               value=_csv_path[0] if not df.empty else None)
                yield f"✅ &nbsp; **{n}** profile{'s' if n != 1 else ''} loaded", df, dl

            def _initial_table():
                df = storage.load_all_profiles()
                n  = len(df)
                if not df.empty:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                    df.to_csv(tmp.name, index=False)
                    _csv_path[0] = tmp.name
                dl = gr.update(visible=not df.empty,
                               value=_csv_path[0] if not df.empty else None)
                return f"✅ &nbsp; **{n}** profile{'s' if n != 1 else ''} loaded", df, dl

            all_refresh.click(refresh_table,
                              outputs=[all_status, all_table, all_download],
                              show_progress="hidden")
            demo.load(_initial_table, outputs=[all_status, all_table, all_download])

            gr.HTML('<div class="section-label" style="margin-top:1.5rem">Danger Zone</div>')
            gr.Markdown("Password-protected, **irreversible** actions.")

            with gr.Group(elem_classes=["danger-zone"]):
                gr.Markdown("### 🔐 Admin Actions")
                with gr.Row():
                    danger_pwd = gr.Textbox(
                        label="Admin password",
                        type="password",
                        placeholder="Enter password to unlock…",
                        scale=3,
                    )
                with gr.Row():
                    clear_btn   = gr.Button("🗑️  Clear All Data", variant="stop",     scale=1)
                    restart_btn = gr.Button("🔄  Restart App",    variant="secondary", scale=1)
                danger_status = gr.Markdown("", elem_classes=["status-md"])

            def clear_dataset(password):
                if password != ADMIN_PASSWORD:
                    yield "❌ &nbsp; **Wrong password.** Access denied."
                    return
                yield "⏳ &nbsp; Wiping dataset…"
                try:
                    storage.clear_all_profiles()
                    yield "✅ &nbsp; **Dataset cleared.** All profiles deleted."
                except Exception as e:
                    yield f"❌ &nbsp; Error: {e}"

            def restart_app(password):
                if password != ADMIN_PASSWORD:
                    yield "❌ &nbsp; **Wrong password.** Access denied."
                    return
                yield "🔄 &nbsp; **Restarting…** Reconnect in a few seconds."
                import time
                time.sleep(1.5)
                os.execv(sys.executable, [sys.executable] + sys.argv)

            clear_btn.click(clear_dataset, inputs=danger_pwd,
                            outputs=danger_status, show_progress="hidden")
            restart_btn.click(restart_app, inputs=danger_pwd,
                              outputs=danger_status, show_progress="hidden")

    return demo


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = build_ui()
    app.queue(default_concurrency_limit=5)
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7861,
        css=CUSTOM_CSS,
        head=_FONTS_HEAD,
        js=_JS_SETUP,
        theme=_THEME,
        show_error=True,
        quiet=False,
    )
