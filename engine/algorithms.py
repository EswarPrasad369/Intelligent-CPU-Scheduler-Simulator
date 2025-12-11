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
