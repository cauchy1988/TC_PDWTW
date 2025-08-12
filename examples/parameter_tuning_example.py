#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/12 20:00
# @Author  : Tang Chao
# @File    : parameter_tuning_example.py
# @Software: PyCharm
"""
Example script demonstrating parameter tuning capabilities of the enhanced Parameters class.

This script shows how to:
1. Create parameter tuners
2. Generate random parameter combinations
3. Perform grid search
4. Track performance
5. Export/import parameters
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from parameters import Parameters, create_parameter_tuner, tune_parameters_grid_search, tune_parameters_evolutionary


def example_basic_tuning():
    """Basic parameter tuning example"""
    print("=== Basic Parameter Tuning Example ===")
    
    # Create a parameter tuner
    tuner = create_parameter_tuner()
    
    # Get parameter information
    print(f"Total parameters: {len(tuner._params)}")
    print(f"Tunable parameters: {len(tuner.PARAMETER_RANGES)}")
    
    # Get parameter groups
    groups = tuner.get_parameter_groups()
    for group_name, group in groups.items():
        print(f"\nGroup: {group_name}")
        print(f"  Description: {group.description}")
        print(f"  Parameters: {', '.join(group.parameters)}")
    
    # Generate random parameters for a specific group
    print("\n=== Random Parameters for Shaw Removal ===")
    shaw_params = tuner.generate_random_parameters("shaw_removal")
    for param, value in shaw_params.items():
        print(f"  {param}: {value}")
    
    # Apply new parameters
    print("\n=== Applying New Parameters ===")
    tuner.apply_parameters(shaw_params)
    print("Shaw parameters applied successfully!")
    
    return tuner


def example_grid_search():
    """Grid search parameter tuning example"""
    print("\n=== Grid Search Parameter Tuning ===")
    
    tuner = create_parameter_tuner()
    
    # Define parameter ranges for grid search
    grid_ranges = {
        "alpha": [0.5, 1.0, 2.0],
        "beta": [0.5, 1.0, 2.0],
        "p": [3, 6, 9],
        "p_worst": [2, 3, 4]
    }
    
    # Generate grid search combinations
    combinations = tune_parameters_grid_search(tuner, grid_ranges)
    print(f"Generated {len(combinations)} parameter combinations")
    
    # Show first few combinations
    for i, combo in enumerate(combinations[:5]):
        print(f"  Combination {i+1}: {combo}")
    
    return combinations


def example_performance_tracking():
    """Performance tracking example"""
    print("\n=== Performance Tracking Example ===")
    
    tuner = create_parameter_tuner()
    
    # Simulate some performance results
    test_performances = [
        {"objective_cost": 1500.0, "vehicle_count": 5, "computation_time": 120.5},
        {"objective_cost": 1400.0, "vehicle_count": 4, "computation_time": 135.2},
        {"objective_cost": 1600.0, "vehicle_count": 6, "computation_time": 98.7},
        {"objective_cost": 1300.0, "vehicle_count": 4, "computation_time": 145.8},
    ]
    
    # Record performance for different parameter sets
    for i, performance in enumerate(test_performances):
        # Generate random parameters
        random_params = tuner.generate_random_parameters()
        tuner.apply_parameters(random_params)
        
        # Record performance
        tuner.record_performance(performance)
        print(f"  Recorded performance {i+1}: {performance}")
    
    # Get best parameters
    best_params = tuner.get_best_parameters()
    if best_params:
        print(f"\nBest parameters found: {best_params}")
    
    # Get performance summary
    summary = tuner.get_parameter_summary()
    print(f"\nParameter summary: {summary['total_parameters']} total, {summary['tunable_parameters']} tunable")
    
    return tuner


def example_export_import():
    """Export/import parameters example"""
    print("\n=== Export/Import Parameters Example ===")
    
    tuner = create_parameter_tuner()
    
    # Record some performance data
    tuner.record_performance({"objective_cost": 1200.0, "vehicle_count": 3})
    
    # Export parameters
    export_file = "tuned_parameters.json"
    tuner.export_parameters(export_file)
    print(f"Parameters exported to {export_file}")
    
    # Create new tuner and import parameters
    new_tuner = create_parameter_tuner()
    new_tuner.import_parameters(export_file)
    print("Parameters imported successfully!")
    
    # Verify import
    imported_performance = new_tuner.get_performance_history()
    print(f"Imported {len(imported_performance)} performance records")
    
    # Clean up
    if os.path.exists(export_file):
        os.remove(export_file)
    
    return new_tuner


def example_evolutionary_tuning():
    """Evolutionary parameter tuning example"""
    print("\n=== Evolutionary Parameter Tuning ===")
    
    tuner = create_parameter_tuner()
    
    # Generate evolutionary combinations
    combinations = tune_parameters_evolutionary(tuner, population_size=5, generations=3)
    print(f"Generated {len(combinations)} evolutionary parameter combinations")
    
    # Show some combinations
    for i, combo in enumerate(combinations[:3]):
        print(f"  Combination {i+1}: {combo}")
    
    return combinations


def example_parameter_validation():
    """Parameter validation example"""
    print("\n=== Parameter Validation Example ===")
    
    tuner = create_parameter_tuner()
    
    # Try to set invalid parameters
    try:
        tuner.alpha = -1.0  # Should fail (min is 0.1)
        print("  This should not print")
    except ValueError as e:
        print(f"  Validation error caught: {e}")
    
    try:
        tuner.p = 25  # Should fail (max is 20)
        print("  This should not print")
    except ValueError as e:
        print(f"  Validation error caught: {e}")
    
    # Set valid parameters
    try:
        tuner.alpha = 2.5  # Should succeed
        tuner.p = 10       # Should succeed
        print("  Valid parameters set successfully!")
    except ValueError as e:
        print(f"  Unexpected error: {e}")
    
    return tuner


def main():
    """Main function to run all examples"""
    print("Parameter Tuning Examples")
    print("=" * 50)
    
    try:
        # Run all examples
        tuner1 = example_basic_tuning()
        combinations = example_grid_search()
        tuner2 = example_performance_tracking()
        tuner3 = example_export_import()
        evolutionary_combinations = example_evolutionary_tuning()
        tuner4 = example_parameter_validation()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Parameter grouping and organization")
        print("✓ Random parameter generation")
        print("✓ Grid search combinations")
        print("✓ Performance tracking and best parameter selection")
        print("✓ Export/import functionality")
        print("✓ Parameter validation")
        print("✓ Evolutionary parameter generation")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
