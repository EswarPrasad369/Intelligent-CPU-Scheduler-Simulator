import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from engine.algorithms import (
    fcfs,
    sjf_non_preemptive,
    srtf,
    round_robin,
    priority_non_preemptive,
    priority_preemptive
)

st.title("🧠 Intelligent CPU Scheduler Simulator")

num = st.number_input("Number of Processes", min_value=1, max_value=20, value=3)

process_list = []

for i in range(num):
    st.markdown(f"### Process P{i+1}")
    arrival = st.number_input(f"Arrival Time of P{i+1}", min_value=0, value=0)
    burst = st.number_input(f"Burst Time of P{i+1}", min_value=1, value=1)
    priority = st.number_input(f"Priority of P{i+1}", min_value=1, value=1)

    process_list.append({
        "pid": f"P{i+1}",
        "arrival": arrival,
        "burst": burst,
        "priority": priority
    })

algo = st.selectbox(
    "Choose Scheduling Algorithm",
    [
        "FCFS",
        "SJF (Non-Preemptive)",
        "SRTF (Preemptive SJF)",
        "Round Robin",
        "Priority (Non-Preemptive)",
        "Priority (Preemptive)"
    ]
)

quantum = None
if algo == "Round Robin":
    quantum = st.number_input("Enter Time Quantum", min_value=1, value=2)

if st.button("Run Simulation"):

    if algo == "FCFS":
        gantt, results = fcfs(process_list)
    elif algo == "SJF (Non-Preemptive)":
        gantt, results = sjf_non_preemptive(process_list)
    elif algo == "SRTF (Preemptive SJF)":
        gantt, results = srtf(process_list)
    elif algo == "Round Robin":
        gantt, results = round_robin(process_list, quantum)
    elif algo == "Priority (Non-Preemptive)":
        gantt, results = priority_non_preemptive(process_list)
    elif algo == "Priority (Preemptive)":
        gantt, results = priority_preemptive(process_list)

    st.subheader("Performance Metrics")
    df = pd.DataFrame(results)
    st.dataframe(df)

    st.subheader("Gantt Chart")
    gantt_df = pd.DataFrame(gantt)

    # if gantt is empty, show message
    if gantt_df.empty:
        st.write("No Gantt data to display.")
    else:
        # ensure numeric types
        gantt_df["start"] = gantt_df["start"].astype(float)
        gantt_df["end"] = gantt_df["end"].astype(float)
        gantt_df["duration"] = gantt_df["end"] - gantt_df["start"]

        # preserve order (optional: sort or reverse if you'd like different vertical order)
        gantt_df = gantt_df.reset_index(drop=True)

        unique_pids = gantt_df["pid"].unique().tolist()
        palette = px.colors.qualitative.Plotly
        color_map = {pid: palette[i % len(palette)] for i, pid in enumerate(unique_pids)}

        fig = go.Figure()

        for idx, row in gantt_df.iterrows():
            fig.add_trace(go.Bar(
                x=[row["duration"]],
                y=[row["pid"]],
                base=[row["start"]],
                orientation="h",
                marker=dict(color=color_map[row["pid"]]),
                hovertemplate=(
                    "PID: %{y}<br>"
                    "Start: %{base}<br>"
                    "End: %{x}+%{base}<br>"
                    "Duration: %{x}<extra></extra>"
                ),
                showlegend=False
            ))

        # add legend traces (one per pid)
        for pid in unique_pids:
            fig.add_trace(go.Bar(x=[0], y=[pid], marker=dict(color=color_map[pid]), name=pid, showlegend=True))

        fig.update_layout(
            barmode="stack",
            xaxis=dict(title="Time", range=[0, max(gantt_df["end"].max(), 1)], tick0=0, dtick=1),
            yaxis=dict(title="pid", autorange="reversed"),
            height=400,
            margin=dict(l=80, r=40, t=20, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)
