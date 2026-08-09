import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import heapq

# ---------------------------------------------------------
# University Hostel Stay Registration Queue System
# Performance Modeling and Evaluation
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "Data" / "hostel_registration_dataset.csv"
GRAPH_DIR = BASE_DIR / "Graphs"
GRAPH_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_FILE)

# Convert time columns
for col in ["Arrival_Time", "Registration_Start_Time", "Registration_End_Time"]:
    df[col + "_dt"] = pd.to_datetime(df[col], format="%H:%M")

df["Response_Time_Min"] = df["Waiting_Time_Min"] + df["Service_Time_Min"]

# ---------------------------------------------------------
# 1. BASIC PERFORMANCE METRICS
# ---------------------------------------------------------

total_students = len(df)
avg_wait = df["Waiting_Time_Min"].mean()
max_wait = df["Waiting_Time_Min"].max()
avg_service = df["Service_Time_Min"].mean()
avg_response = df["Response_Time_Min"].mean()
avg_queue = df["Queue_Length"].mean()
max_queue = df["Queue_Length"].max()

arrival_period_min = (
    df["Arrival_Time_dt"].max() - df["Arrival_Time_dt"].min()
).total_seconds() / 60

system_period_min = (
    df["Registration_End_Time_dt"].max() - df["Arrival_Time_dt"].min()
).total_seconds() / 60

arrival_rate = total_students / (arrival_period_min / 60)
throughput = total_students / (system_period_min / 60)
service_rate = 60 / avg_service
number_of_staff = df["Staff_ID"].nunique()
combined_capacity = number_of_staff * service_rate
traffic_intensity = arrival_rate / combined_capacity

print("\n===================================================")
print(" HOSTEL REGISTRATION PERFORMANCE ANALYSIS")
print("===================================================")
print(f"Total Students              : {total_students}")
print(f"Average Waiting Time        : {avg_wait:.2f} minutes")
print(f"Maximum Waiting Time        : {max_wait:.2f} minutes")
print(f"Average Service Time        : {avg_service:.2f} minutes")
print(f"Average Response Time       : {avg_response:.2f} minutes")
print(f"Average Queue Length        : {avg_queue:.2f} students")
print(f"Maximum Queue Length        : {max_queue} students")
print(f"Arrival Rate (lambda)       : {arrival_rate:.2f} students/hour")
print(f"Throughput                  : {throughput:.2f} students/hour")
print(f"Service Rate per Staff (mu) : {service_rate:.2f} students/hour")
print(f"Combined Staff Capacity     : {combined_capacity:.2f} students/hour")
print(f"Traffic Intensity (rho)     : {traffic_intensity:.2f}")

if traffic_intensity > 1:
    print("Finding: Arrival demand is higher than sustainable service capacity.")
else:
    print("Finding: Current service capacity can handle the observed arrival rate.")

# ---------------------------------------------------------
# 2. STAFF RESOURCE UTILIZATION
# ---------------------------------------------------------

staff_busy = df.groupby("Staff_ID")["Service_Time_Min"].sum()
staff_util = (staff_busy / system_period_min) * 100

print("\nSTAFF UTILIZATION")
print("-----------------")
for staff, value in staff_util.items():
    print(f"{staff}: {value:.2f}%")

# ---------------------------------------------------------
# 3. LITTLE'S LAW
# ---------------------------------------------------------

Wq_hours = avg_wait / 60
R_hours = avg_response / 60
Lq = throughput * Wq_hours
L = throughput * R_hours

print("\nLITTLE'S LAW")
print("------------")
print(f"Estimated Lq = X * Wq       : {Lq:.2f} students")
print(f"Observed Average Queue      : {avg_queue:.2f} students")
print(f"Estimated L = X * R         : {L:.2f} students")

# ---------------------------------------------------------
# 4. GRAPH 1 - WAITING TIME
# ---------------------------------------------------------

plt.figure(figsize=(10, 5))
plt.plot(range(1, total_students + 1), df["Waiting_Time_Min"], marker="o", markersize=3)
plt.xlabel("Student Arrival Order")
plt.ylabel("Waiting Time (minutes)")
plt.title("Figure 1: Student Waiting Time")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure1_Waiting_Time.png", dpi=160)
plt.close()

# ---------------------------------------------------------
# 5. GRAPH 2 - QUEUE LENGTH
# ---------------------------------------------------------

plt.figure(figsize=(10, 5))
plt.plot(range(1, total_students + 1), df["Queue_Length"], marker="o", markersize=3)
plt.xlabel("Student Arrival Order")
plt.ylabel("Queue Length (students)")
plt.title("Figure 2: Queue Length During Registration")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure2_Queue_Length.png", dpi=160)
plt.close()

# ---------------------------------------------------------
# 6. GRAPH 3 - THROUGHPUT
# ---------------------------------------------------------

completed = df.copy()
completed["Completion_Hour"] = completed["Registration_End_Time_dt"].dt.floor("h")
hourly_throughput = completed.groupby("Completion_Hour").size()
labels = [t.strftime("%H:%M") for t in hourly_throughput.index]

plt.figure(figsize=(8, 5))
plt.bar(labels, hourly_throughput.values)
plt.xlabel("Completion Hour")
plt.ylabel("Registrations Completed")
plt.title("Figure 3: Registration Throughput")
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure3_Throughput.png", dpi=160)
plt.close()

# ---------------------------------------------------------
# 7. GRAPH 4 - STAFF UTILIZATION
# ---------------------------------------------------------

plt.figure(figsize=(7, 5))
plt.bar(staff_util.index, staff_util.values)
plt.xlabel("Registration Staff")
plt.ylabel("Utilization (%)")
plt.title("Figure 4: Staff Resource Utilization")
plt.ylim(0, max(105, staff_util.max() + 5))
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure4_Staff_Utilization.png", dpi=160)
plt.close()

# ---------------------------------------------------------
# 8. GRAPH 5 - SERVICE TIME BY REGISTRATION TYPE
# ---------------------------------------------------------

service_type = (
    df.groupby("Registration_Type")["Service_Time_Min"]
      .mean()
      .sort_values()
)

plt.figure(figsize=(8, 5))
plt.bar(service_type.index, service_type.values)
plt.xlabel("Registration Type")
plt.ylabel("Average Service Time (minutes)")
plt.title("Figure 5: Service Time by Registration Type")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure5_Service_Time_By_Type.png", dpi=160)
plt.close()

# ---------------------------------------------------------
# 9. GRAPH 6 - DOCUMENT STATUS BOTTLENECK
# ---------------------------------------------------------

document_wait = df.groupby("Document_Status")["Waiting_Time_Min"].mean()

plt.figure(figsize=(7, 5))
plt.bar(document_wait.index, document_wait.values)
plt.xlabel("Document Status")
plt.ylabel("Average Waiting Time (minutes)")
plt.title("Figure 6: Waiting Time by Document Status")
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure6_Document_Status.png", dpi=160)
plt.close()

# ---------------------------------------------------------
# 10. SCALABILITY SIMULATION: 2 STAFF VS 3 STAFF
# ---------------------------------------------------------

# Use the same student arrival times and service times.
# FCFS: each arriving student is assigned to the staff member
# who becomes available first.

first_arrival = df["Arrival_Time_dt"].min()
arrival_minutes = (
    (df["Arrival_Time_dt"] - first_arrival).dt.total_seconds() / 60
).tolist()
service_minutes = df["Service_Time_Min"].tolist()

def simulate_servers(server_count):
    available = [(0.0, server) for server in range(server_count)]
    heapq.heapify(available)

    waits = []
    responses = []
    finish_times = []

    for arrival, service in zip(arrival_minutes, service_minutes):
        free_time, server = heapq.heappop(available)
        start = max(arrival, free_time)
        wait = start - arrival
        finish = start + service

        waits.append(wait)
        responses.append(wait + service)
        finish_times.append(finish)

        heapq.heappush(available, (finish, server))

    return {
        "Staff": server_count,
        "Avg_Wait": sum(waits) / len(waits),
        "Max_Wait": max(waits),
        "Avg_Response": sum(responses) / len(responses),
        "Finish_Time": max(finish_times)
    }

scenario_2 = simulate_servers(2)
scenario_3 = simulate_servers(3)

scenario_df = pd.DataFrame([scenario_2, scenario_3])

print("\nSCALABILITY COMPARISON")
print("----------------------")
print(scenario_df.round(2).to_string(index=False))

plt.figure(figsize=(7, 5))
plt.bar(
    [f"{int(x)} Staff" for x in scenario_df["Staff"]],
    scenario_df["Avg_Wait"]
)
plt.xlabel("System Configuration")
plt.ylabel("Average Waiting Time (minutes)")
plt.title("Figure 7: Scalability - 2 Staff vs 3 Staff")
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure7_Scalability_2_vs_3_Staff.png", dpi=160)
plt.close()

scenario_df.round(2).to_csv(
    GRAPH_DIR / "Scalability_Results.csv",
    index=False
)

# ---------------------------------------------------------
# 11. SYSTEM MODEL DIAGRAM
# ---------------------------------------------------------

plt.figure(figsize=(11, 4))
plt.text(0.08, 0.5, "Student\nArrival", ha="center", va="center", fontsize=11)
plt.text(0.28, 0.5, "Waiting\nQueue", ha="center", va="center", fontsize=11)
plt.text(0.52, 0.65, "ST01\nRegistration Officer", ha="center", va="center", fontsize=10)
plt.text(0.52, 0.35, "ST02\nRegistration Officer", ha="center", va="center", fontsize=10)
plt.text(0.75, 0.5, "Document Check\n& Room Allocation", ha="center", va="center", fontsize=10)
plt.text(0.94, 0.5, "Registration\nCompleted", ha="center", va="center", fontsize=10)

plt.arrow(0.13, 0.5, 0.09, 0, head_width=0.025, length_includes_head=True)
plt.arrow(0.34, 0.52, 0.11, 0.10, head_width=0.025, length_includes_head=True)
plt.arrow(0.34, 0.48, 0.11, -0.10, head_width=0.025, length_includes_head=True)
plt.arrow(0.59, 0.62, 0.09, -0.09, head_width=0.025, length_includes_head=True)
plt.arrow(0.59, 0.38, 0.09, 0.09, head_width=0.025, length_includes_head=True)
plt.arrow(0.83, 0.5, 0.06, 0, head_width=0.025, length_includes_head=True)

plt.axis("off")
plt.title("Figure 8: University Hostel Registration Queue System Model")
plt.tight_layout()
plt.savefig(GRAPH_DIR / "Figure8_System_Model.png", dpi=160)
plt.close()

print("\n8 figures/results generated successfully in the Graphs folder.")
