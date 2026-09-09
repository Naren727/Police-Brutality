"""Dark editorial theme: colors, Plotly template, injected CSS, and layout helpers."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# --- Surfaces and ink -------------------------------------------------------
PAGE = "#0d0d0d"
SURFACE = "#1a1a19"
BORDER = "rgba(255,255,255,0.08)"
GRID = "#2c2c2a"
INK = "#ffffff"
INK_SECONDARY = "#c3c2b7"
INK_MUTED = "#898781"

# --- Data hues --------------------------------------------------------------
# Validated with the dataviz skill's validate_palette.js against the #1a1a19
# surface under --pairs all: worst pair dE 20.9 normal-vision / 9.4 CVD, all
# three >= 3:1 contrast. Re-run that validator before changing any of these.
BLUE = "#3987e5"
AQUA = "#199e70"
ORANGE = "#d95926"
ACCENT = ORANGE

# Sequential ramps run dark (near-surface) -> luminous.
RAMP_BLUE = [[0.0, "#12233a"], [0.5, "#2a5f9e"], [1.0, "#5598e7"]]
RAMP_AQUA = [[0.0, "#0e2b22"], [0.5, "#137a56"], [1.0, "#3fc294"]]
RAMP_ORANGE = [[0.0, "#3a1a0e"], [0.5, "#a8401c"], [1.0, "#f07a45"]]

TEMPLATE = "dossier"


def _register_template() -> None:
    pio.templates[TEMPLATE] = go.layout.Template(
        layout=dict(
            paper_bgcolor=SURFACE,
            plot_bgcolor=SURFACE,
            colorway=[BLUE, ORANGE, AQUA],
            font=dict(family="Inter, system-ui, sans-serif", color=INK_SECONDARY, size=12),
            title=dict(font=dict(color=INK, size=15), x=0, xanchor="left"),
            margin=dict(l=8, r=8, t=52, b=8),
            xaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
                       tickfont=dict(color=INK_MUTED, size=11),
                       title=dict(font=dict(color=INK_MUTED, size=11))),
            yaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
                       tickfont=dict(color=INK_MUTED, size=11),
                       title=dict(font=dict(color=INK_MUTED, size=11))),
            hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER,
                            font=dict(color=INK, family="Inter, system-ui, sans-serif")),
            legend=dict(font=dict(color=INK_SECONDARY)),
        )
    )
    pio.templates.default = TEMPLATE


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

.stApp { background: #0d0d0d; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppViewBlockContainer"], .block-container { max-width: 1180px; padding-top: 3.2rem; }
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

.kicker {
  font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.18em;
  text-transform: uppercase; color: #898781; display: flex; align-items: center; gap: 14px;
}
.kicker::after { content: ''; flex: 1; height: 1px; background: #2c2c2a; }
/* Streamlit styles bare h1/h2/p via `.st-emotion-cache-<hash> h1` (0,1,1). Those
   hashes change between versions, so scope to the stable .stApp class instead —
   .stApp h1.hero-title is (0,2,1) and wins outright rather than by source order. */
.stApp h1.hero-title {
  font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; color: #ffffff;
  font-size: clamp(38px, 6vw, 68px); line-height: 1.04; letter-spacing: -0.015em;
  margin: 20px 0 12px; padding: 0;
}
.stApp h1.hero-title em { font-style: italic; color: #d95926; }
.stApp p.deck { font-size: 16px; line-height: 1.65; color: #c3c2b7; max-width: 64ch; margin-bottom: 30px; }

.kpi-band {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #2c2c2a;
  border-top: 1px solid #2c2c2a; border-bottom: 1px solid #2c2c2a; margin: 4px 0 34px;
}
.kpi { background: #0d0d0d; padding: 18px 16px 20px; }
.kpi .v { font-size: 34px; font-weight: 600; color: #ffffff; letter-spacing: -0.02em;
          font-variant-numeric: tabular-nums; line-height: 1; }
.kpi .l { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.14em;
          text-transform: uppercase; color: #898781; margin-top: 8px; }

.section-head { margin: 34px 0 18px; }
.section-head .eyebrow {
  font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.18em;
  text-transform: uppercase; color: #898781; display: flex; align-items: center; gap: 14px;
}
.section-head .eyebrow .num { color: #d95926; }
.section-head .eyebrow::after { content: ''; flex: 1; height: 1px; background: #2c2c2a; }
.stApp .section-head h2 {
  font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; color: #ffffff;
  font-size: 32px; letter-spacing: -0.01em; margin: 12px 0 0; padding: 0;
}

.stat-split {
  border: 1px solid rgba(255,255,255,0.08); background: #1a1a19; border-radius: 8px;
  padding: 22px 24px 24px;
}
.stat-split .v { font-size: 44px; font-weight: 600; color: #ffffff; letter-spacing: -0.02em;
                 font-variant-numeric: tabular-nums; line-height: 1; }
.stat-split .l { font-size: 14px; color: #c3c2b7; margin-top: 10px; }
.stat-split .track { height: 6px; border-radius: 3px; background: #2c2c2a; margin-top: 18px; overflow: hidden; }
.stat-split .fill { height: 100%; border-radius: 3px; background: #3987e5; }
.stat-split .foot { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.12em;
                    text-transform: uppercase; color: #898781; margin-top: 12px; }

[data-testid="stPlotlyChart"] {
  border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; background: #1a1a19; padding: 6px;
}

[data-testid="stTabs"] button {
  font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important;
  letter-spacing: 0.12em; text-transform: uppercase; color: #898781 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] { color: #ffffff !important; }

[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; }

.body-copy { font-size: 15px; line-height: 1.7; color: #c3c2b7; max-width: 72ch; margin-bottom: 18px; }
.body-copy strong { color: #ffffff; font-weight: 600; }

.method {
  font-family: 'JetBrains Mono', monospace; font-size: 10.5px; line-height: 1.9;
  letter-spacing: 0.04em; color: #898781; border-top: 1px solid #2c2c2a;
  padding-top: 18px; margin-top: 40px;
}
</style>
"""


def apply() -> None:
    """Register the Plotly template and inject the stylesheet. Call once, first."""
    _register_template()
    st.markdown(_CSS, unsafe_allow_html=True)


def masthead(kicker: str, title_html: str, deck: str) -> None:
    st.markdown(
        f'<div class="kicker">{kicker}</div>'
        f'<h1 class="hero-title">{title_html}</h1>'
        f'<p class="deck">{deck}</p>',
        unsafe_allow_html=True,
    )


def kpi_band(items) -> None:
    """items: sequence of (value, label) pairs, already formatted as strings."""
    cells = "".join(
        f'<div class="kpi"><div class="v">{value}</div><div class="l">{label}</div></div>'
        for value, label in items
    )
    st.markdown(f'<div class="kpi-band">{cells}</div>', unsafe_allow_html=True)


def section(number: str, label: str, title: str) -> None:
    st.markdown(
        f'<div class="section-head">'
        f'<div class="eyebrow"><span class="num">{number}</span> {label}</div>'
        f"<h2>{title}</h2>"
        f"</div>",
        unsafe_allow_html=True,
    )


def stat_split(value: str, label: str, pct: float, foot: str) -> None:
    st.markdown(
        f'<div class="stat-split">'
        f'<div class="v">{value}</div>'
        f'<div class="l">{label}</div>'
        f'<div class="track"><div class="fill" style="width:{pct:.1f}%"></div></div>'
        f'<div class="foot">{foot}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def body(text_html: str) -> None:
    st.markdown(f'<div class="body-copy">{text_html}</div>', unsafe_allow_html=True)


def methodology(text_html: str) -> None:
    st.markdown(f'<div class="method">{text_html}</div>', unsafe_allow_html=True)
