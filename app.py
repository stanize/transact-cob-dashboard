import streamlit as st
import subprocess
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Transact COB Dashboard",
    page_icon="💳",
    layout="wide"
)


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


# ---------------------------------------------------------
# Secondary Metrics (Date Synchronization Section)
# ---------------------------------------------------------

from datetime import datetime

# Example values (replace later with your scripts)
transact_date = "2026-03-08"
system_date = datetime.now().strftime("%Y-%m-%d")

# Calculate difference
date_diff = (
    datetime.strptime(system_date, "%Y-%m-%d")
    - datetime.strptime(transact_date, "%Y-%m-%d")
).days

if date_diff == 0:
    diff_text = "IN SYNC"
    diff_color = "#00ff9c"
else:
    diff_text = f"{date_diff} day(s)"
    diff_color = "#ff5c5c"

secondary_metrics = [
    {"label": "Transact Date", "value": transact_date, "color": "#00ff9c"},
    {"label": "System Date", "value": system_date, "color": "#00ff9c"},
    {"label": "Difference", "value": diff_text, "color": diff_color},
]


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

secondary_html = """
<div style="
display:flex;
justify-content:space-between;
align-items:center;
padding:10px 20px;
font-size:18px;
">

<div>
<b>Transact Date</b><br>
2026-03-08
</div>

<div>
<b>System Date</b><br>
2026-03-08
</div>

<div>
<b>Difference</b><br>
<span style="color:#00c853;">IN SYNC</span>
</div>

</div>
"""

st.markdown(secondary_html, unsafe_allow_html=True)





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


