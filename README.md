# Heterogeneous Resource Allocation Algorithms for Containers with DRAM and Persistent Memory

[![Thesis Download](https://img.shields.io/badge/Thesis-Link-blue)](https://thesis.lib.cgu.edu.tw/thesis/detail/8c690681238af8f2441d3ee285ab9604/)

## 📚 Overview

This repository contains code, benchmarks, and experimental data for the Master's thesis:

**"Heterogeneous Resource Allocation Algorithms for Containers with DRAM and Persistent Memory"**  
by Chen Yu Ho, Chang Gung University

The thesis proposes novel scheduling and allocation algorithms that balance **CPU**, **DRAM**, and **persistent memory (Intel Optane DC PMEM)** resources to optimize task execution performance for containerized workloads.

## 🧠 Abstract

To support multimedia and deep learning applications running on containers within a server, not only computing units but also main memory are critical resources for performance tuning.

In this work, we leverage both **DRAM** (for low-latency memory access) and **persistent memory** (for high-capacity memory needs) to build a **heterogeneous memory system**. The problem is modeled as a **2D strip packing problem**, jointly considering CPU and memory allocation. Our scheduling algorithms aim to:

- Reduce Makespan (total task completion time)
- Increase parallelism
- Balance DRAM and persistent memory usage

### 🔬 Key Results

- Achieved **≥18.34% Makespan reduction** compared to baseline methods
- Evaluated on a system with:
  - **512 GB PMEM**
  - **32 GB DRAM**
  - **8 CPU cores**
  - **100 containerized tasks**

## 🚀 Features

- 2D strip packing algorithm for heterogeneous memory scheduling
- Container task modeling and benchmark generation
- Resource-aware scheduling simulator
- Experimental scripts and data visualization tools

## 🛠️ Technologies

- C/C++
- Python (for data visualization & benchmarking)
- Linux shell scripts
- Container tools (Docker or container simulation)

## 📁 Directory Structure

```bash
.
├── src/                   # Core scheduling algorithm 
├── benchmarks/            # Benchmark programs and task generators
├── Algorithm_Evaluation/  # Scripts for running and evaluating experiments
├── results/               # Experimental result data and graphs
├── README.md              # This file
