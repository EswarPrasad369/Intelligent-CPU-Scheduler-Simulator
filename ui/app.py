import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import time
import base64
from datetime import datetime, timezone

from engine.algorithms import (
    fcfs,
    sjf_non_preemptive,
    srtf,
    round_robin,
    priority_non_preemptive,
    priority_preemptive
)

st.set_page_config(layout="wide", page_title="Intelligent CPU Scheduler", initial_sidebar_state="collapsed")

if "started" not in st.session_state:
    st.session_state.started = False
if "sim_time" not in st.session_state:
    st.session_state.sim_time = 0.0
if "playing" not in st.session_state:
    st.session_state.playing = False
if "speed" not in st.session_state:
    st.session_state.speed = 1.0
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Single-line"
if "compare_results" not in st.session_state:
    st.session_state.compare_results = {}
if "run_click" not in st.session_state:
    st.session_state.run_click = False

def default_presets():
    return {
        "Tiny (3)": [
            {"pid":"P1","arrival":0,"burst":1,"priority":1},
            {"pid":"P2","arrival":0,"burst":1,"priority":1},
            {"pid":"P3","arrival":0,"burst":1,"priority":1}
        ],
        "Mixed arrivals": [
            {"pid":"P1","arrival":0,"burst":4,"priority":1},
            {"pid":"P2","arrival":2,"burst":6,"priority":1},
            {"pid":"P3","arrival":3,"burst":1,"priority":1},
            {"pid":"P4","arrival":4,"burst":3,"priority":1},
            {"pid":"P5","arrival":6,"burst":5,"priority":1}
        ],
        "Many short & one long": [
            {"pid":"P1","arrival":0,"burst":1,"priority":1},
            {"pid":"P2","arrival":1,"burst":1,"priority":1},
            {"pid":"P3","arrival":2,"burst":1,"priority":1},
            {"pid":"P4","arrival":3,"burst":12,"priority":1},
            {"pid":"P5","arrival":4,"burst":1,"priority":1}
        ]
    }

PRIMARY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;800&display=swap');
:root { --bg:#0b0f12; --card:#0f1418; --muted:#98a0aa; --accent1:#7f5af0; --accent2:#ff7ab6; --text:#eaf1ff; }
html, body, .stApp { background: linear-gradient(180deg,#07090b 0%,#0b0f12 100%); color: var(--text); font-family: 'Inter', sans-serif; }
.header { display:flex; flex-direction:column; align-items:center; justify-content:center; padding-top:8px; padding-bottom:12px; }
.hero { font-size:44px; font-weight:800; background: linear-gradient(90deg,var(--accent1),var(--accent2)); -webkit-background-clip: text; color: transparent; letter-spacing:-0.6px; }
.lead { color:var(--muted); margin-top:6px; margin-bottom:10px; font-size:14px; }
.container-card { background: rgba(255,255,255,0.02); border-radius:12px; padding:14px; border:1px solid rgba(255,255,255,0.03); box-shadow: 0 6px 20px rgba(0,0,0,0.6); }
.inputs-row .stNumberInput > div { height:44px; }
.compact-table td, .compact-table th { padding:8px 10px; }
.action-btn button { border-radius:10px; padding:8px 14px; font-weight:700; border:none; color:white; background:linear-gradient(90deg,var(--accent1),var(--accent2)); box-shadow:0 10px 30px rgba(127,90,240,0.12); }
.small-muted { color:var(--muted); font-size:13px; }
.legend-grid { display:flex; gap:10px; flex-wrap:wrap; margin-top:8px; }
.legend-item { display:flex; align-items:center; gap:8px; padding:4px 8px; border-radius:8px; background: rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.02); }
.now-running { float:right; padding:6px 12px; border-radius:10px; font-weight:700; background: linear-gradient(90deg,#f5a623,#ffd166); color:#0b0f12; }
.playback-compact { display:flex; gap:8px; align-items:center; margin-bottom:8px; }
.playback-compact .btn { padding:8px 12px; border-radius:8px; background:#11141a; color:#fff; border:1px solid rgba(255,255,255,0.04); }
.sticky-controls { position: sticky; top: 14px; z-index: 999; }
.kv { display:flex; gap:8px; align-items:center; }
.kv .box { width:20px; height:20px; border-radius:4px; box-shadow:0 6px 20px rgba(0,0,0,0.4); }
</style>
"""
st.markdown(PRIMARY_CSS, unsafe_allow_html=True)

preset_map = default_presets()

st.markdown("<div class='header'><div class='hero'>🧠 Intelligent CPU Scheduler</div><div class='lead'>Modern interactive simulator — FCFS · SJF · SRTF · Round Robin · Priority</div></div>", unsafe_allow_html=True)

if not st.session_state.started:
    with st.container():
        st.markdown("<div style='display:flex;justify-content:center'><div style='width:880px' class='container-card'>", unsafe_allow_html=True)
        st.markdown("<div style='display:flex;flex-direction:column;align-items:center;gap:10px'>", unsafe_allow_html=True)
        st.markdown("<div style='width:88px;height:88px;border-radius:16px;display:flex;align-items:center;justify-content:center;background:linear-gradient(90deg,#7f5af0,#ff7ab6);color:white;font-weight:800'>CPU</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight:700;font-size:22px'>Welcome — Click to enter the simulator</div>", unsafe_allow_html=True)
        if st.button("🚀 Enter Simulator", key="enter"):
            st.session_state.started = True
            try:
                st.rerun()
            except Exception:
                try:
                    st.experimental_rerun()
                except Exception:
                    st.warning("Please refresh the page to continue.")
        st.markdown("</div></div></div>", unsafe_allow_html=True)
    st.stop()

left, right = st.columns([1, 1.6])

with left:
    st.markdown("<div class='container-card'>", unsafe_allow_html=True)
    st.markdown("<h3>Controls</h3>", unsafe_allow_html=True)
    preset_choice = st.selectbox("Load preset scenario", options=["Custom"] + list(preset_map.keys()))
    processes = preset_map[preset_choice] if preset_choice != "Custom" else None

    if processes is None:
        n = st.number_input("Number of processes", min_value=1, max_value=20, value=3, key="nproc")
        editable = True
    else:
        n = len(processes)
        editable = False

    rows = []
    palette = px.colors.qualitative.Plotly
    if editable:
        st.markdown("<div>", unsafe_allow_html=True)
        for i in range(int(n)):
            cols = st.columns([0.9,0.9,0.9,1.6,0.7])
            prio = cols[0].number_input(f"Prio {i+1}", min_value=1, value=1, key=f"prio_{i}")
            arr = cols[1].number_input(f"Arr {i+1}", min_value=0, value=0, key=f"arr_{i}")
            burst = cols[2].number_input(f"Burst {i+1}", min_value=1, value=1, key=f"burst_{i}")
            pid = cols[3].text_input(f"PID {i+1}", value=f"P{i+1}", key=f"pid_{i}", max_chars=8)
            cols[4].markdown(f"<div style='display:flex;justify-content:center;align-items:center'><div style='width:24px;height:24px;border-radius:6px;background:{palette[i%len(palette)]};'></div></div>", unsafe_allow_html=True)
            rows.append({"pid":pid or f"P{i+1}","arrival":int(arr),"burst":int(burst),"priority":int(prio)})
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        rows = processes

    process_list = rows
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    algo = st.selectbox("Scheduling algorithm", ["FCFS","SJF (Non-Preemptive)","SRTF (Preemptive SJF)","Round Robin","Priority (Non-Preemptive)","Priority (Preemptive)"], key="algo")
    quantum = None
    if algo == "Round Robin":
        quantum = st.number_input("Time quantum", min_value=1, value=2, key="quantum")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    compare_toggle = st.checkbox("Enable algorithm comparison mode", value=False, key="compare_toggle")
    compare_algs = []
    if compare_toggle:
        compare_algs = st.multiselect("Algorithms to compare", ["FCFS","SJF (Non-Preemptive)","SRTF (Preemptive SJF)","Round Robin","Priority (Non-Preemptive)","Priority (Preemptive)"], default=["FCFS","SJF (Non-Preemptive)"])
        if "Round Robin" in compare_algs:
            q_comp = st.number_input("Quantum for Round Robin (comparison)", min_value=1, value=2, key="qcomp")
        else:
            q_comp = quantum
    else:
        q_comp = quantum

    run_col, save_col = st.columns([1,1])
    if run_col.button("▶ Run Simulation", key="run"):
        st.session_state.last_run = datetime.now(timezone.utc).isoformat()
        st.session_state.run_click = True
    if save_col.button("💾 Save scenario (.json)"):
        buf = io.BytesIO(json.dumps(process_list, indent=2).encode("utf-8"))
        st.download_button("Download scenario", data=buf, file_name="scenario.json", mime="application/json")
    uploaded = st.file_uploader("Load scenario (.json)", type=["json"])
    if uploaded:
        try:
            loaded = json.load(uploaded)
            if isinstance(loaded, list):
                process_list = loaded
            else:
                st.error("Invalid scenario file.")
        except Exception:
            st.error("Failed to load scenario.")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700;margin-bottom:6px'>PID Color Preview</div>", unsafe_allow_html=True)
    preview_html = "<div style='display:flex;gap:10px;flex-wrap:wrap'>"
    for i, p in enumerate(process_list):
        colr = palette[i % len(palette)]
        preview_html += f"<div style='display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:8px;background:rgba(255,255,255,0.015)'><div style='width:14px;height:14px;border-radius:4px;background:{colr};'></div><div style='font-weight:600'>{p['pid']}</div></div>"
    preview_html += "</div>"
    st.markdown(preview_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='container-card'>", unsafe_allow_html=True)
    st.markdown("<h3>Simulation & Visualization</h3>", unsafe_allow_html=True)
    sim_space = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

def run_selected_algorithm(algo_name, plist, quantum=None):
    if algo_name == "FCFS":
        return fcfs(plist)
    if algo_name == "SJF (Non-Preemptive)":
        return sjf_non_preemptive(plist)
    if algo_name == "SRTF (Preemptive SJF)":
        return srtf(plist)
    if algo_name == "Round Robin":
        return round_robin(plist, quantum)
    if algo_name == "Priority (Non-Preemptive)":
        return priority_non_preemptive(plist)
    if algo_name == "Priority (Preemptive)":
        return priority_preemptive(plist)
    return [], []

def prepare_gantt_df(gantt):
    if not gantt:
        return pd.DataFrame()
    df = pd.DataFrame(gantt)
    df["start"] = df["start"].astype(float)
    df["end"] = df["end"].astype(float)
    df["duration"] = df["end"] - df["start"]
    return df

def compact_color_map(pids):
    palette = px.colors.qualitative.Plotly
    cmap = {pid: palette[i % len(palette)] for i, pid in enumerate(pids)}
    return cmap

def build_gantt_figure(gantt_df, sim_time, view_mode="Single-line"):
    if gantt_df.empty:
        fig = go.Figure()
        fig.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    cmap = compact_color_map(gantt_df["pid"].unique().tolist())
    if view_mode == "Single-line":
        df = gantt_df.copy().sort_values(by=["start"]).reset_index(drop=True)
        df["label"] = df.apply(lambda r: f"{r['pid']} ({int(r['start'])}→{int(r['end'])})", axis=1)
        fig = go.Figure()
        for idx, row in df.iterrows():
            duration = row["duration"]
            is_running = (sim_time is not None and row["start"] <= sim_time < row["end"])
            linew = 3 if is_running else 0
            linec = "white" if is_running else "rgba(0,0,0,0)"
            fig.add_trace(go.Bar(
                x=[duration],
                y=["CPU"],
                base=[row["start"]],
                orientation="h",
                marker=dict(color=cmap[row["pid"]], line=dict(color=linec, width=linew)),
                hovertemplate=f"<b>{row['pid']}</b><br>Start: {row['start']}<br>End: {row['end']}<extra></extra>",
                text=[row["label"]],
                textposition="inside",
                insidetextanchor="middle",
                cliponaxis=False,
                showlegend=False
            ))
        fig.update_xaxes(title_text="Time", tick0=0, dtick=1, zeroline=True)
        fig.update_yaxes(visible=False)
        fig.update_layout(barmode="stack", height=240, margin=dict(l=40, r=20, t=10, b=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        if sim_time is not None:
            fig.add_vline(x=sim_time, line=dict(color="white", width=2, dash="dash"), opacity=0.8)
        return fig

    unique = gantt_df["pid"].unique().tolist()
    fig = go.Figure()
    for _, row in gantt_df.iterrows():
        is_running = (sim_time is not None and row["start"] <= sim_time < row["end"])
        linew = 3 if is_running else 0
        linec = "white" if is_running else "rgba(0,0,0,0)"
        fig.add_trace(go.Bar(
            x=[row["duration"]],
            y=[row["pid"]],
            base=[row["start"]],
            orientation="h",
            marker=dict(color=cmap[row["pid"]], line=dict(color=linec, width=linew)),
            hovertemplate=f"<b>{row['pid']}</b><br>Start: {row['start']}<br>End: {row['end']}<extra></extra>",
            text=[row["pid"]],
            textposition="inside",
            insidetextanchor="middle",
            cliponaxis=False,
            showlegend=False
        ))
    for pid in unique:
        fig.add_trace(go.Bar(x=[0], y=[pid], marker=dict(color=cmap[pid]), name=pid, showlegend=True))
    fig.update_layout(barmode="stack", height=420, xaxis=dict(title="Time", tick0=0, dtick=1), yaxis=dict(autorange="reversed"), margin=dict(l=80, r=20, t=10, b=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.add_vline(x=sim_time, line=dict(color="white", width=2, dash="dash"), opacity=0.7)
    return fig

def metrics_from_results(results):
    if not results:
        return pd.DataFrame()
    df = pd.DataFrame(results)
    return df

def generate_html_report(df_metrics, fig, summary):
    html = "<html><head><meta charset='utf-8'><title>Simulation Report</title></head><body style='background:#0b0f12;color:#eaf1ff;font-family:Inter, sans-serif;padding:20px;'>"
    html += "<h1>Simulation Report</h1>"
    html += "<h2>Metrics</h2>"
    html += df_metrics.to_html(index=False)
    html += "<h2>Summary</h2>"
    html += pd.DataFrame([summary]).to_html(index=False)
    try:
        img_bytes = fig.to_image(format="png", width=1200, height=480, scale=2)
        b64 = base64.b64encode(img_bytes).decode()
        html += f"<h2>Gantt Chart</h2><img src='data:image/png;base64,{b64}' style='max-width:100%;height:auto;'/>"
    except Exception:
        pass
    html += "</body></html>"
    return html

st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.code === 'Space') {
        const btn = Array.from(document.querySelectorAll('button')).find(b=>b.innerText && (b.innerText.includes('Play') || b.innerText.includes('Pause')));
        if(btn) btn.click();
    }
    if (e.code === 'ArrowRight') {
        const step = Array.from(document.querySelectorAll('button')).find(b=>b.innerText && b.innerText.includes('Step'));
        if(step) step.click();
    }
});
</script>
""", unsafe_allow_html=True)

if st.session_state.run_click:
    st.session_state.run_click = False
    if compare_toggle and compare_algs:
        results_compare = {}
        for a in compare_algs:
            q = q_comp if (a == "Round Robin" and q_comp is not None) else (quantum if a == "Round Robin" else None)
            g, m = run_selected_algorithm(a, process_list, q)
            results_compare[a] = {"gantt": g, "metrics": m}
        st.session_state.compare_results = results_compare
        first_alg = compare_algs[0]
        st.session_state.gantt = results_compare[first_alg]["gantt"]
        st.session_state.metrics = results_compare[first_alg]["metrics"]
    else:
        results_gantt, results_metrics = run_selected_algorithm(algo, process_list, quantum)
        st.session_state.gantt = results_gantt
        st.session_state.metrics = results_metrics
    st.session_state.sim_time = 0.0

if "gantt" in st.session_state:
    gantt_df = prepare_gantt_df(st.session_state.gantt)
    metrics_df = metrics_from_results(st.session_state.metrics)
else:
    gantt_df = pd.DataFrame()
    metrics_df = pd.DataFrame()

with sim_space.container():
    cols = st.columns([1, 0.02, 1])
    left_panel = cols[0]
    right_panel = cols[2]

    with right_panel:
        st.markdown("<div class='sticky-controls'>", unsafe_allow_html=True)
        st.markdown("**Playback (quick)**")
        pcrow = st.columns([0.9,0.9,0.9,1.2])
        if pcrow[0].button("▶ Play", key="play_top"):
            st.session_state.playing = True
        if pcrow[1].button("⏸ Pause", key="pause_top"):
            st.session_state.playing = False
        if pcrow[2].button("⏭ Step", key="step_top"):
            st.session_state.sim_time = min((gantt_df["end"].max() if not gantt_df.empty else 0), st.session_state.sim_time + 0.5)
        with pcrow[3]:
            if st.button("⏮ Reset", key="reset_top"):
                st.session_state.sim_time = 0.0
                st.session_state.playing = False
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("**Performance Metrics**")
        if metrics_df.empty:
            st.write("No metrics yet. Run the simulation.")
        else:
            st.dataframe(metrics_df, height=200)
            avg_waiting = metrics_df['waiting'].mean()
            avg_turnaround = metrics_df['turnaround'].mean()
            avg_response = metrics_df['response'].mean()
            total_time = gantt_df['end'].max() if not gantt_df.empty else 0.0
            throughput = (len(metrics_df) / total_time) if total_time > 0 else None
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Avg Waiting Time", f"{avg_waiting:.2f}")
            s2.metric("Avg Turnaround Time", f"{avg_turnaround:.2f}")
            s3.metric("Avg Response Time", f"{avg_response:.2f}")
            s4.metric("Throughput (proc / time)", f"{throughput:.3f}" if throughput is not None else "N/A")
            summary = {
                "avg_waiting": round(avg_waiting, 4),
                "avg_turnaround": round(avg_turnaround, 4),
                "avg_response": round(avg_response, 4),
                "throughput": round(throughput, 4) if throughput is not None else None,
                "total_time": float(total_time),
                "n_processes": int(len(metrics_df))
            }

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("**Gantt Chart**")
        view_mode = st.radio("View mode", ["Single-line", "Stacked per PID"], index=0, key="view_radio")
        st.session_state.view_mode = view_mode
        if gantt_df.empty:
            st.write("No Gantt to display.")
        else:
            tnow = st.session_state.sim_time if "sim_time" in st.session_state else 0.0
            fig = build_gantt_figure(gantt_df, tnow, view_mode)
            st.plotly_chart(fig, width='stretch')
            unique = gantt_df["pid"].unique().tolist()
            cmap = compact_color_map(unique)
            legend_html = "<div class='legend-grid'>"
            for pid, colr in cmap.items():
                legend_html += f"<div class='legend-item'><div style='width:12px;height:12px;background:{colr};border-radius:3px;'></div><div style='color:#cfd8e3;font-weight:600'>{pid}</div></div>"
            legend_html += "</div>"
            st.markdown(legend_html, unsafe_allow_html=True)

    with left_panel:
        st.markdown("**Controls & Downloads**")
        if st.session_state.playing and not gantt_df.empty:
            max_t = max(gantt_df["end"].max(), 1)
            st.session_state.sim_time = min(max_t, st.session_state.sim_time + 0.25 * st.session_state.speed)
            time.sleep(0.12)
            try:
                st.rerun()
            except Exception:
                try:
                    st.experimental_rerun()
                except Exception:
                    st.info("Please refresh the page to continue.")
        # Downloads & comparisons
        if st.session_state.compare_results:
            compare_summary = []
            for a, res in st.session_state.compare_results.items():
                m = pd.DataFrame(res["metrics"])
                if not m.empty:
                    compare_summary.append({"algorithm": a, "avg_wait": m["waiting"].mean(), "avg_turn": m["turnaround"].mean(), "avg_resp": m["response"].mean()})
            if compare_summary:
                cdf = pd.DataFrame(compare_summary)
                st.markdown("### Comparison summary")
                st.table(cdf)
                figc = px.bar(cdf.melt(id_vars=["algorithm"], value_vars=["avg_wait","avg_turn","avg_resp"], var_name="metric", value_name="value"), x="algorithm", y="value", color="metric", barmode="group", title="Average metrics per algorithm")
                st.plotly_chart(figc, width='stretch')

        if not metrics_df.empty:
            csv = metrics_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV", data=csv, file_name="metrics.csv", mime="text/csv")
            summary_df = pd.DataFrame([summary]) if 'summary' in locals() else pd.DataFrame()
            combined_csv = pd.concat([metrics_df, pd.DataFrame([{}]), summary_df], ignore_index=True).to_csv(index=False)
            st.download_button("⬇ Download CSV (with summary)", data=combined_csv.encode("utf-8"), file_name="metrics_with_summary.csv", mime="text/csv")
        try:
            if not gantt_df.empty:
                img_bytes = fig.to_image(format="png", width=1200, height=480, scale=2)
                st.download_button("⬇ Download Gantt PNG", data=img_bytes, file_name="gantt.png", mime="image/png")
        except Exception:
            st.info("PNG export requires 'kaleido'. Run: python -m pip install kaleido")
        if not metrics_df.empty and not gantt_df.empty:
            html_report = generate_html_report(metrics_df, fig, summary if 'summary' in locals() else {})
            st.download_button("⬇ Download full HTML report", data=html_report, file_name="report.html", mime="text/html")

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
