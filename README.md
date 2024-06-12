# Comparative Analysis of User-Level and Kernel-Level Scheduling

## Overview
This repository contains the source code and final project report for the comparative analysis of user-level and kernel-level scheduling algorithms. The project evaluates various scheduling algorithms, including Linux’s Completely Fair Scheduler (CFS), custom user-level scheduling, and round-robin scheduling, by analyzing key performance metrics such as throughput, turnaround time, waiting time, CPU utilization, task duration, and total execution time.

## Files
- **Final_Project_Report.pdf**: Detailed report on the comparative analysis of user-level and kernel-level scheduling algorithms.
- **kernelLevel.py**: Implementation of kernel-level scheduling algorithms.
- **userLevel.py**: Implementation of user-level scheduling algorithms.

## Abstract
Efficient CPU scheduling is crucial for optimizing system performance and ensuring fair resource distribution across tasks. This project compares and evaluates various scheduling algorithms, including Linux’s Completely Fair Scheduler (CFS), custom user-level scheduling, and round-robin scheduling. By analyzing key performance metrics such as throughput, turnaround time, waiting time, CPU utilization, task duration, and total execution time, the study reveals the strengths and limitations of each algorithm.

## Key Findings
- **Linux Completely Fair Scheduler (CFS)**: Outperforms other approaches by delivering robust, fair, and dynamic scheduling for general-purpose workloads. It maintains high throughput while minimizing waiting times and ensuring equitable CPU allocation.
- **Custom User-Level Scheduling**: Excels in specialized applications by offering superior performance through prioritization. However, its inherent overhead and frequent context switching limit efficiency.
- **Round-Robin Scheduling**: Provides predictable and equitable CPU time distribution but may struggle in environments with heterogeneous workloads due to its lack of adaptability.

## Methodology
The evaluation environment includes scripts simulating:
- User-Level Preemptive Round-Robin Scheduling
- Linux CFS (Completely Fair Scheduler)
- Monotonous Linear Execution

Tasks executed under each scheduling method cover various computing scenarios, such as I/O-bound tasks, computation-intensive tasks, embarrassingly parallel tasks, and general data processing tasks.

## Performance Metrics
- **Execution Time**
- **System Responsiveness**
- **CPU Utilization**
- **Throughput**
- **Turnaround Time**

## Conclusion
The findings emphasize the need for careful selection of scheduling algorithms based on specific application requirements. In practical applications, a customizable approach like user-level scheduling is ideal for specialized tasks, while CFS remains a robust default option for most workloads. Efficient scheduling plays a pivotal role in optimizing system performance and ensuring that critical tasks receive the necessary resources to run effectively.

## How to Run
1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
2. Ensure you have Python installed on your system.
3. Run the scripts:
    ```sh
    python kernelLevel.py
    python userLevel.py
    ```

## Authors
- Nitin Gopala Krishna Sontineni (Stony Brook University) - nitinGopalaKr.Sontineni@stonybrook.edu
- Sankeerthana Kodumuru (Stony Brook University) - Sankeerthana.Kodumuru@stonybrook.edu

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.