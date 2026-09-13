# Intelligent-CPU-Scheduler-Simulator
# Intelligent CPU Scheduler Simulator

An interactive CPU scheduling simulator built with Python and Streamlit. The application allows users to simulate and visualize different CPU scheduling algorithms, analyze scheduling performance, compare algorithms, and export simulation results.

## Overview

The **Intelligent CPU Scheduler Simulator** is designed to provide an interactive way to understand and analyze CPU scheduling algorithms.

Users can define processes with their arrival time, burst time, and priority, select a scheduling algorithm, run the simulation, and visualize the execution using Gantt charts and performance metrics.

The simulator supports both **preemptive and non-preemptive scheduling algorithms** and provides an algorithm comparison mode for evaluating different scheduling strategies.

## Features

* Interactive process configuration
* Support for six CPU scheduling algorithms
* Preemptive and non-preemptive scheduling
* Interactive Gantt chart visualization
* Algorithm comparison mode
* Performance metric calculation
* Simulation playback controls
* Preset process scenarios
* Save and load process scenarios using JSON
* Export scheduling metrics as CSV
* Export Gantt charts as PNG
* Generate HTML simulation reports
* Responsive Streamlit-based interface

## Scheduling Algorithms

The simulator implements the following algorithms:

### 1. First Come First Serve (FCFS)

Processes are scheduled according to their arrival order.

### 2. Shortest Job First (SJF)

A non-preemptive scheduling algorithm that selects the available process with the shortest burst time.

### 3. Shortest Remaining Time First (SRTF)

A preemptive version of SJF that dynamically selects the process with the smallest remaining execution time.

### 4. Round Robin

A preemptive scheduling algorithm that assigns each process a fixed time quantum and cycles through the ready queue.

### 5. Priority Scheduling — Non-Preemptive

Selects the available process with the highest priority and executes it until completion.

### 6. Priority Scheduling — Preemptive

Allows a newly available higher-priority process to interrupt the currently running process.

## Performance Metrics

For each simulation, the application calculates:

* Completion Time
* Turnaround Time
* Waiting Time
* Response Time
* Average Waiting Time
* Average Turnaround Time
* Average Response Time
* Throughput

These metrics can be used to analyze and compare the efficiency of different scheduling algorithms.

## Visualization

The simulator provides interactive Gantt charts using Plotly.

Two visualization modes are available:

* **Single-line** — displays the complete CPU execution timeline on a single row.
* **Stacked per PID** — separates process execution into individual rows.

The simulation also provides playback controls:

* ▶ Play
* ⏸ Pause
* ⏭ Step
* ⏮ Reset

This allows users to observe the scheduling process progressively.

## Algorithm Comparison

The simulator includes a comparison mode that allows multiple scheduling algorithms to be selected and evaluated using the same process set.

The comparison provides performance information such as:

* Average waiting time
* Average turnaround time
* Average response time

This makes it easier to observe how different scheduling strategies behave under the same workload.

## Scenario Management

The application provides preset scenarios for quickly testing the scheduler.

Users can also create custom process sets using parameters such as:

* Process ID
* Arrival Time
* Burst Time
* Priority
* Time Quantum for Round Robin

Custom scenarios can be downloaded as JSON files and loaded back into the simulator later.

## Export Options

Simulation results can be exported in multiple formats:

* **CSV** — scheduling metrics
* **CSV with Summary** — metrics together with overall performance information
* **PNG** — Gantt chart visualization
* **HTML** — complete simulation report containing metrics, summary information, and the Gantt chart

## Tech Stack

* **Python**
* **Streamlit** — interactive web application
* **Pandas** — data handling and analysis
* **Plotly** — interactive visualization

## Project Structure

```text
Intelligent-CPU-Scheduler-Simulator/
│
├── analytics/
│   ├── __init__.py
│   └── metrics.py
│
├── engine/
│   ├── __init__.py
│   └── algorithms.py
│
├── ui/
│   ├── __init__.py
│   └── app.py
│
├── main.py
├── requirements.txt
├── LICENSE
└── README.md
```

### `engine/`

Contains the implementation of the CPU scheduling algorithms.

### `ui/`

Contains the Streamlit interface, visualization, simulation controls, scenario management, comparison functionality, and export options.

### `analytics/`

Contains the analytics module prepared for metric-related functionality.

## Installation

Clone the repository:

```bash
git clone https://github.com/EswarPrasad369/Intelligent-CPU-Scheduler-Simulator.git
```

Navigate to the project directory:

```bash
cd Intelligent-CPU-Scheduler-Simulator
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit application with:

```bash
streamlit run ui/app.py
```

The application will open in your browser.

## Requirements

The main dependencies are:

```text
streamlit
pandas
plotly
```

For PNG export functionality, Plotly's image export requires the `kaleido` package.

Install it using:

```bash
pip install kaleido
```

## License

This project is licensed under the MIT License.
