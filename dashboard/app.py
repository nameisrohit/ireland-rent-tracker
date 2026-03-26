# dashboard/app.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Streamlit Cloud uses st.secrets instead of .env
# This handles both local (.env) and cloud (st.secrets)
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
# CSS + JS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main { background: #0f1117; color: #ffffff; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f12 0%, #1a3320 100%);
    border-right: 1px solid #2d5a3d;
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00c851, #007e33);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
    animation: fadeInDown 0.8s ease;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: #888;
    margin-bottom: 2rem;
    animation: fadeInUp 0.8s ease;
}

.metric-container {
    background: linear-gradient(135deg, #1a2f1e 0%, #0f1f13 100%);
    border: 1px solid #2d5a3d;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    animation: fadeInUp 0.6s ease;
}
.metric-container:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 200, 81, 0.2);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #00c851;
}
.metric-label {
    font-size: 0.85rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 4px;
}
.metric-delta {
    font-size: 0.9rem;
    color: #ff6b6b;
    margin-top: 6px;
}

.section-header {
    font-size: 1.4rem;
    font-weight: 600;
    color: #ffffff;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #2d5a3d;
}

.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, #00c851, transparent);
    margin: 1.5rem 0;
}

.insight-box {
    background: linear-gradient(135deg, #1a2f1e, #0f1f13);
    border-left: 4px solid #00c851;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 1rem 0;
}
.insight-text {
    color: #cccccc;
    font-size: 0.95rem;
    line-height: 1.6;
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# THEME — No xaxis/yaxis here to avoid conflicts
# ============================================================

PLOT_THEME = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#cccccc', family='Inter'),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#2d5a3d')
)

XAXIS = dict(gridcolor='#1e2d20', linecolor='#2d5a3d', tickcolor='#2d5a3d')
YAXIS = dict(gridcolor='#1e2d20', linecolor='#2d5a3d', tickcolor='#2d5a3d')

# ============================================================
# DATABASE
# ============================================================

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", 5439)),
        dbname=os.getenv("REDSHIFT_DB", "dev"),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD"),
        sslmode="require",
        connect_timeout=10
    )

@st.cache_data(ttl=3600)
def load_data(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

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
    return national, county, bedrooms, falling

# ============================================================
# HELPERS
# ============================================================

def metric_card(label, value, delta=None):
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-delta">{delta}</div>'
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>',
                unsafe_allow_html=True)

def insight_box(text):
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-text">💡 {text}</div>
    </div>
    """, unsafe_allow_html=True)

def divider():
    st.markdown('<div class="custom-divider"></div>',
                unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    st.sidebar.markdown("""
    <div style="text-align:center; padding:1rem 0;">
        <div style="font-size:2.5rem;">🏠</div>
        <div style="font-size:1.3rem; font-weight:700; color:#00c851;">
            Ireland Rent Tracker
        </div>
        <div style="font-size:0.8rem; color:#888; margin-top:0.3rem;">
            2008 — 2024
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        ["📈 National Trends",
         "🗺️ County Comparison",
         "🛏️ Bedroom Analysis",
         "📉 Falling Rents"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size:0.8rem; color:#888; line-height:1.8;">
        <strong style="color:#00c851;">Data Source</strong><br>
        RTB Average Monthly Rent Report<br>
        Central Statistics Office Ireland<br>
        <em>Updated annually</em>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size:0.85rem; color:#aaa;">
        Built by <strong style="color:#00c851;">Rohit</strong><br>
        <a href="https://github.com/nameisrohit/ireland-rent-tracker"
           style="color:#00c851;">GitHub ↗</a>
    </div>
    """, unsafe_allow_html=True)

    return page

# ============================================================
# PAGE 1 — NATIONAL TRENDS
# ============================================================

def page_national_trends(df):
    st.markdown('<div class="hero-title">📈 National Rent Trends</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Average monthly rent across Ireland 2008–2024</div>',
                unsafe_allow_html=True)
    divider()

    latest   = df[df['year'] == df['year'].max()].iloc[0]
    earliest = df[df['year'] == df['year'].min()].iloc[0]
    total_change = ((latest['avg_monthly_rent'] - earliest['avg_monthly_rent'])
                   / earliest['avg_monthly_rent'] * 100)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Avg Rent 2024",
                    f"€{latest['avg_monthly_rent']:,.0f}",
                    f"↑ {latest['yoy_change_pct']}% vs 2023")
    with col2:
        metric_card("Avg Rent 2008",
                    f"€{earliest['avg_monthly_rent']:,.0f}",
                    "Base year")
    with col3:
        metric_card("Total Increase",
                    f"{total_change:.1f}%",
                    "Since 2008")
    with col4:
        metric_card("Peak Annual Rise",
                    f"{df['yoy_change_pct'].max():.1f}%",
                    "Highest single year")

    divider()

    insight_box(
        f"Irish rents have risen {total_change:.1f}% since 2008. "
        f"After falling during the financial crisis (2009–2011), "
        f"rents recovered strongly from 2013. "
        f"The 2024 average of €{latest['avg_monthly_rent']:,.0f}/month "
        f"is a new all-time high."
    )

    section_header("Average Monthly Rent 2008–2024")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['year'], y=df['avg_monthly_rent'],
        fill='tozeroy',
        fillcolor='rgba(0,200,81,0.1)',
        line=dict(color='#00c851', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='#00c851',
                    line=dict(color='white', width=2)),
        hovertemplate='<b>%{x}</b><br>€%{y:,.0f}/month<extra></extra>'
    ))

    bottom_row = df.loc[df['avg_monthly_rent'].idxmin()]
    fig.add_annotation(
        x=bottom_row['year'], y=bottom_row['avg_monthly_rent'],
        text="🔻 Market bottom", showarrow=True, arrowhead=2,
        arrowcolor='#00c851',
        font=dict(color='#ffffff', size=11),
        bgcolor='#1a2f1e', bordercolor='#00c851', borderwidth=1
    )
    fig.add_annotation(
        x=df['year'].max(), y=df['avg_monthly_rent'].max(),
        text="🔺 Current peak", showarrow=True, arrowhead=2,
        arrowcolor='#ff6b6b',
        font=dict(color='#ffffff', size=11),
        bgcolor='#2f1a1a', bordercolor='#ff6b6b', borderwidth=1
    )

    fig.update_layout(
        **PLOT_THEME,
        xaxis=XAXIS,
        yaxis=dict(**YAXIS, tickprefix='€'),
        hovermode='x unified',
        height=420,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    section_header("Year-on-Year Change (%)")

    yoy_df = df.dropna(subset=['yoy_change_pct'])
    colors = ['#ff6b6b' if x > 0 else '#00c851'
              for x in yoy_df['yoy_change_pct']]

    fig2 = go.Figure(go.Bar(
        x=yoy_df['year'], y=yoy_df['yoy_change_pct'],
        marker_color=colors,
        text=yoy_df['yoy_change_pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        textfont=dict(color='#cccccc', size=11),
        hovertemplate='<b>%{x}</b><br>%{y:.2f}%<extra></extra>'
    ))
    fig2.update_layout(
        **PLOT_THEME,
        xaxis=XAXIS,
        yaxis=dict(**YAXIS, ticksuffix='%'),
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("🔴 Red = rent increased  |  🟢 Green = rent decreased")

# ============================================================
# PAGE 2 — COUNTY COMPARISON
# ============================================================

def page_county_comparison(county_df):
    st.markdown('<div class="hero-title">🗺️ County Comparison</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">How rent varies across Ireland\'s counties</div>',
                unsafe_allow_html=True)
    divider()

    years = sorted(county_df['year'].unique(), reverse=True)
    selected_year = st.selectbox("📅 Select Year", years)
    year_data = county_df[county_df['year'] == selected_year].sort_values(
        'avg_monthly_rent', ascending=True
    )

    col1, col2 = st.columns([3, 2])

    with col1:
        section_header(f"Rent by County — {selected_year}")
        fig = px.bar(
            year_data, x='avg_monthly_rent', y='county',
            orientation='h',
            color='avg_monthly_rent',
            color_continuous_scale=[[0,'#00c851'],[0.5,'#ffa500'],[1,'#ff4444']],
            labels={'avg_monthly_rent': 'Avg Monthly Rent (€)', 'county': ''}
        )
        fig.update_layout(
            **PLOT_THEME,
            xaxis=dict(**XAXIS, tickprefix='€'),
            yaxis=YAXIS,
            coloraxis_showscale=False,
            height=600,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Top 10 Most Expensive")
        top10 = year_data.nlargest(10, 'avg_monthly_rent').reset_index(drop=True)
        for i, row in top10.iterrows():
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;
                        padding:8px 12px;margin:4px 0;
                        background:#1a2f1e;border-radius:8px;
                        border-left:3px solid #00c851;">
                <span style="color:#ccc;">{medal} {row['county']}</span>
                <span style="color:#00c851;font-weight:600;">
                    €{row['avg_monthly_rent']:,.0f}
                </span>
            </div>
            """, unsafe_allow_html=True)

        section_header("Most Affordable")
        bottom5 = year_data.nsmallest(5, 'avg_monthly_rent').reset_index(drop=True)
        for i, row in bottom5.iterrows():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;
                        padding:8px 12px;margin:4px 0;
                        background:#1a2f1e;border-radius:8px;
                        border-left:3px solid #28a745;">
                <span style="color:#ccc;">✅ {row['county']}</span>
                <span style="color:#28a745;font-weight:600;">
                    €{row['avg_monthly_rent']:,.0f}
                </span>
            </div>
            """, unsafe_allow_html=True)

    divider()
    section_header("County Trends Over Time")

    counties = sorted(county_df['county'].unique())
    defaults = [c for c in ['Dublin','Cork','Galway','Limerick']
                if c in counties][:4] or counties[:4]

    selected = st.multiselect("Select counties to compare",
                               counties, default=defaults)
    if selected:
        filtered = county_df[county_df['county'].isin(selected)]
        fig3 = px.line(
            filtered, x='year', y='avg_monthly_rent',
            color='county', markers=True,
            labels={'year':'Year',
                    'avg_monthly_rent':'Avg Monthly Rent (€)',
                    'county':'County'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig3.update_layout(
            **PLOT_THEME,
            xaxis=XAXIS,
            yaxis=dict(**YAXIS, tickprefix='€'),
            hovermode='x unified',
            height=400,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# PAGE 3 — BEDROOM ANALYSIS
# ============================================================

def page_bedroom_analysis(bedrooms_df):
    st.markdown('<div class="hero-title">🛏️ Bedroom Analysis</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">How rent varies by number of bedrooms</div>',
                unsafe_allow_html=True)
    divider()

    national_beds = bedrooms_df.groupby(
        ['year','bedrooms']
    )['avg_monthly_rent'].mean().reset_index()

    section_header("National Average Rent by Bedroom Type")
    fig = px.line(
        national_beds, x='year', y='avg_monthly_rent',
        color='bedrooms', markers=True,
        labels={'year':'Year',
                'avg_monthly_rent':'Avg Monthly Rent (€)',
                'bedrooms':'Bedrooms'},
        color_discrete_sequence=['#00c851','#ffa500','#ff6b6b','#6c63ff']
    )
    fig.update_layout(
        **PLOT_THEME,
        xaxis=XAXIS,
        yaxis=dict(**YAXIS, tickprefix='€'),
        hovermode='x unified',
        height=420,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    divider()

    col1, col2 = st.columns(2)
    with col1:
        years = sorted(bedrooms_df['year'].unique(), reverse=True)
        selected_year = st.selectbox("📅 Select Year", years)
    with col2:
        counties = sorted(bedrooms_df['county'].unique())
        selected_county = st.selectbox("📍 Select County", counties)

    # Only show specific bedroom counts
    # Remove grouped categories like '1 to 2 bed'
    specific_beds = ['One bed', 'Two bed', 'Three bed', 'Four plus bed']

    year_county = bedrooms_df[
        (bedrooms_df['year'] == selected_year) &
        (bedrooms_df['county'] == selected_county) &
        (bedrooms_df['bedrooms'].isin(specific_beds))
    ]

    if not year_county.empty:
        section_header(f"{selected_county} — {selected_year}")

        # Sort bedrooms in logical order
        bedroom_order = ['One bed', 'Two bed', 'Three bed', 'Four plus bed']
        year_county = year_county.copy()
        year_county['sort_key'] = year_county['bedrooms'].apply(
            lambda x: bedroom_order.index(x)
            if x in bedroom_order else 99
        )
        year_county = year_county.sort_values('sort_key')

        fig2 = px.bar(
            year_county, x='bedrooms', y='avg_monthly_rent',
            color='avg_monthly_rent',
            color_continuous_scale=[[0,'#00c851'],[0.5,'#ffa500'],[1,'#ff4444']],
            labels={'bedrooms':'Bedroom Type',
                    'avg_monthly_rent':'Avg Monthly Rent (€)'},
            text=year_county['avg_monthly_rent'].apply(lambda x: f"€{x:,.0f}")
        )
        fig2.update_layout(
            **PLOT_THEME,
            xaxis=XAXIS,
            yaxis=dict(**YAXIS, tickprefix='€'),
            coloraxis_showscale=False,
            showlegend=False,
            height=380,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        fig2.update_traces(textposition='outside',
                           textfont=dict(color='white'))
        st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# PAGE 4 — FALLING RENTS
# ============================================================

def page_falling_rents(falling_df):
    st.markdown('<div class="hero-title">📉 Falling Rents</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Areas where rent decreased year on year</div>',
                unsafe_allow_html=True)
    divider()

    if falling_df.empty:
        st.info("No areas with falling rents found.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Areas With Falling Rents", len(falling_df))
    with col2:
        metric_card("Biggest Drop",
                    f"{falling_df['change_pct'].min():.1f}%")
    with col3:
        metric_card("Most Affected County", falling_df.iloc[0]['county'])

    divider()

    insight_box(
        f"While rents are rising nationally, {len(falling_df)} specific areas "
        f"have seen year-on-year decreases. The biggest drop was "
        f"{falling_df['change_pct'].min():.1f}% in "
        f"{falling_df.iloc[0]['location']}, {falling_df.iloc[0]['county']}."
    )

    section_header("Top 20 Areas With Biggest Rent Drops")

    fig = px.bar(
        falling_df.head(20),
        x='change_pct', y='location',
        orientation='h',
        color='change_pct',
        color_continuous_scale=[[0,'#ff4444'],[0.5,'#ffa500'],[1,'#00c851']],
        labels={'change_pct':'Year-on-Year Change (%)', 'location':''},
        hover_data=['county','avg_monthly_rent','prev_year_rent','year']
    )
    fig.update_layout(
        **PLOT_THEME,
        xaxis=dict(**XAXIS, ticksuffix='%'),
        yaxis=YAXIS,
        coloraxis_showscale=False,
        height=520,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    section_header("Full Data")
    display = falling_df[['year','location','county',
                           'prev_year_rent','avg_monthly_rent','change_pct']].copy()
    display.columns = ['Year','Area','County',
                       'Previous Rent (€)','Current Rent (€)','Change (%)']
    st.dataframe(display, use_container_width=True, height=300)

# ============================================================
# MAIN
# ============================================================

def main():
    page = render_sidebar()

    with st.spinner("Loading data from Redshift..."):
        try:
            national, county, bedrooms, falling = load_all_data()
        except Exception as e:
            st.error(f"❌ Database error: {e}")
            st.info("Check your .env file and AWS Security Group.")
            return

    if page == "📈 National Trends":
        page_national_trends(national)
    elif page == "🗺️ County Comparison":
        page_county_comparison(county)
    elif page == "🛏️ Bedroom Analysis":
        page_bedroom_analysis(bedrooms)
    elif page == "📉 Falling Rents":
        page_falling_rents(falling)

if __name__ == "__main__":
    main()