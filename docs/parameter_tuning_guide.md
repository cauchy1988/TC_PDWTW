# Parameter Tuning Guide

This guide explains how to use the enhanced parameter tuning capabilities in the TC_PDWTW project.

## Overview

The enhanced `Parameters` class provides comprehensive parameter tuning capabilities for the PDWTW (Pickup and Delivery Problem with Time Windows) solver. It includes parameter validation, organized grouping, performance tracking, and multiple tuning strategies.

## Key Features

### 1. Parameter Organization
Parameters are organized into logical groups for easier management:

- **Objective Weights**: `alpha`, `beta`, `gama` - Control the balance between distance, time, and unassigned requests
- **Shaw Removal**: `shaw_param_1` to `shaw_param_4` - Control Shaw removal heuristic behavior
- **Roulette Wheel**: `p`, `p_worst` - Control roulette wheel selection in removal heuristics
- **Simulated Annealing**: `w`, `annealing_p`, `c` - Control simulated annealing algorithm
- **Adaptive Weights**: `r`, `eta`, `initial_weight` - Control adaptive weight updates in ALNS
- **Algorithm Control**: `iteration_num`, `epsilon`, `segment_num`, `theta`, `tau` - Control algorithm execution
- **Removal Bounds**: `remove_upper_bound`, `remove_lower_bound` - Control request removal operations

### 2. Parameter Validation
All parameters have defined ranges and constraints to prevent invalid values:

```python
# Example parameter ranges
"alpha": ParameterRange(0.1, 10.0, description="Weight for distance cost")
"p": ParameterRange(1, 20, is_integer=True, description="Roulette wheel parameter")
"iteration_num": ParameterRange(1000, 100000, is_integer=True, description="Total iterations")
```

### 3. Performance Tracking
Track performance metrics for different parameter combinations:

```python
# Record performance
tuner.record_performance({
    "objective_cost": 1500.0,
    "vehicle_count": 5,
    "computation_time": 120.5
})

# Get best parameters
best_params = tuner.get_best_parameters()
```

## Usage Examples

### Basic Parameter Tuning

```python
from parameters import create_parameter_tuner

# Create a parameter tuner
tuner = create_parameter_tuner()

# Generate random parameters for a specific group
shaw_params = tuner.generate_random_parameters("shaw_removal")

# Apply new parameters
tuner.apply_parameters(shaw_params)

# Reset to original values
tuner.reset()
```

### Grid Search Tuning

```python
from parameters import tune_parameters_grid_search

# Define parameter ranges
grid_ranges = {
    "alpha": [0.5, 1.0, 2.0],
    "beta": [0.5, 1.0, 2.0],
    "p": [3, 6, 9]
}

# Generate all combinations
combinations = tune_parameters_grid_search(tuner, grid_ranges)

# Test each combination
for combo in combinations:
    tuner.apply_parameters(combo)
    # Run your algorithm here
    result = run_algorithm(tuner)
    tuner.record_performance(result)
```

### Evolutionary Tuning

```python
from parameters import tune_parameters_evolutionary

# Generate evolutionary combinations
combinations = tune_parameters_evolutionary(
    tuner, 
    population_size=20, 
    generations=10
)

# Test combinations
for combo in combinations:
    tuner.apply_parameters(combo)
    # Run algorithm and record performance
```

### Performance Tracking

```python
# Record performance for current parameters
tuner.record_performance({
    "objective_cost": 1500.0,
    "vehicle_count": 5,
    "computation_time": 120.5,
    "solution_quality": 0.85
})

# Get performance history
history = tuner.get_performance_history()

# Get best performing parameters
best_params = tuner.get_best_parameters()

# Get parameter summary
summary = tuner.get_parameter_summary()
```

### Export/Import Parameters

```python
# Export current parameters and performance data
tuner.export_parameters("tuned_parameters.json")

# Import parameters in another session
new_tuner = create_parameter_tuner()
new_tuner.import_parameters("tuned_parameters.json")
```

## Parameter Groups and Descriptions

### Objective Weights
- **alpha**: Weight for distance cost in objective function (0.1 - 10.0)
- **beta**: Weight for time cost in objective function (0.1 - 10.0)
- **gama**: Penalty for unassigned requests (1000.0 - 1e12)

### Shaw Removal Parameters
- **shaw_param_1**: Weight for distance in Shaw removal (1.0 - 20.0)
- **shaw_param_2**: Weight for time difference in Shaw removal (1.0 - 20.0)
- **shaw_param_3**: Weight for load difference in Shaw removal (1.0 - 20.0)
- **shaw_param_4**: Weight for vehicle set difference in Shaw removal (1.0 - 20.0)

### Roulette Wheel Selection
- **p**: Roulette wheel parameter for Shaw removal (1 - 20)
- **p_worst**: Roulette wheel parameter for worst removal (1 - 10)

### Simulated Annealing
- **w**: Initial temperature parameter (0.01 - 0.5)
- **annealing_p**: Annealing parameter (0.1 - 1.0)
- **c**: Cooling rate (0.9 - 0.9999)

### Adaptive Weights
- **r**: Weight update rate (0.01 - 0.5)
- **eta**: Weight update threshold (0.01 - 0.1)
- **initial_weight**: Initial weight for operators (0.1 - 10.0)

### Algorithm Control
- **iteration_num**: Total number of iterations (1000 - 100000)
- **epsilon**: Fraction of requests to remove (0.1 - 1.0)
- **segment_num**: Number of segments for weight updates (10 - 1000)
- **theta**: Maximum total iterations for two-stage (1000 - 100000)
- **tau**: ALNS iterations for two-stage (100 - 10000)

### Removal Bounds
- **remove_upper_bound**: Upper bound for request removal (10 - 200)
- **remove_lower_bound**: Lower bound for request removal (1 - 20)

## Best Practices

### 1. Start with Default Parameters
Always start with the default parameters to establish a baseline performance.

### 2. Tune One Group at a Time
Focus on one parameter group at a time to understand the impact of each group.

### 3. Use Appropriate Tuning Strategy
- **Grid Search**: For small parameter spaces (2-4 parameters)
- **Random Search**: For large parameter spaces
- **Evolutionary**: For complex parameter landscapes

### 4. Track Multiple Metrics
Record multiple performance metrics to get a comprehensive view:
- Objective cost
- Vehicle count
- Computation time
- Solution quality
- Constraint violations

### 5. Validate Parameter Changes
Always validate that new parameters are within acceptable ranges before applying them.

### 6. Save Good Configurations
Export and save parameter configurations that perform well for future use.

## Example Workflow

```python
# 1. Create tuner with default parameters
tuner = create_parameter_tuner()

# 2. Establish baseline performance
baseline_result = run_algorithm(tuner)
tuner.record_performance(baseline_result)

# 3. Tune objective weights
weight_combinations = tune_parameters_grid_search(tuner, {
    "alpha": [0.5, 1.0, 2.0],
    "beta": [0.5, 1.0, 2.0]
})

for combo in weight_combinations:
    tuner.apply_parameters(combo)
    result = run_algorithm(tuner)
    tuner.record_performance(result)

# 4. Get best parameters
best_params = tuner.get_best_parameters()

# 5. Save configuration
tuner.export_parameters("best_parameters.json")
```

## Troubleshooting

### Common Issues

1. **Parameter Validation Errors**: Check that parameters are within defined ranges
2. **Performance Not Improving**: Try different parameter groups or tuning strategies
3. **Memory Issues**: Clear performance history if tracking many combinations
4. **File Import Errors**: Ensure JSON files are properly formatted

### Debugging Tips

1. Use `tuner.get_parameter_info(param_name)` to check parameter details
2. Use `tuner.get_parameter_summary()` for an overview
3. Check parameter groups with `tuner.get_parameter_groups()`
4. Validate parameters before applying with `tuner._validate_parameter(name, value)`

## Advanced Features

### Custom Parameter Ranges
You can extend the parameter ranges by modifying the `PARAMETER_RANGES` dictionary:

```python
# Add custom parameter
tuner.PARAMETER_RANGES["custom_param"] = ParameterRange(
    0.0, 100.0, description="Custom parameter"
)
```

### Performance Analysis
Analyze performance patterns across different parameter combinations:

```python
# Get performance history
history = tuner.get_performance_history()

# Analyze patterns
for record in history:
    params = record["parameters"]
    perf = record["performance"]
    print(f"Params: {params}, Performance: {perf}")
```

This enhanced parameter tuning system provides a robust foundation for optimizing your PDWTW solver. Use it systematically to find the best parameter combinations for your specific problem instances.
