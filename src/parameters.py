#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2024 cauchy1988

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import copy
import json
import random
from typing import Dict, Any, List, Optional, Union


class ParameterRange:
    """Define the range and constraints for a parameter"""
    
    def __init__(self, min_value: Union[int, float], max_value: Union[int, float], 
                 step: Optional[Union[int, float]] = None, is_integer: bool = False, 
                 description: str = ""):
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.is_integer = is_integer
        self.description = description
    
    def validate(self, value: Union[int, float]) -> bool:
        """Validate if a value is within the parameter range"""
        if self.is_integer and not isinstance(value, int):
            return False
        return self.min_value <= value <= self.max_value
    
    def get_random_value(self) -> Union[int, float]:
        """Get a random value within the parameter range"""
        if self.step is None:
            if self.is_integer:
                return random.randint(int(self.min_value), int(self.max_value))
            else:
                return random.uniform(self.min_value, self.max_value)
        else:
            steps = int((self.max_value - self.min_value) / self.step) + 1
            step_index = random.randint(0, steps - 1)
            value = self.min_value + step_index * self.step
            return int(value) if self.is_integer else value


class ParameterGroup:
    """Group related parameters for easier management"""
    
    def __init__(self, name: str, parameters: List[str], description: str = ""):
        self.name = name
        self.parameters = parameters
        self.description = description


class Parameters:
    """
    Enhanced Parameters class with tuning capabilities.
    
    This class provides:
    - Parameter validation and constraints
    - Random parameter generation for tuning
    - Parameter grouping for organized tuning
    - Export/import functionality
    - Performance tracking
    """
    
    # Define parameter groups for organized tuning
    PARAMETER_GROUPS = {
        "objective_weights": ParameterGroup(
            "Objective Weights",
            ["alpha", "beta", "gama"],
            "Weights for distance, time, and unassigned requests in objective function"
        ),
        "shaw_removal": ParameterGroup(
            "Shaw Removal Parameters",
            ["shaw_param_1", "shaw_param_2", "shaw_param_3", "shaw_param_4"],
            "Parameters controlling Shaw removal heuristic"
        ),
        "roulette_wheel": ParameterGroup(
            "Roulette Wheel Selection",
            ["p", "p_worst"],
            "Parameters for roulette wheel selection in removal heuristics"
        ),
        "simulated_annealing": ParameterGroup(
            "Simulated Annealing",
            ["w", "annealing_p", "c"],
            "Parameters for simulated annealing algorithm"
        ),
        "adaptive_weights": ParameterGroup(
            "Adaptive Weight Updates",
            ["r", "eta", "initial_weight"],
            "Parameters for adaptive weight updates in ALNS"
        ),
        "algorithm_control": ParameterGroup(
            "Algorithm Control",
            ["iteration_num", "epsilon", "segment_num", "theta", "tau"],
            "Parameters controlling algorithm execution"
        ),
        "removal_bounds": ParameterGroup(
            "Removal Bounds",
            ["remove_upper_bound", "remove_lower_bound"],
            "Bounds for request removal operations"
        )
    }
    
    # Define parameter ranges and constraints
    PARAMETER_RANGES = {
        "alpha": ParameterRange(1e-8, 10.0, description="Weight for distance cost"),
        "beta": ParameterRange(1e-8, 10.0, description="Weight for time cost"),
        "gama": ParameterRange(1000.0, 1e12, description="Penalty for unassigned requests"),
        
        "shaw_param_1": ParameterRange(1.0, 20.0, description="Weight for distance in Shaw removal"),
        "shaw_param_2": ParameterRange(1.0, 20.0, description="Weight for time difference in Shaw removal"),
        "shaw_param_3": ParameterRange(1.0, 20.0, description="Weight for load difference in Shaw removal"),
        "shaw_param_4": ParameterRange(1.0, 20.0, description="Weight for vehicle set difference in Shaw removal"),
        
        "p": ParameterRange(1, 20, is_integer=True, description="Roulette wheel parameter for Shaw removal"),
        "p_worst": ParameterRange(1, 10, is_integer=True, description="Roulette wheel parameter for worst removal"),
        
        "w": ParameterRange(0.01, 0.5, description="Initial temperature parameter"),
        "annealing_p": ParameterRange(0.1, 1.0, description="Annealing parameter"),
        "c": ParameterRange(0.9, 0.9999, description="Cooling rate"),
        
        "r": ParameterRange(0.01, 0.5, description="Weight update rate"),
        "eta": ParameterRange(0.01, 0.1, description="Weight update threshold"),
        "initial_weight": ParameterRange(0.1, 10.0, description="Initial weight for operators"),
        
        "iteration_num": ParameterRange(1000, 100000, is_integer=True, description="Total number of iterations"),
        "epsilon": ParameterRange(0.1, 1.0, description="Fraction of requests to remove"),
        "segment_num": ParameterRange(10, 1000, is_integer=True, description="Number of segments for weight updates"),
        "theta": ParameterRange(1000, 100000, is_integer=True, description="Maximum total iterations for two-stage"),
        "tau": ParameterRange(100, 10000, is_integer=True, description="ALNS iterations for two-stage"),
        
        "remove_upper_bound": ParameterRange(10, 200, is_integer=True, description="Upper bound for request removal"),
        "remove_lower_bound": ParameterRange(1, 20, is_integer=True, description="Lower bound for request removal"),
        
        "unlimited_float": ParameterRange(1e6, 1e15, description="Large value for unlimited operations"),
        "unlimited_float_bound": ParameterRange(1e6, 1e15, description="Boundary value for unlimited operations")
    }
    
    def __init__(self, **kwargs):
        # Initialize default parameters
        self._params = {
            "alpha": 1.0,
            "beta": 1e-6,
            "gama": 1000000000.0,
            "shaw_param_1": 9.0,
            "shaw_param_2": 3.0,
            "shaw_param_3": 3.0,
            "shaw_param_4": 5.0,
            "p": 6,
            "p_worst": 3,
            "w": 0.05,
            "annealing_p": 0.5,
            "c": 0.99975,
            "r": 0.1,
            "reward_adds": [10, 6, 3],
            "eta": 0.025,
            "initial_weight": 1,
            "iteration_num": 25000,
            "epsilon": 0.4,
            "segment_num": 50,
            "unlimited_float": 100000000000000.0,
            "unlimited_float_bound": 100000000000000.0 + 100.0,
            "theta": 25000,
            "tau": 2000,
            "remove_upper_bound": 100,
            "remove_lower_bound": 4
        }
        
        # Update with provided parameters
        self._params.update(kwargs)
        
        # Store original parameters for reset
        self._original_params = copy.deepcopy(self._params)
        
        # Performance tracking
        self._performance_history: List[Dict[str, Any]] = []
        self._best_performance: Optional[Dict[str, Any]] = None
        
        # Validate all parameters
        self._validate_all_parameters()
    
    def _validate_all_parameters(self) -> None:
        """Validate all parameters against their defined ranges"""
        for param_name, param_range in self.PARAMETER_RANGES.items():
            if param_name in self._params:
                value = self._params[param_name]
                if not param_range.validate(value):
                    raise ValueError(f"Parameter {param_name}={value} is outside valid range "
                                  f"[{param_range.min_value}, {param_range.max_value}]")
    
    def _validate_parameter(self, name: str, value: Any) -> None:
        """Validate a single parameter"""
        if name in self.PARAMETER_RANGES:
            param_range = self.PARAMETER_RANGES[name]
            if not param_range.validate(value):
                raise ValueError(f"Parameter {name}={value} is outside valid range "
                              f"[{param_range.min_value}, {param_range.max_value}]")
    
    def reset(self) -> None:
        """Reset parameters to their original values"""
        self._params = copy.deepcopy(self._original_params)
        self._performance_history.clear()
        self._best_performance = None
    
    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a parameter"""
        if param_name not in self.PARAMETER_RANGES:
            return None
        
        param_range = self.PARAMETER_RANGES[param_name]
        return {
            "name": param_name,
            "current_value": self._params.get(param_name),
            "min_value": param_range.min_value,
            "max_value": param_range.max_value,
            "step": param_range.step,
            "is_integer": param_range.is_integer,
            "description": param_range.description,
            "group": self._get_parameter_group(param_name)
        }
    
    def _get_parameter_group(self, param_name: str) -> Optional[str]:
        """Get the group name for a parameter"""
        for group_name, group in self.PARAMETER_GROUPS.items():
            if param_name in group.parameters:
                return group_name
        return None
    
    def get_tunable_parameters(self, group_name: Optional[str] = None) -> List[str]:
        """Get list of tunable parameters, optionally filtered by group"""
        if group_name is None:
            return list(self.PARAMETER_RANGES.keys())
        
        if group_name not in self.PARAMETER_GROUPS:
            raise ValueError(f"Unknown parameter group: {group_name}")
        
        return self.PARAMETER_GROUPS[group_name].parameters
    
    def get_parameter_groups(self) -> Dict[str, ParameterGroup]:
        """Get all parameter groups"""
        return copy.deepcopy(self.PARAMETER_GROUPS)
    
    def generate_random_parameters(self, group_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate random values for tunable parameters"""
        params = {}
        param_names = self.get_tunable_parameters(group_name)
        
        for param_name in param_names:
            if param_name in self.PARAMETER_RANGES:
                param_range = self.PARAMETER_RANGES[param_name]
                params[param_name] = param_range.get_random_value()
        
        return params
    
    def tune_parameters(self, group_name: Optional[str] = None, 
                       num_combinations: int = 10) -> List[Dict[str, Any]]:
        """Generate multiple parameter combinations for tuning"""
        combinations = []
        
        for _ in range(num_combinations):
            combination = self.generate_random_parameters(group_name)
            combinations.append(combination)
        
        return combinations
    
    def apply_parameters(self, new_params: Dict[str, Any]) -> None:
        """Apply new parameter values with validation"""
        for name, value in new_params.items():
            if name in self._params:
                self._validate_parameter(name, value)
                self._params[name] = value
            else:
                raise ValueError(f"Unknown parameter: {name}")
    
    def record_performance(self, performance_metrics: Dict[str, Any]) -> None:
        """Record performance metrics for parameter tuning"""
        record = {
            "parameters": copy.deepcopy(self._params),
            "performance": performance_metrics,
            "timestamp": copy.deepcopy(self._params)  # Use current parameters as timestamp
        }
        
        self._performance_history.append(record)
        
        # Update the best performance if better
        if self._best_performance is None:
            self._best_performance = record
        else:
            # Compare based on objective cost (lower is better)
            current_cost = performance_metrics.get("objective_cost", float('inf'))
            best_cost = self._best_performance["performance"].get("objective_cost", float('inf'))
            
            if current_cost < best_cost:
                self._best_performance = record
    
    def get_best_parameters(self) -> Optional[Dict[str, Any]]:
        """Get the best performing parameter combination"""
        if self._best_performance is None:
            return None
        return copy.deepcopy(self._best_performance["parameters"])
    
    def get_performance_history(self) -> List[Dict[str, Any]]:
        """Get the complete performance history"""
        return copy.deepcopy(self._performance_history)
    
    def export_parameters(self, filename: str) -> None:
        """Export current parameters to a JSON file"""
        export_data = {
            "parameters": self._params,
            "performance_history": self._performance_history,
            "best_performance": self._best_performance
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_parameters(self, filename: str) -> None:
        """Import parameters from a JSON file"""
        with open(filename, 'r') as f:
            import_data = json.load(f)
        
        if "parameters" in import_data:
            self.apply_parameters(import_data["parameters"])
        
        if "performance_history" in import_data:
            self._performance_history = import_data["performance_history"]
        
        if "best_performance" in import_data:
            self._best_performance = import_data["best_performance"]
    
    def get_parameter_summary(self) -> Dict[str, Any]:
        """Get a summary of all parameters and their current values"""
        summary = {
            "groups": {},
            "total_parameters": len(self._params),
            "tunable_parameters": len(self.PARAMETER_RANGES)
        }
        
        for group_name, group in self.PARAMETER_GROUPS.items():
            summary["groups"][group_name] = {
                "description": group.description,
                "parameters": {}
            }
            
            for param_name in group.parameters:
                if param_name in self._params:
                    param_info = self.get_parameter_info(param_name)
                    if param_info:
                        summary["groups"][group_name]["parameters"][param_name] = {
                            "current_value": param_info["current_value"],
                            "range": f"[{param_info['min_value']}, {param_info['max_value']}]",
                            "description": param_info["description"]
                        }
        
        return summary
    
    def __getattr__(self, name: str) -> Any:
        """Get parameter value by attribute access"""
        if name in self._params:
            return self._params[name]
        raise AttributeError(f"'Parameters' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Set parameter value with validation"""
        if name == "_params" or name.startswith("_"):
            super().__setattr__(name, value)
        elif "_params" in self.__dict__ and name in self._params:
            self._validate_parameter(name, value)
            self._params[name] = value
        else:
            super().__setattr__(name, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary"""
        return copy.deepcopy(self._params)
    
    def __str__(self) -> str:
        """String representation of parameters"""
        return f"Parameters({len(self._params)} parameters, {len(self._performance_history)} performance records)"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Parameters(parameters={self._params}, performance_history={len(self._performance_history)})"


# Convenience functions for parameter tuning
def create_parameter_tuner(initial_params: Optional[Dict[str, Any]] = None) -> Parameters:
    """Create a parameter tuner with optional initial parameters"""
    return Parameters(**(initial_params or {}))


def tune_parameters_grid_search(base_params: Parameters, 
                              param_ranges: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """Generate grid search combinations for parameter tuning"""
    combinations = []
    
    # Generate all combinations
    import itertools
    param_names = list(param_ranges.keys())
    param_values = list(param_ranges.values())
    
    for combination in itertools.product(*param_values):
        param_dict = dict(zip(param_names, combination))
        combinations.append(param_dict)
    
    return combinations


def tune_parameters_evolutionary(base_params: Parameters, 
                                population_size: int = 20, 
                                generations: int = 10) -> List[Dict[str, Any]]:
    """Generate evolutionary algorithm combinations for parameter tuning"""
    combinations = []
    
    for _ in range(population_size * generations):
        combination = base_params.generate_random_parameters()
        combinations.append(combination)
    
    return combinations
