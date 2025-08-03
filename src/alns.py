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

_iteration_num = 25000
_ep_tion = 0.4

_w = 0.05
_p = 0.5

# this parameter seems not to be set in the paper
_initial_weight = 1

_c = 0.99975
_r = 0.1
_segment_num = 100
_reward_adds = [33, 9, 13]

_eta = 0.025

def _objective_noise_wrapper(max_distance: float, use_noise: bool):
	def _objective_noise(cost: float):
		if use_noise:
			noise = _eta * max_distance
			return max(0.0, random.uniform(-noise, noise) + cost)
		return cost
	return _objective_noise

def _select_function_with_weight(funcs, weights):
	selected_index = random.choices(
		range(len(funcs)),
		weights=weights,
		k=1
	)[0]

	return funcs[selected_index], selected_index

def _compute_initial_temperature(z0: float, w: float, p: float) -> float:
	if p <= 0 or p >= 1:
		raise ValueError("receptive ratio p should be in the range (0,1)")
	delta = w * z0
	t_start = -delta / math.log(p)
	return t_start

def adaptive_large_neighbourhood_search(meta_obj: Meta, initial_solution: PDWTWSolution):
	requests_num = len(meta_obj.requests)
	q_upper_bound = min(100, int(_ep_tion * requests_num))
	q_lower_bound = 4
	
	w_removal = [_initial_weight, _initial_weight, _initial_weight]
	removal_function_list = [shaw_removal, random_removal, worst_removal]
	removal_rewards = [0, 0, 0]
	removal_theta = [0, 0, 0]
	
	m = len(initial_solution.paths) + len(initial_solution.vehicle_bank)
	w_insertion = [_initial_weight, _initial_weight, _initial_weight, _initial_weight, _initial_weight]
	insertion_function_list = [basic_greedy_insertion, regret_insertion_wrapper(2), regret_insertion_wrapper(3),
	                           regret_insertion_wrapper(4), regret_insertion_wrapper(m)]
	insertion_rewards = [0, 0, 0, 0, 0]
	insertion_theta = [0, 0, 0, 0, 0]

	# part 3.6 in the paper
	w_noise = [_initial_weight, _initial_weight]
	noise_rewards = [0, 0]
	noise_theta = [0, 0]
	max_distance = meta_obj.get_max_distance()
	noise_function_list = [_objective_noise_wrapper(max_distance, False), _objective_noise_wrapper(max_distance, True)]

	s_best = initial_solution.copy()
	s = initial_solution.copy()

	t_start = _compute_initial_temperature(initial_solution.objective_cost_without_request_bank, _w, _p)
	t_current = t_start

	accepted_solution_set = set()
	
	for i in range(0, _iteration_num):
		q = random.randint(q_lower_bound, q_upper_bound)
		
		remove_func, remove_func_idx = _select_function_with_weight(removal_function_list, w_removal)
		insertion_func, insertion_func_idx = _select_function_with_weight(insertion_function_list, w_insertion)

		insertion.global_noise_func, noise_func_idx = _select_function_with_weight(noise_function_list, w_noise)
		
		removal_theta[remove_func_idx] += 1
		insertion_theta[insertion_func_idx] += 1
		noise_theta[noise_func_idx] += 1
		
		s_p = s.copy()
		remove_func(meta_obj, s_p, q)
		insertion_func(meta_obj, s_p, q)
		
		if s_p.finger_print in accepted_solution_set:
			continue

		is_new_best = False
		if s_p.objective_cost < s_best.objective_cost:
			is_new_best = True
			s_best = s_p.copy()
			removal_rewards[remove_func_idx] += _reward_adds[0]
			insertion_rewards[insertion_func_idx] += _reward_adds[0]
			
			noise_theta[noise_func_idx] += _reward_adds[0]

		# accept logic
		is_accepted = False
		if s_p.objective_cost <= s.objective_cost:
			is_accepted = True
			s = s_p.copy()
			if not is_new_best:
				removal_rewards[remove_func_idx] += _reward_adds[1]
				insertion_rewards[insertion_func_idx] += _reward_adds[1]
				
				noise_theta[noise_func_idx] += _reward_adds[1]
		else:
			delta_objective_cost = s_p.objective_cost - s.objective_cost
			accept_ratio = math.exp((-1 * delta_objective_cost) / t_current)
			accept_random = random.random()
			if accept_random <= accept_ratio:
				is_accepted = True
				s = s_p.copy()
				removal_rewards[remove_func_idx] += _reward_adds[2]
				insertion_rewards[insertion_func_idx] += _reward_adds[2]
				
				noise_theta[noise_func_idx] += _reward_adds[2]

		if is_accepted:
			accepted_solution_set.add(s_p.finger_print)
		
		if ((i + 1) % _segment_num) == 0:
			assert len(w_removal) == len(removal_rewards) and len(removal_rewards) == len(removal_theta)
			w_removal = [(1 - _r) * origin_w + _r * (new_reward / new_theta) for origin_w, new_reward, new_theta in zip(w_removal, removal_rewards, removal_theta)]
			
			assert len(w_insertion) == len(insertion_rewards) and len(insertion_rewards) == len(insertion_theta)
			w_insertion = [(1 - _r) * origin_w + _r * (new_reward / new_theta) for origin_w, new_reward, new_theta in zip(w_insertion, insertion_rewards, insertion_theta)]
			
			assert len(w_noise) == len(noise_rewards) and len(noise_rewards) == len(noise_theta)
			w_noise = [(1 - _r) * origin_w + _r * (new_noise / new_theta) for origin_w, new_noise, new_theta in zip(w_noise, noise_rewards, noise_theta)]

			removal_rewards = [0, 0, 0]
			removal_theta = [0, 0, 0]
			
			insertion_rewards = [0, 0, 0, 0]
			insertion_theta = [0, 0, 0, 0]
			
			# optional
			noise_rewards = [0, 0]
			noise_theta = [0, 0]

		t_current *= _c
