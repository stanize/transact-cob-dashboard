import streamlit as st
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from streamlit_autorefresh import st_autorefresh
import uuid
from pathlib import Path
import os

st.set_page_config(
    page_title="Transact Dashboard",
    page_icon="💳",
    layout="wide"
)

st.markdown(dedent("""
<style>

/* ---------------------------------------------------------
   GLOBAL LAYOUT
--------------------------------------------------------- */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* ---------------------------------------------------------
   TABS
--------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    padding: 0;
    margin-top: 6px;
    margin-bottom: 14px;
    border-bottom: 1px solid #dbe3ea;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    padding: 0 18px;
    background: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    color: #334155;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #f8fafc;
    color: #0f172a;
}

.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-bottom: 1px solid #ffffff !important;
    box-shadow: 0 -1px 0 #ffffff inset;
}

.stTabs [data-baseweb="tab-panel"] {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 0 12px 12px 12px;
    padding: 18px 18px 20px 18px;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

/* ---------------------------------------------------------
   TOP STATUS BAR
--------------------------------------------------------- */
.top-status-bar {
    background: #0f172a;
    border-radius: 14px;
    padding: 14px;
    margin-top: 10px;
    margin-bottom: 20px;
    display: grid;
    grid-template-columns: repeat(3, minmax(220px, 1fr));
    gap: 14px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.18);
}

.top-status-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 14px 16px;
    min-height: 92px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.top-status-label {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 8px;
}

.top-status-main {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}

.top-status-sub {
    font-size: 13px;
    color: #cbd5e1;
    margin-top: 8px;
}

.top-status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}

@media (max-width: 1100px) {
    .top-status-bar {
        grid-template-columns: 1fr;
    }
}

/* ---------------------------------------------------------
   SECONDARY METRICS
--------------------------------------------------------- */
.secondary-metrics {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    gap: 14px;
    margin-bottom: 10px;
}

.secondary-card {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.secondary-label {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 6px;
}

.secondary-value {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
}

/* ---------------------------------------------------------
   Start COB Button (green)
--------------------------------------------------------- */
button[kind="primary"] {
    background-color: #16a34a !important;
}

button[kind="primary"]:hover {
    background-color: #15803d !important;
}

/* ---------------------------------------------------------
   COB SUMMARY CARD
--------------------------------------------------------- */
.cob-summary-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 20px 22px 18px 22px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
    margin-bottom: 18px;
}

.cob-summary-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
}

.cob-summary-subtitle {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 12px;
}

.cob-big-pct {
    text-align: right;
    font-size: 34px;
    font-weight: 800;
}

/* ---------------------------------------------------------
   CUSTOM PROGRESS BARS
--------------------------------------------------------- */
.progress-track {
    width: 100%;
    border-radius: 999px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.5s ease-in-out;
}

.progress-overall-track {
    background: #d1d5db;
    height: 18px;
}

.progress-stage-track {
    background: #cbd5e1;
    height: 16px;
}

/* ---------------------------------------------------------
   STAGE TABLE
--------------------------------------------------------- */
.stage-header {
    font-size: 12px;
    font-weight: 700;
    color: #475569;
    margin-bottom: 8px;
}

.stage-cell {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 14px 16px;
    min-height: 56px;
    display: flex;
    align-items: center;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.stage-name-wrap {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.stage-name {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
}

.stage-number {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
}

.stage-pct {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
}

/* ---------------------------------------------------------
   STATUS PILLS
--------------------------------------------------------- */
.status-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    width: fit-content;
}

.status-completed {
    background: #dcfce7;
    color: #166534;
}

.status-running {
    background: #dbeafe;
    color: #1d4ed8;
}

.status-pending {
    background: #f3f4f6;
    color: #4b5563;
}

.status-failed {
    background: #fee2e2;
    color: #b91c1c;
}

/* subtle dashboard background */
.stApp {
    background-color: #f3f4f6;
}

/* cleaner spacing between blocks */
[data-testid="stVerticalBlock"] > div {
    gap: 0.6rem;
}

</style>
"""), unsafe_allow_html=True)

SCRIPTS_DIR = Path(__file__).parent / "scripts"

if "cob_start_in_progress" not in st.session_state:
    st.session_state.cob_start_in_progress = False

if "cob_start_requested" not in st.session_state:
    st.session_state.cob_start_requested = False

if not st.session_state.cob_start_in_progress:
    st_autorefresh(interval=5000, key="refresh")

if "jboss_restart_requested" not in st.session_state:
    st.session_state.jboss_restart_requested = False

if "jboss_restart_in_progress" not in st.session_state:
    st.session_state.jboss_restart_in_progress = False
    

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

    if output in ["SCRIPT NOT FOUND", "ERROR", "TIMEOUT"]:
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
        "TIMEOUT": "#f97316",
        "SCRIPT NOT FOUND": "#f97316"
    }.get(status, "#6b7280")


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


METRICS = [
    {
        "name": "JBoss",
        "type": "status",
        "script": "db_check_jboss_status.sh"
    },
    {
        "name": "JBoss Uptime",
        "type": "text",
        "script": "db_get_jboss_uptime.sh"
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


def metric_lookup(name):
    for metric in metric_values:
        if metric["name"] == name:
            return metric["value"]
    return "N/A"


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


def get_stage_status(processed, total):
    if total > 0 and processed >= total:
        return "COMPLETED"
    elif processed > 0:
        return "RUNNING"
    else:
        return "PENDING"


def get_status_pill_class(status):
    return {
        "COMPLETED": "status-completed",
        "RUNNING": "status-running",
        "PENDING": "status-pending",
        "FAILED": "status-failed"
    }.get(status, "status-pending")


def run_script_live(script_name):
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        return False, ["SCRIPT NOT FOUND"]

    lines = []

    try:
        process = subprocess.Popen(
            ["bash", str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        stage_placeholder = st.empty()
        log_placeholder = st.empty()

        for line in process.stdout:
            clean_line = line.rstrip()
            lines.append(clean_line)

            if clean_line.startswith("[STAGE]"):
                stage_placeholder.info(clean_line.replace("[STAGE] ", ""))

            log_placeholder.code("\n".join(lines), language="bash")

        process.wait()

        return process.returncode == 0, lines

    except Exception as e:
        return False, [f"ERROR: {str(e)}"]


LOG_DIR = Path("/tmp/transact_dashboard_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_RETENTION_DAYS = 3
LOG_RETENTION_SECONDS = LOG_RETENTION_DAYS * 24 * 60 * 60

def cleanup_old_logs():
    now = time.time()

    for log_file in LOG_DIR.glob("session_*.log"):
        try:
            file_age = now - log_file.stat().st_mtime

            if file_age > LOG_RETENTION_SECONDS:
                log_file.unlink()
        except Exception:
            pass
            
cleanup_old_logs()


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

SESSION_LOG_FILE = LOG_DIR / f"session_{st.session_state.session_id}.log"
GLOBAL_LOG_FILE = LOG_DIR / "global_audit.log"

if "log_lines" not in st.session_state:
    st.session_state.log_lines = []

def append_log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {message}"

    st.session_state.log_lines.append(formatted)

    with open(SESSION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

    with open(GLOBAL_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[session:{st.session_state.session_id}] {formatted}\n")


def clear_logs():
    st.session_state.log_lines = []

def run_streaming_command(script_name):
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        append_log(f"Script not found: {script_path}", "ERROR")
        return 1

    append_log("=" * 80)
    append_log(f"Starting: {script_name}")
    append_log("=" * 80)

    log_placeholder = st.empty()

    process = subprocess.Popen(
        ["bash", str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in iter(process.stdout.readline, ''):
        line = line.rstrip()
        if line:
            append_log(line)
            log_placeholder.text_area(
                "Execution Output",
                value="\n".join(st.session_state.log_lines),
                height=300,
                key="live_log_explorer",
                disabled=True
            )

    process.stdout.close()
    return_code = process.wait()

    if return_code == 0:
        append_log(f"Command finished successfully with exit code {return_code}", "SUCCESS")
    else:
        append_log(f"Command failed with exit code {return_code}", "ERROR")

    return return_code

def render_jboss_restart():
    if st.button("Restart JBoss", type="primary", key="restart_jboss_btn"):
        run_streaming_command("db_restart_jboss.sh")    


# ── DATA COLLECTION ──────────────────────────────────────────────────────────

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
        diff_color = "#16a34a"
    else:
        diff_text = f"{date_diff} day(s)"
        diff_color = "#ff5c5c"

except ValueError:
    transact_date = f"INVALID ({transact_raw})"
    diff_text = "ERROR"
    diff_color = "#ff5c5c"

cob_progress_data, cob_progress_error = get_cob_progress()

# ── PAGE HEADER ──────────────────────────────────────────────────────────────

st.title("💳 Transact Dashboard")
#st.caption("Temenos Transact COB Operations Dashboard")

# ── METRIC LOOKUPS ───────────────────────────────────────────────────────────

jboss_status = metric_lookup("JBoss")
jboss_uptime = metric_lookup("JBoss Uptime")
tsm_status = metric_lookup("TSM")
tsm_last_run = metric_lookup("TSM Last Run")
concurrent_users = metric_lookup("Concurrent Users")
license_expiry = metric_lookup("License Expiry")

# ── TOP STATUS BAR ───────────────────────────────────────────────────────────

card_jboss = (
    '<div class="top-status-card">'
    '<div class="top-status-label">JBoss</div>'
    '<div class="top-status-main">'
    f'<span class="top-status-dot" style="background:{get_color(jboss_status)};"></span>'
    f'<span>{jboss_status}</span>'
    '</div>'
    f'<div class="top-status-sub">Uptime: {jboss_uptime}</div>'
    '</div>'
)

card_tsm = (
    '<div class="top-status-card">'
    '<div class="top-status-label">TSM</div>'
    '<div class="top-status-main">'
    f'<span class="top-status-dot" style="background:{get_color(tsm_status)};"></span>'
    f'<span>{tsm_status}</span>'
    '</div>'
    f'<div class="top-status-sub">Last run: {tsm_last_run}</div>'
    '</div>'
)

card_platform = (
    '<div class="top-status-card">'
    '<div class="top-status-label">Platform</div>'
    f'<div class="top-status-main">{concurrent_users} users</div>'
    f'<div class="top-status-sub">License expiry: {license_expiry}</div>'
    '</div>'
)

st.markdown(
    f'<div class="top-status-bar">{card_jboss}{card_tsm}{card_platform}</div>',
    unsafe_allow_html=True
)

# ── SECONDARY METRICS BAR ────────────────────────────────────────────────────

card_transact = (
    '<div class="secondary-card">'
    '<div class="secondary-label">Transact Date</div>'
    f'<div class="secondary-value">{transact_date}</div>'
    '</div>'
)

card_system = (
    '<div class="secondary-card">'
    '<div class="secondary-label">System Date</div>'
    f'<div class="secondary-value">{system_date}</div>'
    '</div>'
)

card_diff = (
    '<div class="secondary-card">'
    '<div class="secondary-label">Difference</div>'
    f'<div class="secondary-value" style="color:{diff_color};">{diff_text}</div>'
    '</div>'
)

st.markdown(
    f'<div class="secondary-metrics">{card_transact}{card_system}{card_diff}</div>',
    unsafe_allow_html=True
)

# ── TABS ─────────────────────────────────────────────────────────────────────

tab_operations, tab_cob = st.tabs(["Operations", "COB Monitor"])

# ── TAB: OVERVIEW ────────────────────────────────────────────────────────────

with tab_operations:
    with st.container(border=True):
        render_jboss_restart()
        
# ── TAB: COB MONITOR ─────────────────────────────────────────────────────────

with tab_cob:

    st.markdown("""
    <div style="
        background-color: #1e293b;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        border: 1px dashed #475569;
        margin-top: 10px;
    ">
        <h3 style="margin-bottom:10px;">🚧 Work in Progress</h3>
        <p style="color:#94a3b8; margin-bottom:0;">
            COB execution and monitoring features are currently under development.<br>
            This section is not available yet.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── LOG EXPLORER ───────────────────────────────────────────────────────────────────
st.markdown("### Log Explorer")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Clear Logs"):
        clear_logs()
        st.rerun()

with col2:
    st.caption(f"{len(st.session_state.log_lines)} log lines")

st.text_area(
    "Execution Output",
    value="\n".join(st.session_state.log_lines),
    height=300,
    key="log_explorer",
    disabled=True
)
# ── FOOTER ───────────────────────────────────────────────────────────────────

st.markdown(dedent("""
---
<center>

⚡ **Transact Dashboard**

Powered by **Streamlit • Python • Bash • Coffee • Mild Panic**  
Created by **Ignatius Stanislaus**

🛠️ If it works, it was planned. If it breaks, it's still under development.
</center>
"""), unsafe_allow_html=True)



# --- CODE TO BE USED IN THE FUTURE -----

def future_cob_tab():
    cob_service_control = run_script("db_get_cob_service_control.sh").strip().upper()

    if cob_service_control == "STOP":

        with st.container(border=True):
            start_cob_clicked = st.button(
                "Start COB",
                type="primary",
                disabled=st.session_state.cob_start_in_progress
            )

        if start_cob_clicked:
            st.session_state.cob_start_requested = True
            st.rerun()

        if st.session_state.cob_start_requested and not st.session_state.cob_start_in_progress:
            st.session_state.cob_start_in_progress = True
            st.session_state.cob_start_requested = False
            st.rerun()

        if st.session_state.cob_start_in_progress:
            st.subheader("COB Start Workflow Log")

            ok, log_lines = run_script_live("db_start_cob.sh")

            st.session_state.cob_start_in_progress = False

            if ok:
                st.success("COB start workflow completed.")
            else:
                st.error("COB start workflow failed.")

    elif cob_service_control == "START":

        raw_tx = run_script("db_get_cob_transactions.sh")

        try:
            current_tx = int(raw_tx)
        except Exception:
            current_tx = 0

        now_ts = time.time()

        if "tx_history" not in st.session_state:
            st.session_state.tx_history = []

        st.session_state.tx_history.append((now_ts, current_tx))

        st.session_state.tx_history = [
            item for item in st.session_state.tx_history
            if now_ts - item[0] <= 180
        ]

        transactions_processed = f"{current_tx:,}"
        tx_rate_text = "Avg: --/min"

        if len(st.session_state.tx_history) >= 2:
            oldest_ts, oldest_tx = st.session_state.tx_history[0]
            newest_ts, newest_tx = st.session_state.tx_history[-1]

            elapsed = newest_ts - oldest_ts
            delta = newest_tx - oldest_tx

            if elapsed > 0:
                avg_per_min = int(delta * 60 / elapsed)

                if avg_per_min > 0:
                    tx_rate_text = f"+{avg_per_min:,}/min"
                elif avg_per_min == 0:
                    tx_rate_text = "0/min"
                else:
                    tx_rate_text = f"{avg_per_min:,}/min"

        if cob_progress_error:
            st.error(f"Unable to load COB progress: {cob_progress_error}")

        elif cob_progress_data and cob_progress_data.get("stages"):
            stages = cob_progress_data.get("stages", [])

            stage_rows = [
                row for row in stages
                if row.get("stage", "").strip().upper() != "COB"
            ]

            cob_row = next(
                (row for row in stages if row.get("stage", "").strip().upper() == "COB"),
                None
            )

            if cob_row:
                total_processed = safe_int(cob_row.get("processed", 0))
                total_jobs = safe_int(cob_row.get("total", 0))
            else:
                total_processed = sum(safe_int(row.get("processed", 0)) for row in stage_rows)
                total_jobs = sum(safe_int(row.get("total", 0)) for row in stage_rows)

            overall_pct = (total_processed / total_jobs) * 100 if total_jobs > 0 else 0

            if overall_pct >= 100:
                overall_color = "#22c55e"
            elif overall_pct > 0:
                overall_color = "#16a34a"
            else:
                overall_color = "#64748b"

            title_col, tx_col, pct_col = st.columns([4, 1.2, 1])

            with title_col:
                st.markdown(
                    '<div class="cob-summary-card">'
                    '<div class="cob-summary-title">COB Progress</div>'
                    '<div class="progress-track progress-overall-track">'
                    f'<div class="progress-fill" style="background:#22c55e;width:{min(overall_pct, 100)}%;height:100%;"></div>'
                    '</div>'
                    f'<div class="cob-summary-subtitle" style="margin-top:10px;margin-bottom:0;">{total_processed} / {total_jobs} jobs completed</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

            with tx_col:
                st.markdown(
                    '<div class="cob-summary-card">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;gap:6px;">'
                    f'<div class="cob-big-pct" style="color:#0f172a;margin:0;">{transactions_processed}</div>'
                    f'<span style="font-size:12px;font-weight:600;color:#64748b;white-space:nowrap;">{tx_rate_text}</span>'
                    '</div>'
                    '<div class="cob-summary-subtitle" style="margin-top:6px;margin-bottom:0;text-align:center;">Transactions processed</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

            with pct_col:
                st.markdown(
                    '<div class="cob-summary-card">'
                    f'<div class="cob-big-pct" style="color:{overall_color};">{overall_pct:.2f}%</div>'
                    '<div class="cob-summary-subtitle" style="text-align:right;margin-bottom:0;">Overall progress</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

            header_cols = st.columns([2.4, 4, 1.2, 1.2, 1.4])
            header_cols[0].markdown('<div class="stage-header">Stage</div>', unsafe_allow_html=True)
            header_cols[1].markdown('<div class="stage-header">Progress</div>', unsafe_allow_html=True)
            header_cols[2].markdown('<div class="stage-header">Processed</div>', unsafe_allow_html=True)
            header_cols[3].markdown('<div class="stage-header">Total</div>', unsafe_allow_html=True)
            header_cols[4].markdown('<div class="stage-header">% Completed</div>', unsafe_allow_html=True)

            for row in stage_rows:
                stage = row.get("stage", "N/A")
                processed = safe_int(row.get("processed", 0))
                total = safe_int(row.get("total", 0))
                pct = safe_float(row.get("pct_completed", 0))
                status = get_stage_status(processed, total)
                pill_class = get_status_pill_class(status)

                if status == "COMPLETED":
                    progress_color = "#16a34a"
                elif status == "RUNNING":
                    progress_color = "#1e3a5f"
                else:
                    progress_color = "#64748b"

                cols = st.columns([2.4, 4, 1.2, 1.2, 1.4])

                cols[0].markdown(
                    '<div class="stage-cell">'
                    '<div class="stage-name-wrap">'
                    f'<div class="stage-name">{stage}</div>'
                    f'<span class="status-pill {pill_class}">{status}</span>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                cols[1].markdown(
                    '<div class="stage-cell">'
                    '<div class="progress-track progress-stage-track">'
                    f'<div class="progress-fill" style="background:{progress_color};width:{min(pct, 100)}%;height:100%;"></div>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                cols[2].markdown(
                    f'<div class="stage-cell"><div class="stage-number">{processed}</div></div>',
                    unsafe_allow_html=True
                )

                cols[3].markdown(
                    f'<div class="stage-cell"><div class="stage-number">{total}</div></div>',
                    unsafe_allow_html=True
                )

                cols[4].markdown(
                    f'<div class="stage-cell"><div class="stage-pct">{pct:.2f}%</div></div>',
                    unsafe_allow_html=True
                )

        else:
            st.warning("No COB progress data available.")
