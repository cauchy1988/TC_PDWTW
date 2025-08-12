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
import random
from typing import Optional

from solution import PDWTWSolution
from alns import adaptive_large_neighbourhood_search


class TwoStageError(Exception):
    """Custom exception for two-stage algorithm operations"""
    pass


def first_stage_to_limit_vehicle_num_in_homogeneous_fleet(one_solution: PDWTWSolution) -> PDWTWSolution:
    """
    First stage: minimize the number of vehicles in a homogeneous fleet.
    
    This stage works in two phases:
    1. Insert all requests by adding vehicles as needed
    2. Iteratively remove vehicles and try to reassign requests
    
    Args:
        one_solution: Initial solution to optimize
        
    Returns:
        Optimized solution with minimal vehicle count
        
    Raises:
        TwoStageError: If algorithm fails to converge or encounters errors
    """
    if one_solution is None:
        raise ValueError("one_solution cannot be None")
    
    # Phase 1: Insert all requests by adding vehicles as needed
    requests_in_bank = one_solution.request_bank.copy()
    
    a_iteration_num = 0
    max_iterations = 1000  # Prevent infinite loops
    new_vehicle_add_flag = False
    
    while requests_in_bank and a_iteration_num < max_iterations:
        a_iteration_num += 1
        
        current_request = requests_in_bank.pop(0)
        if one_solution.insert_one_request_to_any_vehicle_route_optimal(current_request):
            new_vehicle_add_flag = False
            continue
        else:
            # Check if we're stuck in a loop
            if new_vehicle_add_flag:
                raise TwoStageError(f"Failed to insert request {current_request} even after adding new vehicle. "
                                  f"Algorithm may be stuck.")
            
            one_solution.add_one_same_vehicle()
            requests_in_bank.append(current_request)
            new_vehicle_add_flag = True
    
    if a_iteration_num >= max_iterations:
        raise TwoStageError(f"First stage failed to converge after {max_iterations} iterations")
    
    result_solution = one_solution.copy()
    
    # Phase 2: Iteratively remove vehicles and try to reassign requests
    total_iteration_num = a_iteration_num
    max_total_iterations = one_solution.meta_obj.parameters.theta
    
    while total_iteration_num <= max_total_iterations:
        # Get the vehicle with maximum ID to remove
        max_vehicle_id = one_solution.max_vehicle_id()
        if max_vehicle_id is None:
            break
        
        # Remove the vehicle and its route
        one_solution.delete_vehicle_and_its_route(max_vehicle_id)
        
        # Temporarily modify parameters for ALNS
        original_iteration_num = one_solution.meta_obj.parameters.iteration_num
        one_solution.meta_obj.parameters.iteration_num = one_solution.meta_obj.parameters.tau
        
        try:
            # Try to reassign requests using ALNS
            adaptive_large_neighbourhood_search(one_solution.meta_obj, one_solution, insert_unlimited=True)
            
            if not one_solution.request_bank:
                # Successfully reassigned all requests
                result_solution = one_solution.copy()
                total_iteration_num += one_solution.meta_obj.parameters.iteration_num
            else:
                # Failed to reassign all requests, stop here
                break
        finally:
            # Restore original parameters
            one_solution.meta_obj.parameters.iteration_num = original_iteration_num
    
    # Reset parameters to original values
    result_solution.meta_obj.parameters.reset()
    return result_solution


def two_stage_algorithm_in_homogeneous_fleet(initial_solution: PDWTWSolution) -> PDWTWSolution:
    """
    Two-stage algorithm for solving PDWTW with homogeneous fleet.
    
    Stage 1: Minimize the number of vehicles
    Stage 2: Optimize the solution using ALNS
    
    Args:
        initial_solution: Initial solution to optimize
        
    Returns:
        Optimized solution
        
    Raises:
        TwoStageError: If algorithm fails to converge
        ValueError: If input is invalid
    """
    if initial_solution is None:
        raise ValueError("initial_solution cannot be None")
    
    if not hasattr(initial_solution, 'meta_obj') or initial_solution.meta_obj is None:
        raise ValueError("initial_solution must have a valid meta_obj")
    
    try:
        # Stage 1: Minimize vehicle count
        result_solution = first_stage_to_limit_vehicle_num_in_homogeneous_fleet(initial_solution)
        
        # Stage 2: Optimize using ALNS
        adaptive_large_neighbourhood_search(result_solution.meta_obj, result_solution, insert_unlimited=True)
        
        return result_solution
        
    except Exception as e:
        raise TwoStageError(f"Two-stage algorithm failed: {str(e)}") from e


def _validate_solution(one_solution: PDWTWSolution) -> None:
    """
    Validate that a solution is ready for two-stage algorithm.
    
    Args:
        one_solution: Solution to validate
        
    Raises:
        ValueError: If solution is invalid
    """
    if one_solution is None:
        raise ValueError("Solution cannot be None")
    
    if not hasattr(one_solution, 'meta_obj'):
        raise ValueError("Solution must have meta_obj attribute")
    
    if not hasattr(one_solution, 'request_bank'):
        raise ValueError("Solution must have request_bank attribute")
    
    if not hasattr(one_solution, 'vehicle_bank'):
        raise ValueError("Solution must have vehicle_bank attribute")
    
    if not hasattr(one_solution.meta_obj, 'parameters'):
        raise ValueError("Solution meta_obj must have parameters attribute")


def safe_two_stage_algorithm(initial_solution: PDWTWSolution) -> PDWTWSolution:
    """
    Safely execute two-stage algorithm with input validation.
    
    Args:
        initial_solution: Initial solution to optimize
        
    Returns:
        Optimized solution
        
    Raises:
        TwoStageError: If algorithm fails
    """
    _validate_solution(initial_solution)
    return two_stage_algorithm_in_homogeneous_fleet(initial_solution)