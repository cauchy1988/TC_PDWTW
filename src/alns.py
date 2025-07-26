#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/25 11:49
# @Author  : Tang Chao
# @File    : alns.py
# @Software: PyCharm
from meta import Meta
from solution import PDWTWSolution
from removal import *
from insertion import *
import random

_iteration_num = 25000
_ep_tion = 0.4

_w = 0.05
_c = 0.99975
_r = 0.1
_segment_num = 100
_reward_adds = [33, 9, 13]


def _select_function_with_weight(funcs, weights):
	"""
	根据权重随机选择一个函数及其下标
	:param funcs: 函数列表
	:param weights: 对应的权重列表
	:return: (选中的函数, 下标)
	"""
	# 使用random.choices根据权重选择下标
	selected_index = random.choices(
		range(len(funcs)),  # 生成下标列表[0,1,2...]
		weights=weights,    # 对应的权重
		k=1                 # 选择1个元素
	)[0]  # 提取结果中的第一个元素（整数下标）

	return funcs[selected_index], selected_index


def adaptive_large_neighbourhood_search(meta_obj: Meta, initial_solution: PDWTWSolution):
	requests_num = len(meta_obj.requests)
	q_upper_bound = min(100, int(_ep_tion * requests_num))
	q_lower_bound = 4
	
	w_removal = [_w, _w, _w]
	removal_function_list = [shaw_removal, random_removal, worst_removal]
	removal_rewards = [0, 0, 0]
	removal_theta = [0, 0, 0]
	
	m = len(initial_solution.paths) + len(initial_solution.vehicle_bank)
	w_insertion = [_w, _w, _w, _w, _w]
	insertion_function_list = [basic_greedy_insertion, regret_insertion_wrapper(2), regret_insertion_wrapper(3),
	                           regret_insertion_wrapper(4), regret_insertion_wrapper(m)]
	insertion_rewards = [0, 0, 0, 0, 0]
	insertion_theta = [0, 0, 0, 0, 0]
	
	s_best = initial_solution.copy()
	s = initial_solution.copy()
	for i in range(0, _iteration_num):
		q = random.randint(q_lower_bound, q_upper_bound)
		
		remove_func, remove_func_idx = _select_function_with_weight(removal_function_list, w_removal)
		insertion_func, insertion_func_idx = _select_function_with_weight(insertion_function_list, w_insertion)
		
		removal_theta[remove_func_idx] += 1
		insertion_theta[insertion_func_idx] += 1
		
		s_p = s.copy()
		remove_func(meta_obj, s_p, q)
		insertion_func(meta_obj, s_p, q)
		
		# TODO: check accepted solution
		
		if s_p.objective_cost < s_best.objective_cost:
			s_best = s_p.copy()
			removal_rewards[remove_func_idx] += _reward_adds[0]
			insertion_rewards[insertion_func_idx] += _reward_adds[0]

		# accept logic
		if s_p.objective_cost <= s.objective_cost:
			s = s_p.copy()
			removal_rewards[remove_func_idx] += _reward_adds[1]
			insertion_rewards[insertion_func_idx] += _reward_adds[1]
		else:
			# TODO: simulated annealing logic
			pass
