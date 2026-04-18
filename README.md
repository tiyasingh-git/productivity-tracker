# StudyPulse — Student Productivity Tracker

StudyPulse is a data-driven productivity tracker built for students. It goes beyond simply logging the data as it analyses your habits and surfaces personalised insights so you can make better decisions about how you spend your time.

---

## Live Demo

Try it here:


---

## Features

- Session Logging: Log tasks with name, category, duration (minutes), and optional notes; data persists locally.
- Dynamic Category Manager: Add/delete custom categories (with emoji support); each gets an auto-assigned color stored in categories.json.
- Daily Goals System: Set per-category task-keyword goals (e.g., “Physics” → 120 min/day); matching sessions count automatically and reset daily.
- Dashboard (Tab 1): Visual analytics including stacked daily hours, donut distribution, trend with 7-day average, and all-time category totals.
- Insight Engine (Tab 2): Auto-generates insights like weekly stats, top category, longest session, missed categories, daily average, streaks, peak hour, and balance score with radar chart.
- Goals Tab (Tab 3): Real-time goal tracking with color-coded progress bars and 7-day completion history + summary table.
- Session Log (Tab 4): Complete session history with newest-first view and CSV export.
- Heatmap (Tab 5): Day × hour heatmap plus hourly distribution chart to identify productivity patterns.
- Today's Goal Banners: Always-visible top cards showing progress, remaining time, and completion status for each goal.

---

## Tech Stack

- Language: Python 3.10+
- Libraries: streamlit — UI framework, sidebar, tabs, forms, metrics
             pandas — all data manipulation, groupby, rolling averages, filtering
             numpy — balance score calculation (np.std)
             plotly — all charts (bar, pie, line, heatmap, radar)

---