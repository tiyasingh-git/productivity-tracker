import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict
import plotly.express as px
import plotly.graph_objects as go

#page configuration
st.set_page_config(
    page_title="StudyPulse · Productivity Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

#css
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@0,400;0,500&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0d0f14; color: #e8e6e0; }
.stApp { background-color: #0d0f14; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

[data-testid="stSidebar"] { background-color: #13151d !important; border-right: 1px solid #1f2230; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #161824 0%, #1a1d2e 100%);
    border: 1px solid #2a2d3e; border-radius: 12px; padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"] { color: #7c7f99 !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; color: #c9f542 !important; font-size: 2rem !important; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

.stButton > button {
    background: #c9f542 !important; color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.55rem 1.6rem !important; transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #deff60 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(201,245,66,0.3) !important;
}

.stTextInput input, .stNumberInput input, .stSelectbox select {
    background-color: #161824 !important; border: 1px solid #2a2d3e !important;
    border-radius: 8px !important; color: #e8e6e0 !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #13151d; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 8px; color: #7c7f99;
    font-family: 'Syne', sans-serif; font-weight: 600; padding: 8px 20px;
}
.stTabs [aria-selected="true"] { background: #c9f542 !important; color: #0d0f14 !important; }

.insight-card {
    background: linear-gradient(135deg, #161824, #1a1d2e);
    border: 1px solid #2a2d3e; border-left: 3px solid #c9f542;
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
}
.insight-card.warning { border-left-color: #ff6b6b; }
.insight-card.info    { border-left-color: #54d4ff; }
.insight-card.success { border-left-color: #c9f542; }

.goal-card {
    background: #161824; border: 1px solid #2a2d3e; border-radius: 12px;
    padding: 1rem 1.2rem; margin-bottom: 0.8rem;
}
.goal-card.done   { border-left: 3px solid #c9f542; }
.goal-card.warn   { border-left: 3px solid #ff9f43; }
.goal-card.danger { border-left: 3px solid #ff6b6b; }

.progress-bar-bg   { background: #2a2d3e; border-radius: 6px; height: 10px; width: 100%; margin-top: 6px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 6px; transition: width 0.4s ease; }

.section-label {
    font-family: 'DM Mono', monospace; font-size: 0.7rem;
    letter-spacing: 0.15em; color: #c9f542; text-transform: uppercase; margin-bottom: 0.4rem;
}
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800; line-height: 1.1;
    background: linear-gradient(90deg, #c9f542 0%, #54d4ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { color: #7c7f99; font-size: 0.95rem; margin-top: 0.3rem; }
hr { border-color: #1f2230 !important; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

#file path
DATA_FILE       = "productivity_data.json"
CATEGORIES_FILE = "categories.json"
GOALS_FILE      = "goals.json"

PALETTE = [
    "#c9f542", "#54d4ff", "#ff9f43", "#a29bfe",
    "#fd79a8", "#00cec9", "#ffeaa7", "#e17055",
    "#6c5ce7", "#00b894", "#d63031", "#0984e3",
]

# category
def load_categories() -> dict:
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE) as f:
            return json.load(f)
    defaults = {
        "Study":"#c9f542",
        "Coding":"#54d4ff",
        "Gym":"#ff9f43",
        "Reading":"#a29bfe",
    }
    save_categories(defaults)
    return defaults

def save_categories(cats: dict):
    with open(CATEGORIES_FILE, "w") as f:
        json.dump(cats, f)

def add_category(name: str, cats: dict) -> dict:
    used   = set(cats.values())
    colour = next((c for c in PALETTE if c not in used), PALETTE[len(cats) % len(PALETTE)])
    cats[name] = colour
    save_categories(cats)
    return cats

def delete_category(name: str, cats: dict) -> dict:
    cats.pop(name, None)
    save_categories(cats)
    g = load_goals()
    g.pop(name, None)
    save_goals(g)
    return cats

#goals
def load_goals() -> dict:
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE) as f:
            return json.load(f)
    return {}

def save_goals(goals: dict):
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f)

def upsert_goal(category: str, task_name: str, daily_minutes: int, goals: dict) -> dict:
    if category not in goals:
        goals[category] = {}
    goals[category][task_name] = daily_minutes
    save_goals(goals)
    return goals

def delete_goal(category: str, task_name: str, goals: dict) -> dict:
    if category in goals and task_name in goals[category]:
        del goals[category][task_name]
        if not goals[category]:
            del goals[category]
    save_goals(goals)
    return goals

# session data
def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            records = json.load(f)
        df = pd.DataFrame(records)
        if not df.empty:
            df["timestamp"]  = pd.to_datetime(df["timestamp"])
            df["time_spent"] = pd.to_numeric(df["time_spent"])
        return df
    return pd.DataFrame(columns=["task_name", "category", "time_spent", "timestamp", "notes"])

def save_record(record: dict):
    records = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            records = json.load(f)
    records.append(record)
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, default=str)

def delete_all_data():
    for fp in [DATA_FILE, CATEGORIES_FILE, GOALS_FILE]:
        if os.path.exists(fp):
            os.remove(fp)

#goal progress
def compute_goal_progress(df: pd.DataFrame, goals: dict) -> list:
    results   = []
    today_str = datetime.now().date()

    for category, tasks in goals.items():
        for task_name, target_min in tasks.items():
            if not df.empty:
                mask = (
                    (df["timestamp"].dt.date == today_str) &
                    (df["category"] == category) &
                    (df["task_name"].str.lower().str.contains(task_name.lower(), na=False))
                )
                logged_min = int(df[mask]["time_spent"].sum())
            else:
                logged_min = 0

            remaining = max(0, target_min - logged_min)
            pct       = min(100, round(logged_min / target_min * 100))
            status    = "done" if pct >= 100 else ("warn" if pct >= 60 else "danger")

            results.append({
                "category":  category,
                "task_name": task_name,
                "target":    target_min,
                "logged":    logged_min,
                "remaining": remaining,
                "pct":       pct,
                "status":    status,
            })
    return results

# insights
def generate_insights(df: pd.DataFrame, cats: dict) -> list:
    if df.empty:
        return [{"type": "info", "text": "Log your first task to unlock personalised insights!"}]

    insights = []
    today    = pd.Timestamp(datetime.now()).normalize()
    week_ago = today - timedelta(days=7)
    recent   = df[df["timestamp"] >= week_ago]

    total_hrs = recent["time_spent"].sum() / 60
    insights.append({"type": "success", "text": f"⏱ You've logged {total_hrs:.1f} hours this week across {len(recent)} sessions."})

    if not recent.empty:
        top_cat = recent.groupby("category")["time_spent"].sum().idxmax()
        top_hrs = recent.groupby("category")["time_spent"].sum().max() / 60
        insights.append({"type": "success", "text": f"🏆 Power zone: {top_cat} — {top_hrs:.1f} hours this week."})

    longest_idx = df["time_spent"].idxmax()
    longest_name = str(df.loc[longest_idx, "task_name"])
    longest_mins = int(float(str(df.loc[longest_idx, "time_spent"])))
    longest_date = pd.to_datetime(str(df.loc[longest_idx, "timestamp"])).strftime("%b %d")
    insights.append({"type": "info", "text": f"🔥 Longest session ever: {longest_name} ({longest_mins} min) on {longest_date}."})

    all_cats  = set(df["category"].unique())
    week_cats = set(recent["category"].unique()) if not recent.empty else set()
    missing   = all_cats - week_cats
    if missing:
        insights.append({"type": "warning", "text": f"⚠️ Skipped this week: {', '.join(missing)}. Don't let habits slip!"})

    daily_avg = recent.groupby(recent["timestamp"].dt.date)["time_spent"].sum().mean() / 60 if not recent.empty else 0
    if daily_avg < 1:
        insights.append({"type": "warning", "text": f"Daily average is only {daily_avg:.1f} hours. Aim for at least 2 hrs of focused work."})
    else:
        insights.append({"type": "success", "text": f"Solid daily average of {daily_avg:.1f} hours this week!"})

    streak, check = 0, today.date()
    days_logged = df.groupby(df["timestamp"].dt.date).size()
    while check in days_logged.index:
        streak += 1
        check  -= timedelta(days=1)
    if streak > 0:
        insights.append({"type": "success", "text": f"🔥 You're on a {streak}-day streak! Don't break the chain."})

    df_h      = df.copy()
    df_h["hour"] = df_h["timestamp"].dt.hour
    peak_hour = int(df_h.groupby("hour")["time_spent"].sum().idxmax())
    am_pm = "AM" if peak_hour < 12 else "PM"
    h12   = peak_hour if peak_hour <= 12 else peak_hour - 12
    insights.append({"type": "info", "text": f"Peak productivity hour: {h12}:00 {am_pm} — schedule tough tasks then!"})

    return insights

#charts
CHART_LAYOUT: Dict[str, Any] = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter", "color": "#7c7f99", "size": 12},
    "margin": {"l": 10, "r": 10, "t": 30, "b": 10},
    "legend": {"bgcolor": "rgba(0,0,0,0)", "bordercolor": "#2a2d3e"},
}

def chart_daily_hours(df, cat_colors):
    d = df.copy()
    d["date"] = d["timestamp"].dt.date
    d = d.groupby(["date", "category"])["time_spent"].sum().reset_index()
    d["hours"] = d["time_spent"] / 60
    fig = px.bar(d, x="date", y="hours", color="category",
                 color_discrete_map=cat_colors, title="Daily Hours by Category",
                 labels={"hours": "Hours", "date": "Date", "category": "Category"})
    fig.update_layout(**CHART_LAYOUT)
    fig.update_traces(marker_line_width=0)
    return fig

def chart_category_pie(df, cat_colors):
    d = df.groupby("category")["time_spent"].sum().reset_index()
    d["hours"] = d["time_spent"] / 60
    fig = px.pie(d, names="category", values="hours", color="category",
                 color_discrete_map=cat_colors, title="Time Distribution", hole=0.55)
    fig.update_layout(**CHART_LAYOUT)
    fig.update_traces(textfont_color="#e8e6e0", pull=[0.02] * len(d))
    return fig

def chart_heatmap(df):
    d = df.copy()
    d["hour"] = d["timestamp"].dt.hour
    d["day"]  = d["timestamp"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = d.groupby(["day", "hour"])["time_spent"].sum().unstack(fill_value=0)
    pivot = pivot.reindex([x for x in day_order if x in pivot.index])
    fig = go.Figure(go.Heatmap(
        z=pivot.values / 60, x=list(pivot.columns), y=list(pivot.index),
        colorscale=[[0, "#13151d"], [0.5, "#2a4a0f"], [1, "#c9f542"]],
        showscale=True, colorbar=dict(tickfont=dict(color="#7c7f99")),
    ))
    fig.update_layout(title="Productivity Heatmap (Hours)", **CHART_LAYOUT,
                      xaxis=dict(title="Hour of Day", tickfont=dict(color="#7c7f99")),
                      yaxis=dict(title="", tickfont=dict(color="#7c7f99")))
    return fig

def chart_trend(df):
    d = df.groupby(df["timestamp"].dt.date)["time_spent"].sum().reset_index()
    d.columns = ["date", "minutes"]
    d["hours"]   = d["minutes"] / 60
    d["rolling"] = d["hours"].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d["date"], y=d["hours"], name="Daily", marker_color="#1f2f14", marker_line_width=0))
    fig.add_trace(go.Scatter(x=d["date"], y=d["rolling"], name="7-day avg", line=dict(color="#c9f542", width=2.5)))
    fig.update_layout(title="Productivity Trend", **CHART_LAYOUT, yaxis_title="Hours")
    return fig

def chart_category_bar(df, cat_colors):
    d = df.groupby("category")["time_spent"].sum().reset_index()
    d["hours"] = (d["time_spent"] / 60).round(1)
    d = d.sort_values("hours")
    colors = [cat_colors.get(c, "#c9f542") for c in d["category"]]
    fig = go.Figure(go.Bar(
        x=d["hours"], y=d["category"], orientation="h",
        marker_color=colors,
        text=d["hours"].apply(lambda x: f"{x} hours"),
        textposition="outside", textfont=dict(color="#e8e6e0"),
    ))
    fig.update_layout(title="All-Time Hours by Category", **CHART_LAYOUT,
                      xaxis_title="Hours", yaxis=dict(tickfont=dict(color="#e8e6e0")))
    return fig

# load state
cats  = load_categories()
goals = load_goals()
df    = load_data()

#sidebar
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.7rem">⚡ StudyPulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Track · Analyse · Improve</div>', unsafe_allow_html=True)
    st.divider()

    #log sessions 
    st.markdown('<div class="section-label">Log a Session</div>', unsafe_allow_html=True)

    with st.form("log_form", clear_on_submit=True):
        task_name = st.text_input("Task Name", placeholder="e.g. Physics — Kinematics")
        cat_names = list(cats.keys())
        category = st.selectbox("Category", cat_names) if cat_names else None
        time_spent = st.number_input("Time Spent (minutes)", min_value=1, max_value=600, value=30, step=5)
        notes = st.text_area("Notes (optional)", placeholder="What did you achieve?", height=70)
        submitted = st.form_submit_button("➕ Log Session", use_container_width=True)

    if submitted:
        if not task_name.strip():
            st.error("Please enter a task name.")
        elif not cat_names:
            st.error("Add at least one category first.")
        else:
            save_record({
                "task_name": task_name.strip(),
                "category": category,
                "time_spent": time_spent,
                "timestamp": datetime.now().isoformat(),
                "notes": notes.strip(),
            })
            st.success(f"✅ Logged {time_spent} min of {task_name}!")
            st.rerun()

    st.divider()

    #categories
    st.markdown('<div class="section-label">Manage Categories</div>', unsafe_allow_html=True)

    with st.form("add_cat_form", clear_on_submit=True):
        new_cat = st.text_input("New Category Name", placeholder="e.g. 🧪 Chemistry")
        add_cat = st.form_submit_button("➕ Add Category", use_container_width=True)

    if add_cat:
        nc = new_cat.strip()
        if not nc:
            st.error("Enter a category name.")
        elif nc in cats:
            st.warning(f"'{nc}' already exists.")
        else:
            cats = add_category(nc, cats)
            st.success(f"Added {nc}!")
            st.rerun()

    if cats:
        del_cat = st.selectbox("Delete a category", ["— select —"] + list(cats.keys()), key="del_cat_sel")
        if st.button("Delete Category", use_container_width=True):
            if del_cat != "— select —":
                cats = delete_category(del_cat, cats)
                st.success(f"Deleted {del_cat}.")
                st.rerun()

    st.divider()

    #daily goals
    st.markdown('<div class="section-label">Daily Goals</div>', unsafe_allow_html=True)
    st.caption("Set a minimum daily time target for a task keyword within a category.")

    with st.form("goal_form", clear_on_submit=True):
        goal_cat  = st.selectbox("Category", list(cats.keys()) if cats else ["—"], key="goal_cat")
        goal_task = st.text_input("Task Keyword", placeholder="e.g. Physics")
        goal_mins = st.number_input("Daily Goal (minutes)", min_value=5, max_value=600, value=60, step=5)
        save_goal = st.form_submit_button("🎯 Save Goal", use_container_width=True)

    if save_goal:
        gt = goal_task.strip()
        if not gt:
            st.error("Enter a task keyword.")
        else:
            goals = upsert_goal(goal_cat, gt, int(goal_mins), goals)
            st.success(f"Goal saved: **{gt}** → {int(goal_mins)} min/day in {goal_cat}")
            st.rerun()

    if goals:
        st.markdown('<div class="section-label" style="margin-top:0.6rem">Active Goals</div>', unsafe_allow_html=True)
        for gcat, gtasks in goals.items():
            for gtask, gmins in gtasks.items():
                col1, col2 = st.columns([3, 1])
                col1.markdown(
                    f"<small style='color:#7c7f99'>{gcat}</small><br>"
                    f"<span style='font-size:0.85rem;color:#e8e6e0'>{gtask} — {gmins} min</span>",
                    unsafe_allow_html=True,
                )
                if col2.button("✕", key=f"del_goal_{gcat}_{gtask}"):
                    goals = delete_goal(gcat, gtask, goals)
                    st.rerun()

    st.divider()
    if st.button("🗑 Clear All Data", use_container_width=True):
        delete_all_data()
        st.rerun()

# header
st.markdown('<div class="hero-title">Student Productivity Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Your personal command centre for deep work and smart habits.</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# todays goals banner
progress_items = compute_goal_progress(df, goals)

if progress_items:
    st.markdown('<div class="section-label">Today\'s Goal Progress</div>', unsafe_allow_html=True)
    n_cols = min(len(progress_items), 3)
    cols   = st.columns(n_cols)

    for i, p in enumerate(progress_items):
        bar_color = {"done": "#c9f542", "warn": "#ff9f43", "danger": "#ff6b6b"}[p["status"]]
        icon      = {"done": "✅", "warn": "⚠️", "danger": "🔴"}[p["status"]]
        msg       = "Goal reached! 🎉" if p["status"] == "done" else f"{p['remaining']} min remaining"

        cols[i % n_cols].markdown(f"""
        <div class="goal-card {p['status']}">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:0.9rem;font-weight:500;color:#e8e6e0">{icon} {p['task_name']}</span>
                <span style="font-size:0.72rem;color:#7c7f99">{p['category']}</span>
            </div>
            <div style="font-size:0.75rem;color:#7c7f99;margin-top:4px">
                {p['logged']} / {p['target']} min logged today
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width:{p['pct']}%;background:{bar_color}"></div>
            </div>
            <div style="font-size:0.75rem;margin-top:6px;color:{bar_color};font-weight:500">{msg} ({p['pct']}%)</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

#kpi row
c1, c2, c3, c4, c5 = st.columns(5)

if df.empty:
    for col, lbl in zip([c1, c2, c3, c4, c5], ["Total Sessions", "Total Hours", "This Week (hrs)", "Avg Session (min)", "Categories Logged"]):
        col.metric(lbl, "0")
else:
    week_ago      = pd.Timestamp(datetime.now()) - timedelta(days=7)
    recent        = df[df["timestamp"] >= week_ago]
    prev_week_ago = week_ago - timedelta(days=7)
    prev_week     = df[(df["timestamp"] >= prev_week_ago) & (df["timestamp"] < week_ago)]
    week_hours    = recent["time_spent"].sum() / 60 if not recent.empty else 0
    delta_hrs     = week_hours - (prev_week["time_spent"].sum() / 60)

    c1.metric("Total Sessions",    str(len(df)))
    c2.metric("Total Hours",       f"{df['time_spent'].sum()/60:.1f}")
    c3.metric("This Week (hrs)",   f"{week_hours:.1f}", f"{delta_hrs:+.1f} vs prev")
    c4.metric("Avg Session (min)", f"{df['time_spent'].mean():.0f}")
    c5.metric("Categories Logged", str(df["category"].nunique()))

st.divider()

#tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Insights", "Goals", "Log", "Heatmap"])

#dashb
with tab1:
    if df.empty:
        st.info("No data yet — log your first session in the sidebar!")
    else:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.plotly_chart(chart_daily_hours(df, cats), use_container_width=True)
        with col_r:
            st.plotly_chart(chart_category_pie(df, cats), use_container_width=True)
        col_l2, col_r2 = st.columns([3, 2])
        with col_l2:
            st.plotly_chart(chart_trend(df), use_container_width=True)
        with col_r2:
            st.plotly_chart(chart_category_bar(df, cats), use_container_width=True)

#insights
with tab2:
    st.markdown("### Personalised Insights")
    st.markdown('<div class="hero-sub">Powered by your own data — not generic advice.</div><br>', unsafe_allow_html=True)

    for ins in generate_insights(df, cats):
        st.markdown(f'<div class="insight-card {ins["type"]}">{ins["text"]}</div>', unsafe_allow_html=True)

    if not df.empty:
        st.divider()
        st.markdown("#### Category Balance Score")
        cat_names_logged = list(df["category"].unique())
        cat_hrs          = df.groupby("category")["time_spent"].sum() / 60
        actual_pct       = cat_hrs / cat_hrs.sum()
        balance_score    = max(0, 100 - int(np.std(actual_pct.values) * 300))

        colA, colB = st.columns([1, 3])
        colA.metric("Balance Score", f"{balance_score}/100", "higher = more balanced")

        fig_radar = go.Figure(go.Scatterpolar(
            r=list(cat_hrs.reindex(cat_names_logged, fill_value=0).values),
            theta=cat_names_logged, fill="toself",
            line_color="#c9f542", fillcolor="rgba(201,245,66,0.15)",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, tickfont=dict(color="#7c7f99"), gridcolor="#2a2d3e"),
                angularaxis=dict(tickfont=dict(color="#e8e6e0"), gridcolor="#2a2d3e"),
            ),
            showlegend=False, **CHART_LAYOUT,
        )
        colB.plotly_chart(fig_radar, use_container_width=True)

#goals
with tab3:
    st.markdown("### Daily Goal Tracker")
    st.markdown('<div class="hero-sub">Set daily minimums and see exactly where you stand.</div><br>', unsafe_allow_html=True)

    if not goals:
        st.info("No goals set yet. Use **Daily Goals** in the sidebar to add one.")
    else:
        today_label = datetime.now().strftime("%A, %B %d")
        st.markdown(f"**Today — {today_label}**")
        st.markdown("")

        for p in progress_items:
            bar_color = {"done": "#c9f542", "warn": "#ff9f43", "danger": "#ff6b6b"}[p["status"]]
            icon      = {"done": "✅", "warn": "⚠️", "danger": "🔴"}[p["status"]]
            msg       = "🎉 Goal met!" if p["status"] == "done" else f"{p['remaining']} min to go"

            col1, col2, col3 = st.columns([3, 2, 2])
            col1.markdown(
                f"**{icon} {p['task_name']}**  \n"
                f"<small style='color:#7c7f99'>{p['category']}</small>",
                unsafe_allow_html=True,
            )
            col2.markdown(f"**{p['logged']}** / {p['target']} min")
            col3.markdown(f"<span style='color:{bar_color};font-weight:500'>{msg}</span>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="progress-bar-bg" style="margin-bottom:1.2rem">
                <div class="progress-bar-fill" style="width:{p['pct']}%;background:{bar_color}"></div>
            </div>
            """, unsafe_allow_html=True)

        # comparison of last 7 days performance record
        if not df.empty:
            st.divider()
            st.markdown("#### Last 7 Days — Goal Performance")

            rows = []
            for back in range(7):
                day = (datetime.now() - timedelta(days=back)).date()
                for gcat, gtasks in goals.items():
                    for gtask, gmins in gtasks.items():
                        mask = (
                            (df["timestamp"].dt.date == day) &
                            (df["category"] == gcat) &
                            (df["task_name"].str.lower().str.contains(gtask.lower(), na=False))
                        )
                        logged = int(df[mask]["time_spent"].sum())
                        rows.append({
                            "Date":     day.strftime("%b %d"),
                            "Task":     gtask,
                            "Category": gcat,
                            "Logged":   logged,
                            "Target":   gmins,
                            "% Done":   min(100, round(logged / gmins * 100)),
                            "Met":      "✅" if logged >= gmins else "❌",
                        })

            if rows:
                hist_df = pd.DataFrame(rows)
                fig_hist = px.bar(
                    hist_df, x="Date", y="% Done", color="Task",
                    barmode="group", title="% of Daily Goal Met (last 7 days)",
                    labels={"% Done": "% Completed"},
                    color_discrete_sequence=PALETTE,
                )
                fig_hist.add_hline(
                    y=100, line_dash="dash", line_color="#c9f542",
                    annotation_text="100% target", annotation_position="top right",
                )
                fig_hist.update_layout(**CHART_LAYOUT)
                st.plotly_chart(fig_hist, use_container_width=True)

                st.dataframe(
                    hist_df[["Date", "Task", "Category", "Logged", "Target", "Met"]],
                    use_container_width=True, hide_index=True,
                )

#log
with tab4:
    st.markdown("### Session Log")
    if df.empty:
        st.info("No sessions logged yet.")
    else:
        display_df = df.copy().sort_values("timestamp", ascending=False)
        display_df["Date"]     = display_df["timestamp"].dt.strftime("%b %d, %Y %H:%M")
        display_df["Duration"] = display_df["time_spent"].apply(lambda m: f"{int(m)} min")
        st.dataframe(
            display_df[["Date", "task_name", "category", "Duration", "notes"]].rename(
                columns={"task_name": "Task", "category": "Category", "notes": "Notes"}
            ),
            use_container_width=True, hide_index=True,
        )
        st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(), "productivity_log.csv", "text/csv")

# heatmap
with tab5:
    st.markdown("### When are you most productive?")
    if df.empty:
        st.info("Log a few sessions to see your heatmap.")
    else:
        st.plotly_chart(chart_heatmap(df), use_container_width=True)

        df_h = df.copy()
        df_h["hour"] = df_h["timestamp"].dt.hour
        hour_sum = df_h.groupby("hour")["time_spent"].sum().reset_index()
        hour_sum["hours"] = hour_sum["time_spent"] / 60
        fig_h = px.bar(hour_sum, x="hour", y="hours",
                       labels={"hour": "Hour of Day", "hours": "Total Hours"},
                       title="Total Hours by Hour of Day",
                       color="hours",
                       color_continuous_scale=[[0, "#13151d"], [1, "#c9f542"]])
        fig_h.update_layout(**CHART_LAYOUT, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_h, use_container_width=True)