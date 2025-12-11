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
 



from collections import deque

def round_robin(process_list, quantum):
    processes = [
        {"pid": p["pid"], "arrival": p["arrival"], "burst": p["burst"], "remaining": p["burst"]}
        for p in process_list
    ]

    processes.sort(key=lambda x: x["arrival"])

    time = 0
    queue = deque()
    gantt_chart = []
    completed_count = 0
    n = len(processes)
    last_pid = None
    i = 0
    response_time = {p["pid"]: None for p in processes}

    while completed_count < n:
        while i < n and processes[i]["arrival"] <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time += 1
            continue

        current = queue.popleft()

        if response_time[current["pid"]] is None:
            response_time[current["pid"]] = time - current["arrival"]

        if current["pid"] != last_pid:
            gantt_chart.append({"pid": current["pid"], "start": time})
            last_pid = current["pid"]

        exec_time = min(quantum, current["remaining"])
        current["remaining"] -= exec_time
        time += exec_time

        gantt_chart[-1]["end"] = time

        while i < n and processes[i]["arrival"] <= time:
            queue.append(processes[i])
            i += 1

        if current["remaining"] == 0:
            current["completion"] = time
            current["turnaround"] = current["completion"] - current["arrival"]
            current["waiting"] = current["turnaround"] - current["burst"]
            current["response"] = response_time[current["pid"]]
            completed_count += 1
        else:
            queue.append(current)

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




def priority_non_preemptive(process_list):
    processes = sorted(process_list, key=lambda x: x["arrival"])
    completed = []
    gantt_chart = []
    time = 0
    n = len(processes)

    while len(completed) < n:
        available = [p for p in processes if p["arrival"] <= time and p not in completed]

        if not available:
            time += 1
            continue

        current = min(available, key=lambda x: x["priority"])
        start = time
        end = time + current["burst"]

        gantt_chart.append({"pid": current["pid"], "start": start, "end": end})

        current["completion"] = end
        current["turnaround"] = end - current["arrival"]
        current["waiting"] = current["turnaround"] - current["burst"]
        current["response"] = start - current["arrival"]

        completed.append(current)
        time = end

    results = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "burst": p["burst"],
        "priority": p["priority"],
        "completion": p["completion"],
        "turnaround": p["turnaround"],
        "waiting": p["waiting"],
        "response": p["response"]
    } for p in completed]

    return gantt_chart, results




def priority_preemptive(process_list):
    processes = [
        {"pid": p["pid"], "arrival": p["arrival"], "burst": p["burst"],
         "priority": p["priority"], "remaining": p["burst"]}
        for p in process_list
    ]

    time = 0
    completed = 0
    n = len(processes)
    gantt_chart = []
    last_pid = None
    response = {p["pid"]: None for p in processes}

    while completed < n:
        available = [p for p in processes if p["arrival"] <= time and p["remaining"] > 0]

        if not available:
            time += 1
            continue

        current = min(available, key=lambda x: x["priority"])

        if current["pid"] != last_pid:
            gantt_chart.append({"pid": current["pid"], "start": time})
            last_pid = current["pid"]

        if response[current["pid"]] is None:
            response[current["pid"]] = time - current["arrival"]

        current["remaining"] -= 1
        time += 1
        gantt_chart[-1]["end"] = time

        if current["remaining"] == 0:
            current["completion"] = time
            current["turnaround"] = time - current["arrival"]
            current["waiting"] = current["turnaround"] - current["burst"]
            current["response"] = response[current["pid"]]
            completed += 1

    results = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "burst": p["burst"],
        "priority": p["priority"],
        "completion": p["completion"],
        "turnaround": p["turnaround"],
        "waiting": p["waiting"],
        "response": p["response"]
    } for p in processes]

    return gantt_chart, results



