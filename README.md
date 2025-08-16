# 🚚 TC_PDWTW: Pickup and Delivery Problem with Time Windows Solver

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)](https://github.com/cauchy1988/TC_PDWTW)

> **Implementation of Two-Stage Algorithm with Adaptive Large Neighborhood Search for PDPTW**

## 📖 Overview

**TC_PDWTW** is a research implementation of the **Two-Stage Algorithm** for solving the **Pickup and Delivery Problem with Time Windows (PDPTW)**. This project implements:

- **Stage 1**: Minimize the number of vehicles required
- **Stage 2**: Optimize the solution using Adaptive Large Neighborhood Search (ALNS)

## 🏗️ Architecture

```
TC_PDWTW/
├── 📁 src/                    # Core implementation
│   ├──  alns.py            # Adaptive Large Neighborhood Search
│   ├──  two_stage.py       # Two-stage algorithm
│   ├── 🛣️ solution.py        # Solution representation
│   ├── ⚙️ meta.py            # Problem metadata
│   ├── 🛣️ path.py            # Path optimization
│   ├──  insertion.py       # Insertion operators
│   ├── 🗑️ removal.py         # Removal operators
│   ├──  vehicle.py         # Vehicle management
│   ├──  request.py         # Request handling
│   ├── 🎛️ parameters.py      # Algorithm parameters
│   └── 📊 benchmark_reader_for_lim_dataset.py  # Data reader
├── 📁 examples/               # Usage examples
├── 📁 benchmark/              # Test datasets
└── 📁 papers/                 # Research papers
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Running the Core Example

```bash
# Run the two-stage algorithm example
python examples/two_stage_algorithms_for_lim_data_set_example.py
```

This example demonstrates:
1. **Data Loading**: Reads Li & Lim benchmark dataset
2. **Stage 1**: Minimizes vehicle count using ALNS
3. **Stage 2**: Optimizes solution quality using ALNS

## 🔧 Core Components

### Two-Stage Algorithm (`src/two_stage.py`)
- **Stage 1**: `first_stage_to_limit_vehicle_num_in_homogeneous_fleet()`
- **Stage 2**: `two_stage_algorithm_in_homogeneous_fleet()`

### ALNS Implementation (`src/alns.py`)
- **Destroy Operators**: Shaw removal, random removal, worst removal
- **Repair Operators**: Basic greedy insertion, regret-k insertion
- **Adaptive Weighting**: Operator performance-based weight updates
- **Simulated Annealing**: Temperature-based acceptance criteria

### Solution Management (`src/solution.py`)
- **PDWTWSolution**: Complete solution representation
- **Path Management**: Individual vehicle routes
- **Request Assignment**: Pickup-delivery pair handling

##  Benchmark Datasets

The project supports Li & Lim benchmark datasets:
- **LR1_2_1.txt**: 50 vehicles, 105 requests
- **lr202.txt**: 50 vehicles, 200 requests  
- **lr204.txt**: 50 vehicles, 400 requests

##  Testing

```bash
# Run tests (if available)
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **Original Research**: "An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows"
- **Academic Community**: Operations Research and Optimization Research Community

## 📞 Contact

- **Project Maintainer**: [cauchy1988](https://github.com/cauchy1988)
- **Project Homepage**: [https://github.com/cauchy1988/TC_PDWTW](https://github.com/cauchy1988/TC_PDWTW)

---

<div align="center">

**⭐ Star this repository if you find it useful! ⭐**

*Built with ❤️ for the optimization research community*

</div>
