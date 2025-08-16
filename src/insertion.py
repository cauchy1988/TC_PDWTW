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
from typing import Dict, Callable, Optional, List, Tuple, Any
from meta import Meta
from solution import PDWTWSolution


class InsertionError(Exception):
    """Custom exception for insertion operations"""
    pass


def _get_request_vehicle_cost(meta_obj: Meta, one_solution: PDWTWSolution, 
                             noise_func: Optional[Callable[[float], float]]) -> Dict[int, Dict[int, float]]:
    """
    Calculate the cost of inserting each request into each vehicle.
    
    Args:
        meta_obj: Meta object containing problem parameters
        one_solution: Current solution to analyze
        noise_func: Optional noise function to modify costs
        
    Returns:
        Dictionary mapping request_id -> vehicle_id -> insertion_cost
        
    Raises:
        ValueError: If vehicle IDs are not unique
    """
    if meta_obj is None:
        raise ValueError("meta_obj cannot be None")
    
    if one_solution is None:
        raise ValueError("one_solution cannot be None")
    
    request_vehicle_cost: Dict[int, Dict[int, float]] = {}
    
    # Get all available vehicles - avoid expensive set operations
    vehicles = set(one_solution.vehicle_bank)
    vehicles.update(one_solution.paths.keys())
    
    # Validate vehicle uniqueness
    if len(vehicles) < len(one_solution.vehicle_bank) + len(one_solution.paths):
        raise ValueError("Vehicle IDs must all be unique in one solution's vehicle bank and paths!")
    
    # Calculate insertion costs for each request-vehicle pair
    for request_id in one_solution.request_bank:
        request_vehicle_cost[request_id] = {}
        
        for vehicle_id in vehicles:
            ok, cost = one_solution.cost_if_insert_request_to_vehicle_path(request_id, vehicle_id)
            
            if not ok:
                cost = float(meta_obj.parameters.unlimited_float_bound)
            
            # Apply noise function if provided and valid
            if ok and noise_func and callable(noise_func):
                cost = noise_func(cost)
            
            request_vehicle_cost[request_id][vehicle_id] = cost
    
    return request_vehicle_cost


def _update_request_vehicle_cost(meta_obj: Meta, already_inserted_path_vehicle_id: int,
                                request_vehicle_cost: Dict[int, Dict[int, float]], 
                                one_solution: PDWTWSolution,
                                already_inserted_request_id: int, 
                                noise_func: Optional[Callable[[float], float]]) -> Dict[int, Dict[int, float]]:
    """
    Update the request-vehicle cost matrix after inserting a request.
    
    Args:
        meta_obj: Meta object containing problem parameters
        already_inserted_path_vehicle_id: Vehicle ID where request was inserted
        request_vehicle_cost: Current cost matrix
        one_solution: Current solution
        already_inserted_request_id: Request ID that was inserted
        noise_func: Optional noise function
        
    Returns:
        Updated cost matrix
        
    Raises:
        KeyError: If request or vehicle not found in cost matrix
        RuntimeError: If vehicle not found in vehicle dictionary
    """
    if already_inserted_request_id not in request_vehicle_cost:
        raise KeyError(f'Request {already_inserted_request_id} does not exist in cost matrix')
    
    new_request_vehicle_cost = copy.deepcopy(request_vehicle_cost)
    
    # Remove the inserted request
    del new_request_vehicle_cost[already_inserted_request_id]
    
    # Update costs for the vehicle where request was inserted
    for request_id, vehicle_id_dict in new_request_vehicle_cost.items():
        if already_inserted_path_vehicle_id not in vehicle_id_dict:
            raise RuntimeError(f'Vehicle {already_inserted_path_vehicle_id} not found in cost matrix for request {request_id}')
        
        ok, cost = one_solution.cost_if_insert_request_to_vehicle_path(request_id, already_inserted_path_vehicle_id)
        
        if not ok:
            cost = float(meta_obj.parameters.unlimited_float_bound)
        
        # Apply noise function if provided and valid
        if ok and noise_func and callable(noise_func):
            cost = noise_func(cost)
        
        vehicle_id_dict[already_inserted_path_vehicle_id] = cost
    
    return new_request_vehicle_cost


def _find_best_insertion(request_vehicle_cost: Dict[int, Dict[int, float]], 
                         unlimited_float: float) -> Tuple[Optional[int], Optional[int], float]:
    """
    Find the best request-vehicle insertion pair.
    
    Args:
        request_vehicle_cost: Cost matrix
        unlimited_float: Threshold for unlimited cost
        
    Returns:
        Tuple of (request_id, vehicle_id, cost) or (None, None, float('inf'))
    """
    minimum_cost = float('inf')
    request_id_for_insertion = None
    vehicle_id_for_insertion = None
    
    for request_id, vehicle_id_dict in request_vehicle_cost.items():
        for vehicle_id, cost in vehicle_id_dict.items():
            if cost < minimum_cost:
                minimum_cost = cost
                request_id_for_insertion = request_id
                vehicle_id_for_insertion = vehicle_id
    
    return request_id_for_insertion, vehicle_id_for_insertion, minimum_cost


def basic_greedy_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int, 
                          insert_unlimited: bool, noise_func: Optional[Callable[[float], float]]) -> None:
    """
    Basic greedy insertion algorithm.
    
    Args:
        meta_obj: Meta object containing problem parameters
        one_solution: Solution to modify
        q: Maximum number of insertions
        insert_unlimited: Whether to insert all possible requests
        noise_func: Optional noise function to modify costs
        
    Raises:
        ValueError: If input parameters are invalid
        InsertionError: If insertion fails
    """
    print('start greedy insertion')
    
    if q <= 0:
        raise ValueError(f"q must be positive, got {q}")
    
    if meta_obj is None:
        raise ValueError("meta_obj cannot be None")
    
    if one_solution is None:
        raise ValueError("one_solution cannot be None")
    
    # Calculate actual number of insertions to attempt
    qq = min(len(one_solution.request_bank), q)
    
    # Get initial cost matrix
    print("start _get_request_vehicle_cost")
    request_vehicle_cost = _get_request_vehicle_cost(meta_obj, one_solution, noise_func)
    print("end _get_request_vehicle_cost")

    iteration_num = 0
    max_iterations = qq * 2  # Prevent infinite loops
    
    while (insert_unlimited or iteration_num < qq) and iteration_num < max_iterations:
        # Check if we can still insert requests
        if not request_vehicle_cost or not one_solution.request_bank:
            break
        
        # Find best insertion
        request_id_for_insertion, vehicle_id_for_insertion, minimum_cost = _find_best_insertion(
            request_vehicle_cost, meta_obj.parameters.unlimited_float
        )
        
        # Check if insertion is possible
        if (request_id_for_insertion is None or vehicle_id_for_insertion is None or 
            minimum_cost > meta_obj.parameters.unlimited_float):
            break
        
        # Attempt insertion
        ok = one_solution.insert_one_request_to_one_vehicle_route_optimal(
            request_id_for_insertion, vehicle_id_for_insertion
        )
        
        if not ok:
            raise InsertionError(f'Insertion failed for request {request_id_for_insertion} in vehicle {vehicle_id_for_insertion}!')
        
        # Update cost matrix
        request_vehicle_cost = _update_request_vehicle_cost(
            meta_obj, vehicle_id_for_insertion, request_vehicle_cost, 
            one_solution, request_id_for_insertion, noise_func
        )
        
        iteration_num += 1
	    
    print('end greedy insertion')


def _calculate_regret_cost(request_vehicle_list: Dict[int, List[Tuple[int, float]]], k: int) -> List[Tuple[int, float]]:
    """
    Calculate regret cost for each request.
    
    Args:
        request_vehicle_list: Dictionary mapping request_id to sorted (vehicle_id, cost) list
        k: Number of top vehicles to consider
        
    Returns:
        List of (request_id, regret_cost) tuples sorted by regret cost
    """
    request_k_cost_list = []
    
    for request_id, vehicle_cost_list in request_vehicle_list.items():
        if len(vehicle_cost_list) < k:
            raise ValueError(f"Request {request_id} has fewer than {k} vehicle options")
        
        # Calculate regret cost (difference between k-th best and best)
        k_cost_sum = 0.0
        best_cost = vehicle_cost_list[0][1]
        
        for i in range(k):
            k_cost_sum += (vehicle_cost_list[i][1] - best_cost)
        
        request_k_cost_list.append((request_id, k_cost_sum))
    
    # Sort by regret cost (highest first)
    request_k_cost_list.sort(key=lambda tp: tp[1], reverse=True)
    return request_k_cost_list


def regret_insertion_wrapper(k: int) -> Callable[[Meta, PDWTWSolution, int, bool, Optional[Callable]], None]:
    """
    Create a regret-k insertion function.
    
    Args:
        k: Number of top vehicles to consider for regret calculation
        
    Returns:
        Regret-k insertion function
        
    Raises:
        ValueError: If k is too small
    """
    _LOWEST_K_VALUE = 2
    
    if k < _LOWEST_K_VALUE:
        raise ValueError(f"k must be at least {_LOWEST_K_VALUE}, got {k}")
    
    def _regret_k_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int, 
                           insert_unlimited: bool, noise_func: Optional[Callable[[float], float]]) -> None:
        """
        Regret-k insertion algorithm.
        
        Args:
            meta_obj: Meta object containing problem parameters
            one_solution: Solution to modify
            q: Maximum number of insertions
            insert_unlimited: Whether to insert all possible requests
            noise_func: Optional noise function to modify costs
            
        Raises:
            ValueError: If input parameters are invalid
            RuntimeError: If k is larger than available vehicles
            InsertionError: If insertion fails
        """
        print('start ', k, ' regret insertion')
        
        if q <= 0:
            raise ValueError(f"q must be positive, got {q}")
        
        if meta_obj is None:
            raise ValueError("meta_obj cannot be None")
        
        if one_solution is None:
            raise ValueError("one_solution cannot be None")
        
        # Validate k value
        total_vehicle_num = len(one_solution.vehicle_bank) + len(one_solution.paths)
        if k > total_vehicle_num:
            raise RuntimeError(f"Regret number {k} is bigger than total vehicle number {total_vehicle_num}!")
        
        # Calculate actual number of insertions to attempt
        qq = min(len(one_solution.request_bank), q)
        
        # Get initial cost matrix
        request_vehicle_cost = _get_request_vehicle_cost(meta_obj, one_solution, noise_func)
        
        iteration_num = 0
        max_iterations = qq * 2  # Prevent infinite loops
        
        while (insert_unlimited or iteration_num < qq) and iteration_num < max_iterations:
            # Check if we can still insert requests
            if not request_vehicle_cost or not one_solution.request_bank:
                break
            
            # Build request-vehicle list with sorted costs
            request_vehicle_list: Dict[int, List[Tuple[int, float]]] = {}
            
            for request_id, cost_dict in request_vehicle_cost.items():
                if len(cost_dict) < k:
                    raise ValueError(f"Request {request_id} has fewer than {k} vehicle options")
                
                # Create sorted list of (vehicle_id, cost) tuples
                vehicle_cost_list = [(vehicle_id, cost) for vehicle_id, cost in cost_dict.items()]
                vehicle_cost_list.sort(key=lambda tp: tp[1])
                request_vehicle_list[request_id] = vehicle_cost_list
            
            # Calculate regret costs
            request_k_cost_list = _calculate_regret_cost(request_vehicle_list, k)
            
            # Find first request with feasible insertion
            j = 0
            while j < len(request_k_cost_list):
                request_id = request_k_cost_list[j][0]
                if request_id in request_vehicle_list and request_vehicle_list[request_id]:
                    best_cost = request_vehicle_list[request_id][0][1]
                    if best_cost <= meta_obj.parameters.unlimited_float:
                        break
                j += 1
            
            # Check if we found a feasible insertion
            if j >= len(request_k_cost_list):
                break
            
            # Get insertion details
            request_id_for_insertion = request_k_cost_list[j][0]
            vehicle_id_for_insertion = request_vehicle_list[request_id_for_insertion][0][0]
            
            # Attempt insertion
            ok = one_solution.insert_one_request_to_one_vehicle_route_optimal(
                request_id_for_insertion, vehicle_id_for_insertion
            )
            
            if not ok:
                raise InsertionError(f'Insertion failed for request {request_id_for_insertion} in vehicle {vehicle_id_for_insertion}!')
            
            # Update cost matrix
            request_vehicle_cost = _update_request_vehicle_cost(
                meta_obj, vehicle_id_for_insertion, request_vehicle_cost, 
                one_solution, request_id_for_insertion, noise_func
            )
            
            iteration_num += 1
    
    print('end ', k, ' regret insertion')
    return _regret_k_insertion



