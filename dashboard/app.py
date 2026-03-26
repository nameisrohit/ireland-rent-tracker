# dashboard/app.py
# Ireland Rent Tracker — Editorial Data Dashboard
# Design: Financial Times / Irish Times inspired
# Clean, trustworthy, data-forward

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

import os
for key in ['REDSHIFT_HOST', 'REDSHIFT_PORT', 'REDSHIFT_DB',
            'REDSHIFT_USER', 'REDSHIFT_PASSWORD', 'REDSHIFT_SCHEMA',
            'AWS_REGION', 'S3_BUCKET']:
    if key not in os.environ and hasattr(st, 'secrets') and key in st.secrets:
        os.environ[key] = str(st.secrets[key])

st.set_page_config(
    page_title="Ireland Rent Tracker",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS — Editorial Design System
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --navy:    #0d1b2a;
    --ink:     #1a1a2e;
    --amber:   #e8a020;
    --red:     #c0392b;
    --green:   #1a7a4a;
    --paper:   #faf8f5;
    --cream:   #f0ece4;
    --border:  #d4cfc7;
    --muted:   #7a7670;
    --white:   #ffffff;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--paper) !important;
    color: var(--ink) !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide sidebar collapse button */
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Main background */
.main .block-container {
    background: var(--paper);
    padding: 2rem 3rem;
    max-width: 1400px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none;
    padding: 0;
}

[data-testid="stSidebar"] * {
    color: #c8d0dc !important;
}

.sidebar-logo {
    padding: 2rem 1.5rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1.5rem;
}

.sidebar-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff !important;
    line-height: 1.3;
    margin-top: 0.5rem;
}

.sidebar-subtitle {
    font-size: 0.75rem;
    color: var(--amber) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

.sidebar-nav-label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #5a6a7a !important;
    padding: 0 1.5rem;
    margin-bottom: 0.5rem;
}

.sidebar-stat {
    padding: 1rem 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.07);
}

.sidebar-stat-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    color: var(--amber) !important;
    font-weight: 500;
}

.sidebar-stat-label {
    font-size: 0.75rem;
    color: #5a6a7a !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    font-size: 0.9rem !important;
    color: #c8d0dc !important;
    padding: 6px 0 !important;
}

[data-testid="stRadio"] div[data-checked="true"] label {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* ── MASTHEAD ── */
.masthead {
    border-bottom: 3px solid var(--navy);
    padding-bottom: 1rem;
    margin-bottom: 0.5rem;
}

.masthead-eyebrow {
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
}

.masthead-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--navy);
    line-height: 1.1;
    margin: 0.3rem 0 0.2rem;
}

.masthead-deck {
    font-size: 1.05rem;
    color: var(--muted);
    font-weight: 300;
    max-width: 600px;
}

.masthead-rule {
    height: 3px;
    background: linear-gradient(90deg, var(--navy) 0%, var(--amber) 40%, transparent 100%);
    margin: 1rem 0;
    border: none;
}

/* ── STAT CARDS ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    margin: 1.5rem 0;
}

.stat-card {
    background: var(--white);
    padding: 1.2rem 1.5rem;
    position: relative;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--navy);
}

.stat-card.highlight::before {
    background: var(--amber);
}

.stat-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1;
}

.stat-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-top: 0.4rem;
}

.stat-delta {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    margin-top: 0.5rem;
    font-weight: 500;
}

.stat-delta.up { color: var(--red); }
.stat-delta.down { color: var(--green); }
.stat-delta.neutral { color: var(--muted); }

/* ── SECTION HEADERS ── */
.section-label {
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    border-top: 1px solid var(--border);
    padding-top: 0.8rem;
    margin: 2rem 0 0.8rem;
}

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 0.3rem;
}

/* ── INSIGHT BOX ── */
.insight {
    background: var(--cream);
    border-left: 4px solid var(--amber);
    padding: 1rem 1.2rem;
    margin: 1rem 0 1.5rem;
    font-size: 0.95rem;
    color: var(--ink);
    line-height: 1.7;
}

.insight strong {
    color: var(--navy);
}

/* ── RANKING LIST ── */
.rank-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid var(--cream);
    background: var(--white);
    transition: background 0.15s;
}

.rank-item:hover {
    background: var(--cream);
}

.rank-number {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: var(--muted);
    width: 1.5rem;
}

.rank-name {
    flex: 1;
    font-size: 0.9rem;
    color: var(--ink);
    padding: 0 0.8rem;
}

.rank-value {
    font-family: 'DM Mono', monospace;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--navy);
}

.rank-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    margin-left: 0.5rem;
}

.rank-badge.expensive { background: #fde8e8; color: var(--red); }
.rank-badge.affordable { background: #e8f5ee; color: var(--green); }

/* ── DATA TABLE ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── MULTISELECT ── */
[data-testid="stMultiSelect"] > div {
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
}

/* ── CAPTION ── */
.chart-caption {
    font-size: 0.75rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    margin-top: 0.3rem;
    padding-top: 0.5rem;
    border-top: 1px solid var(--border);
}

/* ── FOOTER ── */
.dash-footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 0.75rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# PLOTLY THEME — Editorial / FT Style
# ============================================================

PLOT_BG = 'rgba(0,0,0,0)'
GRID    = '#e8e4de'
TEXT    = '#1a1a2e'
MUTED   = '#7a7670'
NAVY    = '#0d1b2a'
AMBER   = '#e8a020'
RED     = '#c0392b'
GREEN   = '#1a7a4a'

PLOT_THEME = dict(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PLOT_BG,
    font=dict(family='DM Sans', color=TEXT, size=12),
    legend=dict(
        bgcolor='rgba(0,0,0,0)',
        bordercolor=GRID,
        borderwidth=1,
        font=dict(size=11)
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

XAXIS = dict(
    gridcolor=GRID,
    linecolor=GRID,
    tickcolor=GRID,
    tickfont=dict(family='DM Mono', size=11, color=MUTED),
    showgrid=False,
    zeroline=False
)

YAXIS = dict(
    gridcolor=GRID,
    linecolor='rgba(0,0,0,0)',
    tickcolor=GRID,
    tickfont=dict(family='DM Mono', size=11, color=MUTED),
    showgrid=True,
    zeroline=False
)

# ============================================================
# DATABASE
# ============================================================

@st.cache_resource
def get_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("REDSHIFT_HOST"),
            port=int(os.getenv("REDSHIFT_PORT", 5439)),
            dbname=os.getenv("REDSHIFT_DB", "dev"),
            user=os.getenv("REDSHIFT_USER"),
            password=os.getenv("REDSHIFT_PASSWORD"),
            sslmode="require",
            connect_timeout=30,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

@st.cache_data(ttl=3600)
def load_data(query):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        if conn.closed:
            st.cache_resource.clear()
            conn = get_connection()
        return pd.read_sql(query, conn)
    except Exception as e:
        st.cache_resource.clear()
        return pd.DataFrame()

def load_all_data():
    national = load_data("""
        SELECT year, avg_monthly_rent, yoy_change_pct, min_rent, max_rent
        FROM staging.national_trends ORDER BY year
    """)
    county = load_data("""
        SELECT year, county, avg_monthly_rent, yoy_change_pct
        FROM staging.rent_by_county ORDER BY year, county
    """)
    bedrooms = load_data("""
        SELECT year, county, bedrooms, avg_monthly_rent
        FROM staging.rent_by_bedrooms ORDER BY year, bedrooms
    """)
    falling = load_data("""
        SELECT year, location, county, avg_monthly_rent,
               prev_year_rent, change_pct
        FROM staging.falling_rents
        ORDER BY change_pct ASC LIMIT 50
    """)
    for df in [national, county, bedrooms, falling]:
        if 'year' in df.columns and not df.empty:
            df['year'] = df['year'].astype(int)
    return national, county, bedrooms, falling

# ============================================================
# HELPERS
# ============================================================

def masthead(eyebrow, title, deck):
    st.markdown(f"""
    <div class="masthead">
        <div class="masthead-eyebrow">{eyebrow}</div>
        <div class="masthead-title">{title}</div>
        <div class="masthead-deck">{deck}</div>
    </div>
    <hr class="masthead-rule">
    """, unsafe_allow_html=True)

def stat_card(label, value, delta=None, delta_dir="up", highlight=False):
    cls = "stat-card highlight" if highlight else "stat-card"
    delta_html = ""
    if delta:
        delta_html = f'<div class="stat-delta {delta_dir}">{delta}</div>'
    st.markdown(f"""
    <div class="{cls}">
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def section(label, title):
    st.markdown(f"""
    <div class="section-label">{label}</div>
    <div class="section-title">{title}</div>
    """, unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight">{text}</div>',
                unsafe_allow_html=True)

def chart_caption(text):
    st.markdown(f'<div class="chart-caption">{text}</div>',
                unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar(national_df):
    latest_rent = "€1,497"
    latest_yoy  = "+8.4%"

    if not national_df.empty:
        latest = national_df[national_df['year'] == national_df['year'].max()].iloc[0]
        latest_rent = f"€{latest['avg_monthly_rent']:,.0f}"
        latest_yoy  = f"+{latest['yoy_change_pct']:.1f}%"

    st.sidebar.markdown(f"""
    <div class="sidebar-logo">
        <div style="font-size:0.7rem;letter-spacing:0.15em;
                    text-transform:uppercase;color:#5a6a7a;">
            Ireland
        </div>
        <div class="sidebar-title">Rent<br>Tracker</div>
        <div class="sidebar-subtitle">2008 — 2024</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(
        '<div class="sidebar-nav-label">Navigate</div>',
        unsafe_allow_html=True
    )

    page = st.sidebar.radio(
        "",
        ["National Trends",
         "County Comparison",
         "Bedroom Analysis",
         "Falling Rents"]
    )

    st.sidebar.markdown(f"""
    <div class="sidebar-stat">
        <div class="sidebar-stat-value">{latest_rent}</div>
        <div class="sidebar-stat-label">National avg. 2024</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-value" style="color:#e8a020;">
            {latest_yoy}
        </div>
        <div class="sidebar-stat-label">Year-on-year change</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-value">438</div>
        <div class="sidebar-stat-label">Areas tracked</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-value">26</div>
        <div class="sidebar-stat-label">Counties covered</div>
    </div>
    <div style="padding:1.5rem;border-top:1px solid rgba(255,255,255,0.07);
                margin-top:1rem;">
        <div style="font-size:0.7rem;color:#3a4a5a;line-height:1.8;">
            Source: RTB / CSO Ireland<br>
            Updated annually<br><br>
            <a href="https://github.com/nameisrohit/ireland-rent-tracker"
               style="color:#e8a020;text-decoration:none;">
               GitHub ↗
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return page

# ============================================================
# PAGE 1 — NATIONAL TRENDS
# ============================================================

def page_national_trends(df):
    masthead(
        "Ireland Housing Market — National Overview",
        "The Rent Crisis in Numbers",
        "How average monthly rents have changed across Ireland from 2008 to 2024"
    )

    if df.empty:
        st.warning("No data available.")
        return

    latest   = df[df['year'] == df['year'].max()].iloc[0]
    earliest = df[df['year'] == df['year'].min()].iloc[0]
    bottom   = df.loc[df['avg_monthly_rent'].idxmin()]
    total_change = ((latest['avg_monthly_rent'] - earliest['avg_monthly_rent'])
                   / earliest['avg_monthly_rent'] * 100)

    # Stat cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card("Average rent — 2024",
                  f"€{latest['avg_monthly_rent']:,.0f}",
                  f"↑ {latest['yoy_change_pct']:.1f}% vs 2023",
                  "up", highlight=True)
    with col2:
        stat_card("Average rent — 2008",
                  f"€{earliest['avg_monthly_rent']:,.0f}",
                  "Base year", "neutral")
    with col3:
        stat_card("Total increase since 2008",
                  f"{total_change:.1f}%",
                  "Over 16 years", "up")
    with col4:
        stat_card("Market bottom",
                  f"€{bottom['avg_monthly_rent']:,.0f}",
                  f"In {int(bottom['year'])}", "down")

    insight(
        f"Irish rents reached a new all-time high of "
        f"<strong>€{latest['avg_monthly_rent']:,.0f}/month</strong> in 2024 — "
        f"a <strong>{total_change:.1f}% increase</strong> since 2008. "
        f"After falling to €{bottom['avg_monthly_rent']:,.0f} during the financial crisis, "
        f"rents have risen almost every year since 2013."
    )

    # Main trend chart
    section("Chart 1 of 2", "Average Monthly Rent 2008–2024")

    fig = go.Figure()

    # Recession shading
    fig.add_vrect(x0=2008.5, x1=2012.5,
                  fillcolor="#fde8e8", opacity=0.4,
                  layer="below", line_width=0,
                  annotation_text="Financial Crisis",
                  annotation_position="top left",
                  annotation_font=dict(size=10, color=RED))

    # Area fill
    fig.add_trace(go.Scatter(
        x=df['year'], y=df['avg_monthly_rent'],
        fill='tozeroy',
        fillcolor='rgba(13,27,42,0.06)',
        line=dict(color=NAVY, width=2.5),
        mode='lines+markers',
        marker=dict(
            size=7, color=NAVY,
            line=dict(color='white', width=2)
        ),
        hovertemplate=(
            '<b>%{x}</b><br>'
            'Average rent: €%{y:,.0f}/month'
            '<extra></extra>'
        )
    ))

    # Annotations
    fig.add_annotation(
        x=int(bottom['year']), y=bottom['avg_monthly_rent'],
        text=f"Low: €{bottom['avg_monthly_rent']:,.0f}",
        showarrow=True, arrowhead=2, ay=-40,
        arrowcolor=GREEN, font=dict(size=10, color=GREEN),
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor=GREEN, borderwidth=1, borderpad=4
    )
    fig.add_annotation(
        x=df['year'].max(), y=df['avg_monthly_rent'].max(),
        text=f"High: €{df['avg_monthly_rent'].max():,.0f}",
        showarrow=True, arrowhead=2, ay=-40,
        arrowcolor=RED, font=dict(size=10, color=RED),
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor=RED, borderwidth=1, borderpad=4
    )

    fig.update_layout(
        **PLOT_THEME,
        xaxis=dict(**XAXIS, dtick=1, tickformat='d'),
        yaxis=dict(**YAXIS, tickprefix='€', tickformat=',.0f'),
        hovermode='x unified',
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(
        "Source: RTB Average Monthly Rent Report, Central Statistics Office Ireland. "
        "Shaded area indicates financial crisis period."
    )

    # YoY chart
    section("Chart 2 of 2", "Year-on-Year Percentage Change")

    yoy_df = df.dropna(subset=['yoy_change_pct'])
    colors = [RED if x > 0 else GREEN for x in yoy_df['yoy_change_pct']]

    fig2 = go.Figure(go.Bar(
        x=yoy_df['year'],
        y=yoy_df['yoy_change_pct'],
        marker_color=colors,
        marker_line_width=0,
        text=yoy_df['yoy_change_pct'].apply(lambda x: f"{x:+.1f}%"),
        textposition='outside',
        textfont=dict(family='DM Mono', size=10, color=MUTED),
        hovertemplate='<b>%{x}</b><br>Change: %{y:+.2f}%<extra></extra>'
    ))

    fig2.add_hline(y=0, line_color=GRID, line_width=1.5)

    fig2.update_layout(
        **PLOT_THEME,
        xaxis=dict(**XAXIS, dtick=1, tickformat='d'),
        yaxis=dict(**YAXIS, ticksuffix='%'),
        height=320,
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)
    chart_caption(
        "Red bars indicate rent increases. Green bars indicate rent decreases."
    )

    st.markdown("""
    <div class="dash-footer">
        Ireland Rent Tracker &nbsp;|&nbsp;
        Data: RTB/CSO Ireland &nbsp;|&nbsp;
        Built by Rohit &nbsp;|&nbsp;
        github.com/nameisrohit/ireland-rent-tracker
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE 2 — COUNTY COMPARISON
# ============================================================

def page_county_comparison(county_df):
    masthead(
        "Ireland Housing Market — Regional Breakdown",
        "County by County",
        "Comparing average monthly rents across all Irish counties"
    )

    if county_df.empty:
        st.warning("No data available.")
        return

    years = sorted(county_df['year'].unique(), reverse=True)
    col_sel, _ = st.columns([1, 3])
    with col_sel:
        selected_year = st.selectbox("Select year", years)

    year_data = county_df[
        county_df['year'] == selected_year
    ].sort_values('avg_monthly_rent', ascending=False)

    col1, col2 = st.columns([3, 2])

    with col1:
        section("Chart", f"Average Monthly Rent by County — {selected_year}")

        sorted_asc = year_data.sort_values('avg_monthly_rent', ascending=True)

        fig = px.bar(
            sorted_asc,
            x='avg_monthly_rent',
            y='county',
            orientation='h',
            color='avg_monthly_rent',
            color_continuous_scale=[
                [0.0, '#e8f5ee'],
                [0.3, '#1a7a4a'],
                [0.7, '#e8a020'],
                [1.0, '#c0392b']
            ],
            labels={
                'avg_monthly_rent': 'Average Monthly Rent (€)',
                'county': ''
            }
        )

        fig.update_layout(
            **PLOT_THEME,
            xaxis=dict(**XAXIS, tickprefix='€', tickformat=',.0f'),
            yaxis=dict(**YAXIS, tickfont=dict(size=10)),
            coloraxis_showscale=False,
            height=620
        )
        st.plotly_chart(fig, use_container_width=True)
        chart_caption(
            f"Average monthly rent across all tracked counties. {selected_year}."
        )

    with col2:
        section("Rankings", f"Most Expensive — {selected_year}")
        top10 = year_data.head(10).reset_index(drop=True)

        st.markdown('<div style="border:1px solid #d4cfc7;">', unsafe_allow_html=True)
        for i, row in top10.iterrows():
            rank = i + 1
            badge = '<span class="rank-badge expensive">High</span>' if rank <= 3 else ''
            st.markdown(f"""
            <div class="rank-item">
                <div class="rank-number">{rank:02d}</div>
                <div class="rank-name">{row['county']}{badge}</div>
                <div class="rank-value">€{row['avg_monthly_rent']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        section("Rankings", f"Most Affordable — {selected_year}")
        bottom5 = year_data.tail(5).sort_values(
            'avg_monthly_rent', ascending=True
        ).reset_index(drop=True)

        st.markdown('<div style="border:1px solid #d4cfc7;">', unsafe_allow_html=True)
        for i, row in bottom5.iterrows():
            st.markdown(f"""
            <div class="rank-item">
                <div class="rank-number">{i+1:02d}</div>
                <div class="rank-name">{row['county']}
                    <span class="rank-badge affordable">Low</span>
                </div>
                <div class="rank-value">€{row['avg_monthly_rent']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Trend comparison
    section("Chart", "County Rent Trends Over Time")

    counties = sorted(county_df['county'].unique())
    defaults = [c for c in ['Dublin', 'Cork', 'Galway', 'Limerick']
                if c in counties][:4] or counties[:4]

    selected = st.multiselect(
        "Select counties to compare",
        counties, default=defaults
    )

    if selected:
        filtered = county_df[county_df['county'].isin(selected)]
        fig3 = px.line(
            filtered, x='year', y='avg_monthly_rent',
            color='county', markers=True,
            labels={
                'year': 'Year',
                'avg_monthly_rent': 'Avg Monthly Rent (€)',
                'county': 'County'
            },
            color_discrete_sequence=[NAVY, AMBER, RED, GREEN,
                                      '#6c5ce7', '#00b894']
        )
        fig3.update_layout(
            **PLOT_THEME,
            xaxis=dict(**XAXIS, dtick=1, tickformat='d'),
            yaxis=dict(**YAXIS, tickprefix='€', tickformat=',.0f'),
            hovermode='x unified',
            height=400,
            legend=dict(
                orientation='h',
                yanchor='bottom', y=1.02,
                xanchor='left', x=0
            )
        )
        fig3.update_traces(line_width=2, marker_size=6)
        st.plotly_chart(fig3, use_container_width=True)
        chart_caption("Source: RTB Average Monthly Rent Report, CSO Ireland.")

# ============================================================
# PAGE 3 — BEDROOM ANALYSIS
# ============================================================

def page_bedroom_analysis(bedrooms_df):
    masthead(
        "Ireland Housing Market — Property Size",
        "The Bedroom Premium",
        "How rent varies by number of bedrooms across Ireland"
    )

    if bedrooms_df.empty:
        st.warning("No data available.")
        return

    specific_beds = ['One bed', 'Two bed', 'Three bed', 'Four plus bed']
    df_filtered = bedrooms_df[bedrooms_df['bedrooms'].isin(specific_beds)]

    national_beds = df_filtered.groupby(
        ['year', 'bedrooms']
    )['avg_monthly_rent'].mean().reset_index()

    section("Chart 1 of 2", "National Average Rent by Bedroom Type — 2008 to 2024")

    colors_bed = {
        'One bed':       NAVY,
        'Two bed':       AMBER,
        'Three bed':     RED,
        'Four plus bed': GREEN
    }

    fig = go.Figure()
    for bed in specific_beds:
        bed_data = national_beds[national_beds['bedrooms'] == bed]
        if bed_data.empty:
            continue
        fig.add_trace(go.Scatter(
            x=bed_data['year'],
            y=bed_data['avg_monthly_rent'],
            name=bed,
            mode='lines+markers',
            line=dict(color=colors_bed.get(bed, NAVY), width=2.5),
            marker=dict(size=6, color=colors_bed.get(bed, NAVY)),
            hovertemplate=f'<b>{bed}</b><br>€%{{y:,.0f}}/month<extra></extra>'
        ))

    fig.update_layout(
        **PLOT_THEME,
        xaxis=dict(**XAXIS, dtick=1, tickformat='d'),
        yaxis=dict(**YAXIS, tickprefix='€', tickformat=',.0f'),
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation='h',
            yanchor='bottom', y=1.02,
            xanchor='left', x=0,
            font=dict(size=11)
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    chart_caption("National averages. Source: RTB/CSO Ireland.")

    section("Chart 2 of 2", "Rent by Bedroom Type — County Detail")

    col1, col2 = st.columns(2)
    with col1:
        years = sorted(bedrooms_df['year'].unique(), reverse=True)
        selected_year = st.selectbox("Year", years)
    with col2:
        counties = sorted(bedrooms_df['county'].unique())
        selected_county = st.selectbox("County", counties)

    year_county = df_filtered[
        (df_filtered['year'] == selected_year) &
        (df_filtered['county'] == selected_county)
    ].copy()

    bedroom_order = ['One bed', 'Two bed', 'Three bed', 'Four plus bed']
    year_county['sort_key'] = year_county['bedrooms'].apply(
        lambda x: bedroom_order.index(x) if x in bedroom_order else 99
    )
    year_county = year_county.sort_values('sort_key')

    if not year_county.empty:
        col_chart, col_table = st.columns([3, 2])

        with col_chart:
            bar_colors = [NAVY, AMBER, RED, GREEN]
            fig2 = go.Figure(go.Bar(
                x=year_county['bedrooms'],
                y=year_county['avg_monthly_rent'],
                marker_color=bar_colors[:len(year_county)],
                marker_line_width=0,
                text=year_county['avg_monthly_rent'].apply(
                    lambda x: f"€{x:,.0f}"
                ),
                textposition='outside',
                textfont=dict(family='DM Mono', size=11, color=MUTED),
                hovertemplate='<b>%{x}</b><br>€%{y:,.0f}/month<extra></extra>'
            ))
            fig2.update_layout(
                **PLOT_THEME,
                xaxis=XAXIS,
                yaxis=dict(**YAXIS, tickprefix='€', tickformat=',.0f'),
                height=350,
                showlegend=False,
                title=dict(
                    text=f"{selected_county} — {selected_year}",
                    font=dict(
                        family='Playfair Display',
                        size=14,
                        color=NAVY
                    )
                )
            )
            st.plotly_chart(fig2, use_container_width=True)

        with col_table:
            st.markdown(
                f'<div class="section-label">Data Table — '
                f'{selected_county} {selected_year}</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div style="border:1px solid #d4cfc7;">',
                        unsafe_allow_html=True)
            for _, row in year_county.iterrows():
                st.markdown(f"""
                <div class="rank-item">
                    <div class="rank-name">{row['bedrooms']}</div>
                    <div class="rank-value">
                        €{row['avg_monthly_rent']:,.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"No bedroom data available for {selected_county} in {selected_year}.")

# ============================================================
# PAGE 4 — FALLING RENTS
# ============================================================

def page_falling_rents(falling_df):
    masthead(
        "Ireland Housing Market — Affordability",
        "Where Rents Are Falling",
        "Areas that have seen year-on-year decreases in average monthly rent"
    )

    if falling_df.empty:
        st.info("No areas with falling rents found in the dataset.")
        return

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card("Areas with falling rents",
                  str(len(falling_df)), highlight=True)
    with col2:
        stat_card("Biggest single drop",
                  f"{falling_df['change_pct'].min():.1f}%",
                  "Year-on-year", "down")
    with col3:
        stat_card("Most affected county",
                  falling_df.iloc[0]['county'])
    with col4:
        stat_card("Average drop",
                  f"{falling_df['change_pct'].mean():.1f}%",
                  "Across falling areas", "down")

    insight(
        f"While national rents are rising, <strong>{len(falling_df)} specific areas</strong> "
        f"have recorded year-on-year decreases. The largest single drop was "
        f"<strong>{falling_df['change_pct'].min():.1f}%</strong> in "
        f"{falling_df.iloc[0]['location']}, {falling_df.iloc[0]['county']}. "
        f"These are often smaller towns or areas with new housing supply."
    )

    section("Chart", "Top 20 Areas With Largest Rent Decreases")

    top20 = falling_df.head(20)

    fig = px.bar(
        top20,
        x='change_pct',
        y='location',
        orientation='h',
        color='change_pct',
        color_continuous_scale=[
            [0.0, RED],
            [0.5, AMBER],
            [1.0, GREEN]
        ],
        labels={
            'change_pct': 'Year-on-Year Change (%)',
            'location': ''
        },
        hover_data={
            'county': True,
            'avg_monthly_rent': ':,.0f',
            'prev_year_rent': ':,.0f',
            'year': True,
            'change_pct': ':.2f'
        }
    )

    fig.update_layout(
        **PLOT_THEME,
        xaxis=dict(**XAXIS, ticksuffix='%'),
        yaxis=dict(**YAXIS, tickfont=dict(size=10)),
        coloraxis_showscale=False,
        height=520
    )
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(
        "Negative values indicate rent decreases. "
        "Source: RTB Average Monthly Rent Report, CSO Ireland."
    )

    section("Data", "Full Dataset — All Areas With Falling Rents")

    display = falling_df[[
        'year', 'location', 'county',
        'prev_year_rent', 'avg_monthly_rent', 'change_pct'
    ]].copy()
    display.columns = [
        'Year', 'Area', 'County',
        'Previous Rent (€)', 'Current Rent (€)', 'Change (%)'
    ]
    st.dataframe(display, use_container_width=True, height=320)

# ============================================================
# MAIN
# ============================================================

def main():
    with st.spinner("Loading data..."):
        try:
            national, county, bedrooms, falling = load_all_data()
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            return

    page = render_sidebar(national)

    if page == "National Trends":
        page_national_trends(national)
    elif page == "County Comparison":
        page_county_comparison(county)
    elif page == "Bedroom Analysis":
        page_bedroom_analysis(bedrooms)
    elif page == "Falling Rents":
        page_falling_rents(falling)

if __name__ == "__main__":
    main()