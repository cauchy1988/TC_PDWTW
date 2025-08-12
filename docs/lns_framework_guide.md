# LNS Framework Guide

This guide explains how to use the new generic Large Neighborhood Search (LNS) framework, which provides a flexible and configurable foundation for implementing various LNS variants, including ALNS (Adaptive Large Neighborhood Search).

## Overview

The LNS Framework is designed to be:
- **Generic**: Works with any solution type that supports the required interface
- **Configurable**: Easy to customize acceptance criteria, reward mechanisms, and operator sets
- **Extensible**: Simple to add new operators and strategies
- **Reusable**: Can be used for different problem types and LNS variants

## Architecture

### Core Components

1. **LNSFramework**: Main framework class that orchestrates the search process
2. **LNSConfig**: Configuration class for algorithm parameters
3. **OperatorConfig**: Configuration for individual operators
4. **AcceptanceCriterion**: Abstract base for acceptance strategies
5. **RewardMechanism**: Abstract base for reward mechanisms

### Key Features

- **Multiple Acceptance Strategies**: Always, Better Only, Simulated Annealing, Probabilistic
- **Multiple Reward Mechanisms**: Simple, Adaptive, Rank-based
- **Configurable Operator Weights**: Dynamic weight updates based on performance
- **Statistics and Monitoring**: Built-in performance tracking
- **Parallel Execution Support**: Framework for parallel operator execution

## Quick Start

### Basic Usage

```python
from lns_framework import LNSFramework, LNSConfig, OperatorConfig
from removal import random_removal
from insertion import basic_greedy_insertion

# Create configuration
config = LNSConfig(
    max_iterations=100,
    segment_length=20,
    acceptance_strategy=AcceptanceStrategy.BETTER_ONLY
)

# Create framework
framework = LNSFramework(config)

# Add operators
framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))

# Solve
best_solution = framework.solve(initial_solution)
```

### Using Pre-configured Variants

```python
from lns_framework import create_alns_framework, create_simple_lns_framework

# Create ALNS framework
alns = create_alns_framework()

# Create simple LNS framework
simple_lns = create_simple_lns_framework()

# Solve
best_solution = alns.solve(initial_solution)
```

## Configuration Options

### LNSConfig Parameters

#### Basic Parameters
- `max_iterations`: Maximum number of iterations
- `segment_length`: Length of segments for weight updates
- `removal_lower_bound`: Lower bound for removal size
- `removal_upper_bound`: Upper bound for removal size
- `removal_epsilon`: Fraction of requests to remove

#### Temperature Parameters (for Simulated Annealing)
- `initial_temperature`: Initial temperature (auto-calculated if None)
- `cooling_rate`: Temperature cooling rate
- `annealing_parameter`: Parameter for temperature calculation

#### Acceptance Parameters
- `acceptance_strategy`: Strategy for accepting solutions
- `acceptance_threshold`: Threshold for probabilistic acceptance

#### Reward Parameters
- `reward_strategy`: Strategy for calculating rewards
- `reward_rates`: Reward rates for different outcomes
- `weight_update_rate`: Rate for updating operator weights

#### Advanced Parameters
- `use_noise`: Whether to use objective noise
- `noise_eta`: Noise parameter
- `enable_parallel`: Enable parallel execution
- `max_workers`: Maximum number of parallel workers

### Acceptance Strategies

#### 1. Always Accept
```python
config = LNSConfig(acceptance_strategy=AcceptanceStrategy.ALWAYS)
```
- Accepts all new solutions
- Useful for exploration-focused search

#### 2. Better Only
```python
config = LNSConfig(acceptance_strategy=AcceptanceStrategy.BETTER_ONLY)
```
- Only accepts better solutions
- Useful for hill-climbing approaches

#### 3. Simulated Annealing
```python
config = LNSConfig(
    acceptance_strategy=AcceptanceStrategy.SIMULATED_ANNEALING,
    cooling_rate=0.99975
)
```
- Accepts worse solutions with probability based on temperature
- Balances exploration and exploitation

#### 4. Probabilistic
```python
config = LNSConfig(
    acceptance_strategy=AcceptanceStrategy.PROBABILISTIC,
    acceptance_threshold=0.2
)
```
- Accepts worse solutions with fixed probability
- Simple alternative to simulated annealing

### Reward Mechanisms

#### 1. Simple Reward
```python
config = LNSConfig(reward_strategy=RewardStrategy.SIMPLE)
```
- Fixed reward rates for different outcomes
- Simple and predictable

#### 2. Adaptive Reward
```python
config = LNSConfig(
    reward_strategy=RewardStrategy.ADAPTIVE,
    weight_update_rate=0.1
)
```
- Dynamic reward calculation
- Adapts to operator performance

## Operator Configuration

### Adding Operators

```python
# Basic operator
framework.add_removal_operator(OperatorConfig("random_removal", random_removal))

# Operator with custom weight
framework.add_removal_operator(OperatorConfig(
    "shaw_removal", shaw_removal, 
    initial_weight=2.0
))

# Operator with bounds and description
framework.add_insertion_operator(OperatorConfig(
    "regret_insertion", regret_insertion_wrapper(3),
    initial_weight=1.5,
    min_weight=0.1,
    max_weight=5.0,
    description="Regret-3 insertion with adaptive weights"
))
```

### Operator Weights

Operator weights are automatically updated based on performance:
- **New Best**: Highest reward
- **Accepted**: Medium reward  
- **Rejected**: Lowest reward

Weights are updated every `segment_length` iterations.

## Custom LNS Variants

### Creating Custom Acceptance Criteria

```python
from lns_framework import AcceptanceCriterion

class CustomAcceptance(AcceptanceCriterion):
    def should_accept(self, current_solution, new_solution, temperature=None):
        # Custom acceptance logic
        if new_solution.objective_cost < current_solution.objective_cost:
            return True
        
        # Custom probabilistic acceptance
        improvement_ratio = (current_solution.objective_cost - new_solution.objective_cost) / current_solution.objective_cost
        return random.random() < max(0.1, improvement_ratio)
```

### Creating Custom Reward Mechanisms

```python
from lns_framework import RewardMechanism

class CustomReward(RewardMechanism):
    def calculate_rewards(self, operators, performances):
        rewards = [0.0] * len(operators)
        
        for perf in performances:
            if perf.get("is_new_best", False):
                rewards[perf["operator_index"]] += 10.0
            elif perf.get("is_accepted", False):
                rewards[perf["operator_index"]] += 5.0
            else:
                rewards[perf["operator_index"]] += 1.0
        
        return rewards
```

### Using Custom Components

```python
# Create framework with custom components
framework = LNSFramework(config)
framework.acceptance_criterion = CustomAcceptance()
framework.reward_mechanism = CustomReward()

# Add operators and solve
framework.add_removal_operator(OperatorConfig("custom_removal", custom_removal))
framework.add_insertion_operator(OperatorConfig("custom_insertion", custom_insertion))

best_solution = framework.solve(initial_solution)
```

## Advanced Features

### Statistics and Monitoring

```python
# Get algorithm statistics
stats = framework.get_statistics()
print(f"Iterations: {stats['iterations']}")
print(f"Best solution: {stats['best_solution']}")
print(f"Accepted solutions: {stats['accepted_solutions_count']}")
print(f"Removal operators: {stats['removal_operators']}")
print(f"Insertion operators: {stats['insertion_operators']}")
```

### Parallel Execution

```python
# Configure for parallel execution
config = LNSConfig(
    enable_parallel=True,
    max_workers=4,
    max_iterations=1000
)

framework = LNSFramework(config)
# Add multiple operators for parallel execution
# Note: Parallel execution requires additional implementation
```

### Custom Temperature Calculation

```python
# Override temperature calculation
def custom_temperature(self, solution):
    # Custom temperature logic
    base_temp = 100.0
    iteration_factor = 1.0 / (1.0 + self.iteration_count * 0.01)
    return base_temp * iteration_factor

framework._compute_temperature = custom_temperature.__get__(framework)
```

## Best Practices

### 1. Start with Pre-configured Variants
Use `create_alns_framework()` or `create_simple_lns_framework()` for common use cases.

### 2. Configure Based on Problem Characteristics
- **Small problems**: Use simple acceptance strategies
- **Large problems**: Use simulated annealing for better exploration
- **Time-constrained**: Reduce max_iterations and segment_length

### 3. Balance Operator Diversity
- Include both greedy and random operators
- Vary operator weights based on expected performance
- Monitor operator performance and adjust weights

### 4. Monitor Convergence
- Track best solution over time
- Adjust parameters if convergence is too slow
- Use statistics to understand algorithm behavior

### 5. Experiment with Different Configurations
- Try different acceptance strategies
- Test various reward mechanisms
- Adjust operator weights and bounds

## Migration from Original ALNS

### Before (Original ALNS)
```python
from alns import adaptive_large_neighbourhood_search

result = adaptive_large_neighbourhood_search(meta_obj, initial_solution, insert_unlimited=True)
```

### After (New Framework)
```python
from lns_framework import create_alns_framework

framework = create_alns_framework()
result = framework.solve(initial_solution)
```

### Benefits of Migration
- **More control**: Fine-tune algorithm parameters
- **Better monitoring**: Track performance and statistics
- **Easier extension**: Add custom operators and strategies
- **Reusability**: Use framework for different problems

## Troubleshooting

### Common Issues

1. **No operators available**: Ensure you've added at least one removal and one insertion operator
2. **Weight update errors**: Check that reward_rates has the correct length
3. **Temperature calculation errors**: Verify that solution has required attributes
4. **Performance tracking issues**: Ensure operators return expected results

### Debugging Tips

1. **Check configuration**: Verify all required parameters are set
2. **Monitor statistics**: Use `get_statistics()` to understand algorithm behavior
3. **Test operators**: Verify individual operators work correctly
4. **Check solution interface**: Ensure solution objects have required methods

## Future Extensions

The framework is designed to be easily extensible:

- **New acceptance criteria**: Implement `AcceptanceCriterion` interface
- **New reward mechanisms**: Implement `RewardMechanism` interface
- **Parallel execution**: Extend with multiprocessing support
- **Hybrid strategies**: Combine multiple acceptance or reward strategies
- **Problem-specific optimizations**: Add domain-specific logic

This framework provides a solid foundation for implementing and experimenting with various LNS variants, making it easier to develop and compare different approaches for your specific optimization problems.
