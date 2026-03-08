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
JBOSS_STATUS_SCRIPT = "db_check_jboss_status.sh"
TSM_STATUS_SCRIPT = "db_check_jboss_status.sh"

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


def get_jboss_status():
    output = run_script(JBOSS_STATUS_SCRIPT)
    if output in ["SCRIPT NOT FOUND", "ERROR"]:
        return output
    status = output.upper()
    if status in ["STOPPED", "LOADING", "RUNNING"]:
        return status
    return "ERROR"


def get_tsm_status
    output = run_script(TSM_STATUS_SCRIPT)
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


jboss_status = get_jboss_status()
tsm_status = get_tsm_status()

st.title("💳 Transact COB Dashboard")
st.caption("Temenos Transact COB Operations Dashboard")

status_bar = f"""
<div style="
background:#0f172a;
border-radius:10px;
padding:12px 20px;
margin-top:10px;
margin-bottom:20px;
display:flex;
justify-content:space-between;
color:white;
font-size:14px;
">

<div>
<b>JBoss</b>
<span style="
display:inline-block;
width:8px;
height:8px;
border-radius:50%;
background:{get_color(jboss_status)};
margin-left:6px;
margin-right:6px;
"></span>
{jboss_status}
</div>

<div>
<b>TSM</b>
<span style="
display:inline-block;
width:8px;
height:8px;
border-radius:50%;
background:{get_color(tsm_status)};
margin-left:6px;
margin-right:6px;
"></span>
{tsm_status}
</div>

</div>
"""

st.markdown(status_bar, unsafe_allow_html=True)

st.info("JBoss status is checked using scripts/db_check_jboss_status.sh")
