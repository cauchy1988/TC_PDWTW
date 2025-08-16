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


from removal import shaw_removal, random_removal, worst_removal
from insertion import basic_greedy_insertion, regret_insertion_wrapper
import random
import math
from typing import Callable, List, Tuple
from meta import Meta
from solution import PDWTWSolution

# Constants
ACCEPTED_SET_MAXLEN = 25000  # Maximum size of accepted solution set to prevent memory overflow

def _objective_noise_wrapper(meta_obj: Meta, use_noise: bool, max_distance: float) -> Callable[[float], float]:
	"""Create an objective function wrapper that optionally adds noise.
	
	Args:
		meta_obj: Meta object containing algorithm parameters
		use_noise: Whether to add noise to the objective function
		max_distance: Maximum distance in the problem instance
		
	Returns:
		Callable that takes a cost and returns potentially noisy cost
	"""
	def _objective_noise(cost: float) -> float:
		nonlocal meta_obj, max_distance
		if use_noise:
			noise = meta_obj.parameters.eta * max_distance
			return float(max(0.0, random.uniform(-noise, noise) + cost))
		return cost
	return _objective_noise

def _select_function_with_weight(funcs: List[Callable], weights: List[float]) -> Tuple[Callable, int]:
	"""Select a function from a list using weighted random selection.
	
	Args:
		funcs: List of functions to choose from
		weights: Corresponding weights for each function
		
	Returns:
		Tuple of (selected_function, index_of_selected_function)
		
	Raises:
		ValueError: If lengths of funcs and weights don't match or weights are invalid
	"""
	if len(funcs) != len(weights):
		raise ValueError('weights must have same length as funcs!')
	
	# Handle case where all weights are zero or negative
	if all(w <= 0 for w in weights):
		# Fallback to uniform selection if all weights are zero/negative
		selected_index = random.randint(0, len(funcs) - 1)
	else:
		# Ensure all weights are non-negative for random.choices
		positive_weights = [max(0.0, w) for w in weights]
		selected_index = random.choices(
			range(len(funcs)),
			weights=positive_weights,
			k=1
		)[0]

	return funcs[selected_index], selected_index

def _compute_initial_temperature(z0: float, w: float, p: float) -> float:
	"""Compute initial temperature for simulated annealing.
	
	Args:
		z0: Initial objective cost (must be positive)
		w: Temperature scaling factor
		p: Initial acceptance probability (must be in (0,1))
		
	Returns:
		Initial temperature value
		
	Raises:
		ValueError: If z0 <= 0 or p not in (0,1)
	"""
	if z0 <= 0.0:
		raise ValueError(f"initial cost z0 should be positive z0={z0}")
	if p <= 0 or p >= 1:
		raise ValueError("receptive ratio p should be in the range (0,1)")
	delta = w * z0
	t_start = -delta / math.log(p)
	return t_start

def _assert_len_equal(w_list: List[float], reward_list: List[float], theta_list: List[int]) -> None:
	"""Assert that three lists have equal length.
	
	Args:
		w_list: List of weights
		reward_list: List of rewards
		theta_list: List of usage counts
		
	Raises:
		AssertionError: If lists have different lengths
	"""
	assert len(w_list) == len(reward_list) and len(theta_list) == len(w_list)

def adaptive_large_neighbourhood_search(meta_obj: Meta, initial_solution: PDWTWSolution, insert_unlimited: bool,
                                        stop_if_all_request_coped: bool) -> Tuple[PDWTWSolution, int]:
	"""Adaptive Large Neighbourhood Search (ALNS) algorithm for PDWTW problems.
	
	This function implements the ALNS metaheuristic which iteratively improves
	a solution by destroying and repairing it using various operators. The algorithm
	adaptively adjusts operator weights based on their performance and uses
	simulated annealing for acceptance decisions.
	
	Args:
		meta_obj: Meta object containing problem instance and parameters
		initial_solution: Starting solution to improve
		insert_unlimited: Whether to allow unlimited insertions
		
	Returns:
		Best solution found during the search
		
	Raises:
		AssertionError: If meta_obj doesn't match initial_solution.meta_obj
		ValueError: If parameters are invalid
		:param stop_if_all_request_coped:
	"""
	# Input validation
	if meta_obj is None:
		raise ValueError("meta_obj cannot be None")
	if initial_solution is None:
		raise ValueError("initial_solution cannot be None")
	if not isinstance(insert_unlimited, bool):
		raise ValueError("insert_unlimited must be a boolean")
	
	assert meta_obj is initial_solution.meta_obj
	
	# Validate algorithm parameters
	if meta_obj.parameters.iteration_num <= 0:
		raise ValueError("iteration_num must be positive")
	if meta_obj.parameters.remove_lower_bound < 0:
		raise ValueError("remove_lower_bound must be non-negative")
	if meta_obj.parameters.remove_upper_bound <= 0:
		raise ValueError("remove_upper_bound must be positive")
	if meta_obj.parameters.epsilon <= 0 or meta_obj.parameters.epsilon > 1:
		raise ValueError("epsilon must be in (0, 1]")
	if meta_obj.parameters.initial_weight <= 0:
		raise ValueError("initial_weight must be positive")
	if meta_obj.parameters.w <= 0:
		raise ValueError("w parameter must be positive")
	if meta_obj.parameters.annealing_p <= 0 or meta_obj.parameters.annealing_p >= 1:
		raise ValueError("annealing_p must be in (0, 1)")
	if meta_obj.parameters.c <= 0 or meta_obj.parameters.c >= 1:
		raise ValueError("cooling factor c must be in (0, 1)")
	if meta_obj.parameters.r < 0 or meta_obj.parameters.r > 1:
		raise ValueError("learning rate r must be in [0, 1]")
	
	# Determine removal bounds based on problem size and parameters
	requests_num = len(meta_obj.requests)
	q_upper_bound = min(meta_obj.parameters.remove_upper_bound, int(meta_obj.parameters.epsilon * requests_num))
	q_lower_bound = meta_obj.parameters.remove_lower_bound
	
	# Validate removal bounds
	if q_upper_bound < q_lower_bound:
		raise ValueError(f"q_upper_bound ({q_upper_bound}) must be >= q_lower_bound ({q_lower_bound})")
	if q_lower_bound < 1:
		raise ValueError("q_lower_bound must be at least 1")
	
	# Initialize removal operators with equal weights
	w_removal = [meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight]
	removal_function_list = [shaw_removal, random_removal, worst_removal]
	removal_rewards = [0, 0, 0]  # Cumulative rewards for each operator
	removal_theta = [0, 0, 0]    # Usage count for each operator
	
	# Initialize insertion operators (greedy + regret-k with varying k values)
	m = len(initial_solution.paths) + len(initial_solution.vehicle_bank)
	w_insertion = [meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight]
	insertion_function_list = [basic_greedy_insertion, regret_insertion_wrapper(2), regret_insertion_wrapper(3),
	                           regret_insertion_wrapper(4), regret_insertion_wrapper(m)]
	insertion_rewards = [0, 0, 0, 0, 0]  # Cumulative rewards for each operator
	insertion_theta = [0, 0, 0, 0, 0]    # Usage count for each operator

	# Initialize noise operators (with/without objective noise - part 3.6 in the paper)
	w_noise = [meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight]
	noise_rewards = [0, 0]  # Cumulative rewards for each noise option
	noise_theta = [0, 0]    # Usage count for each noise option
	max_distance = meta_obj.get_max_distance()
	noise_function_list = [_objective_noise_wrapper(meta_obj, False, max_distance),
	                       _objective_noise_wrapper(meta_obj, True, max_distance)]

	# Initialize solution tracking
	s_best = initial_solution.copy()  # Best solution found so far
	s = initial_solution.copy()       # Current solution

	# Initialize simulated annealing temperature
	t_start = _compute_initial_temperature(initial_solution.objective_cost_without_request_bank, meta_obj.parameters.w, meta_obj.parameters.annealing_p)
	t_current = t_start

	accepted_solution_set: set = set()  # Track accepted solution fingerprints to avoid cycles
	
	# Main ALNS loop
	print('start alns loop, total iteration_num : ', meta_obj.parameters.iteration_num)
	total_iteration_num = 0
	while total_iteration_num <  meta_obj.parameters.iteration_num:
		print("alns loop index : ", total_iteration_num)
		
		# Randomly select number of requests to remove
		q = random.randint(q_lower_bound, q_upper_bound)
		
		# Select operators using adaptive weights
		remove_func, remove_func_idx = _select_function_with_weight(removal_function_list, w_removal)
		insertion_func, insertion_func_idx = _select_function_with_weight(insertion_function_list, w_insertion)

		# Select noise function (note: uses global random state, tests should not run in parallel)
		noise_func, noise_func_idx = _select_function_with_weight(noise_function_list, w_noise)
		
		# Track operator usage
		removal_theta[remove_func_idx] += 1
		insertion_theta[insertion_func_idx] += 1
		noise_theta[noise_func_idx] += 1
		
		# Apply to destroy and repair operations
		s_p = s.copy()  # Create candidate solution
		remove_func(meta_obj, s_p, q)  # Destroy: remove q requests
		insertion_func(meta_obj, s_p, q, insert_unlimited, noise_func)  # Repair: reinsert requests
		
		# Skip if this solution configuration was already explored
		# finger_print唯一性依赖，需保证finger_print实现唯一且不可变
		if s_p.finger_print in accepted_solution_set:
			total_iteration_num += 1
			continue

		# Check if new best solution found
		is_new_best = False
		if s_p.objective_cost < s_best.objective_cost:
			is_new_best = True
			s_best = s_p.copy()
			# Reward operators for finding new best solution
			removal_rewards[remove_func_idx] += meta_obj.parameters.reward_adds[0]
			insertion_rewards[insertion_func_idx] += meta_obj.parameters.reward_adds[0]
			noise_rewards[noise_func_idx] += meta_obj.parameters.reward_adds[0]

		# Solution acceptance logic (simulated annealing)
		is_accepted = False
		if s_p.objective_cost <= s.objective_cost:
			# Accept improving solutions
			is_accepted = True
			s = s_p.copy()
			if not is_new_best:
				# Reward for improving current solution (but not global best)
				removal_rewards[remove_func_idx] += meta_obj.parameters.reward_adds[1]
				insertion_rewards[insertion_func_idx] += meta_obj.parameters.reward_adds[1]
				noise_rewards[noise_func_idx] += meta_obj.parameters.reward_adds[1]
		else:
			# Consider accepting worse solutions based on temperature
			delta_objective_cost = s_p.objective_cost - s.objective_cost
			accept_ratio = math.exp((-1 * delta_objective_cost) / t_current)
			accept_random = random.random()
			if accept_random <= accept_ratio:
				# Accept worse solution with probability based on temperature
				is_accepted = True
				s = s_p.copy()
				# Reward for diversification
				removal_rewards[remove_func_idx] += meta_obj.parameters.reward_adds[2]
				insertion_rewards[insertion_func_idx] += meta_obj.parameters.reward_adds[2]
				noise_rewards[noise_func_idx] += meta_obj.parameters.reward_adds[2]

		# Track accepted solutions to avoid revisiting
		if is_accepted:
			accepted_solution_set.add(s_p.finger_print)
			# 控制accepted_solution_set最大容量，避免内存溢出
			if len(accepted_solution_set) > ACCEPTED_SET_MAXLEN:
				accepted_solution_set.pop()

		# Adaptive weight update at segment boundaries
		if ((total_iteration_num + 1) % meta_obj.parameters.segment_num) == 0:
			# Update removal operator weights based on performance
			_assert_len_equal(w_removal, removal_theta, removal_rewards)
			w_removal = [max(1e-8, (1 - meta_obj.parameters.r) * origin_w + meta_obj.parameters.r * (new_reward / new_theta) if new_theta > 0 else origin_w) for origin_w, new_reward, new_theta in zip(w_removal, removal_rewards, removal_theta)]
			
			# Update insertion operator weights based on performance
			_assert_len_equal(w_insertion, insertion_rewards, insertion_theta)
			w_insertion = [max(1e-8, (1 - meta_obj.parameters.r) * origin_w + meta_obj.parameters.r * (new_reward / new_theta) if new_theta > 0 else origin_w) for origin_w, new_reward, new_theta in zip(w_insertion, insertion_rewards, insertion_theta)]
			
			# Update noise operator weights based on performance
			_assert_len_equal(w_noise, noise_rewards, noise_theta)
			w_noise = [max(1e-8, (1 - meta_obj.parameters.r) * origin_w + meta_obj.parameters.r * (new_noise / new_theta) if new_theta > 0 else origin_w) for origin_w, new_noise, new_theta in zip(w_noise, noise_rewards, noise_theta)]

			# Reset statistics for next segment
			removal_rewards = [0, 0, 0]
			removal_theta = [0, 0, 0]
			insertion_rewards = [0, 0, 0, 0, 0]
			insertion_theta = [0, 0, 0, 0, 0]
			noise_rewards = [0, 0]
			noise_theta = [0, 0]

		# Cool down temperature for simulated annealing (prevent underflow)
		t_current = max(1e-10, t_current * meta_obj.parameters.c)
		total_iteration_num += 1
		if stop_if_all_request_coped and 0 == len(s_best.request_bank):
			break

	# Return the best solution found
	return s_best, total_iteration_num
