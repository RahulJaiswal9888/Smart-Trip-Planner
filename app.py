import json
from datetime import date, datetime, timedelta
from html import escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from database import initialize_database, save_trip, get_trips, delete_trip, cancel_trip
from planner import (
    generate_itinerary,
    calculate_budget,
    itinerary_json,
    DESTINATIONS,
    HOTELS,
)
from destination_data import DESTINATION_DATA
from image_service import hero_images, attraction_images

st.set_page_config(
    page_title="Wanderly | Smart Trip Planner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAMES = [n for n in DESTINATION_DATA if n in DESTINATIONS and n in HOTELS]

# =========================================================
# STYLE
# =========================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@500;600;700&display=swap');
:root{--forest:#1f3d2e;--forest2:#2e5842;--ivory:#f7f3ea;--paper:#fffdf8;--gold:#b08d57;--ink:#2b2b2b;--muted:#6d6a60;--line:#e3dccb;}
.stApp{background:var(--ivory);color:var(--ink);font-family:'Inter',sans-serif;}
h1,h2,h3,h4{font-family:'Playfair Display',serif !important;color:var(--forest) !important;font-weight:600 !important;letter-spacing:-.01em;}
.block-container{max-width:1280px;padding:2rem 3rem 3rem;}
header[data-testid="stHeader"]{background:transparent;}
#MainMenu,footer{visibility:hidden;}

section[data-testid="stSidebar"]{background:var(--forest);}
section[data-testid="stSidebar"] *{color:var(--ivory);}
.brand{font-family:'Playfair Display',serif;font-size:2.1rem;font-weight:600;color:var(--ivory);}
.brand span{color:var(--gold);}
.brand-sub{font-size:.62rem;letter-spacing:.28em;color:#b9c7bd;margin:.1rem 0 1.6rem;}
.side-note{font-size:.72rem;letter-spacing:.12em;color:#b9c7bd;margin-top:2rem;}

.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{
  width:100%;border-radius:2px;min-height:2.8rem;font-weight:500;letter-spacing:.04em;
  border:1px solid var(--forest);background:transparent;color:var(--forest);transition:all .25s ease;}
.stButton>button *,.stDownloadButton>button *,.stFormSubmitButton>button *{color:inherit !important;}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],
.stButton>button[data-testid="stBaseButton-primary"],.stFormSubmitButton>button[data-testid="stBaseButton-primaryFormSubmit"]{
  background:var(--forest);color:var(--ivory);border-color:var(--forest);}
.stButton>button:hover,.stDownloadButton>button:hover,.stFormSubmitButton>button:hover{
  background:var(--gold);border-color:var(--gold);color:#fff;}
section[data-testid="stSidebar"] .stButton>button{
  background:transparent;border:1px solid rgba(247,243,234,.25);color:var(--ivory);
  justify-content:flex-start;text-align:left;}
section[data-testid="stSidebar"] .stButton>button[kind="primary"],
section[data-testid="stSidebar"] .stButton>button[data-testid="stBaseButton-primary"]{
  background:var(--gold);border-color:var(--gold);color:#1b1b1b;}
section[data-testid="stSidebar"] .stButton>button:hover{background:var(--forest2);border-color:var(--gold);color:var(--ivory);}

div[data-testid="stVerticalBlockBorderWrapper"]{background:var(--paper);border:1px solid var(--line);border-radius:3px;box-shadow:none;transition:box-shadow .3s ease;}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{box-shadow:0 10px 28px rgba(31,61,46,.08);}
div[data-testid="stMetric"]{background:var(--paper);border:1px solid var(--line);padding:1rem 1.2rem;border-radius:3px;}
div[data-testid="stMetricValue"]{color:var(--forest);font-family:'Playfair Display',serif;}
div[data-testid="stForm"]{background:var(--paper);border:1px solid var(--line);border-radius:3px;padding:1.6rem;}
button[data-baseweb="tab"]{font-weight:500;}
div[data-baseweb="tab-highlight"]{background:var(--gold);}

/* ---- Form labels and inputs: always readable ---- */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"]{
  color:#1f3d2e !important;font-weight:600;font-size:.88rem;opacity:1 !important;}
div[data-baseweb="input"]>div,
div[data-baseweb="base-input"],
div[data-baseweb="select"]>div{
  background:#ffffff !important;border:1px solid #d8cfbb !important;border-radius:2px !important;}
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
div[data-baseweb="select"] div,
div[data-baseweb="select"] span{color:#2b2b2b !important;-webkit-text-fill-color:#2b2b2b;}
div[data-baseweb="input"] input::placeholder{color:#8a867a !important;-webkit-text-fill-color:#8a867a;}
div[data-testid="stNumberInput"] button{background:#fffdf8 !important;color:#1f3d2e !important;}
div[data-testid="stNumberInput"] button svg{fill:#1f3d2e;}
div[data-baseweb="select"] svg{fill:#1f3d2e;}
div[data-testid="stCheckbox"] label p{color:#2b2b2b !important;}

.eyebrow{color:var(--gold);font-size:.72rem;letter-spacing:.22em;font-weight:600;text-transform:uppercase;}
.sec-title{font-family:'Playfair Display',serif;font-size:2.2rem;color:var(--forest);margin:.25rem 0 .3rem;line-height:1.15;}
.sec-sub{color:var(--muted);margin-bottom:1.5rem;max-width:720px;}
.hero{position:relative;border-radius:3px;display:flex;align-items:flex-end;padding:3rem;margin-bottom:1.2rem;background-size:cover;background-position:center;}
.hero-kicker{color:#e6d5b0;font-size:.74rem;letter-spacing:.26em;font-weight:600;text-transform:uppercase;}
.hero-title{font-family:'Playfair Display',serif;color:#fff;font-size:clamp(2.2rem,5vw,4rem);line-height:1.08;margin:.6rem 0;font-weight:600;}
.hero-text{color:#eef0ea;max-width:620px;line-height:1.7;}
.tile{position:relative;overflow:hidden;border-radius:2px;background:linear-gradient(135deg,#1f3d2e,#2e5842);}
.tile-fallback{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:1rem;color:#d9c79e;font-family:'Playfair Display',serif;font-size:1.3rem;}
.tile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .7s ease;}
.tile:hover img{transform:scale(1.04);}
.card-title{font-family:'Playfair Display',serif;font-size:1.4rem;color:var(--forest);margin:.8rem 0 .15rem;}
.card-meta{color:var(--gold);font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;font-weight:600;margin-bottom:.4rem;}
.card-text{color:var(--muted);font-size:.92rem;line-height:1.55;margin-bottom:.6rem;}
.stat{background:var(--paper);border:1px solid var(--line);padding:1.1rem 1.25rem;min-height:105px;}
.stat-label{color:var(--gold);font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;font-weight:600;margin-bottom:.4rem;}
.stat-value{color:var(--forest);font-family:'Playfair Display',serif;font-size:1.2rem;line-height:1.35;}
.step{padding:1.4rem 1.2rem;border-top:2px solid var(--gold);}
.step-num{font-family:'Playfair Display',serif;font-size:2.4rem;color:var(--gold);line-height:1;}
.day-label{color:var(--gold);font-size:.74rem;letter-spacing:.2em;font-weight:600;margin-bottom:.6rem;}
.slot{color:var(--muted);font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;margin-bottom:.15rem;}
.slot-place{font-family:'Playfair Display',serif;font-size:1.2rem;color:var(--forest);margin-bottom:.2rem;}
.price{font-family:'Playfair Display',serif;font-size:1.7rem;color:var(--forest);}
.price span{font-family:'Inter',sans-serif;font-size:.8rem;color:var(--muted);}
.tips li{margin-bottom:.45rem;color:var(--ink);line-height:1.55;}
.footer{margin-top:3.5rem;padding:1.8rem 0 .5rem;border-top:1px solid var(--line);color:var(--muted);font-size:.82rem;text-align:center;line-height:1.7;}
@media(max-width:700px){
  .block-container{padding:1rem;}
  .hero{min-height:340px !important;padding:1.6rem;}
  .sec-title{font-size:1.7rem;}
}
</style>
"""


def html(markup):
    """Render HTML. Lines are joined so Markdown never treats it as a code block."""
    flat = " ".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(flat, unsafe_allow_html=True)


html(CSS)

# =========================================================
# HELPERS
# =========================================================


def money(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def section(eyebrow, title, subtitle=""):
    html(
        f'<div class="eyebrow">{escape(eyebrow)}</div>'
        f'<div class="sec-title">{escape(title)}</div>'
        + (f'<div class="sec-sub">{escape(subtitle)}</div>' if subtitle else "")
    )


def tile(url, label, height=240):
    """Image tile. A themed placeholder sits underneath, so a missing image never breaks layout."""
    img = ""
    if url:
        img = (f'<img src="{escape(url, quote=True)}" alt="{escape(label)}" '
               f'loading="lazy" referrerpolicy="no-referrer">')
    return (f'<div class="tile" style="height:{height}px">'
            f'<div class="tile-fallback">{escape(label)}</div>{img}</div>')


def hero_html(bg, kicker, title_html, text="", height=460):
    if bg:
        layer = ("linear-gradient(180deg,rgba(18,38,28,.25) 0%,rgba(18,38,28,.85) 100%),"
                 f"url('{escape(bg, quote=True)}')")
    else:
        layer = "linear-gradient(135deg,#1f3d2e,#2e5842)"
    html(
        f'<div class="hero" style="min-height:{height}px;background-image:{layer}"><div>'
        f'<div class="hero-kicker">{escape(kicker)}</div>'
        f'<div class="hero-title">{title_html}</div>'
        f'<div class="hero-text">{escape(text)}</div></div></div>'
    )


def stat(label, value):
    return (f'<div class="stat"><div class="stat-label">{escape(label)}</div>'
            f'<div class="stat-value">{escape(value)}</div></div>')


def trip_total(costs):
    """calculate_budget() returns the final amount under the key 'Total'."""
    if isinstance(costs, dict):
        for key in ("Total", "total", "estimated_total", "grand_total"):
            if key in costs:
                return float(costs[key])
        return sum(float(v) for v in costs.values() if isinstance(v, (int, float)))
    return 0.0


def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def go(page, destination=None):
    """Navigation callback. Runs BEFORE the rerun, so the new page is always respected."""
    st.session_state["page"] = page
    if destination in NAMES:
        st.session_state["selected_destination"] = destination


def flash(kind, message):
    st.session_state["flash"] = (kind, message)


def show_flash():
    item = st.session_state.pop("flash", None)
    if item:
        getattr(st, item[0])(item[1])


def place_notes(destination):
    notes = {}
    for a in DESTINATION_DATA.get(destination, {}).get("attractions", []):
        notes[a["name"].lower()] = a["desc"]
    return notes


def footer():
    html(
        '<div class="footer"><strong>Wanderly</strong> · Smart Trip Planner · MCA mini-project<br>'
        'Built with Python, Streamlit and MySQL<br>'
        'Destination details, costs and hotel rates are sample data, not live quotes or bookings.<br>'
        'Photographs are stored locally in the project\'s images folder.</div>'
    )


# =========================================================
# ITINERARY + BUDGET DISPLAY
# =========================================================


def show_itinerary(itinerary, destination, start=None):
    if isinstance(itinerary, str):
        try:
            itinerary = json.loads(itinerary)
        except ValueError:
            st.write(itinerary)
            return

    start = to_date(start) if start else None
    notes = place_notes(destination)

    for index, item in enumerate(itinerary, start=1):
        if not isinstance(item, dict):
            st.write(item)
            continue

        day = item.get("day", index)
        label = f"DAY {day}"
        if start:
            try:
                label += " · " + (start + timedelta(days=int(day) - 1)).strftime("%a, %d %b %Y").upper()
            except (TypeError, ValueError):
                pass

        with st.container(border=True):
            html(f'<div class="day-label">{escape(label)}</div>')
            cols = st.columns(3)
            for col, (slot, key) in zip(cols, [("Morning", "morning"),
                                               ("Afternoon", "afternoon"),
                                               ("Evening", "evening")]):
                place = str(item.get(key, "")) or "Free time"
                note = notes.get(place.lower(), "")
                with col:
                    html(f'<div class="slot">{slot}</div>'
                         f'<div class="slot-place">{escape(place)}</div>'
                         f'<div class="card-text">{escape(note)}</div>')


def budget_chart(costs):
    items = {k: float(v) for k, v in costs.items()
             if isinstance(v, (int, float)) and str(k).lower() != "total" and v >= 0}
    if not items:
        st.info("No cost categories to chart.")
        return

    fig, ax = plt.subplots(figsize=(7, 3.4))
    fig.patch.set_facecolor("#fffdf8")
    ax.set_facecolor("#fffdf8")
    labels = list(items.keys())[::-1]
    values = list(items.values())[::-1]
    ax.barh(labels, values, color="#1f3d2e", height=.55)
    ax.set_xlabel("Estimated cost (₹)")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="x", alpha=.2)
    ax.set_axisbelow(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# =========================================================
# STATE + DATABASE
# =========================================================

st.session_state.setdefault("page", "Home")
st.session_state.setdefault("selected_destination", NAMES[0])

if not st.session_state.get("db_ready"):
    try:
        initialize_database()
        st.session_state["db_ready"] = True
        st.session_state["db_error"] = ""
    except Exception as exc:
        st.session_state["db_ready"] = False
        st.session_state["db_error"] = str(exc)

# =========================================================
# SIDEBAR
# =========================================================

NAV = ["Home", "Plan a Trip", "My Trips", "About"]
current_page = st.session_state["page"]
active_nav = "Home" if current_page == "Destination Details" else current_page

with st.sidebar:
    html('<div class="brand">Wander<span>ly</span></div><div class="brand-sub">SMART TRIP PLANNER</div>')
    for item in NAV:
        st.button(item, key=f"nav_{item}", on_click=go, args=(item,),
                  type="primary" if item == active_nav else "secondary")
    html('<div class="side-note">PYTHON · STREAMLIT · MYSQL</div>')

# =========================================================
# PAGES
# =========================================================


def page_home():
    show_flash()
    heroes = hero_images()
    bg = next((heroes.get(n) for n in ("Udaipur", "Manali", "Jaipur") if heroes.get(n)), None)

    hero_html(bg, "Travel planning, made simple",
              "Discover places.<br>Create stories.",
              "Wanderly helps you explore six of North India's best-loved destinations, "
              "build a day-wise itinerary and estimate your budget in one place.",
              height=500)
    c1, _ = st.columns([1, 3])
    c1.button("Plan Your Trip", key="home_plan", type="primary", on_click=go, args=("Plan a Trip",))

    st.write("")
    section("Featured destinations", "Find your kind of escape",
            "From Himalayan valleys to lakeside palaces and heritage cities.")

    for start in range(0, len(NAMES), 3):
        cols = st.columns(3)
        for col, name in zip(cols, NAMES[start:start + 3]):
            d = DESTINATION_DATA[name]
            with col, st.container(border=True):
                html(tile(heroes.get(name), name, 230))
                html(f'<div class="card-title">{escape(name)}</div>'
                     f'<div class="card-meta">{escape(d["state"])}</div>'
                     f'<div class="card-text">{escape(d["tagline"])}</div>')
                st.button(f"Explore {name}", key=f"explore_{name}", type="primary",
                          on_click=go, args=("Destination Details", name))

    st.write("")
    section("How it works", "Three simple steps")
    steps = [
        ("01", "Choose a destination", "Browse the destinations and open one to see attractions, food and travel tips."),
        ("02", "Customise your trip", "Pick dates, number of days, travellers, hotel category and transport budget."),
        ("03", "Explore your itinerary", "Get a day-wise plan and cost breakdown, then save or download it."),
    ]
    for col, (num, title, text) in zip(st.columns(3), steps):
        with col:
            html(f'<div class="step"><div class="step-num">{num}</div>'
                 f'<div class="card-title">{title}</div><div class="card-text">{text}</div></div>')
    footer()


def page_details():
    name = st.session_state.get("selected_destination")
    if name not in NAMES:
        name = NAMES[0]
    d = DESTINATION_DATA[name]
    imgs = attraction_images(name)

    top1, top2 = st.columns(2)
    top1.button("← Back to Destinations", key="back_top", on_click=go, args=("Home",))
    top2.button(f"Plan This Trip to {name}", key=f"plan_top_{name}", type="primary",
                on_click=go, args=("Plan a Trip", name))

    hero_html(imgs.get("__hero__"), f"{d['state']} · India", escape(name), d["tagline"], height=440)

    st.write("")
    section("Overview", f"About {name}")
    st.write(d["overview"])

    c1, c2, c3 = st.columns(3)
    c1.markdown(stat("Best time to visit", d["best_time"]), unsafe_allow_html=True)
    c2.markdown(stat("Suggested duration", d["duration"]), unsafe_allow_html=True)
    c3.markdown(stat("Travel highlights", d["highlights"]), unsafe_allow_html=True)

    st.write("")
    section("Sightseeing", f"Places to see in {name}", "Each attraction has its own photograph.")
    atts = d["attractions"]
    for start in range(0, len(atts), 2):
        for col, att in zip(st.columns(2), atts[start:start + 2]):
            with col, st.container(border=True):
                html(tile(imgs.get(att["name"]), att["name"], 270))
                html(f'<div class="card-title">{escape(att["name"])}</div>'
                     f'<div class="card-text">{escape(att["desc"])}</div>')

    st.write("")
    left, right = st.columns(2)
    with left:
        section("Local flavour", "Food and culture")
        st.write(d["food_culture"])
    with right:
        section("Before you go", "Practical tips")
        items = "".join(f"<li>{escape(t)}</li>" for t in d["tips"])
        html(f'<ul class="tips">{items}</ul>')

    st.write("")
    section("Ready?", f"Plan your {name} trip", "Get a day-wise itinerary and an estimated budget.")
    b1, b2 = st.columns(2)
    b1.button("← Back to Destinations", key="back_bottom", on_click=go, args=("Home",))
    b2.button(f"Plan This Trip to {name}", key=f"plan_bottom_{name}", type="primary",
              on_click=go, args=("Plan a Trip", name))
    footer()


def page_plan():
    preferred = st.session_state.get("selected_destination", NAMES[0])
    if preferred not in NAMES:
        preferred = NAMES[0]

    section("Plan a trip", f"Plan your {preferred} trip",
            "Enter your preferences to generate an itinerary and budget estimate.")

    with st.form("trip_form"):
        st.markdown("#### Traveller details")
        a, b = st.columns(2)
        with a:
            traveler_name = st.text_input("Your name", max_chars=100, placeholder="Enter your name")
            start_city = st.text_input("Starting from (city)", max_chars=100, placeholder="e.g. Chandigarh")
        with b:
            destination = st.selectbox("Destination", NAMES, index=NAMES.index(preferred))
            start_date = st.date_input("Travel start date", value=date.today(), min_value=date.today())

        st.markdown("#### Trip preferences")
        c1, c2 = st.columns(2)
        days = c1.number_input("Number of days", min_value=1, max_value=30, value=3, step=1)
        travelers = c2.number_input("Number of people", min_value=1, max_value=20, value=2, step=1)

        c3, c4, c5 = st.columns(3)
        style = c3.selectbox("Travel style", ["Budget", "Standard", "Luxury", "Adventure", "Relaxed"])
        hotel_type = c4.selectbox("Hotel category", ["Budget", "Standard", "Luxury"], index=1)
        transport_cost = c5.number_input("Estimated total travel / transport cost (₹)",
                                         min_value=0, max_value=1000000, value=3000, step=500)

        submitted = st.form_submit_button("Generate My Trip", type="primary")

    if submitted:
        if not traveler_name.strip() or not start_city.strip():
            st.error("Please enter your name and starting city.")
        else:
            try:
                itinerary = generate_itinerary(destination, int(days), style)
                costs = calculate_budget(destination, int(days), int(travelers),
                                         hotel_type, float(transport_cost))
                total = trip_total(costs)
                st.session_state["selected_destination"] = destination
                st.session_state["current_trip"] = {
                    "traveler_name": traveler_name.strip(),
                    "start_city": start_city.strip(),
                    "destination": destination,
                    "start_date": start_date,
                    "duration_days": int(days),
                    "travelers": int(travelers),
                    "budget": total,
                    "travel_style": style,
                    "estimated_total": total,
                    "itinerary_json": itinerary_json(itinerary),
                }
                st.session_state["current_itinerary"] = itinerary
                st.session_state["current_costs"] = costs
                st.session_state["current_hotel_type"] = hotel_type
                st.session_state["saved_trip_id"] = None
                st.success("Your travel plan is ready.")
            except Exception as exc:
                st.error(f"Could not create the trip: {exc}")

    if "current_trip" not in st.session_state:
        footer()
        return

    trip = st.session_state["current_trip"]
    itinerary = st.session_state["current_itinerary"]
    costs = st.session_state["current_costs"]
    hotel_choice = st.session_state.get("current_hotel_type", "Standard")
    total = trip_total(costs)

    st.write("")
    section("Your plan", f"{trip['destination']} · {trip['duration_days']} days",
            f"{trip['traveler_name']} · from {trip['start_city']} · "
            f"{trip['travelers']} traveller(s) · {trip['travel_style']} style")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimated total", money(total))
    m2.metric("Per traveller", money(total / max(trip["travelers"], 1)))
    m3.metric("Duration", f"{trip['duration_days']} days")
    m4.metric("Hotel category", hotel_choice)

    tab1, tab2, tab3 = st.tabs(["Itinerary", "Budget breakdown", "Hotel rates"])

    with tab1:
        show_itinerary(itinerary, trip["destination"], trip["start_date"])

    with tab2:
        left, right = st.columns([1.2, 1])
        with left:
            budget_chart(costs)
        with right:
            rows = [{"Expense": str(k), "Estimated cost": money(v)}
                    for k, v in costs.items() if isinstance(v, (int, float))]
            st.dataframe(pd.DataFrame(rows), hide_index=True)
        st.caption("Estimates only. Hotel is calculated as one room for (days − 1) nights, minimum one night; "
                   "food and local transport are per person per day; a 10% buffer is added.")

    with tab3:
        rates = HOTELS.get(trip["destination"], {})
        if not rates:
            st.info("No hotel rates are available for this destination.")
        else:
            for col, (category, price) in zip(st.columns(3), rates.items()):
                with col, st.container(border=True):
                    label = "Your choice" if category == hotel_choice else "Category"
                    html(f'<div class="card-meta">{label}</div>'
                         f'<div class="card-title">{escape(str(category))}</div>'
                         f'<div class="price">{money(price)}<span> / night</span></div>')
            st.caption("Indicative sample rates from the planner data. Not live availability or a booking.")

    st.write("")
    left, right = st.columns(2)
    with left:
        saved_id = st.session_state.get("saved_trip_id")
        if saved_id:
            st.success(f"Saved as trip #{saved_id}. Open My Trips to view it.")
        elif st.button("Save this trip to MySQL", key="save_trip", type="primary"):
            if not st.session_state.get("db_ready"):
                st.error(f"MySQL connection failed: {st.session_state.get('db_error')}")
            else:
                try:
                    st.session_state["saved_trip_id"] = save_trip(trip)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not save trip: {exc}")
    with right:
        export = {"trip": trip, "itinerary": itinerary, "estimated_costs": costs}
        st.download_button(
            "Download itinerary (JSON)",
            data=json.dumps(export, default=str, indent=2, ensure_ascii=False),
            file_name=f"{trip['destination'].lower()}_trip.json",
            mime="application/json",
        )
    footer()


def page_trips():
    show_flash()
    section("My trips", "Your travel journal", "View and manage saved journeys.")

    if not st.session_state.get("db_ready"):
        st.error(f"Could not connect to MySQL: {st.session_state.get('db_error')}")
        st.caption("Check that the MySQL service is running and the credentials in database.py are correct.")
        footer()
        return

    try:
        trips = get_trips()
    except Exception as exc:
        st.error(f"Could not load saved trips: {exc}")
        footer()
        return

    if not trips:
        st.info("No saved trips yet.")
        st.button("Plan your first trip", key="first_trip", type="primary", on_click=go, args=("Plan a Trip",))
        footer()
        return

    def row_dates(t):
        s = to_date(t["start_date"])
        if not s:
            return str(t["start_date"])
        e = s + timedelta(days=int(t["duration_days"]) - 1)
        return f"{s:%d %b %Y} – {e:%d %b %Y}"

    table = pd.DataFrame([{
        "ID": t["id"],
        "Destination": t["destination"],
        "Dates": row_dates(t),
        "Days": t["duration_days"],
        "Travellers": t["travelers"],
        "Style": t["travel_style"],
        "Status": t.get("status", "Planned"),
        "Estimated total": money(t["estimated_total"]),
        "Saved on": t["created_at"].strftime("%d %b %Y") if hasattr(t["created_at"], "strftime") else str(t["created_at"]),
    } for t in trips])
    st.dataframe(table, hide_index=True)

    st.write("")
    section("Trip details", "View a saved trip")
    by_id = {t["id"]: t for t in trips}
    select_col, action_col = st.columns([2, 1])
    with select_col:
        chosen = st.selectbox(
            "Select a trip", list(by_id.keys()),
            format_func=lambda i: f"#{i} · {by_id[i]['destination']} · {by_id[i]['traveler_name']}",
        )
    t = by_id[chosen]
    status = t.get("status", "Planned")
    with action_col:
        if status == "Cancelled":
            st.button("Trip cancelled", key=f"cancelled_{chosen}", disabled=True)
        else:
            confirm_cancel = st.checkbox(
                "Cancel and remove this trip",
                key=f"confirm_cancel_{chosen}",
            )
            if st.button("Cancel trip", key=f"cancel_{chosen}", disabled=not confirm_cancel):
                try:
                    if cancel_trip(chosen):
                        flash("success", f"Trip #{chosen} was cancelled and removed.")
                    else:
                        flash("warning", f"Trip #{chosen} was not found or is already cancelled.")
                except Exception as exc:
                    flash("error", f"Could not cancel trip: {exc}")
                st.rerun()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Destination", t["destination"])
    m2.metric("Duration", f"{t['duration_days']} days")
    m3.metric("Travellers", t["travelers"])
    m4.metric("Estimated total", money(t["estimated_total"]))
    st.caption(f"{t['traveler_name']} · from {t['start_city']} · {row_dates(t)} · "
               f"{t['travel_style']} style · {status}")

    show_itinerary(t["itinerary_json"], t["destination"], t["start_date"])

    st.write("")
    with st.container(border=True):
        with st.expander("Permanently delete this trip"):
            confirm_delete = st.checkbox(
                "I understand this will permanently delete the trip.",
                key=f"confirm_delete_{chosen}",
            )
            if st.button("Delete trip", key=f"delete_{chosen}", disabled=not confirm_delete):
                try:
                    if delete_trip(chosen):
                        flash("success", f"Trip #{chosen} was deleted.")
                    else:
                        flash("warning", f"Trip #{chosen} was not found.")
                except Exception as exc:
                    flash("error", f"Could not delete trip: {exc}")
                st.rerun()
    footer()


def page_about():
    hero_html(None, "About the project", "Travel planning,<br>made simpler",
              "Wanderly is a student-built smart trip planner developed as an MCA mini-project.", height=300)
    section("Technology", "How it is built")
    items = [
        ("Python", "planner.py generates itineraries and budgets using clear, rule-based logic."),
        ("Streamlit", "app.py provides the interface, navigation and session handling."),
        ("MySQL", "database.py stores saved trips in the smart_trip_planner database."),
    ]
    for col, (title, text) in zip(st.columns(3), items):
        with col, st.container(border=True):
            html(f'<div class="card-title">{title}</div><div class="card-text">{text}</div>')
    st.info("Destination details, attractions, hotel rates and costs are sample data. "
            "They are not live prices, availability or booking confirmations.")
    footer()


PAGES = {
    "Home": page_home,
    "Destination Details": page_details,
    "Plan a Trip": page_plan,
    "My Trips": page_trips,
    "About": page_about,
}
PAGES.get(st.session_state["page"], page_home)()