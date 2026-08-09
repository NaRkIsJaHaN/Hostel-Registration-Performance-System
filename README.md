# University Hostel Stay Registration Queue System

## Project Overview
This project models and evaluates the performance of a university hostel stay registration queue system using a simulated dataset of 50 student registrations.

## Performance Areas
- Waiting time / latency
- Queue length
- Throughput
- Staff resource utilization
- Registration service time
- Bottleneck identification
- Scalability (2 staff vs 3 staff)
- Little's Law validation

## Project Structure
- `Data/hostel_registration_dataset.csv` - 50-row dataset
- `Code/hostel_performance.py` - performance analysis and simulation
- `Graphs/` - generated charts and scenario results

## How to Run
1. Install Python 3.
2. Install dependencies:

```bash
pip install pandas matplotlib
```

3. Open a terminal in the `Code` folder.
4. Run:

```bash
python hostel_performance.py
```

The script prints the main performance metrics and generates the graphs automatically.

## System Model
Student Arrival -> Waiting Queue -> ST01/ST02 -> Document Check & Room Allocation -> Registration Completed
