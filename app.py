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

        return result.stdout.strip()

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
        "name": "Concurrent Users",
        "type": "number",
        "script": "db_check_concurrent_users.sh"
    }
]


def get_metric_value(metric):
    if metric["type"] == "status":
        return get_status(metric["script"])
    return run_script(metric["script"])


metric_values = []

for metric in METRICS:
    metric_values.append({
        "name": metric["name"],
        "type": metric["type"],
        "script": metric["script"],
        "value": get_metric_value(metric)
    })


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


