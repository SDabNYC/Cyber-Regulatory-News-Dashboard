import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timezone, timedelta
from scraper import fetch_all, TYPE_COLORS

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberReg Watch",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── AUTO-REFRESH every 5 minutes (300,000 ms) ───────────────────────────────
refresh_count = st_autorefresh(interval=300_000, debounce=False, key="autorefresh")

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #070B12;
    color: #D4DCE8;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.2rem 1.8rem 3rem; max-width: 100%; }

/* ── Header ── */
.crw-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 24px; margin-bottom: 18px;
    background: linear-gradient(135deg, #0C1220 0%, #101929 100%);
    border: 1px solid #1C2A3E; border-radius: 12px;
}
.crw-brand { display: flex; align-items: center; gap: 12px; }
.crw-brand h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.35rem; font-weight: 600;
    color: #EEF2FF; margin: 0; letter-spacing: -0.3px;
}
.crw-brand .tagline {
    font-size: 0.72rem; color: #3D5A80;
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase; letter-spacing: 1.2px;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #22D3EE; box-shadow: 0 0 8px #22D3EE;
    animation: blink 2.2s infinite; flex-shrink: 0;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Header right: stats + refresh pill */
.crw-right { display: flex; align-items: center; gap: 28px; }
.crw-stats { display: flex; gap: 24px; }
.stat-item { text-align: right; }
.stat-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.3rem; font-weight: 600; color: #EEF2FF;
}
.stat-lbl { font-size: 0.68rem; color: #3D5A80; text-transform: uppercase; letter-spacing: 1px; }

/* Next-refresh pill */
.refresh-pill {
    display: flex; align-items: center; gap: 7px;
    background: #0A1628; border: 1px solid #1C2A3E;
    border-radius: 20px; padding: 6px 13px;
}
.refresh-pill .rf-icon { font-size: 0.75rem; }
.refresh-pill .rf-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem; color: #3D5A80;
    text-transform: uppercase; letter-spacing: 0.8px;
}
.refresh-pill .rf-timer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem; font-weight: 600; color: #22D3EE;
}

/* ── Section label ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 2px;
    color: #3D5A80; margin-bottom: 10px;
}

/* ── News card ── */
.card {
    position: relative;
    background: #0C1220;
    border: 1px solid #1C2A3E;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.15s, background 0.15s;
    overflow: hidden;
}
.card:hover {
    border-color: #2E4A6E;
    background: #0F1829;
}
.card-accent {
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%; border-radius: 10px 0 0 10px;
}

/* Tag pills */
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem; font-weight: 600;
    padding: 2px 7px; border-radius: 4px;
    letter-spacing: 0.3px; white-space: nowrap;
}
.tag-type   { background: rgba(255,255,255,0.06); color: #A0AEC0; border: 1px solid rgba(255,255,255,0.08); }
.tag-geo    { background: rgba(34,211,238,0.08);  color: #67E8F9; border: 1px solid rgba(34,211,238,0.15); }
.tag-sector { background: rgba(168,85,247,0.08);  color: #C4B5FD; border: 1px solid rgba(168,85,247,0.15); }
.tag-src    { background: rgba(255,255,255,0.04); color: #64748B; border: 1px solid #1C2A3E; }

/* Card body */
.card-title {
    font-size: 0.9rem; font-weight: 600; color: #E2E8F0;
    line-height: 1.45; margin-bottom: 6px;
    text-decoration: none; display: block;
}
.card-title:hover { color: #7DD3FC; }
.card-summary {
    font-size: 0.78rem; color: #64748B; line-height: 1.5;
    margin-bottom: 8px;
}
.card-footer {
    display: flex; align-items: center; justify-content: space-between;
}
.card-date {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.64rem; color: #3D5A80;
}
.card-link {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; color: #2563EB;
    text-decoration: none; opacity: 0.7;
    transition: opacity 0.15s;
}
.card-link:hover { opacity: 1; }

/* Filter labels */
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important; text-transform: uppercase;
    letter-spacing: 1.5px; color: #3D5A80 !important;
}

/* Search input */
.stTextInput > div > div > input {
    background: #0C1220 !important; border: 1px solid #1C2A3E !important;
    color: #D4DCE8 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.85rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
}

/* Multiselect pills */
span[data-baseweb="tag"] { background: #1C2A3E !important; }

/* Empty state */
.empty-state {
    text-align: center; padding: 60px 20px;
    color: #3D5A80; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;
}

/* Divider */
.crw-divider { border: none; border-top: 1px solid #111B2A; margin: 14px 0 16px; }
</style>
""", unsafe_allow_html=True)


# ─── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_articles():
    return fetch_all()


with st.spinner("🛰️  Scanning feeds across 35+ sources…"):
    articles = load_articles()

now_utc     = datetime.now(timezone.utc)
total       = len(articles)
sources_cnt = len({a["source"] for a in articles})
today_cnt   = sum(1 for a in articles if a["date"] >= now_utc - timedelta(hours=24))

# ── Next-refresh countdown ────────────────────────────────────────────────────
REFRESH_S = 300
if "page_load_time" not in st.session_state or refresh_count != st.session_state.get("last_rc"):
    st.session_state["page_load_time"] = now_utc
    st.session_state["last_rc"] = refresh_count

elapsed     = int((now_utc - st.session_state["page_load_time"]).total_seconds())
secs_left   = max(0, REFRESH_S - elapsed)
mins_l, sec_p = divmod(secs_left, 60)
next_refresh_str = f"{mins_l}:{sec_p:02d}"
last_fetched_str = '<span id="crw-local-time">--:--</span>'


# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="crw-header">
  <div class="crw-brand">
    <div class="live-dot"></div>
    <div>
      <h1>🛡️ CyberReg Watch</h1>
      <div class="tagline">Cyber regulatory intelligence · live feed · updated {last_fetched_str}</div>
    </div>
  </div>
  <div class="crw-right">
    <div class="crw-stats">
      <div class="stat-item">
        <div class="stat-val">{total}</div>
        <div class="stat-lbl">Articles</div>
      </div>
      <div class="stat-item">
        <div class="stat-val">{sources_cnt}</div>
        <div class="stat-lbl">Sources</div>
      </div>
      <div class="stat-item">
        <div class="stat-val">{today_cnt}</div>
        <div class="stat-lbl">Today</div>
      </div>
    </div>
    <div class="refresh-pill">
      <span class="rf-icon">🔄</span>
      <span class="rf-label">Next refresh</span>
      <span class="rf-timer">{next_refresh_str}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Populate the local-time span with the browser's clock
st.markdown("""
<script>
(function() {
    function setLocalTime() {
        var el = document.getElementById('crw-local-time');
        if (el) {
            var now = new Date();
            var h = String(now.getHours()).padStart(2, '0');
            var m = String(now.getMinutes()).padStart(2, '0');
            var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'local';
            el.textContent = h + ':' + m + ' ' + tz.split('/').pop().replace('_', ' ');
        } else {
            setTimeout(setLocalTime, 100);
        }
    }
    setLocalTime();
})();
</script>
""", unsafe_allow_html=True)


# ─── FILTERS ─────────────────────────────────────────────────────────────────
f1, f2, f3, f4, f5 = st.columns([2.5, 1.8, 1.8, 1.8, 1.4])

with f1:
    search = st.text_input("", placeholder="🔍  Search headlines…", label_visibility="collapsed")

with f2:
    all_types = sorted({a["art_type"] for a in articles})
    sel_types = st.multiselect("Type", all_types, placeholder="All types")

with f3:
    all_geos = sorted({a["geo"] for a in articles})
    sel_geos = st.multiselect("Region", all_geos, placeholder="All regions")

with f4:
    all_sectors = sorted({a["sector"] for a in articles})
    sel_sectors = st.multiselect("Sector", all_sectors, placeholder="All sectors")

with f5:
    all_sources = sorted({a["source"] for a in articles})
    sel_sources = st.multiselect("Source", all_sources, placeholder="All sources")


# ─── APPLY FILTERS ───────────────────────────────────────────────────────────
filtered = articles
if search:
    q = search.lower()
    filtered = [a for a in filtered if q in a["title"].lower() or q in a["summary"].lower()]
if sel_types:
    filtered = [a for a in filtered if a["art_type"] in sel_types]
if sel_geos:
    filtered = [a for a in filtered if a["geo"] in sel_geos]
if sel_sectors:
    filtered = [a for a in filtered if a["sector"] in sel_sectors]
if sel_sources:
    filtered = [a for a in filtered if a["source"] in sel_sources]

is_filtered = bool(search or sel_types or sel_geos or sel_sectors or sel_sources)

st.markdown("<hr class='crw-divider'>", unsafe_allow_html=True)
st.markdown(
    f'<div class="section-label">Showing {len(filtered)} article{"s" if len(filtered) != 1 else ""}'
    f'{" · filtered" if is_filtered else " · sorted by newest"}</div>',
    unsafe_allow_html=True,
)


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def time_ago(dt: datetime) -> str:
    diff = now_utc - dt
    if diff < timedelta(minutes=1):
        return "just now"
    if diff < timedelta(hours=1):
        return f"{int(diff.total_seconds() / 60)}m ago"
    if diff < timedelta(hours=24):
        return f"{int(diff.total_seconds() / 3600)}h ago"
    if diff < timedelta(days=7):
        return f"{diff.days}d ago"
    return dt.strftime("%b %d, %Y")


def accent_color(art_type: str) -> str:
    for k, v in {
        "⚖️ Legislative": "#7C3AED",
        "📋 Regulatory":  "#2563EB",
        "🗂️ Policy":      "#0891B2",
        "📚 Research":    "#059669",
    }.items():
        if k in art_type:
            return v
    return "#334155"


# ─── CARD GRID ───────────────────────────────────────────────────────────────
if not filtered:
    st.markdown(
        '<div class="empty-state">No articles match your filters.<br>Try broadening your search.</div>',
        unsafe_allow_html=True,
    )
else:
    cols = st.columns(3, gap="medium")
    for i, art in enumerate(filtered[:150]):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
              <div class="card-accent" style="background:{accent_color(art['art_type'])};"></div>
              <div class="tags">
                <span class="tag tag-type">{art['art_type']}</span>
                <span class="tag tag-geo">{art['geo']}</span>
                <span class="tag tag-sector">{art['sector']}</span>
                <span class="tag tag-src">{art['source']}</span>
              </div>
              <a class="card-title" href="{art['url']}" target="_blank">{art['title']}</a>
              <div class="card-summary">{art['summary']}</div>
              <div class="card-footer">
                <span class="card-date">{time_ago(art['date'])}</span>
                <a class="card-link" href="{art['url']}" target="_blank">Read →</a>
              </div>
            </div>
            """, unsafe_allow_html=True)