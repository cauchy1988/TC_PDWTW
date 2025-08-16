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


from typing import Set, List, Callable, Tuple
from meta import Meta
from solution import PDWTWSolution, InnerDictForNormalization, generate_normalization_dict
import random


def big_r_function(meta_obj: Meta, base_request_id: int, norm_obj: InnerDictForNormalization) -> Callable[[int], float]:
    """
    Create a function to calculate the relatedness between two requests.
    
    Args:
        meta_obj: Meta object containing problem parameters
        base_request_id: The base request ID for comparison
        norm_obj: Normalization object containing distance and time differences
        
    Returns:
        A function that takes another request ID and returns relatedness score
    """
    def _calculate_relatedness(another_request_id: int) -> float:
        """Calculate relatedness between base_request_id and another_request_id"""
        # Ensure consistent ordering for dictionary access
        if base_request_id > another_request_id:
            first_id, second_id = another_request_id, base_request_id
        else:
            first_id, second_id = base_request_id, another_request_id
        
        # Calculate relatedness using Shaw's parameters
        distance_score = (norm_obj.distance_pick_dict[first_id][second_id] + 
                         norm_obj.distance_delivery_dict[first_id][second_id])
        
        time_score = (norm_obj.start_time_diff_pick_dict[first_id][second_id] + 
                     norm_obj.start_time_diff_delivery_dict[first_id][second_id])
        
        load_score = norm_obj.load_diff_dict[first_id][second_id]
        vehicle_score = norm_obj.vehicle_set_diff_dict[first_id][second_id]
        
        return (meta_obj.parameters.shaw_param_1 * distance_score +
                meta_obj.parameters.shaw_param_2 * time_score +
                meta_obj.parameters.shaw_param_3 * load_score +
                meta_obj.parameters.shaw_param_4 * vehicle_score)
    
    return _calculate_relatedness


def shaw_removal(meta_obj: Meta, one_solution: PDWTWSolution, q: int) -> None:
    """
    Shaw removal heuristic: removes requests based on relatedness.
    
    Args:
        meta_obj: Meta object containing problem parameters
        one_solution: Current solution to modify
        q: Number of requests to remove
        
    Raises:
        ValueError: If q is invalid
        RuntimeError: If solution has insufficient requests
    """
    if q <= 0:
        raise ValueError(f"q must be positive, got {q}")
    
    solution_request_set = set(one_solution.request_id_to_vehicle_id.keys())
    if q > len(solution_request_set):
        raise RuntimeError(f"Cannot remove {q} requests from solution with only {len(solution_request_set)} requests")
    
    if q == 0:
        return
    
    # Start with a random request
    r = random.choice(list(solution_request_set))
    big_d: Set[int] = {r}
    
    # Generate normalization dictionary once
    norm_obj = generate_normalization_dict(meta_obj, one_solution)
    
    while len(big_d) < q:
        # Select a random request from current set
        if not big_d:
            raise RuntimeError("big_d is empty, this should not happen")
        
        r = random.choice(list(big_d))
        
        # Get remaining requests - use set operations for efficiency
        remaining_requests = solution_request_set - big_d
        if not remaining_requests:
            break
        
        # Convert to list only for sorting
        remaining_list = list(remaining_requests)
        
        # Sort by relatedness to selected request
        relatedness_func = big_r_function(meta_obj, r, norm_obj)
        remaining_list.sort(key=relatedness_func)
        
        # Select next request using roulette wheel selection
        y = random.random()
        selection_index = int((y ** meta_obj.parameters.p) * len(remaining_list))
        selection_index = min(selection_index, len(remaining_list) - 1)  # Ensure index is valid
        
        selected_request = remaining_list[selection_index]
        big_d.add(selected_request)
    
    # Remove selected requests
    one_solution.remove_requests(big_d)


def random_removal(meta_obj: Meta, one_solution: PDWTWSolution, q: int) -> None:
    """
    Random removal: removes q random requests from the solution.
    
    Args:
        meta_obj: Meta object containing problem parameters
        one_solution: Current solution to modify
        q: Number of requests to remove
        
    Raises:
        ValueError: If q is invalid or meta_obj is None
        RuntimeError: If solution has insufficient requests
    """
    if q <= 0:
        raise ValueError(f"q must be positive, got {q}")
    
    if meta_obj is None:
        raise ValueError("meta_obj cannot be None")
    
    solution_request_list = list(one_solution.request_id_to_vehicle_id.keys())
    if q > len(solution_request_list):
        raise RuntimeError(f"Cannot remove {q} requests from solution with only {len(solution_request_list)} requests")
    
    if q == 0:
        return
    
    # Select q random requests
    q_request_id_list = random.sample(solution_request_list, q)
    one_solution.remove_requests(set(q_request_id_list))


def worst_removal(meta_obj: Meta, one_solution: PDWTWSolution, q: int) -> None:
    """
    Worst removal: removes requests with highest removal cost.
    
    Args:
        meta_obj: Meta object containing problem parameters
        one_solution: Current solution to modify
        q: Number of requests to remove
        
    Raises:
        ValueError: If q is invalid or meta_obj is None
        RuntimeError: If solution has insufficient requests
    """
    if q <= 0:
        raise ValueError(f"q must be positive, got {q}")
    
    if meta_obj is None:
        raise ValueError("meta_obj cannot be None")
    
    remaining_q = q
    
    while remaining_q > 0:
        # Get all current requests
        current_requests = list(one_solution.request_id_to_vehicle_id.keys())
        
        if not current_requests:
            break
        
        if len(current_requests) == 0:
            raise RuntimeError("No requests available for removal")
        
        # Sort by removal cost (highest first)
        current_requests.sort(key=one_solution.cost_if_remove_request, reverse=True)
        
        # Select request using roulette wheel selection
        y = random.random()
        selection_index = int((y ** meta_obj.parameters.p_worst) * len(current_requests))
        selection_index = min(selection_index, len(current_requests) - 1)  # Ensure index is valid
        
        selected_request = current_requests[selection_index]
        
        # Remove the selected request
        one_solution.remove_requests({selected_request})
        remaining_q -= 1



