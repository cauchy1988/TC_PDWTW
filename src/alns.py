#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/25 11:49
# @Author: Tang Chao
# @File: alns.py
# @Software: PyCharm
from meta import Meta
from solution import PDWTWSolution
from removal import *
from insertion import *
import insertion
import random
import math

def _objective_noise_wrapper(meta_obj: Meta, use_noise: bool, max_distance: float):
	def _objective_noise(cost: float) -> float:
		nonlocal meta_obj, max_distance
		if use_noise:
			noise = meta_obj.parameters.eta * max_distance
			return float(max(0.0, random.uniform(-noise, noise) + cost))
		return cost
	return _objective_noise

def _select_function_with_weight(funcs, weights):
	if len(funcs) != len(weights):
		raise ValueError('weights must have same length as funcs!')
	selected_index = random.choices(
		range(len(funcs)),
		weights=weights,
		k=1
	)[0]

	return funcs[selected_index], selected_index

def _compute_initial_temperature(z0: float, w: float, p: float) -> float:
	if z0 <= 0.0:
		raise ValueError("initial cost z0 should be positive")
	if p <= 0 or p >= 1:
		raise ValueError("receptive ratio p should be in the range (0,1)")
	delta = w * z0
	t_start = -delta / math.log(p)
	return t_start

def _assert_len_equal(w_list, reward_list, theta_list):
	assert len(w_list) == len(reward_list) and len(theta_list) == len(w_list)

def adaptive_large_neighbourhood_search(meta_obj: Meta, initial_solution: PDWTWSolution, insert_unlimited: bool) -> PDWTWSolution:
	assert meta_obj is initial_solution.meta_obj
	
	requests_num = len(meta_obj.requests)
	q_upper_bound = min(meta_obj.parameters.remove_upper_bound, int(meta_obj.parameters.epsilon * requests_num))
	q_lower_bound = meta_obj.parameters.remove_lower_bound
	
	w_removal = [meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight]
	removal_function_list = [shaw_removal, random_removal, worst_removal]
	removal_rewards = [0, 0, 0]
	removal_theta = [0, 0, 0]
	
	m = len(initial_solution.paths) + len(initial_solution.vehicle_bank)
	w_insertion = [meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight]
	insertion_function_list = [basic_greedy_insertion, regret_insertion_wrapper(2), regret_insertion_wrapper(3),
	                           regret_insertion_wrapper(4), regret_insertion_wrapper(m)]
	insertion_rewards = [0, 0, 0, 0, 0]
	insertion_theta = [0, 0, 0, 0, 0]

	# part 3.6 in the paper
	w_noise = [meta_obj.parameters.initial_weight, meta_obj.parameters.initial_weight]
	noise_rewards = [0, 0]
	noise_theta = [0, 0]
	max_distance = meta_obj.get_max_distance()
	noise_function_list = [_objective_noise_wrapper(meta_obj, False, max_distance),
	                       _objective_noise_wrapper(meta_obj, True, max_distance)]

	s_best = initial_solution.copy()
	s = initial_solution.copy()

	t_start = _compute_initial_temperature(initial_solution.objective_cost_without_request_bank, meta_obj.parameters.w, meta_obj.parameters.annealing_p)
	t_current = t_start

	accepted_solution_set = set()
	
	for i in range(0, meta_obj.parameters.iteration_num):
		q = random.randint(q_lower_bound, q_upper_bound)
		
		remove_func, remove_func_idx = _select_function_with_weight(removal_function_list, w_removal)
		insertion_func, insertion_func_idx = _select_function_with_weight(insertion_function_list, w_insertion)

		# it uses a global variable thus tests should not be in parallel!!!
		noise_func, noise_func_idx = _select_function_with_weight(noise_function_list, w_noise)
		
		removal_theta[remove_func_idx] += 1
		insertion_theta[insertion_func_idx] += 1
		noise_theta[noise_func_idx] += 1
		
		s_p = s.copy()
		remove_func(meta_obj, s_p, q)
		insertion_func(meta_obj, s_p, q, insert_unlimited, noise_func)
		
		if s_p.finger_print in accepted_solution_set:
			continue

		is_new_best = False
		if s_p.objective_cost < s_best.objective_cost:
			is_new_best = True
			s_best = s_p.copy()
			removal_rewards[remove_func_idx] += meta_obj.parameters.reward_adds[0]
			insertion_rewards[insertion_func_idx] += meta_obj.parameters.reward_adds[0]
			
			noise_theta[noise_func_idx] += meta_obj.parameters.reward_adds[0]

		# accept logic
		is_accepted = False
		if s_p.objective_cost <= s.objective_cost:
			is_accepted = True
			s = s_p.copy()
			if not is_new_best:
				removal_rewards[remove_func_idx] += meta_obj.parameters.reward_adds[1]
				insertion_rewards[insertion_func_idx] += meta_obj.parameters.reward_adds[1]
				
				noise_rewards[noise_func_idx] += meta_obj.parameters.reward_adds[1]
		else:
			delta_objective_cost = s_p.objective_cost - s.objective_cost
			accept_ratio = math.exp((-1 * delta_objective_cost) / t_current)
			accept_random = random.random()
			if accept_random <= accept_ratio:
				is_accepted = True
				s = s_p.copy()
				removal_rewards[remove_func_idx] += meta_obj.parameters.reward_adds[2]
				insertion_rewards[insertion_func_idx] += meta_obj.parameters.reward_adds[2]
				
				noise_rewards[noise_func_idx] += meta_obj.parameters.reward_adds[2]

		if is_accepted:
			accepted_solution_set.add(s_p.finger_print)
		
		if ((i + 1) % meta_obj.parameters.segment_num) == 0:
			_assert_len_equal(w_removal, removal_theta, removal_rewards)
			w_removal = [0 if new_theta <= 1e6 else (1 - meta_obj.parameters.r) * origin_w + meta_obj.parameters.r * (new_reward / new_theta) for origin_w, new_reward, new_theta in zip(w_removal, removal_rewards, removal_theta)]
			
			_assert_len_equal(w_insertion, insertion_rewards, insertion_theta)
			w_insertion = [0 if new_theta <= 1e6 else (1 - meta_obj.parameters.r) * origin_w + meta_obj.parameters.r * (new_reward / new_theta) for origin_w, new_reward, new_theta in zip(w_insertion, insertion_rewards, insertion_theta)]
			
			_assert_len_equal(w_noise, noise_rewards, noise_theta)
			w_noise = [0 if new_theta <= 1e6 else (1 - meta_obj.parameters.r) * origin_w + meta_obj.parameters.r * (new_noise / new_theta) for origin_w, new_noise, new_theta in zip(w_noise, noise_rewards, noise_theta)]

			removal_rewards = [0, 0, 0]
			removal_theta = [0, 0, 0]
			
			insertion_rewards = [0, 0, 0, 0, 0]
			insertion_theta = [0, 0, 0, 0, 0]
			
			# optional
			noise_rewards = [0, 0]
			noise_theta = [0, 0]

		t_current *= meta_obj.parameters.c
		
	return s_best
