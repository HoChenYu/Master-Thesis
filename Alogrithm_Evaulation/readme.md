# Algorithm Parameters and Input File Format

This repository contains multiple algorithms that work with different hardware resources like DRAM and PMEM. Below are the parameters used in the algorithms and their meanings. Additionally, an example input file format is provided.

## Algorithm Parameters

The following parameters are used in the algorithm Python scripts:

- **`strip_width_dram = 8`**  
  Represents the **DRAM size** in the system. This value determines how much DRAM is allocated for the task processing.

- **`strip_width_pmem = 1000`**  
  Represents the **PMEM size** in the system. This value determines how much Persistent Memory (PMEM) is available for the task processing.

- **`m_value = 8`**  
  Represents the **number of cores** in the system. This value specifies how many processing cores are available to handle tasks.

- **`file_path = "random100rect.txt"`**  
  Represents the **task set** file. The file contains information about the tasks to be scheduled, including memory requirements and execution times on both DRAM and PMEM.

## Input File Format

The input file (e.g., `random100rect.txt`) contains data about the tasks in the following format:

### Example: `random100rect.txt`
![image](https://github.com/user-attachments/assets/37b13eca-f8fa-4793-9201-21ff857c499a)

### Format Explanation:
- The first line contains the number of tasks (e.g., `10`).
- Each subsequent line represents a task, with the following values:
  - **Task ID**: A unique identifier for the task (e.g., `L1`, `L2`, etc.).
  - **DRAM Memory Size**: The amount of memory required by the task on DRAM (e.g., `30.17`).
  - **DRAM Execution Time**: The amount of time required to execute the task on DRAM (e.g., `6.37`).
  - **PMEM Memory Size**: The amount of memory required by the task on PMEM (e.g., `30.17`).
  - **PMEM Execution Time**: The amount of time required to execute the task on PMEM (e.g., `81.79`).

### Example Breakdown:  
L1 30.17 6.37 30.17 81.79


- **Task L1** requires **30.17 units** of DRAM memory, takes **6.37 units** of time to execute on DRAM, requires **30.17 units** of PMEM memory, and takes **81.79 units** of time to execute on PMEM.

## How to Change Parameters

To modify the system configuration or task set, you can adjust the following parameters:

1. **`strip_width_dram`**: Change the size of DRAM. Increasing this value allows more memory for tasks on DRAM.
2. **`strip_width_pmem`**: Change the size of PMEM. Increasing this value allows more memory for tasks on PMEM.
3. **`m_value`**: Adjust the number of available cores for task execution.
4. **`file_path`**: Update the path to the task set file if you want to use a different set of tasks.

To modify the task set, simply update the corresponding values in the input file (`random100rect.txt`) following the format described above.

## Algorithm Descriptions

### 1. **Container-based Heterogeneous Resources Scheduling (CHRS)**

This is the proposed solution of this work, where **Algorithm 3** balances the loading on heterogeneous memory (DRAM and PMEM). It uses **Algorithm 1** and **Algorithm 2** for task packing on DRAM, aiming to minimize the overall Makespan.

The key idea behind **CHRS** is to allocate tasks optimally between DRAM and PMEM by balancing memory usage and execution time across both memory types. It also leverages task packing algorithms to minimize the Makespan.

### 2. **First-Fit Decreasing Height (FFDH)**

**FFDH** sorts all tasks in a **non-increasing** order of their execution time on DRAM (height), then packs tasks one by one. 

- **Modified FFDH**: In this version, the algorithm is aware of both the DRAM size and the number of cores available. Tasks are packed using the **first-fit fashion**.
- If there is no feasible level (i.e., no available space) to accommodate a new task, a **new level** is created for the task.

### 3. **Best-Fit Decreasing Height (BFDH)**

The behavior of **BFDH** is similar to **FFDH**, but instead of packing tasks into the first available level, **BFDH** selects the level with the **minimum remaining DRAM space** that can accommodate the new task.

- This approach tries to pack tasks more efficiently by filling up the levels with the smallest remaining space first.

### 4. **Fixed-Level Random**

This algorithm randomly selects a task and attempts to pack it into available levels. The levels are checked in order:

- The task is assigned to the first level that has enough **remaining DRAM space** and **cores**.
- Additionally, the **height** of the task must not exceed the height of the level.
- If no level is available, a **new level** is created to accommodate the task, and the level height is set equal to the task height.

### 5. **Flexible-Level Random**

Similar to **Fixed-Level Random**, **Flexible-Level Random** allows for a more flexible packing strategy:

- Even if the height of the task exceeds the height of the existing level, the task can still be placed in the level.
- In this case, the **ceiling of the level is extended** to accommodate both the task and the level.

This flexibility helps in better utilization of memory and cores, especially when a task is slightly larger than the level.

## Conclusion

By adjusting the parameters and modifying the input file, you can simulate different configurations for your tasks and resources. This flexibility allows testing various scheduling strategies under different hardware setups.

