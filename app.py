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

_FONTS_HEAD = (
    '<meta name="color-scheme" content="light">'
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Barlow+Condensed:wght@400;600;700&'
    'family=Barlow:ital,wght@0,300;0,400;0,500;0,600;1,400&'
    'family=JetBrains+Mono:wght@400;500;600'
    '&display=swap" rel="stylesheet">'
)

# ── CSS ────────────────────────────────────────────────────────────────────────
# Design tokens: paper-white cards, near-black ink, strong blue accent.
# Every label/input/text is dark enough to read without squinting.
CUSTOM_CSS = """
:root {
    color-scheme: light;
    --bg:       #E8EDF5;
    --card:     #FFFFFF;
    --card2:    #F8FAFD;
    --b0:       #E2E8F0;
    --b1:       #94A3B8;
    --b2:       #475569;
    --blue:     #1D4ED8;
    --blue-dk:  #1E40AF;
    --blue-lo:  rgba(29,78,216,0.07);
    --blue-mid: rgba(29,78,216,0.18);
    --ink:      #0F172A;
    --ink2:     #1E293B;
    --ink3:     #334155;
    --red:      #9F1239;
    --red-lo:   rgba(159,18,57,0.07);
    --red-mid:  rgba(159,18,57,0.32);
    --green:    #14532D;
    --bc:       'Barlow Condensed', sans-serif;
    --b:        'Barlow', sans-serif;
    --m:        'JetBrains Mono', monospace;
    --r:        8px;
}

/* ── Page background — NO pseudo-element that can block clicks ── */
html {
    background: var(--bg) !important;
    /* dot-grid directly on html, safe */
    background-image: radial-gradient(circle, rgba(29,78,216,0.07) 1px, transparent 1px) !important;
    background-size: 26px 26px !important;
    background-attachment: fixed !important;
}

body {
    background: transparent !important;
}

.gradio-container {
    background: transparent !important;
    font-family: var(--b) !important;
    color: var(--ink) !important;
    max-width: 1200px;
}

/* ── ALL text defaults to near-black ── */
.gradio-container * {
    color: var(--ink);
}

/* ── Labels: bold, dark, readable ── */
label span,
label > span,
.block label span,
.block label > span,
.label-wrap span,
.label-wrap > span {
    font-family: var(--m) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: var(--ink2) !important;
}

/* ── Checkbox/radio item text — body font, full size ── */
.checkbox-group label span,
.radio-group label span,
.checkbox-group label,
.radio-group label {
    font-family: var(--b) !important;
    font-size: 0.93rem !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    color: var(--ink) !important;
}

/* ── Blocks ── */
.block,
.form,
.panel {
    background: var(--card) !important;
    border: 1px solid var(--b0) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.06), 0 6px 16px rgba(15,23,42,0.04) !important;
}

/* ── Tab navigation ── */
.tab-nav {
    background: var(--card) !important;
    border: 1px solid var(--b0) !important;
    border-radius: var(--r) !important;
    padding: 4px !important;
    gap: 3px !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.08) !important;
    flex-wrap: wrap !important;
}

.tab-nav > button,
.tab-nav button {
    font-family: var(--bc) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--ink3) !important;
    background: transparent !important;
    border: 1.5px solid transparent !important;
    border-radius: 6px !important;
    padding: 0.48rem 0.95rem !important;
    transition: all 0.14s ease !important;
    white-space: nowrap !important;
}

.tab-nav > button:hover,
.tab-nav button:hover {
    color: var(--blue) !important;
    background: var(--blue-lo) !important;
    border-color: var(--blue-mid) !important;
}

.tab-nav > button.selected,
.tab-nav button.selected,
.tab-nav > button[aria-selected="true"],
.tab-nav button[aria-selected="true"] {
    color: #fff !important;
    background: var(--blue) !important;
    border-color: var(--blue) !important;
    box-shadow: 0 2px 10px rgba(29,78,216,0.3) !important;
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
.svelte-input input {
    background: var(--card2) !important;
    border: 1.5px solid var(--b1) !important;
    border-radius: var(--r) !important;
    color: var(--ink) !important;
    font-family: var(--b) !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 0.75rem !important;
    transition: border-color 0.14s, box-shadow 0.14s !important;
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

::placeholder {
    color: var(--b2) !important;
    opacity: 1 !important;
}

/* ── Range slider ── */
input[type="range"] {
    accent-color: var(--blue) !important;
}

/* Slider numeric value ── */
.slider .wrap,
.slider output,
input[type="range"] + * {
    color: var(--ink2) !important;
    font-family: var(--m) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

/* ── Buttons ── */
button.primary,
.primary-btn {
    background: var(--blue) !important;
    color: #fff !important;
    font-family: var(--bc) !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: var(--r) !important;
    box-shadow: 0 2px 10px rgba(29,78,216,0.22) !important;
    transition: all 0.14s !important;
}

button.primary:hover {
    background: var(--blue-dk) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 18px rgba(29,78,216,0.34) !important;
}

button.primary:active { transform: translateY(0) !important; }

button.secondary,
.secondary-btn {
    background: var(--card) !important;
    color: var(--blue) !important;
    border: 1.5px solid var(--blue-mid) !important;
    font-family: var(--bc) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    border-radius: var(--r) !important;
    transition: all 0.14s !important;
}

button.secondary:hover {
    background: var(--blue-lo) !important;
    border-color: var(--blue) !important;
}

button.stop {
    background: var(--card) !important;
    color: var(--red) !important;
    border: 1.5px solid var(--red-mid) !important;
    font-family: var(--bc) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    border-radius: var(--r) !important;
    transition: all 0.14s !important;
}

button.stop:hover {
    background: var(--red-lo) !important;
}

/* Download button inherits secondary style */
.download-btn {
    color: var(--blue) !important;
    border-color: var(--blue-mid) !important;
}

/* ── Checkboxes ── */
input[type="checkbox"] {
    accent-color: var(--blue) !important;
    width: 16px !important;
    height: 16px !important;
}

/* ── Dropdown / Multiselect ── */
.wrap-inner,
.svelte-select .wrap-inner {
    background: var(--card2) !important;
    border: 1.5px solid var(--b1) !important;
    color: var(--ink) !important;
}

.token {
    background: var(--blue-lo) !important;
    color: var(--blue-dk) !important;
    border: 1px solid var(--blue-mid) !important;
    font-family: var(--m) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
}

.item,
.list-item {
    color: var(--ink) !important;
    font-family: var(--b) !important;
}

.item:hover,
.list-item:hover {
    background: var(--blue-lo) !important;
    color: var(--blue) !important;
}

/* ── Dataframe / Table ── */
.table-wrap,
.svelte-table {
    border: 1px solid var(--b0) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
}

.table-wrap table {
    background: var(--card) !important;
    border-collapse: collapse !important;
    width: 100% !important;
}

.table-wrap thead tr {
    border-bottom: 2px solid var(--blue) !important;
    background: var(--blue-lo) !important;
}

.table-wrap thead th {
    font-family: var(--m) !important;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--blue-dk) !important;
    padding: 0.6rem 0.9rem !important;
}

.table-wrap tbody tr {
    border-bottom: 1px solid var(--b0) !important;
    transition: background 0.1s !important;
}

.table-wrap tbody tr:hover {
    background: var(--blue-lo) !important;
}

.table-wrap tbody td {
    color: var(--ink) !important;
    font-family: var(--b) !important;
    font-size: 0.88rem !important;
    padding: 0.52rem 0.9rem !important;
}

/* ── Markdown ── */
.prose, .md {
    color: var(--ink3) !important;
    font-family: var(--b) !important;
}

.prose p, .md p,
.prose li, .md li {
    color: var(--ink3) !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}

.prose strong, .md strong {
    color: var(--blue-dk) !important;
    font-weight: 700 !important;
}

.prose hr, .md hr {
    border: none !important;
    border-top: 1.5px solid var(--b0) !important;
    margin: 1.5rem 0 !important;
}

.prose h1, .md h1 {
    font-family: var(--bc) !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    color: var(--ink) !important;
    line-height: 1.15 !important;
    margin-bottom: 0.4rem !important;
}

.prose h2, .md h2 {
    font-family: var(--bc) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
    border-bottom: 2px solid var(--blue) !important;
    padding-bottom: 0.25rem !important;
    margin-top: 1.25rem !important;
}

.prose h3, .md h3 {
    font-family: var(--m) !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    color: var(--blue-dk) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

.prose code, .md code {
    font-family: var(--m) !important;
    background: var(--blue-lo) !important;
    color: var(--blue-dk) !important;
    padding: 0.1em 0.4em !important;
    border-radius: 4px !important;
    font-size: 0.84em !important;
    border: 1px solid var(--blue-mid) !important;
}

/* ── Status messages ── */
.status-md p,
.status-md {
    font-family: var(--m) !important;
    font-size: 0.78rem !important;
    color: var(--ink3) !important;
    line-height: 1.5 !important;
}

/* ── Slider row area label ── */
.area-slider-row .prose p,
.area-slider-row .md p,
.area-slider-row .prose strong,
.area-slider-row .md strong {
    font-family: var(--b) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: var(--ink2) !important;
}

/* ── Danger zone ── */
.danger-zone {
    border: 2px solid var(--red-mid) !important;
    background: var(--red-lo) !important;
    border-radius: var(--r) !important;
    padding: 1rem !important;
}

/* ── Custom scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--b1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue); }
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
        font=dict(family="JetBrains Mono, monospace", color="#1E293B"),
        height=660,
        margin=dict(l=95, r=95, t=70, b=70),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#CBD5E1",
            borderwidth=1,
            font=dict(size=12, color="#1E293B"),
        ),
    )

    def _empty_fig(msg):
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=msg, font=dict(color="#475569", size=13)),
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

    # Only show areas with actual data
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

    # Auto-scale with 15 % headroom, capped at 5
    max_val = max(max(i_used, default=0.1), max(e_used, default=0.1))
    r_max   = min(5.0, max(max_val * 1.15, 1.0))

    n = len(areas_used)
    short = [a[:20] + "…" if len(a) > 20 else a for a in areas_used]
    theta = short + [short[0]]
    tick_vals = [round(r_max * t / 5, 2) for t in range(1, 6)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=i_used + [i_used[0]], theta=theta,
        fill="toself", name="Interest (avg)",
        line=dict(color="#1D4ED8", width=2.5),
        fillcolor="rgba(29,78,216,0.10)",
        marker=dict(size=5, color="#1D4ED8"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=e_used + [e_used[0]], theta=theta,
        fill="toself", name="Expertise (avg)",
        line=dict(color="#0F766E", width=2.5),
        fillcolor="rgba(15,118,110,0.08)",
        marker=dict(size=5, color="#0F766E"),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(248,250,253,0.7)",
            radialaxis=dict(
                visible=True,
                range=[0, r_max],
                tickvals=tick_vals,
                tickfont=dict(size=9, color="#64748B"),
                gridcolor="rgba(29,78,216,0.12)",
                linecolor="rgba(29,78,216,0.12)",
                tickcolor="rgba(29,78,216,0.2)",
            ),
            angularaxis=dict(
                gridcolor="rgba(29,78,216,0.09)",
                linecolor="rgba(29,78,216,0.14)",
                tickfont=dict(size=9 if n > 15 else 10, color="#334155"),
                direction="clockwise",
            ),
        ),
        title=dict(
            text=f"Team Deep Tech Radar  ·  {n} active area{'s' if n != 1 else ''}",
            font=dict(size=13, color="#1E293B", family="Barlow Condensed, sans-serif"),
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
# Runs on page load. Intercepts checkbox changes in the area selection group and
# immediately shows/hides the corresponding slider rows without a server round-trip,
# so visibility feedback is instant rather than waiting for the Python response.
_JS_SETUP = """
() => {
  document.addEventListener('change', function(e) {
    if (!e.target || e.target.type !== 'checkbox') return;
    var grp = document.getElementById('area-select-group');
    if (!grp || !grp.contains(e.target)) return;
    var boxes = Array.from(grp.querySelectorAll('input[type="checkbox"]'));
    boxes.forEach(function(cb, i) {
      var row = document.getElementById('area-row-' + i);
      if (row) row.style.display = cb.checked ? 'flex' : 'none';
    });
  });
}
"""


# ── UI ─────────────────────────────────────────────────────────────────────────

def build_ui() -> gr.Blocks:
    areas   = config.EXTENDED_TECH_AREAS
    n_areas = len(areas)

    with gr.Blocks(title=config.APP_TITLE) as demo:

        gr.Markdown(f"# ◈ {config.APP_TITLE}\n\n{config.APP_SUBTITLE}")

        # ── Tab 1: Submit / Update ─────────────────────────────────────────────
        with gr.Tab("📡  Submit / Update Profile"):

            with gr.Row():
                name_dd = gr.Dropdown(
                    choices=config.TEAM_MEMBERS + ["External Collaborator"],
                    label="Your name",
                    value=config.TEAM_MEMBERS[0],
                )
                org_box = gr.Textbox(label="Organisation (external only)", visible=False)

            profile_status = gr.Markdown("", elem_classes=["status-md"])

            area_select = gr.CheckboxGroup(
                choices=areas,
                label="Select your active tech areas",
                elem_id="area-select-group",
            )

            gr.Markdown("### Rate each selected area &nbsp; `0 = not applicable` &nbsp; `5 = leading expert`")

            # Each area gets one Row (hidden by default), with its two sliders
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

            # Show/hide slider rows when checkboxes change
            def show_sliders(selected_areas):
                return [
                    gr.update(visible=(a in (selected_areas or [])))
                    for a in areas
                ]

            area_select.change(
                show_sliders,
                inputs=area_select,
                outputs=slider_rows,
                show_progress="hidden",
            )

            collab_goals = gr.CheckboxGroup(choices=config.COLLAB_GOALS, label="Collaboration goals")
            description  = gr.Textbox(
                lines=3,
                label="Current work / collaboration idea",
                placeholder="e.g. Building a privacy-preserving federated ML system for healthcare…",
            )

            submit_btn    = gr.Button("⬆  Save Profile", variant="primary")
            submit_status = gr.Markdown("", elem_classes=["status-md"])

            # Outputs for name-change pre-fill — order must exactly match the yield below
            _name_outputs = [
                org_box,             # 0
                profile_status,      # 1
                area_select,         # 2
                *slider_rows,        # 3 … 3+n_areas-1       (30)
                *interest_sliders,   # 3+n_areas … 3+2*n-1   (30)
                *expertise_sliders,  # 3+2n … 3+3n-1         (30)
                collab_goals,        # 3+3n
                description,         # 3+3n+1
            ]
            # Total: 2 + 1 + 3*n_areas + 2 = 95

            def _blank_form():
                return (
                    gr.update(value=[]),                              # area_select
                    *[gr.update(visible=False) for _ in areas],       # slider rows
                    *[gr.update(value=0) for _ in areas],             # interest sliders
                    *[gr.update(value=0) for _ in areas],             # expertise sliders
                    gr.update(value=[]),                              # collab_goals
                    gr.update(value=""),                              # description
                )
            # _blank_form returns 1 + 3*n_areas + 2 = 93 items

            def on_name_change(name):
                # First yield: show loading, keep form as-is
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
                )
                radar_refresh = gr.Button("🔄  Refresh", variant="secondary")

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
                                             label="Min. interest / expertise score")
                find_btn = gr.Button("🔍  Search", variant="primary")

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

            # ── Danger Zone ────────────────────────────────────────────────────
            gr.Markdown("---\n## ⚠️ Danger Zone\nPassword-protected, **irreversible** actions.")

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
                yield "⏳ &nbsp; Wiping dataset on HuggingFace…"
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
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7861,
        css=CUSTOM_CSS,
        head=_FONTS_HEAD,
        theme=gr.themes.Soft(),
        js=_JS_SETUP,
    )
