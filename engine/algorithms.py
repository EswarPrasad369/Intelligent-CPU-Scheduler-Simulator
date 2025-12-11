def fcfs(process_list):
    processes = sorted(process_list, key=lambda x: x['arrival'])
    current_time = 0
    gantt_chart = []
    results = []

    for p in processes:
        start_time = max(current_time, p['arrival'])
        end_time = start_time + p['burst']

        gantt_chart.append({
            "pid": p["pid"],
            "start": start_time,
            "end": end_time
        })

        completion_time = end_time
        turnaround_time = completion_time - p['arrival']
        waiting_time = turnaround_time - p['burst']
        response_time = start_time - p['arrival']

        results.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "start": start_time,
            "completion": completion_time,
            "turnaround": turnaround_time,
            "waiting": waiting_time,
            "response": response_time
        })

        current_time = end_time

    return gantt_chart, results





def sjf_non_preemptive(process_list):
    processes = sorted(process_list, key=lambda x: x['arrival'])
    time = 0
    completed = []
    gantt_chart = []

    while len(completed) < len(processes):
        available = [p for p in processes if p['arrival'] <= time and p not in completed]
        if not available:
            time += 1
            continue

        current = min(available, key=lambda x: x['burst'])
        start_time = time
        end_time = time + current['burst']

        gantt_chart.append({
            "pid": current['pid'],
            "start": start_time,
            "end": end_time
        })

        current['completion'] = end_time
        current['turnaround'] = end_time - current['arrival']
        current['waiting'] = current['turnaround'] - current['burst']
        current['response'] = start_time - current['arrival']

        completed.append(current)
        time = end_time

    results = []
    for p in completed:
        results.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "completion": p["completion"],
            "turnaround": p["turnaround"],
            "waiting": p["waiting"],
            "response": p["response"],
        })

    return gantt_chart, results
 


 def srtf(process_list):
    processes = [
        {"pid": p["pid"], "arrival": p["arrival"], "burst": p["burst"], "remaining": p["burst"]}
        for p in process_list
    ]

    time = 0
    completed = 0
    n = len(processes)
    gantt_chart = []
    last_pid = None

    while completed < n:
        available = [p for p in processes if p["arrival"] <= time and p["remaining"] > 0]

        if not available:
            time += 1
            continue

        current = min(available, key=lambda x: x["remaining"])

        if current["pid"] != last_pid:
            gantt_chart.append({"pid": current["pid"], "start": time})
            last_pid = current["pid"]

        current["remaining"] -= 1
        time += 1
        gantt_chart[-1]["end"] = time

        if current["remaining"] == 0:
            current["completion"] = time
            current["turnaround"] = current["completion"] - current["arrival"]
            current["waiting"] = current["turnaround"] - current["burst"]
            current["response"] = gantt_chart[-1]["start"] - current["arrival"]
            completed += 1

    results = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "burst": p["burst"],
        "completion": p["completion"],
        "turnaround": p["turnaround"],
        "waiting": p["waiting"],
        "response": p["response"]
    } for p in processes]

    return gantt_chart, results
 