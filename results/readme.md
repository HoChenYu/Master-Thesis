# results

This directory contains the Python scripts that process data and generate plots for the thesis "Heterogeneous Resource Allocation Algorithms for Containers with DRAM and Persistent Memory". Each Python script reads an Excel file with specific data, performs computations, and outputs a PNG plot file. Below are the details for each script and their I/O operations.

## 📝 Scripts Overview

### `fig0.py`
- **Input**: `fig0.xlsx` (Excel file)
  - The Excel file contains data related to the DRAM size, ranging from 4GB to 256GB.
- **Output**: `fig0.png`
  - A plot showing the results for varying DRAM sizes.
![fig0](https://github.com/user-attachments/assets/f7df5917-a66c-4d2f-a5d3-feda4d1a9a2b)

### `fig1.py`
- **Input**: `fig1.xlsx` (Excel file)
  - The Excel file contains data related to the number of rectangles ranging from 10 to 100.
- **Output**: `fig1.png`
  - A plot showing the results for rectangle quantities.
![fig1](https://github.com/user-attachments/assets/19f135ec-4063-4a20-aeb6-fc97dcee74b0)

### `fig3.py`
- **Input**: `fig3.xlsx` (Excel file)
  - The Excel file contains data related to the number of CPU cores ranging from 1 to 15.
- **Output**: `fig3.png`
  - A plot showing the results for varying core counts.
![fig3](https://github.com/user-attachments/assets/7423b7df-166a-4db5-9a4f-884531ba1b44)

### `fig5.py`
- **Input**: `fig5.xlsx` (Excel file)
  - The Excel file contains data on task lengths and widths ranging from 4 to 32.
- **Output**: `fig5.png`
  - A plot showing the results for varying task dimensions.
![fig5](https://github.com/user-attachments/assets/bc65e3fd-507b-4ea8-9a48-dc9788ff59df)

---

## 📁 Directory Structure

```bash
src/
├── fig0.py          # Script to process `fig0.xlsx` and output `fig0.png`
├── fig1.py          # Script to process `fig1.xlsx` and output `fig1.png`
├── fig3.py          # Script to process `fig3.xlsx` and output `fig3.png`
└── fig5.py          # Script to process `fig5.xlsx` and output `fig5.png`
