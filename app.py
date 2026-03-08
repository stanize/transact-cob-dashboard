import streamlit as st
import subprocess
import json
import textwrap
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Transact COB Dashboard",
    page_icon="💳",
    layout="wide"
)

st.markdown("""
<style>
div[data-testid="stProgress"] > div > div > div > div {
    background-color: #3b82f6;
}
</style>
""", unsafe_allow_html=True)



SCRIPTS_DIR = Path(__file__).parent / "scripts"

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")


def run_script(script_name, timeout=30):
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        return "SCRIPT NOT FOUND"

    try:
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            return "ERROR"

        output = result.stdout.strip()

        if not output:
            return "N/A"

        return output

    except subprocess.TimeoutExpired:
        return "TIMEOUT"

    except Exception:
        return "ERROR"



def get_status(script_name):
    output = run_script(script_name)

    if output in ["SCRIPT NOT FOUND", "ERROR"]:
        return output

    status = output.upper()

    if status in ["STOPPED", "LOADING", "RUNNING"]:
        return status

    return "ERROR"


def get_color(status):
    return {
        "RUNNING": "#22c55e",
        "LOADING": "#facc15",
        "STOPPED": "#ef4444",
        "ERROR": "#ef4444",
        "SCRIPT NOT FOUND": "#f97316"
    }.get(status, "#6b7280")


METRICS = [
    {
        "name": "JBoss",
        "type": "status",
        "script": "db_check_jboss_status.sh"
    },
    {
        "name": "TSM",
        "type": "status",
        "script": "db_check_tsm_status.sh"
    },
    {
        "name": "TSM Last Run",
        "type": "text",
        "script": "db_get_tsm_last_run.sh"
    },    
    {
        "name": "Concurrent Users",
        "type": "number",
        "script": "db_check_concurrent_users.sh"
    },
    {
        "name": "License Expiry",
        "type": "text",
        "script": "db_check_license_expiry.sh"
    }
]


def get_metric_value(metric):
    if metric["type"] == "status":
        return get_status(metric["script"])
    elif metric["type"] in ["number", "text"]:
        return run_script(metric["script"])
    else:
        return "N/A"

metric_values = []

for metric in METRICS:
    metric_values.append({
        "name": metric["name"],
        "type": metric["type"],
        "script": metric["script"],
        "value": get_metric_value(metric)
    })


def get_cob_progress():
    script_path = SCRIPTS_DIR / "db_get_cob_progress_json.sh"

    if not script_path.exists():
        return None, "SCRIPT NOT FOUND"

    try:
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return None, "ERROR"

        output = result.stdout.strip()

        if not output:
            return None, "N/A"

        return json.loads(output), None

    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"

    except Exception:
        return None, "ERROR"


def get_progress_color(pct):
    if pct >= 100:
        return "#22c55e"
    elif pct > 0:
        return "#facc15"
    return "#334155"


# ---------------------------------------------------------
# Secondary Metrics (Date Synchronization Section)
# ---------------------------------------------------------

from datetime import datetime

system_date = datetime.now().strftime("%Y-%m-%d")

transact_raw = run_script("db_get_transact_date.sh")

try:
    transact_date = datetime.strptime(transact_raw, "%Y%m%d").strftime("%Y-%m-%d")
    date_diff = (
        datetime.strptime(system_date, "%Y-%m-%d") -
        datetime.strptime(transact_date, "%Y-%m-%d")
    ).days

    if date_diff == 0:
        diff_text = "IN SYNC"
        diff_color = "#00ff9c"
    else:
        diff_text = f"{date_diff} day(s)"
        diff_color = "#ff5c5c"

except ValueError:
    transact_date = f"INVALID ({transact_raw})"
    diff_text = "ERROR"
    diff_color = "#ff5c5c"


secondary_metrics = [
    {"label": "Transact Date", "value": transact_date, "color": "#00ff9c"},
    {"label": "System Date", "value": system_date, "color": "#00ff9c"},
    {"label": "Difference", "value": diff_text, "color": diff_color},
]

cob_progress_data, cob_progress_error = get_cob_progress()


st.title("💳 Transact COB Dashboard")
st.caption("Temenos Transact COB Operations Dashboard")

status_items = ""

for metric in metric_values:
    value = metric["value"]

    if metric["type"] == "status":
        status_items += f"""
<div>
    <b>{metric['name']}</b>
    <span style="
        display:inline-block;
        width:8px;
        height:8px;
        border-radius:50%;
        background:{get_color(value)};
        margin-left:6px;
        margin-right:6px;
    "></span>
    {value}
</div>
"""
    else:
        status_items += f"""
<div>
    <b>{metric['name']}</b>
    <span style="margin-left:6px;">{value}</span>
</div>
"""

status_bar = f"""
<div style="
    background:#0f172a;
    border-radius:10px;
    padding:12px 20px;
    margin-top:10px;
    margin-bottom:20px;
    display:flex;
    justify-content:flex-start;
    gap:40px;
    color:white;
    font-size:14px;
    flex-wrap:wrap;
">
    {status_items}
</div>
"""

st.markdown(status_bar, unsafe_allow_html=True)


# ---------------------------------------------------------
# Secondary Metrics Display
# ---------------------------------------------------------

# st.markdown("---")

secondary_html = f"""
<div style="
display:flex;
justify-content:space-between;
align-items:center;
padding:10px 20px;
font-size:18px;
">

<div>
<b>Transact Date</b><br>
{transact_date}
</div>

<div>
<b>System Date</b><br>
{system_date}
</div>

<div>
<b>Difference</b><br>
<span style="color:{diff_color};">{diff_text}</span>
</div>

</div>
"""

st.markdown(secondary_html, unsafe_allow_html=True)


# --------------------------------------------------------
# COB Progress
# --------------------------------------------------------

# ---------------------------------------------------------
# COB Progress Display
# ---------------------------------------------------------

st.markdown("---")
st.subheader("COB Monitor")

if cob_progress_error:
    st.error(f"Unable to load COB progress: {cob_progress_error}")
elif cob_progress_data and cob_progress_data.get("stages"):
    system_time = cob_progress_data.get("system_time", "N/A")
    cob_date = cob_progress_data.get("cob_date", "N/A")
    company_id = cob_progress_data.get("company_id", "N/A")
    stages = cob_progress_data.get("stages", [])

    # Remove COB from lower table, because it is shown separately above
    stage_rows = [
        row for row in stages
        if row.get("stage", "").strip().upper() != "COB"
    ]

    # ---------------------------------------------------------
    # Overall COB Progress
    # ---------------------------------------------------------
    cob_row = next(
        (row for row in stages if row.get("stage", "").strip().upper() == "COB"),
        None
    )
    
    if cob_row:
        total_processed = int(cob_row.get("processed", 0))
        total_jobs = int(cob_row.get("total", 0))
    else:
        total_processed = sum(int(row.get("processed", 0)) for row in stage_rows)
        total_jobs = sum(int(row.get("total", 0)) for row in stage_rows)
        
    if total_jobs > 0:
        overall_pct = (total_processed / total_jobs) * 100
    else:
        overall_pct = 0

    if overall_pct >= 100:
        overall_color = "#22c55e"
    elif overall_pct >= 50:
        overall_color = "#3b82f6"
    elif overall_pct > 0:
        overall_color = "#f59e0b"
    else:
        overall_color = "#64748b"
    
  
    box_col1, box_col2 = st.columns([4, 1])
    
    with box_col1:
        st.markdown("**COB Completion**")
    
    with box_col2:
        st.markdown(
            f"""
            <div style="text-align:right; font-size:32px; font-weight:800; color:{overall_color};">
                {overall_pct:.2f}%
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.progress(overall_pct / 100 if total_jobs else 0)
    
    st.caption(f"{total_processed} / {total_jobs} jobs completed")

    
    # ---------------------------------------------------------
    # Stage Progress Table
    # ---------------------------------------------------------

    header_cols = st.columns([2.2, 4, 1.2, 1.2, 1.2])
    header_cols[0].markdown("**Stage**")
    header_cols[1].markdown("**Progress**")
    header_cols[2].markdown("**Processed**")
    header_cols[3].markdown("**Total**")
    header_cols[4].markdown("**% Completed**")

    for row in stage_rows:
        stage = row.get("stage", "N/A")
        processed = row.get("processed", 0)
        total = row.get("total", 0)
        pct = float(row.get("pct_completed", 0))

        cols = st.columns([2.2, 4, 1.2, 1.2, 1.2])

        cols[0].markdown(f"**{stage}**")

        progress_color = get_progress_color(pct)
        progress_html = f"""
        <div style="
            background:#1e293b;
            border-radius:8px;
            height:20px;
            width:100%;
            overflow:hidden;
            border:1px solid #334155;
        ">
            <div style="
                background:{progress_color};
                width:{min(pct, 100)}%;
                height:100%;
                transition:width 0.5s ease-in-out;
            "></div>
        </div>
        """
        cols[1].markdown(progress_html, unsafe_allow_html=True)

        cols[2].markdown(str(processed))
        cols[3].markdown(str(total))
        cols[4].markdown(f"{pct:.2f}%")
else:
    st.warning("No COB progress data available.")


# ---------------------------------------------------------
# Credits Section
# ---------------------------------------------------------

st.markdown(
"""
---
<center>

⚡ **Transact COB Dashboard**

Powered by **Streamlit • Python • Bash • Coffee • Mild Panic**  
Created by **Ignatius Stanislaus**


🛠️ If it works, it was planned. If it breaks, it's still under development.
</center>
""",
unsafe_allow_html=True
)


