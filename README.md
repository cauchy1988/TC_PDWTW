# 🚚 TC_PDWTW: Advanced Large Neighborhood Search Framework

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)](https://github.com/cauchy1988/TC_PDWTW)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A+-brightgreen.svg)](https://github.com/cauchy1988/TC_PDWTW)

> **Research Implementation of Large Neighborhood Search for Pickup and Delivery Problems with Time Windows**

## 📖 Overview

**TC_PDWTW** is a research implementation of the classical operations research paper **"An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows"**. This project aims to provide a **generic, extensible, and highly configurable Large Neighborhood Search (LNS) framework** that makes ALNS a special case. 

**⚠️ Note: This is a work in progress. The core framework is implemented, but dataset reading, benchmarking, and comprehensive testing are still under development.**

### 🎯 Current Features (Implemented)

- **🔧 Generic LNS Framework**: Modular architecture supporting any LNS variant
- **⚡ Adaptive Large Neighborhood Search**: Full ALNS implementation with configurable operators
- **🎛️ Advanced Parameter Tuning**: Intelligent parameter optimization with multiple strategies
- **🔄 Multiple Acceptance Strategies**: Simulated Annealing, Probabilistic, Better-Only, and Always-Accept
- **📊 Performance Monitoring**: Basic tracking and analysis capabilities
- **🧪 Core Testing**: Unit tests for framework components
- **📚 Documentation**: Framework guides and examples
- **🔄 Backward Compatibility**: Seamless migration from existing ALNS implementations

### 🚧 Work in Progress

- **📊 Dataset Reading**: Support for various benchmark datasets (Solomon, Cordeau, etc.)
- **🏆 Benchmarking**: Comprehensive performance evaluation against standard test instances
- **🧪 Integration Testing**: End-to-end testing with real-world scenarios
- **📈 Performance Analysis**: Advanced analytics and visualization tools
- **🌐 Web Interface**: Optional web-based configuration and monitoring

## 🏗️ Architecture

```
TC_PDWTW/
├── 📁 src/                    # Core framework implementation
│   ├── 🎯 lns_framework.py    # Generic LNS framework
│   ├── 🔄 alns_compatibility.py # Backward compatibility layer
│   ├── ⚙️ parameters.py       # Advanced parameter tuning system
│   ├── 🛣️ path.py            # Path optimization algorithms
│   ├── 🚗 vehicle.py         # Vehicle management
│   ├── 📦 request.py         # Request handling
│   └── ...                   # Additional core modules
├── 📁 examples/               # Usage examples and demonstrations
├── 📁 docs/                   # Comprehensive documentation
├── 📁 tests/                  # Test suite
└── 📁 papers/                 # Research papers and references
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
# Simple ALNS usage (backward compatible)
from src.alns_compatibility import adaptive_large_neighbourhood_search
result = adaptive_large_neighbourhood_search(meta_obj, initial_solution, True)

# Modern framework usage (recommended)
from src.lns_framework import create_alns_framework
framework = create_alns_framework()
best_solution = framework.solve(initial_solution)
```

### Advanced Configuration

```python
from src.lns_framework import LNSFramework, LNSConfig, AcceptanceStrategy
from src.lns_framework import OperatorConfig

# Custom LNS configuration
config = LNSConfig(
    max_iterations=2000,
    segment_length=150,
    cooling_rate=0.9998,
    acceptance_strategy=AcceptanceStrategy.SIMULATED_ANNEALING
)

# Create framework with custom operators
framework = LNSFramework(config)
framework.add_removal_operator(OperatorConfig("custom_removal", my_removal_func, 1.0))
framework.add_insertion_operator(OperatorConfig("custom_insertion", my_insertion_func, 1.0))

# Solve optimization problem
best_solution = framework.solve(initial_solution)
```

## 🔧 Parameter Tuning

Our advanced parameter tuning system supports multiple optimization strategies:

```python
from src.parameters import create_parameter_tuner

# Create parameter tuner
tuner = create_parameter_tuner()

# Grid search optimization
best_params = tuner.grid_search(
    param_ranges={
        'iteration_num': [1000, 2000, 3000],
        'segment_num': [50, 100, 150],
        'cooling_rate': [0.9995, 0.99975, 0.9999]
    }
)

# Evolutionary optimization
best_params = tuner.evolutionary_search(
    population_size=50,
    generations=100,
    mutation_rate=0.1
)
```

## 📊 Performance Monitoring

Track and analyze algorithm performance:

```python
# Monitor framework performance
performance_metrics = framework.get_performance_metrics()
print(f"Best solution cost: {performance_metrics['best_cost']}")
print(f"Total iterations: {performance_metrics['total_iterations']}")
print(f"Acceptance rate: {performance_metrics['acceptance_rate']:.2%}")

# Export performance data
framework.export_performance_data("performance_report.json")
```

## 🧪 Testing

Run the current test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_lns_framework.py

# Run with coverage (if pytest-cov is installed)
python -m pytest --cov=src tests/
```

**Note**: Test coverage is currently focused on the core framework. Integration tests with real datasets are planned for future releases.

## 📚 Documentation

- **[Framework Guide](docs/lns_framework_guide.md)**: Comprehensive usage guide
- **[Architecture Summary](docs/lns_framework_summary.md)**: High-level design overview
- **[Parameter Tuning Guide](docs/parameter_tuning_guide.md)**: Advanced parameter optimization
- **[Migration Guide](docs/migration_guide.md)**: From old ALNS to new framework

## 🔬 Research Applications

This framework is designed for researchers and practitioners working on:

- **🚚 Vehicle Routing Problems (VRP)**
- **📦 Pickup and Delivery Problems (PDP)**
- **⏰ Time Window Constraints**
- **🔄 Large Neighborhood Search Algorithms**
- **⚡ Adaptive Operator Selection**
- **🎯 Metaheuristic Optimization**

**Current Focus**: Core algorithm implementation and framework architecture. Dataset support and benchmarking capabilities are being developed.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/cauchy1988/TC_PDWTW.git
cd TC_PDWTW

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original Research**: "An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows"
- **Academic Community**: Operations Research and Optimization Research Community
- **Open Source Contributors**: All contributors who have helped improve this framework

## 📞 Contact

- **Project Maintainer**: [cauchy1988](https://github.com/cauchy1988)
- **Project Homepage**: [https://github.com/cauchy1988/TC_PDWTW](https://github.com/cauchy1988/TC_PDWTW)
- **Issues**: [GitHub Issues](https://github.com/cauchy1988/TC_PDWTW/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cauchy1988/TC_PDWTW/discussions)

---

<div align="center">

**⭐ Star this repository if you find it useful! ⭐**

*Built with ❤️ for the optimization research community*

</div>
